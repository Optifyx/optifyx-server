import serial
import serial.tools.list_ports

def convert_nmea_to_decimal(value: str, direction: str):
    if not value or not direction:
        return "Not Available"
    degrees = int(value[:2])
    minutes = float(value[2:])
    decimal = degrees + (minutes / 60)
    if direction in ['S', 'W']:
        decimal = -decimal
    return round(decimal, 6)

def parse_nmea_data(nmea_sentence: str):
    if nmea_sentence.startswith('$GPGGA') or nmea_sentence.startswith('$GPRMC'):
        parts = nmea_sentence.split(',')
        try:
            if nmea_sentence.startswith('$GPRMC'):
                lat = convert_nmea_to_decimal(parts[3], parts[4])
                lon = convert_nmea_to_decimal(parts[5], parts[6])
            elif nmea_sentence.startswith('$GPGGA'):
                lat = convert_nmea_to_decimal(parts[2], parts[3])
                lon = convert_nmea_to_decimal(parts[4], parts[5])
            else:
                return {"error": "Unsupported NMEA format"}
            return {"latitude": lat, "longitude": lon}
        except (IndexError, ValueError):
            return {"error": "Malformed NMEA data"}
    else:
        return {"error": "Unsupported NMEA sentence"}

def get_gps_data_from_device(port: str, baudrate: int = 9600, timeout: int = 2):
    try:
        with serial.Serial(port, baudrate, timeout=timeout) as ser:
            while True:
                line = ser.readline().decode('ascii', errors='ignore').strip()
                if line.startswith('$GPGGA') or line.startswith('$GPRMC'):
                    return parse_nmea_data(line)
    except Exception as e:
        return {"error": f"Failed to read GPS data from {port}: {str(e)}"}

def detect_gps_device():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        try:
            if "GPS" in port.description or "GNSS" in port.description:
                gps_data = get_gps_data_from_device(port.device)
                if gps_data and "latitude" in gps_data and "longitude" in gps_data:
                    return gps_data
        except Exception:
            continue
    return None