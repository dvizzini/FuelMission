''' just shows that this shit is working '''

from fuellookup import gas_prices
from fuelsolver import *

zip_code = 94709
route = Route(gas_prices(zip_code)[:15])
car = Car()

solver = FuelSolver(car,route)
solver.solve()

def plot_data():
    # here to plot if you want to install pylab 
    from pylab import *
    bought = solver.bought.value.transpose().tolist()[0]
    in_tank = solver.in_tank.value.transpose().tolist()[0]
    prices = [station.regular for station in route.stations]
    profile = route.distance_profile()
    hold(True)
    plot(profile,bought)
    plot(profile,in_tank,'k--')
    ylabel('amount of gas')
    legend(['bought','in tank'],loc='upper left')
    twinx()
    plot(profile,prices,'r-.')
    legend(['prices'],loc='upper right')
    show()
    xlabel('distance')
    ylabel('fuel price')

# show structure of LP
solver.program.show()
print
print
print

# show the amount to buy
print 'buy values:'
print solver.bought.value

