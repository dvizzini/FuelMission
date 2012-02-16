from requests import get
from simplejson import loads

class Station:

    def __init__(self,kwargs):
        self.regular = float(kwargs['regular'])
        self.address = kwargs['address']

    def __repr__(self):
        return '%s: %f' % (self.address, self.regular)

    def __str__(self):
        return self.__repr__()
    

def gas_prices(zip_code):
    url = 'http://api.mshd.net'
    return [Station(item)
            for item in 
            loads(
                get(url, 
                    params=dict(gasprice = zip_code)
                    ).text
                    )['item']]


if __name__ == '__main__':
    print gas_prices(95628)
   
