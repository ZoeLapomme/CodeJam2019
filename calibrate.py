import argparse
import math
import time
import numpy as np
import keyboard
from pynput.keyboard import Key, Listener


from pythonosc import dispatcher
from pythonosc import osc_server
from pythonosc import udp_client

def on_press(key):
    print("key is pressed")

def on_release(key):
    print('{0} release'.format(
        key))
    if key == Key.esc:
        # Stop listener
        return False



def calibrate_user_0(arr_positions):
    # check if the user has hand above shoulder
    print ("hand " )
    print(arr_positions[15 * 2 + 1])
    print ("\nshoulder ")
    print(arr_positions[13*2+1])


    with Listener(
            on_press=on_press,
            on_release=on_release) as listener:
        listener.join()

    if keyboard.is_pressed('d'):
        print("is pressed")
        if (arr_positions[15 * 2 + 1] > arr_positions[13 * 2 + 1]):
            b = arr_positions[len(arr_positions) - 1]
            g = arr_positions[len(arr_positions) - 2]
            r = arr_positions[len(arr_positions) - 3]
            return (r,g,b)
    # if user does not have hand above head then return dummy value
    return -2

def calibrate_user_1(arr_positions):
    # check if the user has hand above shoulder
    if keyboard.is_pressed('c'):
        if arr_positions[15 * 2 + 1] > arr_positions[13 * 2 + 1]:
            b = arr_positions[len(arr_positions) - 1]
            g = arr_positions[len(arr_positions) - 2]
            r = arr_positions[len(arr_positions) - 3]
            return (r,g,b)
    # if user does not have hand above head then return dummy value
    return -2

def calibrate_user_2(arr_positions):
    # check if the user has hand above shoulder
    if keyboard.is_pressed('c'):
        if arr_positions[15 * 2 + 1] > arr_positions[13 * 2 + 1] and keyboard.is_pressed('c'):
            b = arr_positions[len(arr_positions) - 1]
            g = arr_positions[len(arr_positions) - 2]
            r = arr_positions[len(arr_positions) - 3]
            return (r,g,b)
    # if user does not have hand above head then return dummy value
    return -2
