#!/usr/bin/env python

import json
import dns
import dns.rdataclass
import dns.rdatatype
from dns.rdtypes.ANY import LOC

def loc_rdata(lat, lon):
    try:
        rdata = dns.rdtypes.ANY.LOC.LOC(
            dns.rdataclass.IN,
            LOC,
            float(lat),
            float(lon),
            altitude=0)
        return rdata.to_text()
    except:
        pass
    return None

def load():
    # airports.json is from https://github.com/jbrooksuk/JSON-Airports
    airport_array = json.loads(open('airports.json').read())
    airports = {}

    for ap in airport_array:
        if ap['type'] == 'airport':
            lat = lon = None
            try:
                lat = float(ap['lat'])
                lon = float(ap['lon'])
            except:
                pass
            airports[ap['iata']] = {
                'name'  : ap['name'],
                'lat'   : lat,
                'lon'   : lon,
                'cc'    : ap['iso'],
                'loc'   : loc_rdata(lat, lon),
            }

    return airports

# print airports['IBZ'], json.dumps(airports['IBZ'], indent=4)
