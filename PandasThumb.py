import copy
import cv2  # pip install opencv-python
import math
import numpy as np
import random
import sys
import time

# Copyright (c) 2025, Ron Lewis
# Licensed under the MIT License

# We store all points in (X, Y) order. Use this "constant" index instead of 0
# and 1 anyway to make it easy to ID and track. You can't modify these because
# FPOINTS definition assumes (X, Y) order.
X = 0
Y = 1

# Fixed points where x separation is 400 and y is 300 in (x, y) order.
#   3   4   5
#   0   1   2
MARGIN = 100
FPOINTS_6 = [
    (MARGIN+000, MARGIN+300),
    (MARGIN+400, MARGIN+300),
    (MARGIN+800, MARGIN+300),
    (MARGIN+000, MARGIN+000),
    (MARGIN+400, MARGIN+000),
    (MARGIN+800, MARGIN+000),
]
FPOINTS_5 = [
    (MARGIN+150, MARGIN+432),
    (MARGIN+450, MARGIN+432),
    (MARGIN+000, MARGIN+216),
    (MARGIN+600, MARGIN+216),
    (MARGIN+300, MARGIN+000),
]
FPOINTS = FPOINTS_6

# Genetic Algorithm Tuning "Constants"
TOTAL_POP = 100                 # Total Population in each generation
MAX_STEINER_POINTS = 10         # Maximum number of Steiner points we may have in a member
ADD_DEL_SIGMA = 1.0             # Sigma of how many Steiner points to add/delete in each member
PARENT_SIGMA = TOTAL_POP/ 25    # Sigma of selecting parents from sorted list of prior gen
COPY_SIGMA = 2                  # Sigma of tweaks made to X,Y during copy to next gen
MAX_STAGNANT_CNT = 1000         # Stop if we evolve this many generations without improving
MIN_FITNESS_GRAN = .050         # How granular to measure improvement for stopping

# Calculate point height and width "constants"
smallest = [0,0] # define an X,Y pair we can update with smallest value found
largest = [0,0] # define an X,Y pair we can update with largest value found

smallest[X] = min(FPOINTS, key=lambda p: p[X])[X]
smallest[Y] = min(FPOINTS, key=lambda p: p[Y])[Y]
largest[X]  = max(FPOINTS, key=lambda p: p[X])[X]
largest[Y]  = max(FPOINTS, key=lambda p: p[Y])[Y]

PTS_HEIGHT = largest[Y] - smallest[Y]
PTS_WIDTH = largest[X] - smallest[X]

# Graph Disply Config "Constants"
STEP = False                        # set to True to step 1 generation per key press, False to run full speed
IMG_TITLE = "Panda's Thumb Puzzle"
KEY_POS = (50,50)                   # Bottom Left of Key Notice text
KEY_POS_END = (250,0)               # Opposite corner of Key Notice text rectangle
LEN_X_OFFSET = 200                  # Amount to offset "Total Length" from center on screen
GEN_X_OFFSET = 250                  # Amount to offset "Gen" from center on screen
LEN_Y_OFFSET = 15                   # Amount to offset "Total Length" from bottom of screen
GEN_Y_OFFSET = 60                   # Amount to offset "Gen" from bottom of screen
BACKGROUND_COLOR = (255,255,255)    # (B,G,R)   White
FIXED_POINT_COLOR = (0,0,0)         # (B,G,R)   Black
STEINER_POINT_COLOR = (92,209,133)  # (B,G,R)   Dark green
SEGMENT_COLOR = (148, 42, 24)       # (B,G,R)   Dark blue
FONT_COLOR = (0,0,0)                # (B,G,R)   Black
FONT = cv2.FONT_HERSHEY_SIMPLEX
FONT_SCALE = .5
LEN_FONT_SCALE = 1
TEXT_THICKNESS = 1
LEN_TEXT_THICKNESS = 2
LINE_THICKNESS = 3
POINT_RADIUS = 5

# Derived "Constants" (There should be no need to play with these)
WH = PTS_HEIGHT + 2*MARGIN                              # Window Height
WW = PTS_WIDTH + 2*MARGIN                               # Window Width
TITLE_POS = (WW//2 -LEN_X_OFFSET, WH-LEN_Y_OFFSET)      # Bottom Left of "Total Length"
SUB_TITLE_POS = (WW//2 -GEN_X_OFFSET, WH-GEN_Y_OFFSET)  # Bottom Left of "Gen"
MIN_X = MARGIN                                          # Minimum X of a Steiner Point
MAX_X = WW-MARGIN                                       # Maximum X of a Steiner Point
MIN_Y = MARGIN                                          # Minimum Y of a Steiner Point
MAX_Y = WH-MARGIN                                       # Maximum Y of a Steiner Point

pop = []
# population of collections of Steiner points, segments connecting them and fixed
# points and the total length of those segments.
# []:
#   ()
#       float: len
#       spoints [(x,y), (x,y), (x,y) ...]
#       segments[(a,b), (a,b), (a,b) ...]
# Define these offsets and use them for clarity althought there are some places
# where the order is hard coded by position. It is more clear to keep those
# as positition dependent although this means you can't redefine the order
# through these offset "constants"
LENX = 0
SPOINTSX = 1
SEGMENTSX = 2

################################################################################
# return the length of a given line segment given beginning and ending (x, y)
def get_seg_len(a, b):
    return math.sqrt((b[X]-a[X])**2 + (b[Y]-a[Y])**2 )

################################################################################
# return the total length of all segments for a member of the population
# This is used by the list sort
def pop_sort_key(pop_member):
    return pop_member[LENX]

################################################################################
# return the X and Y coordinates as 1 value
# This is used by the list sort
def get_coord_val(c):
    return c[X] * WW + c[Y]


################################################################################
# draw the network - points (both original and Steiner) and the line segments
def draw_network(img, spoints, segments, title, subtitle, exit_text):
    # Set image background color
    img[:,0:WW] = BACKGROUND_COLOR

    # create union of fixed and Steiner points
    points = FPOINTS + spoints

    # draw segments
    for a, b in segments:
        img = cv2.line(img,(points[a][X], points[a][Y]),(points[b][X], points[b][Y]),SEGMENT_COLOR, LINE_THICKNESS)

    # draw points
    for i, p in enumerate(points):
        # Draw point
        color = FIXED_POINT_COLOR if i < len(FPOINTS) else STEINER_POINT_COLOR
        img = cv2.circle(img,(p[X], p[Y]), POINT_RADIUS, color, -1)

    # add title text
    cv2.putText(img, title, TITLE_POS, FONT, LEN_FONT_SCALE, FONT_COLOR, LEN_TEXT_THICKNESS, cv2.LINE_AA)

    # add subtitle txt
    cv2.putText(img, subtitle, SUB_TITLE_POS, FONT, FONT_SCALE, FONT_COLOR, TEXT_THICKNESS, cv2.LINE_AA)

    # add exit text
    cv2.putText(img, exit_text, KEY_POS, FONT , FONT_SCALE, FONT_COLOR, TEXT_THICKNESS, cv2.LINE_AA)

    # display built image
    cv2.imshow(IMG_TITLE, img)

################################################################################
# Connect the passed Steiner points and fixed points, then return the total
# length of all segments and the segments themselves.
#
# Pass it your given set of Steiner points and it will connect the fixed points
# and Steiner points using the shortest set of lines.
#
# This algorithm picks 1 point to be in the network start with. Then finds the
# closest 2 points between those in the network and those out of the network and
# connects them. It repeats until all points are in the network.
def connect_points(spoints):

    in_network = [] # a local list of points we've connected here
    segments = []   # a local list of tuples of pairs of point numbers

    # total list of points
    tpoints = FPOINTS + spoints

    # start with 1st point being in network and the remainder outside
    in_network.append(tpoints[0])
    out_network = tpoints[1:]

    #---------------------------------------------------------------------------
    # Find the closest 2 points between the set of points in network and the set
    # of points outside network. Repeat until all points are in network
    #---------------------------------------------------------------------------

    # while we still have point outside the network to add
    tlen = 0
    while len(out_network) > 0:

        # ensure the first comparison finds itself the shortest
        shortest = float("inf")

        # for each point not in network
        for ox, o in enumerate(out_network):

            # for each point in network
            for ix, i in enumerate(in_network):

                # get length between point outside network and point in network
                seg_len = get_seg_len (i, o)

                # if this is shorter than what we have found so far
                if seg_len < shortest:
                    shortest = seg_len
                    closest_i = i
                    closest_ix = ix
                    closest_o = o
                    closest_ox = ox

        # track total length
        tlen += shortest

        # move point from outside network to inside network
        in_network.append(closest_o)
        del out_network[closest_ox]

        # add segment from that point to closest in network
        segments.append((tpoints.index(closest_i), tpoints.index(closest_o)))

    return (tlen, segments)

################################################################################
# Create an initial population of Steiner point collections with 1 to N Steiner
# points in each collection where the number is a random number with uniform
# distribution.
def init_pop():
    global pop

    # do for each member of population
    for _ in range(TOTAL_POP):

        # do for each Steiner point in this member
        spoints = []
        for _ in range(int(round(random.uniform(1, MAX_STEINER_POINTS)))):

            # generate a random x and y for a Steiner point within the margins
            p = [0,0]
            p[X] = int(random.uniform(MIN_X, MAX_X))
            p[Y] = int(random.uniform(MIN_Y, MAX_Y))

            spoints.append(p)

        # connect the points to determine total segment length
        tlen, segments = connect_points(spoints)

        # Add this collection of Steiner points to population
        pop.append((tlen, spoints, segments))

    # Sort it by shortest to longest and this becomes the current population
    pop.sort(key=pop_sort_key)

################################################################################
# Take existing population and create new one via mix and match:
#   Pick 2 random members, but most fit are most likely to be picked
#       for each Steiner point, 50/50 chance of which parent it comes from
#       This includes when 1 parent has more points, there is a 50/50 chance of
#       whether the child gets a point for that comparison.
#       And then tweak each set of points by a small random copying error amount.
#   There is a small chance we will drop a N points or add N points.
#   We have no "junk DNA". It doesn't appear to be needed.
def evolve():
    global pop

    new_pop = []

    # Create N children
    for _ in range(TOTAL_POP):

        # select 2 parents from current population where fittest is more likely to be picked
        malex = min(math.floor(abs(random.gauss(0, PARENT_SIGMA))), len(pop))
        male_spoints= pop[malex][SPOINTSX]
        femalex = min(math.floor(abs(random.gauss(0, PARENT_SIGMA))), len(pop))
        female_spoints= pop[femalex][SPOINTSX]

        # for each Steiner point in parents
        child_spoints = []
        for i in range(max(len(male_spoints), len(female_spoints))):

            # decide if point comes from male or female 50/50
            if random.random() < .5 :
                parent_spoints = male_spoints
            else:
                parent_spoints = female_spoints

            # does parent have a point?
            if i < len(parent_spoints):

                # Use it with slight copy error
                p=[0,0]
                p[X] = parent_spoints[i][X]
                p[X] = p[X] + int(random.gauss(0, COPY_SIGMA))
                p[X] = min(p[X], MAX_X)
                p[X] = max(p[X], MIN_X)

                p[Y] = parent_spoints[i][Y]
                p[Y] = p[Y] + int(random.gauss(0, COPY_SIGMA))
                p[Y] = min(p[Y], MAX_Y)
                p[Y] = max(p[Y], MIN_Y)

                # now add this point to child
                child_spoints.append(p)

        n = int(random.gauss(0, ADD_DEL_SIGMA))

        # delete N random points
        for _ in range(n, 0):
            if len(child_spoints) == 1 :
                break
            i = math.floor(random.uniform(0, len(child_spoints)))
            del child_spoints[i]

        # add N random points
        for _ in range(0,n):

            if len(child_spoints) < MAX_STEINER_POINTS:

                # generate a random x and y for a Steiner point
                p = [0,0]
                p[X] = int(random.uniform(MIN_X, MAX_X))
                p[Y] = int(random.uniform(MIN_Y, MAX_Y))

                # now add this point to child
                child_spoints.append(p)

        # connect the points and save their length and the line segments connecting them
        tlen, segments = connect_points(child_spoints)

        # put this new child into the new population along with its length and
        # those connecting lines segments
        new_pop.append((tlen, child_spoints, segments))

    # Sort it by shortest to longest and this becomes the current population
    pop = sorted(new_pop, key=pop_sort_key)

################################################################################
# Main as a subroutine so we place it in any order. Also it shows up in IDE
def main():
    # create initial population
    init_pop()


    # for each evolution
    stagnant_cnt = 0
    best = ( float("inf"), [], [] )
    spoints = []
    tlen, segments = connect_points(spoints)
    for gen in range(sys.maxsize):

        # Create an image with 3 channels for BGR
        img = np.zeros((WH, WW, 3), np.uint8)

        # draw the network in the image
        title = 'Total Length = %.3f' % (tlen,)
        subtitle = "Gen %d: %s" % (gen, str(sorted(spoints, key=get_coord_val)))
        exit_text = "[ESC] to exit"
        if STEP:
            exit_text += ", any other key to step"
        draw_network(img, spoints, segments, title, subtitle, exit_text)

        # wait on input 1 ms (or 0 for forever so you can step though generations by pressing any key)
        k = cv2.waitKey(0 if STEP else 1)
        if k == 27: #escape
            break

        ########################################################################
        # now evolve a new population
        evolve()

        # find length of best member of this gen (pop is sorted so 1st is best)
        tlen = pop[0][LENX]
        spoints = pop[0][SPOINTSX]
        segments = pop[0][SEGMENTSX]

        # quite evolving when we no longer can improve fitness
        if ( abs(tlen - best[LENX]) <= MIN_FITNESS_GRAN ):

            # very close to prior best
            stagnant_cnt += 1
        else:
            stagnant_cnt = 0

        # if new best of population is better than prior best of generations
        if tlen < best[LENX]:
            best = pop[0]
            bestGenNum = gen

            # print it
            print("Gen %6d: %4.13f : %s" % (gen, best[LENX], sorted(best[SPOINTSX], key=get_coord_val)))

        # Have we been stagnant too long? (check here AFTER updating best in case last one is best)
        if stagnant_cnt > MAX_STAGNANT_CNT:

            # redraw the best one
            title = 'Total Length = %.3f' % (best[LENX],)
            subtitle = "# of gens: %d. Best: #%d %s" % (gen, bestGenNum, str(sorted(best[SPOINTSX], key=get_coord_val)))
            exit_text = "Complete. Hit any key to exit."
            draw_network(img, best[SPOINTSX], best[SEGMENTSX], title, subtitle, exit_text)

            # wait on input forever (any key)
            cv2.waitKey(0)

            break

###############################################################################
main()
