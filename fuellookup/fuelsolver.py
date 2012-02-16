from cvxpy import *
from geopy import distance
from geopy import geocoders
import time

class Route:
    def __init__(self,stations):
	self.stations = stations
        self.set_distances()

    def set_distances(self):
        self.distances = [self.get_distance(first_stat,
                                            second_stat)
                                            for first_stat,second_stat
                                            in zip(self.stations[:-1],
                                                   self.stations[1:])]
    
    def get_distance(self,st1, st2):
        try:
            print st1
            print st2
            g = geocoders.Google()
            _, d1 = g.geocode(st1.address)
            _, d2 = g.geocode(st2.address)
            max_val =  distance.distance(d1, d2).mi
        except:
            max_val = 5.
        time.sleep(.25)
        if max_val < 2.:
            return 2.
        return max_val

    def distance_profile(self):
        dist = 0
        prof = [dist]
        for distance in self.distances:
            dist+=distance
            prof.append(dist)
        return prof


class Car:
    DEF_ECONOMY = 10.
    DEF_START = 80.
    DEF_TANK = 100.
    def __init__(self, 
                 start=None,
                 economy = None,
                 tank_max = None):
        if start is None:
            start = self.DEF_START
        if economy is None:
            economy = self.DEF_ECONOMY
        if tank_max is None:
            tank_max = self.DEF_TANK
            
	self.start = start
	self.economy = economy
        self.tank_max = tank_max

            

        
class FuelSolver:

    def __init__(self, car, route, gas_min = 10.):
	self.car = car
	self.route = route
	self.gas_min = gas_min


    def solve(self):
	n = len(self.route.stations)
	in_tank = variable(n,name ='gas in tank')
	bought = variable(n,name = 'gas bought')
	constraints = ([eq(in_tank[0,0],self.car.start)] +
		       [eq(in_tank[i+1,0],
                           in_tank[i,0] +
                           bought[i,0] -
                           self.route.distances[i]*self.car.economy)
                            for i in range(n-1)] + 
                        [geq(in_tank,self.gas_min)] + 
                        [leq(in_tank + bought,self.car.tank_max)] +
                        [geq(bought,0)]
                        )
        fuel_cost = sum(
            [self.route.stations[i].regular*
             bought[i,0]
             for i in range(n)]
             )
        print fuel_cost
	p = program(minimize(fuel_cost),
                             constraints)
	p.solve()
        self.bought = bought
        self.in_tank = in_tank
        self.program = p        
	
