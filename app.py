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
# 2. PROMO UI (3D Particles)
# ==========================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>CORE_INTEL | GHOST MODE</title>
    <style>
        body { margin: 0; background: #000; color: #0f0; font-family: monospace; overflow: hidden; }
        #canvas-container { position: fixed; width: 100%; height: 100%; z-index: -1; }
        .ui { position: absolute; width: 100%; height: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center; background: rgba(0,0,0,0.85); }
        .box { border: 2px solid #0f0; padding: 40px; text-align: center; box-shadow: 0 0 25px #0f0; background: rgba(0,10,0,0.95); }
        .btn { color: #00eaff; border: 1px solid #00eaff; padding: 10px 20px; text-decoration: none; display: inline-block; margin-top: 20px; font-weight: bold; text-transform: uppercase; }
        .btn:hover { background: #00eaff; color: #000; box-shadow: 0 0 30px #00eaff; }
        h1 { letter-spacing: 7px; text-shadow: 0 0 10px #0f0; }
    </style>
</head>
<body>
    <div id="canvas-container"></div>
    <div class="ui">
        <div class="box">
            <h1>STRICT_GHOST_SYSTEM</h1>
            <p style="color: #fff;">DEVELOPER: @None_Usernamz</p>
            <a href="https://t.me/none_usernam3_is_here" class="btn">JOIN OFFICIAL CHANNEL</a>
            <p style="margin-top:20px; font-size:11px; color:#333;">ENDPOINT: /ny/none/usr/@None_usernam3/NUMBER/IND/NUM=91XXXXXXXXXX</p>
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
        for(let i=0; i<2000*3; i++) posArr[i] = (Math.random()-0.5) * 600;
        geo.setAttribute('position', new THREE.BufferAttribute(posArr, 3));
        const mesh = new THREE.Points(geo, new THREE.PointsMaterial({ size: 1.5, color: 0x00ff00 }));
        scene.add(mesh);
        camera.position.z = 50;
        function animate() { requestAnimationFrame(animate); mesh.rotation.y += 0.002; renderer.render(scene, camera); }
        animate();
    </script>
</body>
</html>
"""

# ==========================================
# 3. BACKEND (GHOST DATA FILTERING)
# ==========================================

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/ny/none/usr/@None_usernam3/NUMBER/IND/NUM=<number>', methods=['GET'])
def get_ghost_intel(number):
    clean_num = "".join(filter(str.isdigit, str(number)))
    
    # Junk list to block entirely if record contains ONLY these
    JUNK_BLOCK = [
        "Iran Telegram", "Alien TxtBase", "Telegram 2020", 
        "Facebook", "Mcls.gov.ir", "WhatsApp", 
        "At your request, no results were found",
        "In February 2019", "leaked to data"
    ]

    try:
        res = session.get(BASE_API_URL, params={'q': clean_num}, headers=HEADERS, timeout=25)
        
        if res.status_code != 200:
            return jsonify({"status": "error", "message": "Backend Signal Lost"}), 503

        raw_list = res.json().get('data', [])

        if not raw_list:
            return jsonify({"status": "failed", "message": "Zero records in deep database"}), 404

        # --- GHOST CLEANING ENGINE ---
        final_results = []
        for item in raw_list:
            source_val = str(item.get('source_database', '')).strip()
            
            # 1. DELETE 'source_database' key immediately
            item.pop('source_database', None)
            
            # 2. Block records that are just junk placeholders
            if any(junk in source_val for junk in JUNK_BLOCK) or not source_val:
                # Agar us record mein name ya address hi nahi hai, toh skip karo
                if not any(k in item for k in ['full_name', 'address', 'adres', 'telephone']):
                    continue

            # 3. Rename 'adres' to 'address'
            if 'adres' in item:
                item['address'] = item.pop('adres')
            
            # 4. Remove all other metadata
            item.pop('result_no', None)
            item.pop('total_results', None)
            item.pop('intel_count', None)

            final_results.append(item)

        # 5. Network Intel
        network_intel = {}
        try:
            target = clean_num[-10:]
            pn = phonenumbers.parse("+91" + target, "IN")
            network_intel = {
                "carrier": carrier.name_for_number(pn, "en"),
                "location": geocoder.description_for_number(pn, "en")
            }
        except:
            network_intel = {"status": "telemetry_error"}

        # --- FINAL JSON (ZERO DB INFO) ---
        return jsonify({
            "developer": "@None_Usernamz",
            "channel": "https://t.me/none_usernam3_is_here",
            "target": clean_num,
            "telemetry": network_intel,
            "intel": final_results # Only the data, NO DB INFO
        })

    except Exception as e:
        return jsonify({"status": "timeout", "error": str(e)}), 504

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
