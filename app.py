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

# Retry Strategy for stability
session = requests.Session()
retries = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
session.mount('https://', HTTPAdapter(max_retries=retries))

# ==========================================
# 2. PROMO HOMEPAGE
# ==========================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>NONE_USERNAM3 | MAX INTEL</title>
    <style>
        body { margin: 0; background: #000; color: #0f0; font-family: monospace; overflow: hidden; }
        #canvas-container { position: fixed; width: 100%; height: 100%; z-index: -1; }
        .ui { position: absolute; width: 100%; height: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center; background: rgba(0,0,0,0.8); }
        .box { border: 2px solid #0f0; padding: 40px; text-align: center; box-shadow: 0 0 20px #0f0; }
        .btn { color: #00eaff; border: 1px solid #00eaff; padding: 10px 20px; text-decoration: none; display: inline-block; margin-top: 20px; }
        .btn:hover { background: #00eaff; color: #000; box-shadow: 0 0 20px #00eaff; }
    </style>
</head>
<body>
    <div id="canvas-container"></div>
    <div class="ui">
        <div class="box">
            <h1>MAX_INTEL_SYSTEM V4</h1>
            <p>DEVELOPER: @None_usernam3</p>
            <a href="https://t.me/none_usernam3_is_here" class="btn">JOIN TELEGRAM</a>
            <p style="margin-top:20px; font-size:12px; color:#555;">ENDPOINT: /ny/none/usr/@None_usernam3/NUMBER/IND/NUM=91XXXXXXXXXX</p>
        </div>
    </div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script>
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({ alpha: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        document.getElementById('canvas-container').appendChild(renderer.domElement);
        const geo = new THREE.BufferGeometry();
        const posArr = new Float32Array(2000 * 3);
        for(let i=0; i<2000*3; i++) posArr[i] = (Math.random()-0.5) * 500;
        geo.setAttribute('position', new THREE.BufferAttribute(posArr, 3));
        const mesh = new THREE.Points(geo, new THREE.PointsMaterial({ size: 1, color: 0x00ff00 }));
        scene.add(mesh);
        camera.position.z = 50;
        function animate() { requestAnimationFrame(animate); mesh.rotation.y += 0.002; renderer.render(scene, camera); }
        animate();
    </script>
</body>
</html>
"""

# ==========================================
# 3. BACKEND (THE MAX-DATA ENGINE)
# ==========================================

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/ny/none/usr/@None_usernam3/NUMBER/IND/NUM=<number>', methods=['GET'])
def get_max_intel(number):
    clean_num = "".join(filter(str.isdigit, str(number)))
    
    try:
        # Step 1: Hit Main API (25s Timeout for stability)
        response = session.get(BASE_API_URL, params={'q': clean_num}, headers=HEADERS, timeout=25)
        
        if response.status_code != 200:
            return jsonify({"status": "error", "message": "External API is Unreachable"}), 503

        raw_data = response.json()
        raw_list = raw_data.get('data', [])

        if not raw_list:
            return jsonify({"status": "failed", "message": "No data found in deep database"}), 404

        # Step 2: Maximum Data Processing
        # Hum koi field filter nahi karenge, sirf clean karenge
        final_results = []
        for item in raw_list:
            # Skip only the specific leak notice line
            source = str(item.get('source_database', ''))
            if "In February 2019" in source or "leaked to data" in source:
                continue
            
            # Fix 'adres' to 'address' globally if it exists
            if 'adres' in item:
                item['address'] = item.pop('adres')
            
            # Remove result index to keep it professional
            item.pop('result_no', None)

            final_results.append(item)

        # Step 3: Phonenumbers Library Integration
        network_data = {}
        try:
            # Normalize for library (91 + 10 digits)
            target = clean_num[-10:]
            pn = phonenumbers.parse("+91" + target, "IN")
            network_data = {
                "carrier": carrier.name_for_number(pn, "en"),
                "circle": geocoder.description_for_number(pn, "en"),
                "timezone": list(timezone.time_zones_for_number(pn)),
                "is_valid": phonenumbers.is_valid_number(pn)
            }
        except:
            network_data = {"error": "Could not extract network telemetry"}

        # Step 4: Final Unified Output
        return jsonify({
            "developer": "@None_Usernamz",
            "official_channel": "https://t.me/none_usernam3_is_here",
            "target": clean_num,
            "status": "Success",
            "telemetry": network_data,
            "intel_count": len(final_results),
            "records": final_results # Yahan saara ka saara max data aayega
        })

    except Exception as e:
        return jsonify({"status": "timeout", "error": "The server took too long to process (5s+ API lag)"}), 504

if __name__ == '__main__':
    # Vercel handling
    app.run(host='0.0.0.0', port=5000, threaded=True)
