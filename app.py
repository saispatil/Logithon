import sys
import csv
import math
import datetime
import requests
import json
import folium
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QComboBox, QVBoxLayout, QTextBrowser
from PyQt5.QtGui import QFont

class AirportSelector(QWidget):
    def _init_(self):
        super()._init_()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Search bar for source airport
        self.source_search_label = QLabel('Search source airport:')
        self.source_search_label.setFont(QFont('Arial', 16))
        self.source_search_entry = QLineEdit()
        self.source_search_entry.setFont(QFont('Arial', 16))
        self.source_search_entry.textChanged.connect(self.updateSourceMenu)
        layout.addWidget(self.source_search_label)
        layout.addWidget(self.source_search_entry)

        # Source airport dropdown
        self.source_label = QLabel('Source airport:')
        self.source_label.setFont(QFont('Arial', 16))
        self.source_menu = QComboBox()
        self.source_menu.setFont(QFont('Arial', 16))
        layout.addWidget(self.source_label)
        layout.addWidget(self.source_menu)

        # Search bar for destination airport
        self.dest_search_label = QLabel('Search destination airport:')
        self.dest_search_label.setFont(QFont('Arial', 16))
        self.dest_search_entry = QLineEdit()
        self.dest_search_entry.setFont(QFont('Arial', 16))
        self.dest_search_entry.textChanged.connect(self.updateDestinationMenu)
        layout.addWidget(self.dest_search_label)
        layout.addWidget(self.dest_search_entry)

        # Destination airport dropdown
        self.destination_label = QLabel('Destination airport:')
        self.destination_label.setFont(QFont('Arial', 16))
        self.destination_menu = QComboBox()
        self.destination_menu.setFont(QFont('Arial', 16))
        layout.addWidget(self.destination_label)
        layout.addWidget(self.destination_menu)

        # Date entry field
        self.date_label = QLabel('Date of booking (YYYY-MM-DD):')
        self.date_label.setFont(QFont('Arial', 16))
        self.date_entry = QLineEdit()
        self.date_entry.setFont(QFont('Arial', 16))
        layout.addWidget(self.date_label)
        layout.addWidget(self.date_entry)

        # Output display
        self.output_display = QTextBrowser()
        self.output_display.setFont(QFont('Arial', 16))
        layout.addWidget(self.output_display)

        # Button
        self.display_button = QPushButton('Display Weather Forecast & Route')
        self.display_button.setFont(QFont('Arial', 16))
        self.display_button.clicked.connect(self.displayWeatherForecast)
        layout.addWidget(self.display_button)

        self.setLayout(layout)
        self.setWindowTitle('Airport Selector')
        self.loadAirportData()

    def loadAirportData(self):
        with open('airports.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            self.airport_data = list(reader)
            self.populateAirportMenus()

    def populateAirportMenus(self):
        self.source_menu.clear()
        self.destination_menu.clear()

        for airport in self.airport_data:
            self.source_menu.addItem(airport['name'])
            self.destination_menu.addItem(airport['name'])

    def updateSourceMenu(self):
        search_text = self.source_search_entry.text().lower()

        self.source_menu.clear()

        for airport in self.airport_data:
            if search_text in airport['name'].lower():
                self.source_menu.addItem(airport['name'])

    def updateDestinationMenu(self):
        search_text = self.dest_search_entry.text().lower()

        self.destination_menu.clear()

        for airport in self.airport_data:
            if search_text in airport['name'].lower():
                self.destination_menu.addItem(airport['name'])

    def displayWeatherForecast(self):
        source_airport_name = self.source_menu.currentText()
        destination_airport_name = self.destination_menu.currentText()
        booking_date = self.date_entry.text()

        source_airport = next((airport for airport in self.airport_data if airport['name'] == source_airport_name), None)
        destination_airport = next((airport for airport in self.airport_data if airport['name'] == destination_airport_name), None)

        if source_airport and destination_airport and booking_date:
            lat1, lon1 = float(source_airport['lat_decimal']), float(source_airport['lon_decimal'])
            lat2, lon2 = float(destination_airport['lat_decimal']), float(destination_airport['lon_decimal'])
            distance = self.haversine(lat1, lon1, lat2, lon2)
            airspeed = 500  # km/h
            air_time_min = distance / airspeed * 60  # convert distance to minutes
            air_time_hour = air_time_min / 60  # convert minutes to hours

            api_key = '12c7fe32f35f4a1c9f7f12def9acbf59'  # replace with your Weatherbit API key
            forecast = self.get_weather_forecast(datetime.datetime.strptime(booking_date, '%Y-%m-%d'), lat1, lon1, api_key)
            visibility = self.calculate_visibility(forecast)
            wind_speed = self.calculate_wind_speed(forecast)
            output_text = (f'Total travel time: {air_time_hour:.2f} hours\n'
                           f'Total distance: {distance:.2f} km\n'
                           f'Total air time: {air_time_hour:.2f} hours\n'
                           f'Air visibility: {visibility} m\n'
                           f'Wind speed: {wind_speed} m/s\n')
            self.output_display.setText(output_text)

            # Draw the route on the map
            if source_airport and destination_airport:
                route_map = self.draw_route(source_airport, destination_airport)
                route_map.save('route_map.html')
        else:
            self.output_display.setText("Please fill in all the fields.")

    def haversine(self, lat1, lon1, lat2, lon2):
        R = 6371  # Earth radius in km
        dlat = self.deg2rad(lat2 - lat1)
        dlon = self.deg2rad(lon2 - lon1)
        a = (math.sin(dlat / 2) * math.sin(dlat / 2) + math.cos(self.deg2rad(lat1)) * math.cos(self.deg2rad(lat2)) * math.sin(dlon / 2) * math.sin(dlon / 2))
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        d = R * c
        return d

    def deg2rad(self, deg):
        return deg * (math.pi/180)

    def get_weather_forecast(self, date, lat, lon, api_key):
        url = f'https://api.weatherbit.io/v2.0/forecast/daily?lat={lat}&lon={lon}&key={api_key}'
        response = requests.get(url)
        data = json.loads(response.text)
        forecast = []
        for d in data['data']:
            if d['ts'] > date.timestamp():
                forecast.append(d)
        return forecast[0]

    def calculate_visibility(self, forecast):
        visibility = 10000  # default visibility in meters
        if 'visibility' in forecast:
            visibility = forecast['visibility']
        return visibility

    def calculate_wind_speed(self, forecast):
        wind_speed = 0  # default wind speed in m/s
        if 'wind_speed' in forecast:
            wind_speed = forecast['wind_speed']
        return wind_speed

    def draw_route(self, source, destination):
        map = folium.Map(location=[0, 0], zoom_start=2)
        source_coords = self.get_coordinates(source['lat_decimal'], source['lon_decimal'])
        destination_coords = self.get_coordinates(destination['lat_decimal'], destination['lon_decimal'])
        folium.Marker(source_coords, popup=source['name']).add_to(map)
        folium.Marker(destination_coords, popup=destination['name']).add_to(map)
        folium.PolyLine(locations=[source_coords, destination_coords], color='blue').add_to(map)
        return map

    def get_coordinates(self, lat, lon):
        return float(lat), float(lon)

if _name_ == '_main_':
    app = QApplication(sys.argv)
    selector = AirportSelector()
    selector.show()
    sys.exit(app.exec_())