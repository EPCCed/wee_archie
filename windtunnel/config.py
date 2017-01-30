#File containing configuration options and constants



#location of Edinburgh (degrees lat and lon)
lat0=55.98
lon0=-3.18

wlgth = 15 #wing length (m)
mass = 50 #tonnes
thrust = 170 #kN

fuel = 250. #units of fuel in fuel tank
maxrate = 0.1 #amount of fuel used per second at maxthrust


#PROBABLY DO NOT CHANGE THINGS BELOW HERE

re=6371. #earth radius (mean)
lmax = 2000. #runway length (m)

wgt=mass*10*1000. #weight in N


rho = 1.225 #air density (kg/m^3)

atop = 2.0 #top length of wing (m)
aside = 0.2 #side length of wing (m)

dt = 0.05 #timestep (s)

scale = 0.38 #scale metres to pixels
