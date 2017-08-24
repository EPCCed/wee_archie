import urllib
import json
from time import strftime


class LiveWeather(object):

    def __init__(self, place):

        # Read the current hour
        time = int(strftime("%H"))

        try:

            # The UK Met Office live weather url
            url = "http://datapoint.metoffice.gov.uk/public/data/val/wxobs/all/json/" \
                  "%s?res=hourly&key=25617c79-940e-4254-8e5a-fbdc6d5f0f14" % place

            # Grab the data from the url and process it
            response = urllib.urlopen(url)
            data = json.loads(response.read())

            # Get to the right data array
            days_weather = (data["SiteRep"]["DV"]["Location"]["Period"][0]["Rep"])

            hour_num = len(days_weather)
            self.hour = []

            # Loop to get the data from the arrays for the current time
            for i in range(hour_num):
                hour_weather = int(days_weather[i]["$"]) / 60

                if hour_weather == time:
                    self.hour.append(days_weather[i])

        except:

            #print "No internet, using default values instead"
            response = {"d": 'NNE', "Pt": 'R', "H": 40.2, "P": 1014, "S": 7, "T": 19.0, "W": 1, "V": 30000, "Dp": 5.3, }
            self.hour = []
            self.hour.append(response)

    # Function that returns the weather type variable
    def hour_weather(self):

        return int(self.hour[0]["W"])

    # Function that returns the wind direction (compass)
    def wind_direction(self):

        return str(self.hour[0]["D"])

    # Function that returns the wind speed (mph)
    def wind_speed(self):
        return int(self.hour[0]["S"])

    # Function that returns the humidity (%)
    def humidity(self):

        return int(self.hour[0]["H"])

    # Function that returns the pressure (hpa)
    def pressure(self):

        return int(self.hour[0]["P"])

    # Function that returns the pressure tendency (Pa/s)
    def pressure_tendency(self):

        return str(self.hour[0]["Pt"])

    # Function that returns the temperature (C)
    def temperature(self):

        return int(self.hour[0]["T"])

    # Function that returns the visibility (m)
    def visibility(self):

        return int(self.hour[0]["V"])

    # Function that returns the dew point (C)
    def dew_point(self):

        return int(self.hour[0]["Dp"])

#print LiveWeather(3808).hour_weather()
