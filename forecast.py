import json
import discord
import requests
from geopy.geocoders import Nominatim

points_headers = {
    'User-Agent': 'Tarleton Discord Bot Weather Service Display',
    'Accept': 'application/geo+json'
    }

def geocode(client_location):
    geolocator = Nominatim(user_agent=points_headers['User-Agent'])
    location = geolocator.geocode(client_location)
    if location == None:
        return None
    loc = [location.latitude, location.longitude]
    return loc

def get_gridpoints(location):
    client_location = geocode(location)
    try:
        print("https://api.weather.gov/points/{0[0]},{0[1]}".format(client_location))
        points = requests.get(url="https://api.weather.gov/points/{0[0]},{0[1]}".format(client_location), headers=points_headers)
        package = json.loads(points.text)
        url = package["properties"]["forecast"]
    except:
        return None
    return url

def getForecast(location):
    forecast_url = get_gridpoints(location)
    print(forecast_url)
    if forecast_url == None:
        return None
    try:
        url_data = requests.get(url=forecast_url, headers=points_headers)
    except:
        return None
    json_data = json.loads(url_data.text)
    forecast_data = json_data['properties']['periods']
    return forecast_data

def getForecastHourly(location):
    forecast_url = get_gridpoints(location)
    print(forecast_url)
    if forecast_url == None:
        return None
    try:
        url_data = requests.get(url=forecast_url+"/hourly", headers=points_headers)
    except:
        return None
    json_data = json.loads(url_data.text)
    forecast_data = json_data['properties']['periods']
    return forecast_data

def getAllAlerts(location):
    try:
        url_data = requests.get(url="https://api.weather.gov/alerts/active/area/{0}".format(location), headers=points_headers)
        json_data = json.loads(url_data.text)
        alert_data = json_data['features']
    except:
        return None
    return alert_data

def getCountyAlerts(location):
    client_location = geocode(location)
    try:
        points = requests.get(url="https://api.weather.gov/points/{0[0]},{0[1]}".format(client_location), headers=points_headers)
        package = json.loads(points.text)
        county_ID = package['properties']['county'].strip('https://api.weather.gov/zones/county/')
        alerts = requests.get(url=f"https://api.weather.gov/alerts/active?zone={county_ID}", headers=points_headers)
        alerts_data = json.loads(alerts.text)
    except:
        return None
    return alerts_data['features']
        
