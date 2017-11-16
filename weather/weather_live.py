import urllib2
import json
from time import strftime


class LiveWeather(object):

    weather_constants={3166: {"D":"SSW","G":"32","H":"79.0","P":"1010","S":"16","T":"11.8","V":"40000","W":"8","Pt":"F","Dp":"8.3","$":"1140"},
                        3047: {"D":"S","H":"94.1","P":"1007","S":"13","T":"9.2","V":"18000","W":"15","Pt":"F","Dp":"8.3","$":"1140"},
                        3772: {"D":"SW","H":"58.2","P":"1024","S":"7","T":"11.4","V":"35000","W":"1","Pt":"F","Dp":"3.6","$":"900"},
                        3808: {"D":"SSW","H":"83.9","P":"1023","S":"15","T":"11.6","V":"2000","W":"12","Pt":"F","Dp":"9.0","$":"900"}}

    weatherCompassPoints = {"N" : 0, "NNE" : 22, "NE" : 45, "ENE" : 68, "E" : 90, "ESE" : 112, "SE" : 135, "SSE" : 158, "S" : 180, "SSW" : 202, "SW" : 225, "WSW" : 248,
                            "W" : 270, "WNW" : 292, "NW" : 315, "NNW" : 338}

    def __init__(self, place, historical=3, use_internal_values=False):

        # Read the current hour
        time = int(strftime("%H"))

        self.targetTime = time
        if (historical != None): self.targetTime-=historical

        if (use_internal_values):
            print "Using cached weather data"
            response = self.weather_constants[place]
            self.hour = []
            self.hour.append(response)
        else:
            try:
                # The UK Met Office live weather url
                url = "http://datapoint.metoffice.gov.uk/public/data/val/wxobs/all/json/" \
                  "%s?res=hourly&key=25617c79-940e-4254-8e5a-fbdc6d5f0f14" % place

                # Grab the data from the url and process it
                response = urllib2.urlopen(url, timeout=3)
                data = json.loads(response.read())

                # Get to the right data array
                if (len(data["SiteRep"]["DV"]["Location"]["Period"]) >= 2):
                    todayIndex=1
                else:
                    todayIndex=0
                days_weather = (data["SiteRep"]["DV"]["Location"]["Period"][todayIndex]["Rep"])

                hour_num = len(days_weather)
                self.hour = []

                # Loop to get the data from the arrays for the current time
                for i in range(hour_num):
                    hour_weather = int(days_weather[i]["$"]) / 60
                    if hour_weather == self.targetTime:
                        self.hour.append(days_weather[i])
                if len(self.hour) == 0:
                    print "Some error retrieving weather... Using default values for location "+str(place)
                    response = self.weather_constants[place]
                    self.hour = []
                    self.hour.append(response)
            except:
                print "No internet, using default values instead"
                response = self.weather_constants[place]
                self.hour = []
                self.hour.append(response)

    def target_time(self):
        return self.targetTime

    # Function that returns the weather type variable
    def hour_weather(self):

        return int(self.hour[0]["W"])

    def wind_compass_direction(self):
        return self.weatherCompassPoints[self.wind_direction()]

    # Function that returns the wind direction (compass)
    def wind_direction(self):

        return str(self.hour[0]["D"])

    # Function that returns the wind speed (mph)
    def wind_speed(self):
        return int(self.hour[0]["S"])

    def wind_gust(self):
        if "G" in self.hour[0]:
            return int(self.hour[0]["G"])
        else:
            return -1

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

        return float(self.hour[0]["T"])

    # Function that returns the visibility (m)
    def visibility(self):

        return int(self.hour[0]["V"])

    # Function that returns the dew point (C)
    def dew_point(self):

        return int(self.hour[0]["Dp"])

#print LiveWeather(3808).hour_weather()
