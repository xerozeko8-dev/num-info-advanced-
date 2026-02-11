import time
import requests
import phonenumbers
import re
import os
from flask import Flask, jsonify, request, render_template_string
from phonenumbers import carrier, geocoder
from datetime import datetime
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

app = Flask(__name__)

# ==========================================
# 1. CONFIGURATION & SECURITY
# ==========================================
BASE_API_URL = "https://zkwuyi37gjfhgslglaielyawfjha3w.vercel.app/query"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"}

# Rate Limiting Storage (Memory based)
# Format: { ip: { count: X, date: "YYYY-MM-DD" } }
ip_logs = {}

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
    <title>@None_Usernamz </title>
    <style>
        body { margin: 0; background: #000; color: #0f0; font-family: monospace; overflow: hidden; }
        #canvas-container { position: fixed; width: 100%; height: 100%; z-index: -1; }
        .ui { position: absolute; width: 100%; height: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center; background: rgba(0,0,0,0.85); }
        .box { border: 2px solid #0f0; padding: 40px; text-align: center; box-shadow: 0 0 25px #0f0; background: rgba(0,10,0,0.95); }
        .btn { color: #00eaff; border: 1px solid #00eaff; padding: 10px 20px; text-decoration: none; display: inline-block; margin-top: 20px; font-weight: bold; }
        .btn:hover { background: #00eaff; color: #000; box-shadow: 0 0 30px #00eaff; }
        h1 { letter-spacing: 7px; text-shadow: 0 0 10px #0f0; }
        .security-tag { color: #ff0055; font-size: 12px; margin-top: 10px; }
    </style>
</head>
<body>
    <div id="canvas-container"></div>
    <div class="ui">
        <div class="box">
            <h1>buy From :  @None_Usernamz </h1>
            <p style="color: #fff;">DEVELOPER: @None_Usernamz</p>
            <a href="https://t.me/none_usernam3_is_here" class="btn">JOIN OFFICIAL CHANNEL</a>
            <p class="security-tag">SHIELD: ACTIVE | IP_LIMIT: 1000/DAY</p>
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
# 3. BACKEND (STRICT LOGIC + ANTI-DDOS)
# ==========================================

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/ny/none/usr/@None_usernam3/NUMBER/IND/NUM=<number>', methods=['GET'])
def secure_search(number):
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    today = datetime.now().strftime("%Y-%m-%d")

    # --- 1. IP RATE LIMITING (DDOS PROTECTION) ---
    if user_ip not in ip_logs or ip_logs[user_ip]['date'] != today:
        ip_logs[user_ip] = {'count': 1, 'date': today}
    else:
        ip_logs[user_ip]['count'] += 1

    if ip_logs[user_ip]['count'] > 1000:
        return jsonify({
            "status": "DDOS_BLOCK",
            "message": "AN ASSHOLE TRYING DO DDOS BUT NO WORRIES API LIVE IN FEW SECOENDS AND FUCK YOU ASSHOLE 😂"
        }), 429

    # --- 2. LOGGING QUERIES ---
    log_entry = f"{datetime.now()} | IP: {user_ip} | QUERY: {number}\n"
    try:
        # Vercel par ye sirf temp session mein rahega
        with open("queries.txt", "a") as f:
            f.write(log_entry)
    except:
        pass

    # --- 3. STRICT INDIAN NUMBER VALIDATION ---
    # Only digits allow, must be 10 digits or 91 + 10 digits
    clean_num = "".join(filter(str.isdigit, str(number)))
    
    # Check if strictly Indian (Starting with 6-9 and total length 10 or 12 with 91)
    if not re.match(r'^(91)?[6-9][0-9]{9}$', clean_num):
        return jsonify({"error": "TG - @None_Usernamz | ONLY INDIAN NUMBERS ALLOWED"}), 400

    # Junk strings to block
    JUNK_BLOCK = ["Iran Telegram", "Alien TxtBase", "Facebook", "WhatsApp", "In February 2019", "leaked to data"]

    try:
        res = session.get(BASE_API_URL, params={'q': clean_num}, headers=HEADERS, timeout=20)
        
        if res.status_code != 200:
            return jsonify({"error": "BACKEND OFFLINE"}), 503

        raw_list = res.json().get('data', [])
        if not raw_list:
            return jsonify({"status": "failed", "message": "ZERO RECORDS FOUND"}), 404

        # --- GHOST FILTERING ---
        final_results = []
        for item in raw_list:
            source_val = str(item.get('source_database', '')).strip()
            
            # REMOVE DB INFO PERMANENTLY
            item.pop('source_database', None)
            item.pop('result_no', None)
            item.pop('total_results', None)
            item.pop('intel_count', None)

            # Block record if it's just a junk placeholder
            if any(junk in source_val for junk in JUNK_BLOCK) or not source_val:
                if not any(k in item for k in ['full_name', 'address', 'adres', 'telephone']):
                    continue

            # Spelling fix
            if 'adres' in item: item['address'] = item.pop('adres')

            final_results.append(item)

        # Network Intel
        try:
            pn = phonenumbers.parse("+91" + clean_num[-10:], "IN")
            telemetry = {
                "carrier": carrier.name_for_number(pn, "en"),
                "location": geocoder.description_for_number(pn, "en")
            }
        except:
            telemetry = {"status": "error"}

        return jsonify({
            "developer": "@None_Usernamz",
            "target": clean_num,
            "telemetry": telemetry,
            "intel": final_results
        })

    except Exception:
        return jsonify({"status": "timeout", "message": "API OVERLOADED"}), 504

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
