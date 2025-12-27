from flask import Flask, render_template, request, jsonify
import requests
import json
import random
from datetime import datetime
import pytz

app = Flask(__name__)

# Weather API (WeatherAPI - free tier)
WEATHER_API_KEY = "demo"  # Free demo key
WEATHER_URL = "http://api.weatherapi.com/v1/current.json"

# Currency API (free)
CURRENCY_URL = "https://api.exchangerate-api.com/v4/latest/USD"

# Multi-language support
LANGUAGES = {
    'az': {'name': 'Azərbaycan', 'currency': 'AZN', 'timezone': 'Asia/Baku'},
    'en': {'name': 'English', 'currency': 'USD', 'timezone': 'UTC'},
    'tr': {'name': 'Türkçe', 'currency': 'TRY', 'timezone': 'Europe/Istanbul'},
    'ru': {'name': 'Русский', 'currency': 'RUB', 'timezone': 'Europe/Moscow'}
}

# Country detection by IP
COUNTRY_MAPPING = {
    'AZ': {'lang': 'az', 'currency': 'AZN', 'default_city': 'Baku'},
    'TR': {'lang': 'tr', 'currency': 'TRY', 'default_city': 'Istanbul'},
    'US': {'lang': 'en', 'currency': 'USD', 'default_city': 'New York'},
    'GB': {'lang': 'en', 'currency': 'GBP', 'default_city': 'London'},
    'DE': {'lang': 'en', 'currency': 'EUR', 'default_city': 'Berlin'},
    'FR': {'lang': 'en', 'currency': 'EUR', 'default_city': 'Paris'},
    'RU': {'lang': 'ru', 'currency': 'RUB', 'default_city': 'Moscow'}
}

# Azerbaijan regions
AZERBAIJAN_REGIONS = [
    "Baku", "Ganja", "Sumqayit", "Mingachevir", "Lankaran",
    "Shaki", "Shirvan", "Nakhchivan", "Khankandi", "Yevlakh",
    "Absheron", "Agdash", "Aghjabadi", "Aghdam", "Aghstafa",
    "Astara", "Barda", "Beylagan", "Bilasuvar", "Dashkasan",
    "Fuzuli", "Gadabay", "Goranboy", "Goychay", "Hajigabul",
    "Imishli", "Ismayilli", "Jabrayil", "Julfa", "Kalbajar",
    "Kangarli", "Kurdamir", "Lachin", "Lerik", "Masally",
    "Neftchala", "Oghuz", "Ordubad", "Qabala", "Qakh",
    "Qazakh", "Quba", "Qubadli", "Qusar", "Saatly",
    "Sabirabad", "Shabran", "Shakhbuz", "Shamakhi", "Shamkir",
    "Sharur", "Shusha", "Siyazan", "Tartar", "Tovuz",
    "Ujar", "Yardimli", "Zangilan", "Zaqatala", "Zardab"
]

# World capitals
WORLD_CAPITALS = [
    {"name": "London", "country": "UK"},
    {"name": "Paris", "country": "France"},
    {"name": "Berlin", "country": "Germany"},
    {"name": "Madrid", "country": "Spain"},
    {"name": "Rome", "country": "Italy"},
    {"name": "Moscow", "country": "Russia"},
    {"name": "Istanbul", "country": "Turkey"},
    {"name": "Dubai", "country": "UAE"},
    {"name": "Tokyo", "country": "Japan"},
    {"name": "New York", "country": "USA"},
    {"name": "Beijing", "country": "China"},
    {"name": "Delhi", "country": "India"},
    {"name": "Sydney", "country": "Australia"},
    {"name": "Cairo", "country": "Egypt"},
    {"name": "Rio de Janeiro", "country": "Brazil"}
]

def get_user_location():
    """Get user location from IP"""
    try:
        # Free IP geolocation API
        response = requests.get('https://ipapi.co/json/')
        data = response.json()
        return {
            'country': data.get('country_code', 'US'),
            'city': data.get('city', 'New York'),
            'timezone': data.get('timezone', 'UTC')
        }
    except:
        return {'country': 'US', 'city': 'New York', 'timezone': 'UTC'}

def detect_user_preferences():
    """Detect user language and preferences"""
    location = get_user_location()
    country_code = location['country']
    
    # Get user preferences based on country
    if country_code in COUNTRY_MAPPING:
        mapping = COUNTRY_MAPPING[country_code]
        return {
            'lang': mapping['lang'],
            'currency': mapping['currency'],
            'default_city': mapping['default_city'],
            'location': location
        }
    
    # Default to English/USD
    return {
        'lang': 'en',
        'currency': 'USD',
        'default_city': 'New York',
        'location': location
    }

def get_weather(city):
    """Get weather data for city"""
    try:
        # Open-Meteo API (free, no API key needed)
        # City coordinates mapping
        city_coords = {
            "Baku": [40.4093, 49.8671],
            "Ganja": [40.6829, 46.3586],
            "Sumqayit": [40.5897, 49.5113],
            "Absheron": [40.5000, 49.9000],
            "London": [51.5074, -0.1278],
            "Paris": [48.8566, 2.3522],
            "New York": [40.7128, -74.0060],
            "Moscow": [55.7558, 37.6173],
            "Istanbul": [41.0082, 28.9784],
            "Tokyo": [35.6762, 139.6503],
            "Dubai": [25.2048, 55.2708]
        }
        
        # Default coordinates if city not found
        coords = city_coords.get(city, [40.4093, 49.8671])
        
        url = f"https://api.open-meteo.com/v1/forecast?latitude={coords[0]}&longitude={coords[1]}&current_weather=true&hourly=relativehumidity_2m,windspeed_10m&daily=temperature_2m_max,temperature_2m_min,weathercode&timezone=auto"
        
        response = requests.get(url)
        data = response.json()
        
        if 'current_weather' not in data:
            return None
            
        current = data['current_weather']
        temp = current['temperature']
        wind_speed = current['windspeed']
        humidity = data['hourly']['relativehumidity_2m'][0]
        
        # Weather description based on temperature and wind
        if temp > 25:
            desc = "Günəşli"
            icon = "sun"
        elif temp > 15:
            desc = "Qismən buludlu"
            icon = "cloud-sun"
        elif temp > 5:
            desc = "Buludlu"
            icon = "cloud"
        else:
            desc = "Soyuq"
            icon = "snowflake"
            
        return {
            "city": city,
            "temperature": round(temp),
            "description": desc,
            "humidity": humidity,
            "wind": round(wind_speed),
            "icon": icon,
            "feels_like": round(temp),
            "pressure": 1013,
            "visibility": 10
        }
    except Exception as e:
        print(f"Weather API Error: {e}")
        return None

def get_currency_rates():
    """Get currency exchange rates"""
    try:
        response = requests.get(CURRENCY_URL)
        data = response.json()
        return data
    except:
        return None

@app.route('/')
def home():
    # Detect user preferences
    user_prefs = detect_user_preferences()
    return render_template('index.html', user_prefs=user_prefs)

@app.route('/api/weather/<city>')
def api_weather(city):
    weather = get_weather(city)
    if weather:
        return jsonify(weather)
    return jsonify({"error": "City not found"}), 404

@app.route('/api/forecast/<city>')
def api_forecast(city):
    """Get 7-day weather forecast - FIXED VERSION"""
    try:
        # Use Baku coordinates for all Azerbaijan cities for now
        coords = [40.4093, 49.8671]  # Baku coordinates
        
        # FIXED API URL - removed problematic parameters
        url = f"https://api.open-meteo.com/v1/forecast?latitude={coords[0]}&longitude={coords[1]}&daily=temperature_2m_max,temperature_2m_min,weathercode,windspeed_10m_max&timezone=auto"
        
        response = requests.get(url)
        data = response.json()
        
        if 'daily' not in data:
            return jsonify({"error": "Forecast not available"}), 404
            
        daily = data['daily']
        forecast = []
        
        for i in range(len(daily['time'])):
            weather_code = daily['weathercode'][i]
            
            # Weather code to description
            if weather_code in [0, 1]:
                desc = "Günəşli"
                icon = "sun"
            elif weather_code in [2, 3]:
                desc = "Qismən buludlu"
                icon = "cloud-sun"
            elif weather_code in [45, 48]:
                desc = "Buludlu"
                icon = "cloud"
            elif weather_code in [51, 53, 55, 56, 57]:
                desc = "Yağışlı"
                icon = "cloud-rain"
            elif weather_code in [61, 63, 65, 66, 67]:
                desc = "Şiddətli yağış"
                icon = "cloud-showers-heavy"
            elif weather_code in [71, 73, 75, 77, 85, 86]:
                desc = "Qarlı"
                icon = "snowflake"
            else:
                desc = "Dəyişkən"
                icon = "cloud"
                
            forecast.append({
                "date": daily['time'][i],
                "temp_max": round(daily['temperature_2m_max'][i]),
                "temp_min": round(daily['temperature_2m_min'][i]),
                "description": desc,
                "icon": icon,
                "wind": round(daily['windspeed_10m_max'][i]),
                "humidity": 65  # Default humidity since we removed the problematic parameter
            })
            
        return jsonify({
            "city": city,
            "forecast": forecast[:7]  # 7 days
        })
        
    except Exception as e:
        print(f"Forecast API Error: {e}")
        return jsonify({"error": "Forecast not available"}), 500

@app.route('/api/currency')
def api_currency():
    rates = get_currency_rates()
    if rates:
        return jsonify(rates)
    return jsonify({"error": "Currency data unavailable"}), 500

@app.route('/api/regions')
def api_regions():
    return jsonify({
        "azerbaijan": AZERBAIJAN_REGIONS,
        "world": WORLD_CAPITALS
    })

@app.route('/api/user-location')
def api_user_location():
    """Get user's detected location and preferences"""
    return jsonify(detect_user_preferences())

@app.route('/api/set-language/<lang>')
def set_language(lang):
    """Set user language preference"""
    if lang in LANGUAGES:
        return jsonify({
            'success': True,
            'language': lang,
            'currency': LANGUAGES[lang]['currency']
        })
    return jsonify({'success': False, 'error': 'Language not supported'}), 400

if __name__ == '__main__':
    print("Starting Weather & Currency Site... FIXED VERSION")
    print("Open your browser and go to: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
