from cvxpy import program, eq, geq, leq, variable, minimize
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
    DEF_ECONOMY = 0.1#DV set low to get meaningful comparison of methods
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
    ''' the bulk of the operation, holds the DP and LP programs '''
    
    def __init__(self, car, route, gas_min = 10., **kwargs):
        self.car = car
        self.route = route
        self.gas_min = gas_min
        self.method = kwargs.get('method',"linear")
    
    def solve(self):
        ''' solver for the optimal purchasing of gas at stations
        does not return anything, but attaches some resulting properties at the end'''
        
        n = len(self.route.stations)

        if self.method == "dynamic":
            
            def conditionallyFillUp(gas_in_tank,station):
                print 'filling up'
                distance_to_end = sum([self.route.distances[j]
                                       for j in range(station,n)]
                                      )
                bought.append(max(0,min(distance_to_end / self.car.economy, self.car.tank_max) - gas_in_tank))

            prices = [station.regular for station in self.route.stations]
            
            print 'prices: ' + str(prices)
            
            i = 0
            range_of_car = (self.car.tank_max - self.gas_min) * self.car.economy
            print 'range of car: ' + str(range_of_car)
            
            #set initial stations
            current_price = self.route.stations[i].regular
            station_chosen = i
            

            #Probably safe to assume both are zero, call api if necessary
            distance_to_first_station = 0
            distance_from_last_station = 0
            
            if (self.car.start - distance_to_first_station / self.car.economy < self.gas_min):
                raise Exception("Unfeasible to reach")
            else:
                gas_in_tank_at_last_station = self.car.start - (distance_to_first_station / self.car.economy)
            
            #Make parameter (probably as proportion of full tank) on website
            gas_at_end = self.gas_min
                        
            #for export
            stations_chosen = []
            bought = []
            
            #simulte partially filled tank as miles already driven
            miles_since_last_stop = (self.car.tank_max - gas_in_tank_at_last_station) * self.car.economy + distance_to_first_station
            
            #make sure you can get home
            self.route.distances.append(distance_from_last_station)

            while i < n:
                
                #for feasibility check
                firstStationOnTank = i
                
                #determine where car should stop
                while i < n:
                    
                    #check if next stop is cheaper
                    print i
                    print current_price
                    if self.route.stations[i].regular < current_price:
                        current_price = self.route.stations[i].regular
                        station_chosen = i
                        print 'station_chosen: ' + str(station_chosen)
                    
                    #increment
                    miles_since_last_stop += self.route.distances[i]
                    i = i + 1
                    print 'miles_since_last_stop: ' + str(miles_since_last_stop)
                    if miles_since_last_stop > range_of_car:
                        print i
                        if (gas_in_tank_at_last_station - self.route.distances[firstStationOnTank] / self.car.economy < self.gas_min):
                            raise Exception("Unfeasible to reach")
                        stations_chosen.append(station_chosen)
                        current_price = self.route.stations[i].regular
                        station_chosen = i
                        break

                #determine how much gas car should get
                if len(stations_chosen) > 1:
                    distance_between_stations = sum([self.route.distances[j]
                                           for j in range(stations_chosen[len(stations_chosen) - 2],stations_chosen[len(stations_chosen) - 1])]
                                          )
                    print stations_chosen
                    print 'last_station: ' + str(stations_chosen[len(stations_chosen) - 2]) + ", price:" + str(self.route.stations[stations_chosen[len(stations_chosen) - 2]].regular)
                    print 'this station: ' + str(stations_chosen[len(stations_chosen) - 1]) + ", price:" + str(self.route.stations[stations_chosen[len(stations_chosen) - 1]].regular)
                    if (self.route.stations[stations_chosen[len(stations_chosen) - 2]].regular < self.route.stations[stations_chosen[len(stations_chosen) - 1]].regular):
                        #fill 'er up, errr, conditionally
                        conditionallyFillUp(gas_in_tank_at_last_station, stations_chosen[len(stations_chosen) - 2])
                    else:
                        #only get enough gas to get to next station
                        print 'getting minimum'
                        bought.append(distance_between_stations / self.car.economy)
                    
                    gas_in_tank_at_last_station = gas_in_tank_at_last_station - (distance_between_stations / self.car.economy) + bought[len(bought) - 1]
                    
                miles_since_last_stop = 0
                
            stations_chosen.append(station_chosen)
            
            conditionallyFillUp(gas_in_tank_at_last_station, stations_chosen[len(stations_chosen) - 1])
            
            print 'stations_chosen: ' + str(stations_chosen)
            print 'bought: ' + str(bought)
            
            objective_value = sum(
                            [self.route.stations[stations_chosen[j]].regular*bought[j]
                                for j in range(len(stations_chosen))]
                            )
            
            self.stations_chosen = stations_chosen
            
        else: 
            # how to constrain the LP
            in_tank = variable(n,name ='gas in tank') # how much gas in tank var
            bought = variable(n,name = 'gas bought') # how much to buy at each station var

            constraints = ([eq(in_tank[0,0],self.car.start)] + # starting gas
                           [eq(in_tank[i+1,0], # mass balance
                               in_tank[i,0] +
                               bought[i,0] -
                               self.route.distances[i]/self.car.economy)#DV: Changed from * to /
                               for i in range(n-1)] + 
                            [geq(in_tank,self.gas_min)] + # can't dip below certain amount
                            [leq(in_tank + bought,self.car.tank_max)] + # max size of tank
                            [geq(bought,0)] # physical constraint (cannot cyphon gas for sale to bum)
                            )
            
            # the total cost of the fuel
            fuel_cost = sum(
                            [self.route.stations[j].regular*bought[j,0]
                             for j in range(n)]
                            )
            
            # define program
            p = program(minimize(fuel_cost), constraints)
            objective_value = p.solve()
            
            # attach properties to access later
            
            self.in_tank = in_tank
            self.program = p
        
        self.bought = bought
        self.objective_value = objective_value