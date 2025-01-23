# Definition
Steiner's Problem: Given a two-dimensional set of points, what is the most
compact network of straight-line segments that connects the points?
(Additional "Steiner Points" beside the fixed points are allowed.)

Panda's Thumb Challenge:  Use a Genetic Algorithm to solve Steiner's Problem.
Described in Skeptical Enquirer May/June 2020
Re:  
  https://pandasthumb.org/archives/2006/07/target-target-w-1.html  
  https://pandasthumb.org/archives/2006/08/design-challeng-1.html  
  https://skepticalinquirer.org/wp-content/uploads/sites/29/2010/05/p42.pdf

# About
This algorithm usually finds the 3 Steiner point solution first (length=1593)
and then evolves it to find the 4 Steiner point solution, although sometimes
finds the 4 Steiner point immediately. Then it evolves to optimize the 4
Steiner point solution.

This program displays the fittest member of each generation. You can watch it
solve this problem in real time in seconds. When it finds the 3 point
solution, it generally finds a 4 point where the 4th point is very close to
one of the 2 middle fixed points, then stretches away toward the optimal
position over time. Usually within 40 or so generations it is very close to
optimal. And almost always by 100 generations. Although in some cases it does
not find the optimal length of 1586.5331877898545, instead settling around
1586.56.

It often includes some extraneous Steiner points that actually make for longer
paths, but evolves these away as suboptimal. It should be theoretically
possible for them to be included if they happen to land exactly in line with
the optimal points, but I have not seen this happen. The fitness test does not
measure the number of points, only the total length although this could be
added.

# Solution
The optimal solution (There are actually 2 but they are just mirror images)
along with some very close runner ups which just have some of the points off
by 1:

| Length              | Points                                           | Comment |
| ------------------- | ------------------------------------------------ | ------- |
| 1586.5331877898545: | [(183, 217), (458, 191), (542, 309), (817, 283)] |         |
| 1586.5331877898545: | [(183, 283), (458, 309), (542, 191), (817, 217)] | mirror  |
| 1586.533662744926:  | [(184, 217), (458, 191), (542, 309), (817, 283)] |         |
| 1586.533662744926:  | [(184, 283), (458, 309), (542, 191), (817, 217)] | mirror  |
| 1586.5336627449262: | [(183, 283), (458, 309), (542, 191), (816, 217)] |         |
| 1586.5336627449262: | [(183, 217), (458, 191), (542, 309), (816, 283)] | mirror  |
| 1586.533836134074:  | [(183, 283), (459, 309), (542, 192), (816, 218)] |         |
| 1586.533836134074:  | [(183, 217), (459, 191), (542, 308), (816, 282)] | mirror  |
| 1586.533836134074:  | [(184, 282), (458, 308), (541, 191), (817, 217)] |         |

The optimal solution appeared at generation 14,374 on a run of over 2,000,000.
I've also seen it appear as early as generateion 105.
Bump up MAX_STAGNANT_CNT to 100,000 to let this run "forever".

# Traveling Salesman Problem?
I think this could be modified to also solve the Traveling Salesman problem by
making the fitness test be the total length to travel all fixed nodes and not
utilize additional (Steiner) points. We would just evolve the order of travel.
For the 6 node problem, this is 6! (unless you want to specify the starting
node) or 720. For 10, it grows to over 3.6 million! It would be interesting to
input real cities by latitude and longitude. I'd need to add a screen size and
scale the cities up or down to fit. Of course t his ignores the curvature of
the Earth but that is not the point.

