import argparse
import math
import time
import numpy as np
import calibrate as calibrate

from pythonosc import dispatcher
from pythonosc import osc_server
from pythonosc import udp_client

# Defining the mapping between the joint number and its body part
joint_labels = {
    0 : "right ankle",
    1 : "right knee",
    2 : "right hip",
    3 : "left hip",
    4 : "left knee",
    5 : "left ankle",
    6 : "pelvis",
    7 : "thorax",
    8 : "neck",
    9 : "head",
    10 : "right wrist",
    11 : "right elbox",
    12 : "right shoulder",
    13 : "left shoulder",
    14 : "left elbow",
    15 : "left wrist",
    16 : "nose",
    17 : "right eye",
    18 : "right ear",
    19 : "left eye",
    20 : "left ear",
    21 : "right toe",
    22 : "left toe"
}

# Setting up address to send data to about proximity to zone for user 1
ip1 = "192.168.43.1"
port1 = 5005
client1 = udp_client.SimpleUDPClient(ip1, port1)

# Setting up address to send data to about proximity to zone for user 2
ip2 = "192.168.43.1"
port2 = 5005
client2 = udp_client.SimpleUDPClient(ip2, port2)

# Setting up address to send data to about proximity to zone for user 3
ip3 = "192.168.43.1"
port3 = 5005
client3 = udp_client.SimpleUDPClient(ip3, port3)

# Set to true when we have gotten the rgb data from cam1_proximity
got_cam1_rgb = [False, False, False]
got_cam2_rgb = [False, False, False]

# We update this with how close the user is to cam1 and cam2
cam1_proximity = [1, 1, 1]
cam2_proximity = [0.5, 0.5, 0.5]

# make sure right_boundary > left_boundary
left_boundary_cam1 = 0.4
right_boundary_cam1 = 0.6

left_boundary_cam2 = 0.4
right_boundary_cam2 = 0.6

user_rgb_values_cam1 = [(-1,-1,-1),(-1,-1,-1),(-1,-1,-1)]
user_rgb_values_cam2 = [(-1,-1,-1),(-1,-1,-1),(-1,-1,-1)]



# Pass in all the values
# Set cam1 to True if we are using data from camera 1 and False otherwise
def compute_trespassing (arr_number, cam1):

    # Array of strings with name of all body parts trespassing
    body_parts_trespassing = []
    # Set to True as soon as we find a trespassing instance
    trespassing = False
    index = 0

    for num in arr_number:

        # We only care about x axis data
        if index % 2 == 0:

            # Separate camera to know which boundary to use
            if cam1:
                if (num >= left_boundary_cam1).any() and (num <= right_boundary_cam1).any():
                    body_parts_trespassing.append(joint_labels[index / 2])
                    trespassing = True

            else:
                if (num >= left_boundary_cam2).any() and (num <= right_boundary_cam2).any():
                    body_parts_trespassing.append(joint_labels[index / 2])
                    trespassing = True

        index += 1

    # if the window that we are counting as trespassing is too small, we might not have any points between the limits
    # but we may still be in it
    if not trespassing:
        (left, body) = compute_leftmost(arr_number)
        (right, body) = compute_rightmost(arr_number)
        if cam1:
            if left <= left_boundary_cam1 and right >= right_boundary_cam1:
                trespassing = True
        else:
            if left <= left_boundary_cam2 and right >= right_boundary_cam2:
                trespassing = True

    return (trespassing, body_parts_trespassing)




# Find what is the leftmost point of the person
def compute_leftmost (arr_number):

    # set it above maximum
    leftmost_value = 1.1
    leftmost_index = -1
    index = 0
    while index < len(arr_number) :
        if (arr_number[index] < leftmost_value).any() and (arr_number[index] >= 0).any():
            leftmost_value = arr_number[index]
            leftmost_index = index
        index += 2

    #body_part = joint_labels[(leftmost_index) / 2]

    body_part = joint_labels[1]

    return (leftmost_value, body_part)




# Find what is the rightmost point of the person
def compute_rightmost (arr_number):

    # set it below minimum
    rightmost_value = -1
    rightmost_index = -1
    index = 0
    while index < len(arr_number):
        if (arr_number[index] > rightmost_value).any() and (arr_number[index] <= 1).any():
            rightmost_value = arr_number[index]
            rightmost_index = index
        index += 2

    #body_part = joint_labels[(rightmost_index) / 2]

    body_part = joint_labels[1]

    return (rightmost_index, body_part)




# Returns a number between 0 and 1 (0 means close and 1 is far)
# cam1 is set to True if values come from cam1 and False if from cam2
def check_proximity (arr_positions, cam1) :

    (left_point, left_body_part) = compute_leftmost(arr_positions)
    (right_point, right_body_part) = compute_rightmost(arr_positions)

    # distance is min of how close your left point is to the right bounday or how close your right point is to the left boundary
    if cam1:
        return min(abs(left_boundary_cam1 - right_point), abs(right_boundary_cam1 - left_point))
    else:
        return min(abs(left_boundary_cam2 - right_point), abs(right_boundary_cam2 - left_point))




# Handle values from cam1 to check if user is trespassing
def cam1(identification, *args):

    arr_positions = np.asarray(args)

    if not got_cam1_rgb[(int)(identification[6])]:
        if not got_cam1_rgb[0]:
            print("need to calibrate user 0")
            rgb = calibrate.calibrate_user_0(arr_positions)
            if rgb == -2:
                return 1
            user_rgb_values_cam1[0] = rgb
            got_cam1_rgb[0] = True
        elif not got_cam1_rgb[1]:
            print("need to calibrate user 1")
            rgb = calibrate.calibrate_user_1(arr_positions)
            if rgb == -2:
                return 1
            got_cam1_rgb[1] = True
            user_rgb_values_cam1[1] = rgb
        elif not got_cam1_rgb[2]:
            print("need to calibrate user 2")
            rgb = calibrate.calibrate_user_2(arr_positions)
            if rgb == -2:
                return 1
            got_cam1_rgb[2] = True
            user_rgb_values_cam1[2] = rgb

    # remove rgb values
    b = arr_positions[len(arr_positions) - 1]
    np.delete(arr_positions, -1)

    g = arr_positions[len(arr_positions) - 1]
    np.delete(arr_positions, -1)

    r = arr_positions[len(arr_positions) - 1]
    np.delete(arr_positions, -1)

    # Checks id of user we are getting data on
    id = determine_user((r,g,b), True)

    # Checks if we are trespassing and gets the body parts that are trespassing
    (trespassing, body_parts) = compute_trespassing(arr_positions, True)

    proximity = 1

    if trespassing:
        proximity = 0
    else:
        # Returns value from 0 to 1 where 0 means we are trespassing and 1 means we are far away
        proximity = check_proximity(arr_positions, True)

    # Set this user's proximity
    cam1_proximity[id] = proximity
    compute_full_proximity(id)




# Handle values from cam2 to check if user is trespassing
def cam2(identification, *args):

    arr_positions = np.asarray(args)

    if not got_cam2_rgb[(int)(identification[6])]:
        if (int)(identification[6]) == 0:
            print("need to calibrate user 0 cam2")
            rgb = calibrate.calibrate_user_0(arr_positions)
            if rgb == -2:
                return 1
            got_cam2_rgb[0] = True
            user_rgb_values_cam2[0] = rgb
        elif (int)(identification[6]) == 1:
            print("need to calibrate user1 cam2")
            rgb = calibrate.calibrate_user_1(arr_positions)
            if rgb == -2:
                return 1
            got_cam2_rgb[1] = True
            user_rgb_values_cam2[1] = rgb
        elif (int)(identification[6]) == 2:
            print("need to calibrate user2 cam2")
            rgb =calibrate.calibrate_user_2(arr_positions)
            if rgb == -2:
                return 1
            got_cam2_rgb[2] = True
            user_rgb_values_cam2[2] = rgb

    # remove rgb values
    np.delete(arr_positions, -1)
    np.delete(arr_positions, -1)
    np.delete(arr_positions, -1)

    # Checks id of user we are getting data on
    id = determine_user((r,g,b), False)

    # Checks if we are trespassing and gets the body parts that are trespassing
    (trespassing, body_parts) = compute_trespassing(arr_positions, False)

    proximity = 1

    if trespassing:
        proximity = 0
    else:
        # Returns value from 0 to 1 where 0 means we are trespassing and 1 means we are far away
        proximity = check_proximity(arr_positions, False)

    # set this user's proximity
    cam2_proximity[id] = proximity
    compute_full_proximity(id)




# Checks how close the user is and computes proximity
def compute_full_proximity(id):

    # Get distance from zone (use Pythagorean theorem)
    proximity = math.sqrt((cam1_proximity[id]) ** 2 + cam2_proximity[id] ** 2)

    if proximity > 0.5:
        proximity = 1

    time.sleep(0.1)

    # Find which client to send the information to
    if id == 0:
        client1.send_message("/phone", float(proximity))
    elif id == 1:
        client2.send_message("/phone", float(proximity))
    else:
        client3.send_message("/phone", float(proximity))

    # Left for testing
    print(proximity)



# We determine which rgb value is closest to the current one that we have
# cam1 set to True if we are using data from camera1 and false if camera2
def determine_user (rgb, cam1):

    dif0 = 0
    dif1 = 0
    dif2 = 0

    # set up rgb if not done and compute differences to see who is closest
    if cam1:
        index = 0
        for color in rgb:
            dif0 = dif0 + (abs(color - user_rgb_values_cam1[0][index]))
            dif1 = dif1 + (abs(color - user_rgb_values_cam1[1][index]))
            dif2 = dif2 + (abs(color - user_rgb_values_cam1[2][index]))
        if not got_cam1_rgb[1]:
            dif1 = 10000000
        if not got_cam2_rgb[2]:
            dif2 = 10000000

    else:
        for color in rgb:
            dif0 = dif0 + (abs(color - user_rgb_values_cam2[0][index]))
            dif1 = dif1 + (abs(color - user_rgb_values_cam2[1][index]))
            dif2 = dif2 + (abs(color - user_rgb_values_cam2[2][index]))
        if not got_cam2_rgb[1]:
            dif1 = 10000000
        if not got_cam2_rgb[2]:
            dif2 = 10000000

    # determine the smallest difference
    smallest_diff = min(dif0, dif1, dif2)

    # look who had the smallest difference
    if smallest_diff == dif0:
        return 0
    elif smallest_diff == dif1:
        return 1
    else:
        return 2



#############################################################
#                                                           #
#                       __main__                            #
#                                                           #
#############################################################

if __name__ == "__main__":

    dispatcher = dispatcher.Dispatcher()

    # Sending data to functions to judge if trespassing for cam1
    dispatcher.map("/cam0/0", cam1)
    dispatcher.map("/cam0/1", cam1)
    dispatcher.map("/cam0/2", cam1)

    # Sending data to functions to just if trespassing for cam2
    dispatcher.map("/cam1/0", cam2)
    dispatcher.map("/cam1/1", cam2)
    dispatcher.map("/cam1/2", cam2)

    # Getting the data from other computer
    ip = "192.168.43.37"
    port = 1337
    server = osc_server.ThreadingOSCUDPServer((ip, port), dispatcher)
    print("Serving on {}".format(server.server_address))
    server.serve_forever()
