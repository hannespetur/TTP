#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import datetime
import json
import requests
import argparse
from copy import deepcopy

def getJSONfromDohop(language, user_country, departure_airport, arrival_airports, date_from, date_to, optional_parameters):
	urlToDohop = "http://api.dohop.com/api/v1/livestore/%(language)s/%(user_country)s/per-airport/%(departure_airport)s%(arrival_airports)s%(date_from)s/%(date_to)s?id=H4cK3r" % locals()
	for i in optional_parameters:
		urlToDohop += "&"+i
	if args.vverbose:
		print urlToDohop
	return urlToDohop

def findFlights(visited_airports, airports_to_visit, date_from):
	# Látum dlist vera global breyta sem við breytum stöðugt
	global dlist
	global all_perms_found

	date_to = date_from + delta_k
	if args.vverbose:
		print "Visited and left to visit ", visited_airports, airports_to_visit
	i = len(visited_airports)-1
	if (len(airports_to_visit) == 0):
		if args.verbose:
			print "Found a permutation!", visited_airports
		all_perms_found.append(visited_airports[1:-1])
		return 0

	key = visited_airports[-1]
	if key not in dlist[i]:
		if args.vverbose:
			print visited_airports, airports_to_visit, date_from
		if (len(airports_to_visit[1:]) == 0):
			url = getJSONfromDohop(language,user_country,visited_airports[-1],'/'+original_airport+'/',"%d-%d-%d" % (date_from.year,date_from.month,date_from.day) , "%d-%d-%d" % (date_to.year,date_to.month,date_to.day),["fare-format=compact","airport-format=compact","currency=ISK"])
		else:
			url = getJSONfromDohop(language,user_country,visited_airports[-1],'/'+','.join(all_airports[1:])+'/',"%d-%d-%d" % (date_from.year,date_from.month,date_from.day) , "%d-%d-%d" % (date_to.year,date_to.month,date_to.day),["fare-format=compact","airport-format=compact","currency=ISK"])
		r = requests.get(url).json()
		for fare in r["fares"]:
			port_from = fare["a"]
			port_to = fare["b"]
			if args.vverbose:
				print i, port_from, port_to, int(round(fare["conv_fare"])), fare["d1"]

			## Geymum leitarniðurstöðuna
			if port_from not in dlist[i]:
				dlist[i][port_from] = {port_to: [int(round(fare["conv_fare"])), fare["d1"]]}
			else:
				dlist[i][port_from][port_to] = [int(round(fare["conv_fare"])), fare["d1"]]

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

# Brute force algorithm
def bruteForce():
	global dlist
	# Let's hope we can find something smaller than sys.maxint
	min_price = sys.maxint
	min_perm = []
	for perm in all_perms_found:
		if args.verbose:
			print "Trying", perm
		# Start the price as 0 for each permute
		price = 0

		# Loop over all the items in the permute
		for i,airport in enumerate(perm):
			if args.vverbose:
				print i, perm[i-1], airport, dlist[i],

			# Check if the we can travel to the next location
			if (i == 0 and airport in dlist[i][original_airport]):
				price += dlist[i][original_airport][airport][0]
				if args.vverbose:
					print "Case 1 - Price ", price 
			elif (i < n-1 and i > 0 and perm[i-1] in dlist[i] and airport in dlist[i][perm[i-1]]):
				price += dlist[i][perm[i-1]][airport][0]
				if args.vverbose:
					print "Case 2 - Price ", price 
				if (i == n-2 and perm[i] in dlist[i+1]):
					i += 1
					price += dlist[i][perm[i-1]][original_airport][0]
					if args.vverbose:
						print "Case 3 - Price ", price 
			else:
				if args.vverbose:
					print "Case 4 - Price ", price 
				break

			# If we have travelled to the all the location then i == n-1
			if (i == n-1 and price < min_price):
				min_price = price
				min_perm = perm
				if args.verbose:
					print "== Min price is",price,"with perm",perm,"=="
			
			# If we are already over the minimum price there's no point in continuing
			elif (price > min_price):
				break

	return min_price, min_perm

## The Main function
if __name__ == '__main__':
	# Create a argument parser
	parser = argparse.ArgumentParser(description="This program was created as part of the Dohop's Hackathon. The Traveling Tourist Problem (TTP) is a variation of the classic The Traveling Salesman Problem (TSP).")

	## Hint: add_argument(name or flags...[, action][, nargs][, const][, default][, type][, choices][, required][, help][, metavar][, dest])
	parser.add_argument("--verbose","-v",help="Use verbose mode",action="store_true")
	parser.add_argument("--vverbose","-vv",help="Use very verbose mode",action="store_true")
	parser.add_argument("--language","-l",default="en",help="The language to get data from the Dohop API.",action="store")
	parser.add_argument("--user_country","-uc",default="IS",help="The user's country to get data from the Dohop API.",action="store")
	parser.add_argument("--start_airport","-sa",default="KEF",help="The start (and end) airport the user's will start at.",action="store")
	parser.add_argument("--visit_airports","-va",default="CPH,LHR,DUB,LAX",help="A comma seperated list of the airports that the user wants to visit.",action="store")
	parser.add_argument("--min_time","-m",default=1,help="The minimum time per location/airport.")
	parser.add_argument("--trip_time","-t",default=250,type=int,help="Specify the total trip time.")
	parser.add_argument("--currency","-c",default="ISK",help="Specify the currency to display flight prices in.")
	parser.add_argument("--first_flight_date","-f",default="2015.7.1",help="Date on the format YYYY.M.D. This date will determine when the first flight could possibly occur.")

	args = parser.parse_args()

	if args.vverbose:
		args.verbose = True
	
	# Specify input arguments
	language = args.language
	user_country = args.user_country
	original_airport = unicode(args.start_airport)
	airports_to_visit_no_original = args.visit_airports.split(',')
	airports_to_visit_no_original = map(unicode,airports_to_visit_no_original)
	airports_to_visit = [original_airport]+airports_to_visit_no_original
	all_airports = airports_to_visit
	visited_airports = [original_airport]
	total_trip_time = args.trip_time
	min_time_per_location = args.min_time
	currency = args.currency
	arg_date = args.first_flight_date.split('.')
	start_date = datetime.date(int(arg_date[0]),int(arg_date[1]),int(arg_date[2]))

	# start_date = datetime.date(2015,7,1)

	# n is the total number of places to visit
	n = len(airports_to_visit)

	# k is the time (in days) we should stay at each place
	k = int(round(total_trip_time/n - min_time_per_location*(n+1)))

	delta_k = datetime.timedelta(days=k)
	min_days_per_location = datetime.timedelta(days=min_time_per_location)
	date_from = start_date
	# date_to = start_date - min_days_per_location

	dlist = [{} for _ in xrange(n)]

	if args.verbose:
		"Finding all flights..."
	
	# Create a list that will keep track of all permutations found
	all_perms_found = []
	
	# Find all fligths
	findFlights(visited_airports, airports_to_visit, date_from)

	min_price = sys.maxint

	# Brute force it!!
	min_price, min_perm = bruteForce()

	# Print out results nicely
	if args.verbose:
		print "======================================= RESULTS ======================================="
	min_order = original_airport
	for i,location in enumerate(min_perm):
		if i == 0:
			min_order += " --("+dlist[i][original_airport][min_perm[i]][1]+" for "+str(dlist[i][original_airport][min_perm[i]][0])+" "+currency+")"
		else:
			min_order += " --("+dlist[i][min_perm[i-1]][min_perm[i]][1]+" for "+str(dlist[i][min_perm[i-1]][min_perm[i]][0])+" "+currency+")"
		min_order += "--> "+location

	if(min_perm != []):
		min_order += " --("+dlist[-1][min_perm[-1]][original_airport][1]+" for "+str(dlist[-1][min_perm[-1]][original_airport][0])+" "+currency+")--> "+original_airport

	print min_order
	print "Price:", min_price, currency