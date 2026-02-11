import time
import requests
import phonenumbers
from flask import Flask, jsonify, request, render_template_string
from phonenumbers import carrier, geocoder, timezone
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

app = Flask(__name__)

# ==========================================
# 1. CONFIGURATION
# ==========================================
BASE_API_URL = "https://zkwuyi37gjfhgslglaielyawfjha3w.vercel.app/query"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

session = requests.Session()
retries = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
session.mount('https://', HTTPAdapter(max_retries=retries))

# ==========================================
# 2. FRONTEND (Promo UI + Three.js)
# ==========================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NONE_USERNAM3 | INTEL HUB</title>
    <style>
        body { margin: 0; overflow: hidden; background: #000; font-family: 'Courier New', monospace; color: #0f0; }
        #canvas-container { position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: -1; }
        
        #ui-layer {
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            overflow-y: auto; display: flex; flex-direction: column; align-items: center;
            padding-top: 30px; background: rgba(0, 0, 0, 0.85);
        }

        /* Branding Styles */
        .promo-header { text-align: center; margin-bottom: 30px; border: 1px solid #0f0; padding: 20px; background: rgba(0,20,0,0.5); box-shadow: 0 0 15px #0f0; }
        .dev-name { font-size: 24px; color: #fff; text-shadow: 0 0 10px #0f0; margin: 5px 0; }
        .channel-link { color: #00eaff; text-decoration: none; font-weight: bold; border: 1px solid #00eaff; padding: 5px 10px; display: inline-block; margin-top: 10px; transition: 0.3s; }
        .channel-link:hover { background: #00eaff; color: #000; box-shadow: 0 0 20px #00eaff; }

        h1 { font-size: 40px; margin-top: 10px; letter-spacing: 10px; text-shadow: 0 0 20px #0f0; }

        .search-box { display: flex; gap: 10px; margin-top: 20px; z-index: 100; }
        input {
            background: #000; border: 1px solid #0f0; color: #0f0; padding: 15px; font-size: 18px; outline: none; width: 300px;
            box-shadow: inset 0 0 10px #0f0; text-align: center;
        }
        button {
            background: #0f0; color: #000; border: none; padding: 10px 30px; font-size: 18px; cursor: pointer; font-weight: 900;
            box-shadow: 0 0 15px #0f0;
        }
        button:hover { background: #fff; box-shadow: 0 0 30px #fff; }

        .container { width: 90%; max-width: 700px; display: none; flex-direction: column; gap: 20px; padding: 40px 0; }
        .card { background: rgba(0, 10, 0, 0.95); border: 2px solid #00eaff; padding: 25px; border-radius: 5px; box-shadow: 0 0 30px rgba(0, 234, 255, 0.2); }
        
        .data-row { display: flex; justify-content: space-between; margin: 15px 0; border-bottom: 1px solid rgba(0,255,0,0.2); padding-bottom: 5px; }
        .label { color: #88ff88; font-weight: bold; font-size: 14px; }
        .value { color: #fff; font-weight: bold; font-size: 16px; text-align: right; }

        .loading { display: none; font-size: 20px; color: #00eaff; margin: 20px 0; }
        .blink { animation: blinker 0.6s linear infinite; }
        @keyframes blinker { 50% { opacity: 0; } }
        .error-msg { color: #ff0055; margin-top: 20px; font-weight: bold; display: none; }
    </style>
</head>
<body>
    <div id="canvas-container"></div>

    <div id="ui-layer">
        <div class="promo-header">
            <div class="dev-name">DEVELOPER: @None_usernam3</div>
            <a href="https://t.me/none_usernam3_is_here" target="_blank" class="channel-link">JOIN OFFICIAL CHANNEL</a>
        </div>

        <h1>CORE_SCAN</h1>
        
        <div class="search-box">
            <input type="text" id="phoneInput" placeholder="ENTER NUMBER (10 DIGIT)" maxlength="10">
            <button onclick="fetchData()">SCAN</button>
        </div>

        <div class="loading" id="loader">
            <span class="blink">>> PENETRATING DATABASE...</span>
        </div>

        <div class="error-msg" id="error-box"></div>

        <div class="container" id="results">
            <div class="card">
                <h2 style="color:#00eaff; border-bottom:1px solid #00eaff; padding-bottom:10px;">IDENTITY RESULTS</h2>
                <div id="main-content"></div>
            </div>
        </div>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script>
        // THREE.JS GALAXY ANIMATION
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({ alpha: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        document.getElementById('canvas-container').appendChild(renderer.domElement);

        const starGeo = new THREE.BufferGeometry();
        const starCount = 6000;
        const posArray = new Float32Array(starCount * 3);
        for(let i=0; i<starCount*3; i++) posArray[i] = (Math.random()-0.5) * 600;
        starGeo.setAttribute('position', new THREE.BufferAttribute(posArray, 3));
        const starMat = new THREE.PointsMaterial({ size: 0.7, color: 0x00ff00 });
        const starMesh = new THREE.Points(starGeo, starMat);
        scene.add(starMesh);
        camera.position.z = 1;

        function animate() {
            requestAnimationFrame(animate);
            starMesh.rotation.y += 0.001;
            starMesh.rotation.x += 0.0005;
            renderer.render(scene, camera);
        }
        animate();

        async function fetchData() {
            const num = document.getElementById('phoneInput').value;
            const loader = document.getElementById('loader');
            const results = document.getElementById('results');
            const errorBox = document.getElementById('error-box');
            
            if(num.length < 10) { showError("INVALID LENGTH"); return; }

            loader.style.display = 'block';
            results.style.display = 'none';
            errorBox.style.display = 'none';

            try {
                const response = await fetch(`/api/search?number=${num}`);
                const data = await response.json();
                
                if(!response.ok) throw new Error(data.error);

                let html = "";
                const m = data.data;
                html += row("NAME", m.name, "#00eaff");
                html += row("FATHER", m.father, "#fff");
                html += row("ADDRESS", m.address, "#fff");
                html += row("CARRIER", m.carrier, "#0f0");
                html += row("LOCATION", m.location, "#0f0");
                if(m.alt_phones.length) html += row("LINKED", m.alt_phones.join(', '), "#ff0055");

                document.getElementById('main-content').innerHTML = html;
                loader.style.display = 'none';
                results.style.display = 'flex';
            } catch(e) {
                loader.style.display = 'none';
                showError(e.message);
            }
        }

        function showError(msg) {
            const e = document.getElementById('error-box');
            e.innerText = ">> ERROR: " + msg;
            e.style.display = 'block';
        }

        function row(l, v, c) {
            if(!v || v == "N/A") return "";
            return `<div class="data-row"><span class="label">${l}:</span> <span class="value" style="color:${c}">${v}</span></div>`;
        }
    </script>
</body>
</html>
"""

# ==========================================
# 3. BACKEND (STRICT DATA ONLY)
# ==========================================

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/search')
def api_search():
    raw_num = request.args.get('number', '')
    clean_num = "".join(filter(str.isdigit, raw_num))
    
    try:
        # Long timeout for your 5s API
        res = session.get(BASE_API_URL, params={'q': clean_num}, headers=HEADERS, timeout=25)
        
        if res.status_code != 200:
            return jsonify({"error": "DATABASE OFFLINE"}), 404
            
        raw_list = res.json().get('data', [])
        if not raw_list:
            return jsonify({"error": "NO RECORDS IN DEEP DB"}), 404

        # Cleaning logic
        profile = {"name": "N/A", "father": "N/A", "address": "N/A", "alt_phones": []}
        for item in raw_list:
            # Skip the specific leak description line you mentioned
            if "In February 2019" in str(item.get('source_database', '')): continue
            
            if 'adres' in item: item['address'] = item.pop('adres')
            if item.get('full_name'): profile['name'] = item['full_name']
            if item.get('the_name_of_the_father'): profile['father'] = item['the_name_of_the_father']
            if item.get('address'): profile['address'] = item['address']
            if item.get('telephone') and item['telephone'] != clean_num: 
                profile['alt_phones'].append(item['telephone'])

        # Add Network Info
        pn = phonenumbers.parse("+91" + clean_num[-10:], "IN")
        profile['carrier'] = carrier.name_for_number(pn, "en")
        profile['location'] = geocoder.description_for_number(pn, "en")
        profile['alt_phones'] = list(set(profile['alt_phones']))

        return jsonify({"data": profile})

    except Exception as e:
        return jsonify({"error": "CONNECTION TIMEOUT"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
