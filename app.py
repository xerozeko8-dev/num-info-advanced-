import os
import time
import requests
import phonenumbers
from flask import Flask, jsonify, request
from phonenumbers import carrier, geocoder, timezone
from datetime import datetime

# ==========================================
# CONFIGURATION & BRANDING
# ==========================================
DEVELOPER = "Himanshu"
CHANNEL = "Premium Cybersecurity Hub"
MAIN_API_ENDPOINT = "https://zkwuyi37gjfhgslglaielyawfjha3w.vercel.app/query"

app = Flask(__name__)

# Terminal interface styling
def print_banner():
    print("\033[94m" + "="*50)
    print(f"       🚀 {DEVELOPER.upper()}'S ADVANCED FLASK API")
    print(f"       📡 STATUS: ACTIVE | PORT: 5000")
    print(f"       🛡️  PROTECTION: API MASKING ENABLED")
    print("="*50 + "\033[0m")

# ==========================================
# HELPER FUNCTIONS
# ==========================================

def get_branding():
    return {
        "developer": DEVELOPER,
        "channel_owner": "@None_usernam3",
        "official_channel": CHANNEL,
        "server_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "Authorized Access"
    }

# ==========================================
# MAIN ROUTE
# ==========================================

@app.route('/ny/none/usr/@None_usernam3/NUMBER/IND/NUM=<number>', methods=['GET'])
def fetch_indian_intel(number):
    start_time = time.time()
    branding_info = get_branding()

    # 1. Input Cleaning & Strict Alphabet Block
    # Sirf numbers allow honge
    if not number.isdigit():
        return jsonify({
            "branding": branding_info,
            "error": "Access Denied: Alphabets and symbols are not allowed.",
            "code": 403
        }), 403

    # 2. Advanced Indian Number Validation
    try:
        # 91 add karna agar user ne sirf 10 digit daale hain
        formatted_num = number if number.startswith('91') else f"91{number}"
        parsed_num = phonenumbers.parse(f"+{formatted_num}", "IN")

        # Check if it's a real Indian number
        if not phonenumbers.is_valid_number(parsed_num):
            return jsonify({
                "branding": branding_info,
                "error": "Invalid Indian Mobile Number.",
                "tip": "Ensure the number is 10 digits or starts with 91"
            }), 400
        
        if phonenumbers.region_code_for_number(parsed_num) != "IN":
            return jsonify({
                "branding": branding_info,
                "error": "Operation Restricted: Only Indian database access allowed."
            }), 403

    except Exception:
        return jsonify({"error": "Encryption/Parsing Error"}), 500

    # 3. Extraction from Local Library (Always Works)
    local_intel = {
        "service_provider": carrier.name_for_number(parsed_num, "en") or "Unknown Carrier",
        "state_location": geocoder.description_for_number(parsed_num, "en") or "India",
        "time_zone": list(timezone.time_zones_for_number(parsed_num)),
        "valid_format": phonenumbers.is_possible_number(parsed_num)
    }

    # 4. Silent Backend API Call (Main API Hidden)
    try:
        # Calling the hidden Vercel API
        response = requests.get(MAIN_API_ENDPOINT, params={'q': number}, timeout=6)
        
        if response.status_code == 200:
            deep_data = response.json()
        else:
            deep_data = {"message": "Deep database currently busy or no record found."}
            
    except requests.exceptions.RequestException:
        deep_data = {"message": "Connection to Main API failed, showing local data only."}

    # 5. Final Response Construction
    execution_speed = f"{round(time.time() - start_time, 4)}s"
    
    # Terminal Logging for Developer
    print(f"[\033[92mLOG\033[0m] Request for: {number} | Speed: {execution_speed} | Status: Success")

    return jsonify({
        "branding": branding_info,
        "performance": {"load_time": execution_speed},
        "number_info": {
            "raw_input": number,
            "country": "India",
            "local_extraction": local_intel
        },
        "external_database": deep_data
    }), 200

# ==========================================
# SERVER START
# ==========================================

if __name__ == '__main__':
    # Clearing terminal for clean look (Windows)
    os.system('cls' if os.name == 'nt' else 'clear')
    print_banner()
    
    # Threaded=True for handling multiple users at once
    # Host 0.0.0.0 helps in accessing within local network
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
