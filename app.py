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
BASE_API_URL = "https://zkwuyi37gjfhgslglaielyawfjha3w.vercel.app/query"

BRANDING = {
    "developer": "Himanshu",
    "channel_owner": "@None_usernam3",
    "official_channel": "Premium Cybersecurity Hub",
    "server_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "status": "Authorized Access"
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# ==========================================
# DATA CLEANING ENGINE (The Magic Part)
# ==========================================
def process_raw_data(raw_list):
    """
    Ye function gande data ko clean aur professional banata hai.
    """
    if not raw_list:
        return None

    # Consolidated Profile (Best Data Ek Jagah)
    profile = {
        "full_name": "N/A",
        "father_name": "N/A",
        "address": "N/A",
        "document_id": "N/A",
        "alternate_phones": []
    }

    cleaned_records = []
    
    seen_sources = set()

    for item in raw_list:
        # 1. REMOVE BAD STRING (TrueCaller Leak Text)
        source = item.get('source_database', '')
        if "In February 2019" in source or "leaked to data" in source:
            item['source_database'] = "TrueCaller Verified"  # Replace with professional text

        # 2. FIX SPELLING (adres -> address)
        if 'adres' in item:
            item['address'] = item.pop('adres') # Rename key

        # 3. BUILD PROFILE (Extract best info)
        if item.get('full_name'):
            profile['full_name'] = item['full_name']
        
        if item.get('the_name_of_the_father'):
            profile['father_name'] = item['the_name_of_the_father']
        
        if item.get('address'):
            profile['address'] = item['address']
            
        if item.get('document_number'):
            profile['document_id'] = item['document_number']

        # 4. FILTER USELESS RECORDS (Sirf phone number wale records hatana)
        # Agar record me sirf 'result_no' aur 'telephone' hai, toh usse skip karo
        # lekin agar koi unique info hai toh rakho.
        keys = item.keys()
        if len(keys) <= 3 and 'telephone' in keys and 'result_no' in keys and 'source_database' not in keys:
             # Add to alternates list instead of main records
             if item.get('telephone'):
                 profile['alternate_phones'].append(item['telephone'])
             continue

        cleaned_records.append(item)

    # Alternate phones duplicate remove
    profile['alternate_phones'] = list(set(profile['alternate_phones']))

    return {
        "target_summary": profile,
        "detailed_records": cleaned_records
    }

# ==========================================
# MAIN ROUTE
# ==========================================
@app.route('/ny/none/usr/@None_usernam3/NUMBER/IND/NUM=<number>', methods=['GET'])
def get_info(number):
    start_time = time.time()
    
    # 1. Validation
    clean_num = "".join(filter(str.isdigit, number))
    if not clean_num or len(clean_num) < 10:
        return jsonify({"error": "Invalid Number"}), 400

    # 2. Local Extraction
    try:
        fmt_num = f"+{clean_num}" if clean_num.startswith('91') else f"+91{clean_num}"
        parsed_num = phonenumbers.parse(fmt_num, "IN")
        local_data = {
            "carrier": carrier.name_for_number(parsed_num, "en"),
            "circle": geocoder.description_for_number(parsed_num, "en"),
            "valid": phonenumbers.is_valid_number(parsed_num)
        }
    except:
        local_data = {"error": "Local parsing failed"}

    # 3. Main API Call
    api_status = "success"
    try:
        response = requests.get(BASE_API_URL, params={'q': clean_num}, headers=HEADERS, timeout=12)
        if response.status_code == 200:
            raw_json = response.json()
            # Yahan hum Data Cleaning Function ko call kar rahe hain
            processed_data = process_raw_data(raw_json.get('data', []))
        else:
            processed_data = {"message": "No records found"}
            api_status = "empty"
    except Exception as e:
        processed_data = {"message": "Database unreachable", "error": str(e)}
        api_status = "failed"

    # 4. Final Professional JSON Output
    current_branding = BRANDING.copy()
    current_branding["server_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return jsonify({
        "branding": current_branding,
        "status": api_status,
        "performance_latency": f"{round(time.time() - start_time, 4)}s",
        "input_details": {
            "number": clean_num,
            "network_info": local_data
        },
        "intelligence_report": processed_data
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
