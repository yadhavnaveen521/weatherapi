from django.shortcuts import render, redirect
from .form import CityForm
from .models import City
from urllib.parse import quote
import requests
from django.contrib import messages

def home(request):
    api_key = '3b41bc71c0f7474b85d1c65959b9b480'
    url = 'http://api.openweathermap.org/data/2.5/weather?q={}&appid={}&units=metric'

    if request.method == "POST":
        form = CityForm(request.POST)
        if form.is_valid():
            city_name = form.cleaned_data['name']
            encoded_city = quote(city_name)  # Encode city name for URL
            existing_city_count = City.objects.filter(name=city_name).count()

            if existing_city_count == 0:
                response = requests.get(url.format(encoded_city, api_key))
                if response.status_code == 200:
                    weather_data = response.json()
                    City.objects.create(name=city_name)
                    messages.success(request, f"{city_name} added successfully!")
                else:
                    messages.error(request, "City does not exist!")
            else:
                messages.error(request, "City already exists!")

    form = CityForm()
    cities = City.objects.all()
    data = []
    for city in cities:
        encoded_city = quote(city.name)  # Encode city name for URL
        response = requests.get(url.format(encoded_city, api_key))
        if response.status_code == 200:
            weather_data = response.json()
            city_weather = {
                'city': city.name,
                'temperature': weather_data.get('main', {}).get('temp'),
                'description': weather_data.get('weather', [{}])[0].get('description'),
                'country': weather_data.get('sys', {}).get('country'),
                'icon': weather_data.get('weather', [{}])[0].get('icon'),
            }
            data.append(city_weather)
        else:
            messages.error(request, f"Failed to retrieve data for {city.name}.")

    context = {'data': data, 'form': form}
    return render(request, "weatherapp.html", context)

def delete_city(request, city_name):
    City.objects.filter(name=city_name).delete()
    messages.success(request, f"{city_name} removed successfully!")
    return redirect('home')
