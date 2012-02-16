from cvxpy import *
from geopy import distance
from geopy import geocoders
import time

class Route:
    ''' holds a list of stations (which are assumed to be in order)'''
    def __init__(self,stations):
	self.stations = stations
        # create the distances between cities right off the bat
        self.set_distances()

    def set_distances(self):
        ''' just calls the get_distance function 
        over all station neighbors '''
        
        self.distances = [self.get_distance(first_stat,
                                            second_stat)
                                            for first_stat,second_stat
                                            in zip(self.stations[:-1],
                                                   self.stations[1:])]
    
    def get_distance(self,st1, st2):
        ''' with some basic error handling cheating (and spacing stations)
        this function makes some google maps calls to get 
        the distance between addresses '''
        
        try:
            print st1
            print st2
            g = geocoders.Google()
            # get lat long pairs
            _, d1 = g.geocode(st1.address)
            _, d2 = g.geocode(st2.address)
            # get the miles between the lat longs
            max_val =  distance.distance(d1, d2).mi
            # bunch of wonky error handling follows
        except:
            max_val = 5.
        # the api is rate limited, thus the sleeping
        time.sleep(.25)
        if max_val < 2.:
            return 2.
        return max_val

    def distance_profile(self):
        ''' creates mileage markers for the stations '''
        dist = 0
        prof = [dist]
        for distance in self.distances:
            dist+=distance
            prof.append(dist)
        return prof


class Car:
    ''' just holds some properties that are vehicle-dependent'''
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
    ''' the bulk of the operation, holds the LP program '''
    
    def __init__(self, car, route, gas_min = 10.):
	self.car = car
	self.route = route
	self.gas_min = gas_min


    def solve(self):
        ''' solver for the optimal purchasing of gas at stations
        does not return anything, but attaches some resulting properties at the end'''
        
	n = len(self.route.stations)
	in_tank = variable(n,name ='gas in tank') # how much gas in tank var
	bought = variable(n,name = 'gas bought') # how much to buy at each station var
        
        # how to constrain the LP
	constraints = ([eq(in_tank[0,0],self.car.start)] + # starting gas
                       [eq(in_tank[i+1,0], # mass balance
                           in_tank[i,0] +
                           bought[i,0] -
                           self.route.distances[i]*self.car.economy)
                            for i in range(n-1)] + 
                        [geq(in_tank,self.gas_min)] + # can't dip below certain amount
                        [leq(in_tank + bought,self.car.tank_max)] + # max size of tank
                        [geq(bought,0)] # physical constraint
                        )
        
        # the total cost of the fuel
        fuel_cost = sum(
            [self.route.stations[i].regular*
             bought[i,0]
             for i in range(n)]
             )
        
        # define program
	p = program(minimize(fuel_cost),
                             constraints)
	p.solve()
        
        # attach properties to access later
        self.bought = bought
        self.in_tank = in_tank
        self.program = p        
	
