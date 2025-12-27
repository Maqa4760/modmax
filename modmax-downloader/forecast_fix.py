import requests

def test_forecast_api():
    """Test forecast API for different cities"""
    cities = ["Baku", "Ganja", "Sumqayit", "Absheron"]
    
    for city in cities:
        # Use Open-Meteo API with Baku coordinates for all Azerbaijan cities
        coords = [40.4093, 49.8671]  # Baku coordinates
        
        url = f"https://api.open-meteo.com/v1/forecast?latitude={coords[0]}&longitude={coords[1]}&daily=temperature_2m_max,temperature_2m_min,weathercode,windspeed_10m_max,relativehumidity_2m_mean&timezone=auto"
        
        try:
            response = requests.get(url)
            data = response.json()
            
            print(f"City: {city}")
            print(f"Status: {response.status_code}")
            print(f"Has daily data: {'daily' in data}")
            
            if 'daily' in data:
                daily = data['daily']
                print(f"Days available: {len(daily['time'])}")
                print("First day data:")
                print(f"  Temp max: {daily['temperature_2m_max'][0]}")
                print(f"  Temp min: {daily['temperature_2m_min'][0]}")
                print(f"  Weather code: {daily['weathercode'][0]}")
            else:
                print(f"Error: {data}")
            print("-" * 50)
            
        except Exception as e:
            print(f"Exception for {city}: {e}")
            print("-" * 50)

if __name__ == "__main__":
    test_forecast_api()
