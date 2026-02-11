import time
import requests
import phonenumbers
from flask import Flask, jsonify, request, render_template_string
from phonenumbers import carrier, geocoder, timezone
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

app = Flask(__name__)

# ==========================================
# 1. ROBUST CONFIGURATION
# ==========================================
BASE_API_URL = "https://zkwuyi37gjfhgslglaielyawfjha3w.vercel.app/query"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# --- RETRY SESSION (Connection Tute Na) ---
# Ye setup automatic 3 baar try karega agar API 5 sec se zyada le rahi hai
session = requests.Session()
retries = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
session.mount('https://', HTTPAdapter(max_retries=retries))

# ==========================================
# 2. FRONTEND (3D Hacker Theme)
# ==========================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HIMANSHU | TARGET TRACKER</title>
    <style>
        body { margin: 0; overflow: hidden; background: #000; font-family: 'Courier New', monospace; color: #0f0; }
        #canvas-container { position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: -1; }
        
        #ui-layer {
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            overflow-y: auto; display: flex; flex-direction: column; align-items: center;
            padding-top: 40px; background: rgba(0, 0, 0, 0.75);
        }

        h1 { text-shadow: 0 0 15px #0f0; letter-spacing: 3px; border-bottom: 2px solid #0f0; padding-bottom: 10px; }

        .search-box { display: flex; gap: 10px; margin-bottom: 20px; z-index: 100; }
        input {
            background: #001100; border: 1px solid #0f0; color: #0f0; padding: 12px; font-size: 18px; outline: none; width: 280px;
            box-shadow: inset 0 0 10px #0f0; font-family: monospace; font-weight: bold;
        }
        button {
            background: #0f0; color: #000; border: none; padding: 10px 25px; font-size: 18px; cursor: pointer; font-weight: 900;
            box-shadow: 0 0 15px #0f0; transition: 0.2s;
        }
        button:hover { background: #fff; box-shadow: 0 0 30px #fff; transform: scale(1.05); }

        .container { width: 90%; max-width: 700px; display: none; flex-direction: column; gap: 25px; padding-bottom: 60px; }

        .card {
            background: rgba(0, 15, 0, 0.9); border: 1px solid #0f0; padding: 25px; border-radius: 8px;
            box-shadow: 0 0 20px rgba(0, 255, 0, 0.15); backdrop-filter: blur(10px);
            position: relative;
        }

        /* UPPER SECTION - NEON BLUE (MAIN API) */
        #main-api-section { border: 2px solid #00eaff; box-shadow: 0 0 25px rgba(0, 234, 255, 0.2); }
        #main-api-section h2 { color: #00eaff; border-bottom: 1px dashed #00eaff; text-shadow: 0 0 8px #00eaff; }
        
        /* LOWER SECTION - GREEN (LOCAL API) */
        #local-api-section { border: 2px solid #0f0; }

        h2 { margin-top: 0; font-size: 22px; padding-bottom: 8px; letter-spacing: 1px; }
        .data-row { display: flex; justify-content: space-between; margin: 12px 0; border-bottom: 1px solid rgba(0,255,0,0.2); padding-bottom: 5px; }
        .label { font-weight: bold; opacity: 0.8; }
        .value { text-align: right; font-weight: bold; text-shadow: 0 0 2px currentColor; }

        /* Loader */
        .loading { display: none; font-size: 20px; color: #00eaff; text-shadow: 0 0 10px #00eaff; margin-bottom: 20px; }
        .blink { animation: blinker 1s linear infinite; }
        @keyframes blinker { 50% { opacity: 0; } }

    </style>
</head>
<body>
    <div id="canvas-container"></div>

    <div id="ui-layer">
        <h1>CYBER INTEL V2.0</h1>
        
        <div class="search-box">
            <input type="text" id="phoneInput" placeholder="Enter 10 Digit Number" maxlength="10">
            <button onclick="fetchData()">SEARCH</button>
        </div>

        <div class="loading" id="loader">
            <span class="blink">>> ESTABLISHING SECURE CONNECTION...</span>
        </div>

        <div class="container" id="results">
            <div class="card" id="main-api-section">
                <h2>⚡ TARGET IDENTITY (DEEP SCAN)</h2>
                <div id="main-content"></div>
            </div>

            <div class="card" id="local-api-section">
                <h2>📡 NETWORK TELEMETRY</h2>
                <div id="local-content"></div>
            </div>
        </div>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script>
        // THREE.JS BACKGROUND
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({ alpha: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        document.getElementById('canvas-container').appendChild(renderer.domElement);

        const particles = new THREE.BufferGeometry();
        const count = 3000;
        const posArray = new Float32Array(count * 3);
        for(let i=0; i<count*3; i++) posArray[i] = (Math.random()-0.5) * 150;
        particles.setAttribute('position', new THREE.BufferAttribute(posArray, 3));
        const material = new THREE.PointsMaterial({ size: 0.2, color: 0x00ff00 });
        const mesh = new THREE.Points(particles, material);
        scene.add(mesh);
        camera.position.z = 50;

        function animate() {
            requestAnimationFrame(animate);
            mesh.rotation.y += 0.002;
            mesh.rotation.x += 0.001;
            renderer.render(scene, camera);
        }
        animate();

        // FETCH LOGIC
        async function fetchData() {
            const num = document.getElementById('phoneInput').value;
            const loader = document.getElementById('loader');
            const results = document.getElementById('results');
            
            if(!num || num.length < 10) { alert("Enter valid 10 digit number"); return; }

            loader.style.display = 'block';
            results.style.display = 'none';

            try {
                // Request sent to Python Backend
                const response = await fetch(`/api/search?number=${num}`);
                const data = await response.json();
                
                render(data);
                loader.style.display = 'none';
                results.style.display = 'flex';
            } catch(e) {
                alert("Server Error: Check Console");
                loader.style.display = 'none';
            }
        }

        function render(data) {
            // Main Data Render
            const m = data.main_data;
            let mHtml = "";
            if(m.found) {
                mHtml += row("FULL NAME", m.name, "#00eaff");
                mHtml += row("ADDRESS", m.address, "#fff");
                mHtml += row("FATHER NAME", m.father, "#fff");
                mHtml += row("EMAIL", m.email, "#fff");
                if(m.alt_phones.length) mHtml += row("LINKED NUMBERS", m.alt_phones.join(', '), "#ff0055");
            } else {
                mHtml = "<div style='text-align:center; color:red'>DATA NOT FOUND IN DEEP DB</div>";
            }
            document.getElementById('main-content').innerHTML = mHtml;

            // Local Data Render
            const l = data.local_data;
            let lHtml = "";
            lHtml += row("CARRIER", l.carrier, "#0f0");
            lHtml += row("LOCATION", l.location, "#0f0");
            lHtml += row("TIMEZONE", l.timezone, "#fff");
            document.getElementById('local-content').innerHTML = lHtml;
        }

        function row(label, value, color) {
            if(value == "N/A" || !value) return "";
            return `<div class="data-row"><span class="label">${label}:</span> <span class="value" style="color:${color}">${value}</span></div>`;
        }
    </script>
</body>
</html>
"""

# ==========================================
# 3. BACKEND ROUTES
# ==========================================

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/search')
def api_search():
    raw_num = request.args.get('number', '')
    clean_num = "".join(filter(str.isdigit, raw_num))
    
    # 1. Local Data (Fast)
    try:
        pn = phonenumbers.parse("+91" + clean_num[-10:], "IN")
        local_data = {
            "carrier": carrier.name_for_number(pn, "en"),
            "location": geocoder.description_for_number(pn, "en"),
            "timezone": str(timezone.time_zones_for_number(pn)[0])
        }
    except:
        local_data = {"carrier": "Unknown", "location": "Unknown", "timezone": "N/A"}

    # 2. Main API (Deep) - WITH 20s TIMEOUT
    main_data = {"found": False, "name": "N/A", "father": "N/A", "address": "N/A", "email": "N/A", "alt_phones": []}
    
    try:
        # TIMEOUT BADHA DIYA HAI: 20 SECONDS
        res = session.get(BASE_API_URL, params={'q': clean_num}, headers=HEADERS, timeout=20)
        
        if res.status_code == 200:
            data = res.json().get('data', [])
            if data:
                main_data['found'] = True
                # Clean Data Logic
                for item in data:
                    # Typo fix
                    if 'adres' in item: item['address'] = item.pop('adres')
                    # Spam fix
                    if "In February" in item.get('source_database', ''): item['source_database'] = "Verified"

                    if item.get('full_name'): main_data['name'] = item['full_name']
                    if item.get('the_name_of_the_father'): main_data['father'] = item['the_name_of_the_father']
                    if item.get('address'): main_data['address'] = item['address']
                    if item.get('email'): main_data['email'] = item['email']
                    if item.get('telephone'): main_data['alt_phones'].append(item['telephone'])
                
                # Remove duplicates & current number
                main_data['alt_phones'] = list(set(main_data['alt_phones']))
                
    except Exception as e:
        print(f"Main API Error: {e}") # Terminal mein error dikhega
        # Data found false hi rahega agar error aaya

    return jsonify({
        "local_data": local_data,
        "main_data": main_data
    })

if __name__ == '__main__':
    print("SERVER ON: http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, threaded=True)
