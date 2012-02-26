from requests import get
from simplejson import loads
import multiprocessing

class Station:
    ''' just holds some data we would need for stations'''
    
    def __init__(self,kwargs):
        self.regular = float(kwargs['regular'])
        self.address = kwargs['address']

    def __repr__(self):
        return '%s: %f' % (self.address, self.regular)

    #being a bit anal: http://stackoverflow.com/questions/1307014/python-str-versus-unicode
    def __unicode__(self):
        return self.__repr__()
    
    def __str__(self):
        return unicode(self).encode('utf-8')

def gas_prices(zip_code):
    ''' creates a list of stations from a zip code query'''
    
    url = 'http://api.mshd.net'
    return [Station(item)
            for item in 
            loads(
                get(url, 
                    params=dict(gasprice = zip_code)
                    ).text
                    )['item']]


def multi_prices(zip_codes):
    pool = multiprocessing.Pool(len(zip_codes))
    zip_stats = pool.map(gas_prices,zip_codes)
    
    return [{'address':stat.address,'price':stat.regular} for z in zip_stats for stat in z]
                                    
if __name__ == '__main__':
    print 'hello'
