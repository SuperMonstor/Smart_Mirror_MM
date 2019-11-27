import pyowm #python OpenWeatherMap

owm = pyowm.OWM('f449ddb5863b9e4173397eb610b09505')#API KEY

loc=owm.weather_at_place('Bangalore')
weather=loc.get_weather()
w.get_weather_icon_url()
print(weather)

fc = owm.three_hours_forecast('Bangalore')
f = fc.get_forecast()

for weather in f:
      print (weather.get_weather(),weather.get_status())

