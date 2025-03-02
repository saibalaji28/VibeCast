from flask import Flask, render_template, request, redirect, url_for, jsonify
import requests
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

app = Flask(__name__)

# Configuration
OPENWEATHERMAP_API_KEY = '#'
TWILIO_ACCOUNT_SID = '#'
TWILIO_AUTH_TOKEN = '#'
TWILIO_PHONE_NUMBER = '#'

# Global variable to store weather data temporarily
weather_data = {}

def fetch_weather(city):
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHERMAP_API_KEY}&units=metric'
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def recommend_outfit(temperature):
    if temperature < 10:
        return "Wear a heavy coat, gloves, and a hat."
    elif 10 <= temperature < 20:
        return "Wear a light jacket and long pants."
    else:
        return "Wear a t-shirt and shorts."

def send_whatsapp_message(name, number, city, outfit):
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    message = (f"Hello {name},\n\n"
               f"The current weather in {city} is as follows:\n"
               f"Temperature: {weather_data['main']['temp']}°C\n"
               f"Humidity: {weather_data['main']['humidity']}%\n"
               f"Pressure: {weather_data['main']['pressure']} hPa\n"
               f"Weather: {weather_data['weather'][0]['description']}\n"
               f"Wind Speed: {weather_data['wind']['speed']} m/s\n\n"
               f"We recommend you to {outfit}.\n\n"
               f"Stay comfortable and have a great day!")
    try:
        print(f"Sending message to {number}...")
        msg = client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=f'whatsapp:{number}'
        )
        print(f"Message sent: SID={msg.sid}")
    except TwilioRestException as e:
        print(f"Failed to send message: {e}")
        print(f"Twilio Error Code: {e.code}")
        print(f"Twilio Error Message: {e.msg}")
        print(f"More information: {e.more_info}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    global weather_data
    
    name = request.form['name']
    number = request.form['number']
    city = request.form['city']
    
    try:
        weather_data = fetch_weather(city)
        temperature = weather_data['main']['temp']
        outfit = recommend_outfit(temperature)
        
        send_whatsapp_message(name, number, city, outfit)
        
        return redirect(url_for('details', name=name, city=city))
    except requests.exceptions.HTTPError as http_err:
        return jsonify({'error': f'HTTP error occurred: {http_err}'}), 500
    except Exception as err:
        return jsonify({'error': f'An error occurred: {err}'}), 500

@app.route('/details')
def details():
    global weather_data
    if not weather_data:
        return redirect(url_for('index'))

    temperature = weather_data['main']['temp']
    humidity = weather_data['main']['humidity']
    pressure = weather_data['main']['pressure']
    weather_description = weather_data['weather'][0]['description']
    wind_speed = weather_data['wind']['speed']
    outfit = recommend_outfit(temperature)
    
    name = request.args.get('name')
    city = request.args.get('city')
    
    return render_template('details.html', temperature=temperature, humidity=humidity, pressure=pressure, weather_description=weather_description, wind_speed=wind_speed, outfit=outfit, name=name, city=city)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
