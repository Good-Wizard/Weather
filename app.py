from flask import Flask, request, abort, render_template
import requests
import logging
from logging.handlers import RotatingFileHandler

app = Flask(__name__, static_folder='static')

WEATHER_API_URL = "http://api.openweathermap.org/data/2.5/weather"
API_KEY = "8ec6af652686cbe5b7b800002c8fba1a"

logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# file_handler = RotatingFileHandler('api_logs.log', maxBytes=10000, backupCount=1, encoding='utf-8')
# formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s - IP: %(ip)s')
# file_handler.setFormatter(formatter)
# logger.addHandler(file_handler)

def validate_response_data(data):
    """Validate the weather data response from the API."""
    if "main" not in data or "weather" not in data:
        abort(500, description="Invalid weather data format")

@app.before_request
def log_request_info():
    """Log request information before handling the request."""
    # logger.info('Request Headers: %s', request.headers, extra={'ip': request.remote_addr})

@app.route('/', methods=['GET', 'POST'])
def index():
    """Render the index page and handle form submission."""
    return render_template('index.html')

@app.route('/weather', methods=['POST'])
def weather():
    """Fetch weather data for a given city and render it on a new page."""
    city = request.form.get('city')
    units = request.form.get('units', 'metric')

    if not city:
        return render_template('index.html', error="City parameter is required")

    try:
        params = {"q": city, "appid": API_KEY, "units": units}
        response = requests.get(WEATHER_API_URL, params=params)
        response.raise_for_status()
        
        weather_data = response.json()
        validate_response_data(weather_data)

        data = {
            'city': city,
            'weather_description': weather_data['weather'][0]['description'],
            'temperature': weather_data['main']['temp'],
            'humidity': weather_data['main']['humidity'],
            'wind_speed': weather_data['wind']['speed'],
            'pressure': weather_data['main']['pressure'],
            'weather_icon': weather_data['weather'][0]['icon']
        }
        
        return render_template('weather.html', weather=data)

    except requests.exceptions.HTTPError as e:
        # logger.error("HTTP Error occurred: %s", e, extra={'ip': request.remote_addr})
        return render_template('index.html', error="City not found or HTTP Error")
    
    except Exception as e:
        # logger.error("An unexpected error occurred: %s", e, extra={'ip': request.remote_addr})
        return render_template('index.html', error="An unexpected error occurred")

if __name__ == "__main__":
    app.run(debug=True)
