import time
import requests
import phonenumbers
from flask import Flask, jsonify, request, render_template_string
from phonenumbers import carrier, geocoder, timezone
from datetime import datetime

app = Flask(__name__)

# ==========================================
# 1. CONFIGURATION
# ==========================================
BASE_API_URL = "https://zkwuyi37gjfhgslglaielyawfjha3w.vercel.app/query"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# ==========================================
# 2. FRONTEND (HTML + CSS + JS inside Python)
# ==========================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HIMANSHU | CYBER INTEL</title>
    <style>
        body { margin: 0; overflow: hidden; background: #000; font-family: 'Courier New', Courier, monospace; color: #0f0; }
        
        /* 3D Background */
        #canvas-container { position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: -1; }

        /* UI Overlay */
        #ui-layer {
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            overflow-y: auto; display: flex; flex-direction: column; align-items: center;
            padding-top: 50px;
            background: rgba(0, 0, 0, 0.6);
        }

        h1 { text-shadow: 0 0 10px #0f0; letter-spacing: 5px; border-bottom: 2px solid #0f0; padding-bottom: 10px; }

        /* Search Box */
        .search-box { display: flex; gap: 10px; margin-bottom: 30px; z-index: 10; }
        input {
            background: rgba(0, 20, 0, 0.9); border: 1px solid #0f0; color: #0f0; padding: 10px; font-size: 18px; outline: none; width: 300px;
            box-shadow: 0 0 10px #0f0 inset; font-family: monospace;
        }
        button {
            background: #0f0; color: #000; border: none; padding: 10px 20px; font-size: 18px; cursor: pointer; font-weight: bold;
            box-shadow: 0 0 15px #0f0; transition: 0.3s;
        }
        button:hover { background: #fff; box-shadow: 0 0 25px #fff; }

        /* Results Container */
        .container { width: 90%; max-width: 800px; display: none; flex-direction: column; gap: 20px; padding-bottom: 50px; z-index: 10; }

        /* Cards */
        .card {
            background: rgba(0, 10, 0, 0.85); border: 1px solid #0f0; padding: 20px; border-radius: 5px;
            box-shadow: 0 0 20px rgba(0, 255, 0, 0.2); backdrop-filter: blur(5px);
            position: relative; overflow: hidden;
        }
        
        /* Neon Effect for Main Data */
        #main-api-section { border: 2px solid #00ffea; box-shadow: 0 0 25px rgba(0, 255, 234, 0.3); }
        #main-api-section h2 { color: #00ffea; border-color: #00ffea; text-shadow: 0 0 5px #00ffea; }

        h2 { margin-top: 0; color: #fff; text-shadow: 0 0 5px #fff; font-size: 20px; border-bottom: 1px dashed #0f0; padding-bottom: 5px; }
        
        .data-row { display: flex; justify-content: space-between; margin: 10px 0; border-bottom: 1px solid rgba(0, 255, 0, 0.2); padding-bottom: 5px; }
        .label { color: #88ff88; font-weight: bold; }
        .value { color: #fff; text-align: right; word-break: break-all; }

        .loading { color: #0f0; font-size: 20px; display: none; margin-bottom: 20px; }
        
        /* Loader Animation */
        .loader-ring { display: inline-block; width: 20px; height: 20px; border: 3px solid #0f0; border-radius: 50%; border-top-color: transparent; animation: spin 1s linear infinite; margin-right: 10px; vertical-align: middle; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

    </style>
</head>
<body>

    <div id="canvas-container"></div>

    <div id="ui-layer">
        <h1>CYBER INTEL HUB</h1>
        
        <div class="search-box">
            <input type="text" id="phoneInput" placeholder="Enter Indian Number (+91)" maxlength="13">
            <button onclick="fetchData()">SCAN</button>
        </div>

        <div class="loading" id="loader">
            <div class="loader-ring"></div> ACCESSING ENCRYPTED DATABASE...
        </div>

        <div class="container" id="results">
            
            <div class="card" id="main-api-section">
                <h2>⚡ TARGET INTELLIGENCE (DEEP WEB)</h2>
                <div id="main-content"></div>
            </div>

            <div class="card" id="local-api-section">
                <h2>📡 NETWORK SIGNAL DATA</h2>
                <div id="local-content"></div>
            </div>

        </div>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    
    <script>
        // --- THREE.JS ANIMATION (Star Tunnel) ---
        const scene = new THREE.Scene();
        scene.fog = new THREE.FogExp2(0x000000, 0.002);

        const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({ alpha: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        document.getElementById('canvas-container').appendChild(renderer.domElement);

        // Particles
        const geometry = new THREE.BufferGeometry();
        const counts = 5000;
        const positions = new Float32Array(counts * 3);
        
        for(let i=0; i < counts * 3; i++) {
            positions[i] = (Math.random() - 0.5) * 800; // Spread
        }
        
        geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        const material = new THREE.PointsMaterial({ size: 1.5, color: 0x00ff00 });
        const particles = new THREE.Points(geometry, material);
        scene.add(particles);

        camera.position.z = 100;

        function animate() {
            requestAnimationFrame(animate);
            particles.rotation.z += 0.002; // Rotate tunnel
            camera.position.z -= 0.5;      // Move forward
            
            // Loop effect
            if(camera.position.z < -100) camera.position.z = 100;
            
            renderer.render(scene, camera);
        }
        animate();

        window.addEventListener('resize', () => {
            renderer.setSize(window.innerWidth, window.innerHeight);
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
        });

        // --- FETCH DATA LOGIC ---
        async function fetchData() {
            const num = document.getElementById('phoneInput').value;
            const loader = document.getElementById('loader');
            const results = document.getElementById('results');
            
            if(!num) { alert("Enter Number!"); return; }

            loader.style.display = 'block';
            results.style.display = 'none';

            try {
                const response = await fetch(`/api/search?number=${num}`);
                const data = await response.json();
                
                if(!response.ok) {
                    alert(data.error || "Error");
                    loader.style.display = 'none';
                    return;
                }

                renderData(data);
                loader.style.display = 'none';
                results.style.display = 'flex';
            } catch(e) {
                alert("Connection Failed");
                loader.style.display = 'none';
            }
        }

        function renderData(data) {
            // 1. Render Deep Data (Top)
            const m = data.main_data;
            let mainHTML = "";
            if(m && m.name !== "N/A") {
                mainHTML += `<div class="data-row"><span class="label">FULL NAME:</span> <span class="value">${m.name}</span></div>`;
                mainHTML += `<div class="data-row"><span class="label">ADDRESS:</span> <span class="value">${m.address}</span></div>`;
                mainHTML += `<div class="data-row"><span class="label">FATHER NAME:</span> <span class="value">${m.father}</span></div>`;
                mainHTML += `<div class="data-row"><span class="label">EMAIL:</span> <span class="value">${m.email}</span></div>`;
                if(m.other_phones.length > 0) {
                     mainHTML += `<div class="data-row"><span class="label">LINKED NUMBERS:</span> <span class="value">${m.other_phones.join(', ')}</span></div>`;
                }
            } else {
                mainHTML = "<div style='color:red; text-align:center;'>NO DEEP RECORDS FOUND</div>";
            }
            document.getElementById('main-content').innerHTML = mainHTML;

            // 2. Render Local Data (Bottom)
            const l = data.local_data;
            let localHTML = "";
            if(l && !l.error) {
                localHTML += `<div class="data-row"><span class="label">CARRIER:</span> <span class="value">${l.carrier}</span></div>`;
                localHTML += `<div class="data-row"><span class="label">LOCATION:</span> <span class="value">${l.location}</span></div>`;
                localHTML += `<div class="data-row"><span class="label">TIMEZONE:</span> <span class="value">${l.timezone}</span></div>`;
                localHTML += `<div class="data-row"><span class="label">VALID:</span> <span class="value" style="color:${l.valid?'#0f0':'red'}">${l.valid}</span></div>`;
            } else {
                localHTML = "<div style='color:red'>INVALID NETWORK DATA</div>";
            }
            document.getElementById('local-content').innerHTML = localHTML;
        }
    </script>
</body>
</html>
"""

# ==========================================
# 3. BACKEND LOGIC & ROUTES
# ==========================================

@app.route('/')
def home():
    # Serves the HTML template defined above
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/search', methods=['GET'])
def search_api():
    number = request.args.get('number')
    
    # Cleaning
    clean_num = "".join(filter(str.isdigit, number))
    if not clean_num or len(clean_num) < 10:
        return jsonify({"error": "Invalid Format. Enter 10 digits."}), 400

    # A. Local Data Extraction
    try:
        fmt_num = f"+{clean_num}" if clean_num.startswith('91') else f"+91{clean_num}"
        parsed_num = phonenumbers.parse(fmt_num, "IN")
        
        local_data = {
            "carrier": carrier.name_for_number(parsed_num, "en") or "Unknown",
            "location": geocoder.description_for_number(parsed_num, "en") or "India",
            "timezone": str(timezone.time_zones_for_number(parsed_num)[0]),
            "valid": phonenumbers.is_valid_number(parsed_num)
        }
    except:
        local_data = {"error": "Parsing Failed"}

    # B. Main API Call (Deep Search)
    try:
        # 12s timeout for slow API
        res = requests.get(BASE_API_URL, params={'q': clean_num}, headers=HEADERS, timeout=12)
        if res.status_code == 200:
            cleaned_main = clean_deep_data(res.json().get('data', []))
        else:
            cleaned_main = {"name": "N/A", "error": "Database Empty"}
    except:
        cleaned_main = {"name": "N/A", "error": "Server Timeout"}

    return jsonify({
        "main_data": cleaned_main,
        "local_data": local_data
    })

def clean_deep_data(raw_list):
    """
    Cleans raw API data, removes spam text, fixes typos.
    """
    if not raw_list: return {"name": "N/A"}
    
    profile = {
        "name": "N/A", "father": "N/A", "address": "N/A", 
        "email": "N/A", "other_phones": []
    }

    for item in raw_list:
        # Spam Text Remover
        if "In February" in item.get('source_database', ''): 
            item['source_database'] = "Verified DB"

        # Typo Fixer
        if 'adres' in item: item['address'] = item.pop('adres')

        # Data Priority
        if item.get('full_name'): profile['name'] = item['full_name']
        if item.get('the_name_of_the_father'): profile['father'] = item['the_name_of_the_father']
        if item.get('address'): profile['address'] = item['address']
        if item.get('email'): profile['email'] = item['email']
        
        # Collect alternate numbers
        if item.get('telephone'): 
            profile['other_phones'].append(item['telephone'])

    # Remove duplicates
    profile['other_phones'] = list(set(profile['other_phones']))
    
    # Filter out the searched number itself from alternate list
    # (Optional logic, kept simple here)
    
    return profile

if __name__ == '__main__':
    # Run server
    print("SERVER STARTED: http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, threaded=True)
