# The traveling tourist problem (TTP)

## Motivation
Currently, [Dohop](http://www.dohop.is/) is providing fast and efficient flight results going from one to place to another and optionally returning back to your original location. These flights are on the format A -> B, or A -> B -> A and probably cover a very large portion of all flight searches. However, in many cases, one would want to travel to multiple places in no specific order, i.e. A -> {B,C,D,E,...} -> A. The number of possibilies to consider is n! where n is the number of places to visit (excluding the original one). For humans to figure out which order is the cheapest is quite tedious. If choosing a single flight from A -> B takes 1 minute, finding the cheapest route with 10 locations would take 2520 days or about 7 years (or if we did the search on the tidal planet from [Interstellar](http://www.imdb.com/title/tt0816692/) it would take about 423 millennia on Earth), assuming of course that we could get the flight schedule and prices 7 years into the future. My goal is to make a search like this a more viable choice for travelers.


## Project description
I propose there's a better way to solve this problem than using the poor humans. We'll use the computer, it loves tedious tasks.<sup>[citation needed]</sup> I suggest formulating the problem as an extension of the well researched Traveling salesman problem (TSP).

### The Traveling salesman problem
*Given a list of cities and the distances between each pair of cities, what is the shortest possible route that visits each city once and then returns to the origin* [[1]](http://en.wikipedia.org/wiki/Travelling_salesman_problem).

The most direct way to solving this problem is using the brute-force method, simply trying out every single route and calculate the length of the path. This always give us the optimal solution but it requires O(n!) time (n is the number of locations). Better exact algorithms have been created, such as the Held-Karp algorithm, which uses dynamic programming to solve the problem in O(n<sup>2</sup> 2<sup>n</sup>) time, and the Applegate algorithm which uses a tree based algorithm.

### From the TSP to the modern traveling tourist problem
For the modern traveling tourist problem we can formulte the problem as such:
*Given a list of airports and prices between some pair of airports at given a time, what is the cheapest flight route that will visit every city once and then return to the original airport*

We can extend the TSP to help us trying to solve the problem state, I'd like to note the major differences in the two problems:

1. We are opimizing prices instead of distances.
2. We cannot travel from one to all other airports.
3. The price from going from one place to another is in general not the same.
4. It is possible that no solution exists.
5. Traveling from one place to another changes over time.

The 4th item in the list might make you shake your head, throw your hands in the air and considered stop reading right there. However, if we need, we can allow ourselves to visit each airport more then once and should solve almost all issue. Then we can only face no solution in very extreme cases (i.e. if we fly to a airport that has no outgoing flights). Also the 5th item makes this problem quite hard to solve since, if we look at the problem from the TSP perspective, the points are always changing positions. There exists algortihms to solve a moving-target TSP, such as [[2]](http://www.cs.virginia.edu/~robins/papers/The_Moving_Target_Traveling_Salesman_Problem.pdf), but they assume a certain speed of the points. In our case the points are fluctating chaoticly.

### My solution
Using Dohop's API [[3]](http://www.dohop.com/hackathon/livestore-api.html?utm_source=Hackathon&utm_campaign=068fd7455e-Hackathon_Rules3_13_2015&utm_medium=email&utm_term=0_b8116760b6-068fd7455e-200097185) my idea of a solution was originally to create a variation of Held–Karp algorithm. The most important statement of the algorithm is the following:

*Every subpath of the optimal path, is the optimal subpath*

However, which I later realized is that I cannot really apply this statement to my problem because the fluctating points may cause the optimal subpath change in every timestep! So I will only stick to a brute force method for now. So my plan is this:

1. Find all possible permutations to travel trought the airports given
2. Calculate the price for each flight leg
3. Find the minimum price for a route that visits all airports.

## Prerequisites

The code is written and tested on Python 2.7 on Ubundu 14.04 (Trusty Tahr). It should of course run on other platforms as well. No external modules were used.

## Example

	`./travelingtp.py --visit_airports CPH,LHR,DUB,LAX,PEK,FRA,ORD --trip_time 250 --first_flight_date "2015.7.1"`
	
Output:	
	`KEF --(2015-07-21 for 8998 ISK)--> DUB --(2015-08-04 for 89398 ISK)--> ORD --(2015-08-27 for 71122 ISK)--> PEK --(2015-09-20 for 94407 ISK)--> LAX --(2015-10-03 for 75197 ISK)--> LHR --(2015-10-26 for 19000 ISK)--> FRA --(2015-12-01 for 12760 ISK)--> CPH --(2015-12-15 for 17639 ISK)--> KEF
	Price: 388521 ISK`

## References
[1] http://en.wikipedia.org/wiki/Travelling_salesman_problem

[2] http://www.cs.virginia.edu/~robins/papers/The_Moving_Target_Traveling_Salesman_Problem.pdf

[3] http://www.dohop.com/hackathon/livestore-api.html?utm_source=Hackathon&utm_campaign=068fd7455e-Hackathon_Rules3_13_2015&utm_medium=email&utm_term=0_b8116760b6-068fd7455e-200097185