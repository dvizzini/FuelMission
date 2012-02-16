

from fuellookup import gas_prices
from fuelsolver import *


stations = gas_prices(95628)

print distances(stations[0],stations[1])
