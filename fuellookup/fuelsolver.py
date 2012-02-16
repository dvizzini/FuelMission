from cvxpy import *

from geopy import distance
from geopy import geocoders


class Route:
    def __init__(self,stations):
	self.stations = stations



class Car:
    DEF_ECONOMY = 1.
    DEF_START = 100.
    def __init__(self, start = DEF_START, economy = DEF_ECONOMY):
	self.start = start
	self.economy = economy


def distances(st1, st2):
    g = geocoders.Google()
    _, d1 = g.geocode(st1.address)
    _, d2 = g.geocode(st2.address)
    return distance.distance(d1, d2)

        
class FuelSolver:

    def __init__(self, car, route, gas_min = 5.):
	self.car = car
	self.route = route
	self.gas_min = gas_min


    def solve(self):
	n = len(self.route.stations)
	in_tank = variable(n+1,name ='gas in tank')
	bought = variable(n+1,name = 'gas bought')
	constraints = ([eq(bought[0],self.car.start)] +
		       [eq(next_tank,
			   prev_tank + prev_gas - 
			   self.car.economy*distances(prev_stat, next_stat)
			   ) 
			   for prev_tank, 
			       next_tank, 
			       prev_stat, 
			       next_stat, 
			       prev_gas
			       in zip(in_tank[:n],
				      in_tank[1:],
				      self.route.stations[:n],
				      self.route.stations[1:],
				      in_tank[:n])] +
			 [ge(g,self.gas_min)])
	p = program(minimize(sum([station.regular*stat_bought 
				  for station,
				      stat_bought 
				      in zip(self.stations,
					     bought)])),
		    constraints)
	p.solve()
	return [b.value() for b in bought]
	
