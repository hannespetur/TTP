#!/usr/bin/python
# -*- coding: utf-8 -*-

from urllib2 import Request, urlopen, URLError
import json

request2 = Request('http://placekitten.com/')
request = Request('http://api.dohop.com/api/v1/livestore/is/DK/per-airport/CPH,MMX/2015-02-01/2016-02-01?id=H4cK3r&pretty=true&fare-format=full&airport-format=compact&b_max=1&currency=FKP&include_split=true&stay=1-30')
try:
	response = urlopen(request)
	data = json.load(response) 
	response2 = urlopen(request2)  
	print data["airports"]["KEF"]
	print >> open('dump.json','w'), json.dumps(data)
	print data["fares"][0]
	kittens = response2.read()
	print kittens[519:1000]
except URLError, e:
    print 'No kittez. Got an error code:', e

## Parametrar sem eg þarf
minimum_stay = 1
maximum_stay = 30
start_airport = "KEF"
end_airport = "KEF"


