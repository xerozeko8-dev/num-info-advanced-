import time
import requests
import phonenumbers
from flask import Flask, jsonify, request, render_template_string
from phonenumbers import carrier, geocoder, timezone
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

app = Flask(__name__)

# ==========================================
# 1. CONFIGURATION (STRICT MODE)
# ==========================================
BASE_API_URL = "https://zkwuyi37gjfhgslglaielyawfjha3w.vercel.app/query"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# Retry Strategy (To handle 5 sec delay)
session = requests.Session()
retries = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
session.mount('https://', HTTPAdapter(max_retries=retries))

# ==========================================
# 2. FRONTEND (Hacker UI + Three.js)
# ==========================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HIMANSHU | STRICT INTEL</title>
    <style>
        body { margin: 0; overflow: hidden; background: #000; font-family: 'Courier New', monospace; color: #0f0; }
        #canvas-container { position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: -1; }
        
        #ui-layer {
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            overflow-y: auto; display: flex; flex-direction: column; align-items: center;
            padding-top: 50px; background: rgba(0, 0, 0, 0.8);
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
            background: rgba(0, 15, 0, 0.95); border: 1px solid #0f0; padding: 25px; border-radius: 4px;
            box-shadow: 0 0 30px rgba(0, 255, 0, 0.1); backdrop-filter: blur(5px);
        }

        /* MAIN API CARD */
        #main-api-section { border: 2px solid #00eaff; box-shadow: 0 0 30px rgba(0, 234, 255, 0.15); }
        #main-api-section h2 { color: #00eaff; border-bottom: 1px dashed #00eaff; text-shadow: 0 0 8px #00eaff; }

        h2 { margin-top: 0; font-size: 22px; padding-bottom: 8px; letter-spacing: 1px; }
        .data-row { display: flex; justify-content: space-between; margin: 12px 0; border-bottom: 1px solid rgba(0,255,0,0.2); padding-bottom: 5px; }
        .label { font-weight: bold; opacity: 0.8; }
        .value { text-align: right; font-weight: bold; color: #fff; }

        /* Loader */
        .loading { display: none; font-size: 18px; color: #00eaff; margin-bottom: 20px; letter-spacing: 2px; }
        .blink { animation: blinker 0.5s linear infinite; }
        @keyframes blinker { 50% { opacity: 0; } }

        /* Error Box */
        .error-msg { color: #ff0055; font-weight: bold; margin-top: 20px; text-shadow: 0 0 10px #ff0055; display: none; }

    </style>
</head>
<body>
    <div id="canvas-container"></div>

    <div id="ui-layer">
        <h1>TARGET ACQUISITION</h1>
        
        <div class="search-box">
            <input type="text" id="phoneInput" placeholder="ENTER TARGET NUMBER" maxlength="10">
            <button onclick="fetchData()">EXECUTE</button>
        </div>

        <div class="loading" id="loader">
            <span class="blink">>> ACCESSING CLASSIFIED DATABASE...</span>
        </div>

        <div class="error-msg" id="error-box"></div>

        <div class="container" id="results">
            <div class="card" id="main-api-section">
                <h2>⚡ IDENTITY CONFIRMED</h2>
                <div id="main-content"></div>
            </div>
        </div>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script>
        // THREE.JS ANIMATION (Matrix Rain Effect)
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({ alpha: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        document.getElementById('canvas-container').appendChild(renderer.domElement);

        const geometry = new THREE.BufferGeometry();
        const count = 4000;
        const positions = new Float32Array(count * 3);
        for(let i=0; i<count*3; i++) {
            positions[i] = (Math.random()-0.5) * 200;
        }
        geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        const material = new THREE.PointsMaterial({ size: 0.3, color: 0x00ff00 });
        const particles = new THREE.Points(geometry, material);
        scene.add(particles);
        camera.position.z = 50;

        function animate() {
            requestAnimationFrame(animate);
            particles.rotation.y += 0.002; // Rotate
            particles.position.z += 0.1;   // Move forward
            if(particles.position.z > 20) particles.position.z = -20;
            renderer.render(scene, camera);
        }
        animate();

        // FETCH LOGIC
        async function fetchData() {
            const num = document.getElementById('phoneInput').value;
            const loader = document.getElementById('loader');
            const results = document.getElementById('results');
            const errorBox = document.getElementById('error-box');
            
            if(!num || num.length < 10) { 
                showError("INVALID INPUT FORMAT"); return; 
            }

            // Reset UI
            loader.style.display = 'block';
            results.style.display = 'none';
            errorBox.style.display = 'none';

            try {
                const response = await fetch(`/api/search?number=${num}`);
                const data = await response.json();
                
                if(!response.ok) {
                    throw new Error(data.error || "CONNECTION REFUSED");
                }

                render(data);
                loader.style.display = 'none';
                results.style.display = 'flex';
            } catch(e) {
                loader.style.display = 'none';
                showError(e.message);
            }
        }

        function showError(msg) {
            const errorBox = document.getElementById('error-box');
            errorBox.innerHTML = `>> ERROR: ${msg}`;
            errorBox.style.display = 'block';
        }

        function render(data) {
            const m = data.data;
            let html = "";
            
            html += row("FULL NAME", m.name, "#00eaff");
            html += row("ADDRESS", m.address, "#fff");
            html += row("FATHER NAME", m.father, "#fff");
            html += row("EMAIL", m.email, "#fff");
            html += row("CARRIER (SIM)", m.carrier, "#0f0");
            html += row("LOCATION", m.location, "#0f0");
            
            if(m.alt_phones.length) {
                html += row("LINKED CONTACTS", m.alt_phones.join('<br>'), "#ff0055");
            }

            document.getElementById('main-content').innerHTML = html;
        }

        function row(label, value, color) {
            if(!value || value == "N/A") return "";
            return `<div class="data-row"><span class="label">${label}:</span> <span class="value" style="color:${color}">${value}</span></div>`;
        }
    </script>
</body>
</html>
"""

# ==========================================
# 3. BACKEND ROUTES (STRICT LOGIC)
# ==========================================

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/search')
def api_search():
    raw_num = request.args.get('number', '')
    clean_num = "".join(filter(str.isdigit, raw_num))
    
    if len(clean_num) < 10:
        return jsonify({"error": "INVALID NUMBER LENGTH"}), 400

    # 1. Main API Call (STRICT - MUST SUCCEED)
    try:
        # 25s timeout for safety
        res = session.get(BASE_API_URL, params={'q': clean_num}, headers=HEADERS, timeout=25)
        
        if res.status_code != 200:
            # AGAR MAIN API FAIL HUI, TOH ABORT KAR DO.
            return jsonify({"error": "DATABASE OFFLINE / NO RECORD FOUND"}), 404
            
        json_data = res.json()
        raw_list = json_data.get('data', [])

        if not raw_list:
            return jsonify({"error": "TARGET NOT FOUND IN MAIN DB"}), 404

    except Exception as e:
        # AGAR TIMEOUT YA ERROR AAYA, TOH BHI RETURN ERROR
        print(f"API Error: {e}")
        return jsonify({"error": "SERVER CONNECTION FAILED"}), 500

    # 2. DATA CLEANING & PROCESSING
    profile = {
        "name": "N/A", "father": "N/A", "address": "N/A", 
        "email": "N/A", "alt_phones": [],
        "carrier": "N/A", "location": "N/A"
    }

    for item in raw_list:
        # --- REMOVE BAD LINES ---
        # Wo lambi TrueCaller wali line ko detect karke skip kar rahe hain
        source = item.get('source_database', '')
        if "In February" in source or "leaked to data" in source:
             item['source_database'] = "Verified DB" # Clean replacement
        
        # Remove 'total_results' key (waise ye list ke bahar hota hai usually, but safety)
        if 'total_results' in item:
            del item['total_results']

        # Fix spelling
        if 'adres' in item: item['address'] = item.pop('adres')

        # Extract Info
        if item.get('full_name'): profile['name'] = item['full_name']
        if item.get('the_name_of_the_father'): profile['father'] = item['the_name_of_the_father']
        if item.get('address'): profile['address'] = item['address']
        if item.get('email'): profile['email'] = item['email']
        if item.get('telephone') and item['telephone'] != clean_num: 
            profile['alt_phones'].append(item['telephone'])

    # 3. Add Local Data (ONLY IF MAIN API SUCCEEDED)
    try:
        pn = phonenumbers.parse("+91" + clean_num[-10:], "IN")
        profile['carrier'] = carrier.name_for_number(pn, "en")
        profile['location'] = geocoder.description_for_number(pn, "en")
    except:
        pass

    profile['alt_phones'] = list(set(profile['alt_phones']))

    return jsonify({"data": profile})

if __name__ == '__main__':
    print("STRICT SERVER STARTED: http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, threaded=True)
