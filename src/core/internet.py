import requests

def get_public_ip():
    try:
        response = requests.get("https://api64.ipify.org?format=json", timeout=5)
        response.raise_for_status()
        ip_data = response.json()
        return {"public_ip": ip_data.get("ip", "Not Available")}
    except Exception as e:
        return {"error": f"Failed to fetch public IP: {str(e)}"}