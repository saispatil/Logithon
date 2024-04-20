from flask import Flask, render_template, request
import requests

app = Flask(_name_)

GOOGLE_MAPS_API_KEY = 'AIzaSyBNJlRiTXD1y9q1g-BVi3fgOVCkUnrPOxY'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/directions', methods=['POST'])
def directions():
    origin = request.form['origin']
    destination = request.form['destination']

    directions_data = get_directions(origin, destination)
    distance, fuel_consumption = calculate_distance_and_fuel_consumption(directions_data)

    return render_template('directions.html', origin=origin, destination=destination, distance=distance, fuel_consumption=fuel_consumption)

def get_directions(origin, destination):
    url = f"https://maps.googleapis.com/maps/api/directions/json?origin={origin}&destination={destination}&key={GOOGLE_MAPS_API_KEY}"
    response = requests.get(url)
    data = response.json()
    return data

def calculate_distance_and_fuel_consumption(directions):
    distance = directions['routes'][0]['legs'][0]['distance']['text']
    steps = directions['routes'][0]['legs'][0]['steps']
    fuel_consumption = 0

    for step in steps:
        distance_in_km = step['distance']['value'] / 1000
        fuel_consumption += distance_in_km * 0.08  # Assuming 8 liters per 100 kilometers

    return distance, round(fuel_consumption, 2)

if _name_ == '_main_':
    app.run(debug=True)