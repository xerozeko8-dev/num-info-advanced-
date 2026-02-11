import os
import time
import requests
import phonenumbers
from flask import Flask, jsonify
from phonenumbers import carrier, geocoder, timezone
from datetime import datetime

app = Flask(__name__)

# ==========================================
# CONFIGURATION
# ==========================================
# Main API URL
BASE_API_URL = "https://zkwuyi37gjfhgslglaielyawfjha3w.vercel.app/query"

# Branding Details
BRANDING = {
    "developer": "Himanshu",
    "channel_owner": "@None_usernam3",
    "official_channel": "Premium Cybersecurity Hub",
    "server_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "status": "Authorized Access"
}

# Browser jaisa dikhne ke liye Headers (Important for success)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# ==========================================
# ROUTE
# ==========================================
@app.route('/ny/none/usr/@None_usernam3/NUMBER/IND/NUM=<number>', methods=['GET'])
def get_info(number):
    start_time = time.time()
    
    # 1. CLEANING & VALIDATION
    # Remove any extra characters, keep only digits
    clean_num = "".join(filter(str.isdigit, number))
    
    # Check length (Indian numbers are usually 10 digits without country code)
    if not clean_num or len(clean_num) < 10:
        return jsonify({
            "branding": BRANDING,
            "error": "Invalid Number Length",
            "message": "Please enter a valid Indian number."
        }), 400

    # 2. LOCAL EXTRACTION (Phonenumbers Library)
    try:
        # Format number with +91 if missing
        fmt_num = f"+{clean_num}" if clean_num.startswith('91') else f"+91{clean_num}"
        parsed_num = phonenumbers.parse(fmt_num, "IN")
        
        # Check if valid Indian number
        if not phonenumbers.is_valid_number(parsed_num) or phonenumbers.region_code_for_number(parsed_num) != "IN":
            return jsonify({
                "branding": BRANDING,
                "error": "Non-Indian Number detected",
                "message": "Only +91 Indian numbers are allowed."
            }), 400

        local_data = {
            "valid_format": True,
            "service_provider": carrier.name_for_number(parsed_num, "en"),
            "state_location": geocoder.description_for_number(parsed_num, "en"),
            "time_zone": list(timezone.time_zones_for_number(parsed_num))
        }
    except Exception as e:
        local_data = {"error": "Local parsing failed", "details": str(e)}

    # 3. MAIN API CALL (Deep Search)
    # Timeout badha kar 12 seconds kar diya hai (aapki API 5-6s leti hai, so ye safe hai)
    try:
        response = requests.get(
            BASE_API_URL, 
            params={'q': clean_num}, 
            headers=HEADERS, 
            timeout=12
        )
        
        if response.status_code == 200:
            external_data = response.json()
        else:
            external_data = {
                "status": "failed", 
                "http_code": response.status_code, 
                "message": "Main API reachable but returned error."
            }
            
    except requests.exceptions.Timeout:
        # Ye tab chalega agar 12 seconds se bhi zyada time laga
        external_data = {
            "status": "timeout",
            "message": "Main API took too long (>12s) to respond."
        }
    except requests.exceptions.RequestException as e:
        external_data = {
            "status": "connection_error",
            "message": str(e)
        }

    # 4. FINAL RESPONSE
    total_time = f"{round(time.time() - start_time, 4)}s"
    
    # Update server time in branding for every request
    current_branding = BRANDING.copy()
    current_branding["server_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return jsonify({
        "branding": current_branding,
        "performance": {"load_time": total_time},
        "number_info": {
            "raw_input": number,
            "country": "India",
            "local_extraction": local_data
        },
        "external_database": external_data
    }), 200

# ==========================================
# SERVER EXECUTION
# ==========================================
if __name__ == '__main__':
    # Threaded=True se parallel requests handle hongi
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
