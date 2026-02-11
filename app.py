import os
import requests
import phonenumbers
from flask import Flask, jsonify
from phonenumbers import carrier, geocoder, timezone

app = Flask(__name__)

# Backend API Configuration
BASE_API_URL = "https://zkwuyi37gjfhgslglaielyawfjha3w.vercel.app/query"
# Session use karne se speed 20-30% badh jati hai
session = requests.Session()

BRANDING = {
    "developer": "Himanshu",
    "status": "Premium High-Speed Server",
    "endpoint_type": "Secured Tunnel"
}

@app.route('/ny/none/usr/@None_usernam3/NUMBER/IND/NUM=<number>', methods=['GET'])
def get_info(number):
    # 1. Faster Validation (Regex se pehle hi filter)
    clean_num = "".join(filter(str.isdigit, number))
    
    if not clean_num or len(clean_num) < 10:
        return jsonify({"branding": BRANDING, "error": "Invalid Indian Number"}), 400

    # 2. Local Info Extraction (Instant - 0.01s)
    try:
        parsed_num = phonenumbers.parse(f"+{clean_num}" if clean_num.startswith('91') else f"+91{clean_num}", "IN")
        local_intel = {
            "operator": carrier.name_for_number(parsed_num, "en"),
            "state": geocoder.description_for_number(parsed_num, "en"),
            "timezone": list(timezone.time_zones_for_number(parsed_num))
        }
    except:
        local_intel = {"info": "Phonenumbers library error"}

    # 3. Handling the Slow 6-Second API
    try:
        # Timeout 9 seconds rakha hai taaki Vercel ke 10s limit se pehle response mil jaye
        external_res = session.get(BASE_API_URL, params={'q': clean_num}, timeout=9)
        
        if external_res.status_code == 200:
            deep_data = external_res.json()
        else:
            deep_data = {"msg": "No record found in main database"}
            
    except requests.exceptions.Timeout:
        deep_data = {"msg": "Main API is too slow today. Showing local results only."}
    except Exception as e:
        deep_data = {"msg": "Main API Error"}

    # Final Response
    return jsonify({
        "branding": BRANDING,
        "input": clean_num,
        "extraction": local_intel,
        "external_db": deep_data
    }), 200

if __name__ == '__main__':
    app.run(threaded=True)
