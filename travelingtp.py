#!/usr/bin/python
# -*- coding: utf-8 -*-

# Open street map: http://nominatim.openstreetmap.org/search?q=paris%20france&format=json
# README.md: file:///home/sennap/git/traveling-tourist-problem/README.md

import sys
import datetime
import json
import requests
import argparse
from copy import deepcopy
from itertools import permutations

def getJSONfromDohop(language, user_country, departure_airport, arrival_airports, date_from, date_to, optional_parameters):
	urlToDohop = "http://api.dohop.com/api/v1/livestore/%(language)s/%(user_country)s/per-airport/%(departure_airport)s%(arrival_airports)s%(date_from)s/%(date_to)s?id=H4cK3r" % locals()
	for i in optional_parameters:
		urlToDohop += "&"+i
	if verbose:
		print urlToDohop
	return urlToDohop

# Specify input arguments
language = "en"
user_country = "IS"
arrival_airports = "/"
original_airport = u"KEF"
# airports_to_visit = [u"CPH",u"LHR",u"DUB"]
airports_to_visit_no_original = [u"CPH",u"LHR",u"DUB",u"LAX"]
airports_to_visit = [original_airport]+airports_to_visit_no_original
all_airports = airports_to_visit
visited_airports = [original_airport]
total_trip_time = 250
min_time_per_location = 1
# Total trip time
n = len(airports_to_visit)
k = int(round(total_trip_time/n - min_time_per_location*(n+1)))
delta_k = datetime.timedelta(days=k)
start_date = datetime.date(2015,7,1)
min_days_per_location = datetime.timedelta(days=min_time_per_location)
date_from = start_date
# date_to = start_date - min_days_per_location
verbose = True

dlist = [{} for _ in xrange(n)]

def findFlights(visited_airports, airports_to_visit, date_from):
	# Látum dlist vera global breyta sem við breytum stöðugt
	global dlist
	date_to = date_from + delta_k
	if verbose:
		print "Visited and left to visit ", visited_airports, airports_to_visit
	i = len(visited_airports)-1
	if (len(airports_to_visit) == 0):
		if verbose:
			print "I'm done!", visited_airports
		return 0

	key = visited_airports[-1]
	if key not in dlist[i]:
		if (len(airports_to_visit[1:]) == 0):
			url = getJSONfromDohop(language,user_country,visited_airports[-1],'/'+original_airport+'/',"%d-%d-%d" % (date_from.year,date_from.month,date_from.day) , "%d-%d-%d" % (date_to.year,date_to.month,date_to.day),["fare-format=compact","airport-format=compact","currency=ISK"])
		else:
			url = getJSONfromDohop(language,user_country,visited_airports[-1],'/'+','.join(all_airports[1:])+'/',"%d-%d-%d" % (date_from.year,date_from.month,date_from.day) , "%d-%d-%d" % (date_to.year,date_to.month,date_to.day),["fare-format=compact","airport-format=compact","currency=ISK"])
		r = requests.get(url).json()
		for fare in r["fares"]:
			port_from = fare["a"]
			port_to = fare["b"]
			if verbose:
				print i, port_from, port_to, int(round(fare["conv_fare"]))

			## Geymum leitarniðurstöðuna
			if port_from not in dlist[i]:
				dlist[i][port_from] = {port_to: int(round(fare["conv_fare"]))}
			else:
				if port_to in dlist[i][port_from]:
					print "TTTTTTTHHHHHHHHHHHIIIIIIIIISSSSS shouldn't happen ever"
				dlist[i][port_from][port_to] = int(round(fare["conv_fare"]))

			if (len(airports_to_visit) == 1 and port_to == original_airport):
				## Eigum bara eftir að fara heim
				findFlights(visited_airports+[port_to], [], date_from+delta_k+min_days_per_location)
			elif (port_to != original_airport):
				## Förum hvert sem er (bara ekki heim)
				try:
					airports_to_visit2 = deepcopy(airports_to_visit)
					airports_to_visit2.remove(port_to)
				except:
					# print port_to+", I don't need to visit that sacred place anyway!"
					continue
				findFlights(visited_airports+[port_to], airports_to_visit2, date_from+delta_k+min_days_per_location)
	else:
		for port_to in dlist[i][key]:
			try:
				airports_to_visit2 = deepcopy(airports_to_visit)
				airports_to_visit2.remove(port_to)
			except:
				continue
			findFlights(visited_airports+[port_to], airports_to_visit2, date_from+delta_k+min_days_per_location)

findFlights(visited_airports, airports_to_visit, date_from)
if verbose:
	print "===========================RESULTS==========================="
	for d in dlist:
		print d

# Brute force algorithm
def bruteForce(dlist):
	# Let's hope we can find something smaller than sys.maxint
	min_price = sys.maxint
	min_perm = []
	for perm in permutations(airports_to_visit_no_original):
		# Start the price as 0 for each permute
		price = 0

		# Loop over all the items in the permute
		for i,airport in enumerate(perm):
			if verbose:
				print i, perm[i-1], airport, dlist[i],

			# Check if the we can travel to the next location
			if (i == 0 and airport in dlist[i][original_airport]):
				price += dlist[i][original_airport][airport]
				if verbose:
					print "Case 1 - Price ", price 
			elif (i < n-1 and i > 0 and airport in dlist[i][perm[i-1]]):
				price += dlist[i][perm[i-1]][airport]
				if verbose:
					print "Case 2 - Price ", price 
				if (i == n-2 and perm[i] in dlist[i+1]):
					i += 1
					price += dlist[i][perm[i-1]][original_airport]
					if verbose:
						print "Case 3 - Price ", price 
			else:
				if verbose:
					print "Case 4 - Price ", price 
				break

			# If we have travelled to the all the location then i == n-1
			if (i == n-1 and price < min_price):
				min_price = price
				min_perm = perm
				if verbose:
					print i,"MINPRICE ER",price,perm
			
			# If we are already over the minimum price there's no point in continuing
			elif (price > min_price):
				break

	return min_price, min_perm

visited_airports = [0]*n
visited_airports[0] = original_airport


min_price = sys.maxint

# Brute force it!!
min_price, min_perm = bruteForce(dlist)

# Print out results nicely
min_order = original_airport
for location in min_perm:
	min_order += "->"+location

min_order += "->"+original_airport

print min_price, min_order


## The Main function
if __name__ == '__main__':
	# Create a argument parser
	parser = argparse.ArgumentParser(description="This program was created as part of the Dohop's Hackathon. The Traveling Tourist Problem (TTP) is a variation of the classic The Traveling Salesman Problem (TSP).")

	## Hint: add_argument(name or flags...[, action][, nargs][, const][, default][, type][, choices][, required][, help][, metavar][, dest])
	parser.add_argument('--verbose','-v',action='store_true')
	parser.add_argument('--test','-t',action='store_true')
	# parser.add_argument('--input','-i',default='',help='The input directory (i.e. where the files you want to organize).',action='store')
	# parser.add_argument('--output','-o',default='',help='The output directory (i.e. where you want to move your files).',action='store')
	parser.add_argument('--config','-c',default='config.json',help='Location of the config.json file',action='store')

	args = parser.parse_args()

