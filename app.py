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
# 2. HOMEPAGE TEMPLATE (PROMO & CURL DOCS)
# ==========================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NONE_USERNAM3 | API DOCS</title>
    <style>
        body { margin: 0; overflow: hidden; background: #000; font-family: 'Courier New', monospace; color: #0f0; }
        #canvas-container { position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: -1; }
        
        #ui-layer {
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            overflow-y: auto; display: flex; flex-direction: column; align-items: center;
            padding-top: 50px; background: rgba(0, 0, 0, 0.85);
        }

        .promo-box { border: 2px solid #0f0; padding: 30px; background: rgba(0,20,0,0.8); box-shadow: 0 0 20px #0f0; text-align: center; max-width: 600px; width: 90%; }
        .dev-tag { font-size: 22px; color: #fff; text-shadow: 0 0 10px #0f0; }
        .channel-btn { color: #00eaff; text-decoration: none; font-weight: bold; border: 1px solid #00eaff; padding: 10px 20px; display: inline-block; margin: 15px 0; transition: 0.3s; }
        .channel-btn:hover { background: #00eaff; color: #000; box-shadow: 0 0 25px #00eaff; }

        .docs-section { margin-top: 40px; width: 90%; max-width: 800px; text-align: left; }
        .curl-box { background: #111; border-left: 5px solid #00eaff; padding: 15px; margin: 15px 0; color: #00eaff; font-size: 14px; overflow-x: auto; white-space: pre; }
        .endpoint-title { color: #fff; font-size: 18px; text-decoration: underline; }
        
        h1 { letter-spacing: 5px; text-shadow: 0 0 10px #0f0; }
        .blink { animation: blinker 1s linear infinite; }
        @keyframes blinker { 50% { opacity: 0; } }
    </style>
</head>
<body>
    <div id="canvas-container"></div>

    <div id="ui-layer">
        <div class="promo-box">
            <h1>CORE_NETWORK_V3</h1>
            <div class="dev-tag">DEVELOPER: @None_usernam3</div>
            <a href="https://t.me/none_usernam3_is_here" target="_blank" class="channel-btn">JOIN TELEGRAM CHANNEL</a>
            <p class="blink">STATUS: SYSTEMS ONLINE</p>
        </div>

        <div class="docs-section">
            <h2 style="color: #fff;">API ENDPOINTS (CURL)</h2>
            
            <div class="endpoint-title">1. DEEP SEARCH ENDPOINT</div>
            <div class="curl-box">
curl -X GET "https://{{host}}/ny/none/usr/@None_usernam3/NUMBER/IND/NUM=91XXXXXXXXXX"
            </div>

            <div class="endpoint-title">2. JSON RAW DATA</div>
            <div class="curl-box">
curl -X GET "https://{{host}}/api/raw?number=91XXXXXXXXXX"
            </div>
            
            <p style="color: #888; font-size: 12px;">* Replace {{host}} with your current domain.</p>
        </div>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script>
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({ alpha: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        document.getElementById('canvas-container').appendChild(renderer.domElement);

        const starGeo = new THREE.BufferGeometry();
        const starCount = 4000;
        const posArray = new Float32Array(starCount * 3);
        for(let i=0; i<starCount*3; i++) posArray[i] = (Math.random()-0.5) * 600;
        starGeo.setAttribute('position', new THREE.BufferAttribute(posArray, 3));
        const starMat = new THREE.PointsMaterial({ size: 0.8, color: 0x00ff00 });
        const starMesh = new THREE.Points(starGeo, starMat);
        scene.add(starMesh);
        camera.position.z = 1;

        function animate() {
            requestAnimationFrame(animate);
            starMesh.rotation.y += 0.001;
            renderer.render(scene, camera);
        }
        animate();
    </script>
</body>
</html>
"""

# ==========================================
# 3. BACKEND ENDPOINTS
# ==========================================

@app.route('/')
def home():
    # Automatically get host name for curl docs
    host = request.host
    return render_template_string(HTML_TEMPLATE, host=host)

# --- THE MAIN ENDPOINT YOU REQUESTED ---
@app.route('/ny/none/usr/@None_usernam3/NUMBER/IND/NUM=<number>', methods=['GET'])
def long_endpoint_search(number):
    return perform_search(number)

# --- SHORT ENDPOINT FOR FAST CURL ---
@app.route('/api/raw', methods=['GET'])
def short_endpoint_search():
    num = request.args.get('number')
    return perform_search(num)

def perform_search(number):
    if not number:
        return jsonify({"error": "No number provided"}), 400
        
    clean_num = "".join(filter(str.isdigit, str(number)))
    
    try:
        # Strict timeout for your 5s API
        res = session.get(BASE_API_URL, params={'q': clean_num}, headers=HEADERS, timeout=25)
        
        if res.status_code != 200:
            return jsonify({"status": "error", "message": "Main API Offline"}), 404
            
        raw_list = res.json().get('data', [])
        if not raw_list:
            return jsonify({"status": "empty", "message": "No data found for this target"}), 404

        # Cleaning logic
        profile = {
            "developer": "@None_usernam3",
            "full_name": "N/A", 
            "father_name": "N/A", 
            "address": "N/A", 
            "carrier": "N/A",
            "linked_numbers": []
        }

        for item in raw_list:
            # Remove the specific long leak string you mentioned
            if "In February 2019" in str(item.get('source_database', '')): continue
            
            # Fix typos and extract data
            if 'adres' in item: item['address'] = item.pop('adres')
            if item.get('full_name'): profile['full_name'] = item['full_name']
            if item.get('the_name_of_the_father'): profile['father_name'] = item['the_name_of_the_father']
            if item.get('address'): profile['address'] = item['address']
            if item.get('telephone') and item['telephone'] != clean_num: 
                profile['linked_numbers'].append(item['telephone'])

        # Local library info
        try:
            pn = phonenumbers.parse("+91" + clean_num[-10:], "IN")
            profile['carrier'] = carrier.name_for_number(pn, "en")
        except:
            pass

        profile['linked_numbers'] = list(set(profile['linked_numbers']))

        # Return the clean JSON
        return jsonify(profile)

    except Exception as e:
        return jsonify({"status": "timeout", "message": "Server took too long to respond"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
