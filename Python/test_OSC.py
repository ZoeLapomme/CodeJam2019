from __future__ import print_function, division

import argparse
import sys

import numpy as np
import cv2
import wrnchAI
from visualizer import Visualizer
from utils import videocapture_context

from pythonosc import udp_client

model_width = 328
model_height = 184
red = (22, 22, 229)
blue = (51, 51, 255)
green =(51, 255, 51)
yellow = (255, 255, 51)
purple = (127, 0, 255)
white = (255, 255, 255)

userColor = [blue, green, yellow, purple, white, blue, green, yellow, purple, white, blue, green, yellow, purple, white]

camID = 0

sys.path.append('D:/Development Projects/Hackathons/CodeJam 2019/Python/CodeJam2019/wrnchAI-engine-Win/lib/python/3.7')
models_dir = "D:/Development Projects/Hackathons/CodeJam 2019/Python/CodeJam2019/wrnchAI-engine-Win/bin/wrModels"

# OSC Stuff 
# Proximity detection
IPaddress = "192.168.43.37"
Port = 1337
# Unity server
IPaddress_Unity = "192.168.43.45"
Port_Unity = 6969


def main(args):
    camID = args.cam_ID
    print("Setting up cam" + str(camID))
    osc_camID = "/cam" + str(camID) + "/"
    print(osc_camID)

    # OSC Init
    print('Connection to OSC...')
    client = udp_client.SimpleUDPClient(IPaddress, Port)
    client.send_message(osc_camID, "Bonjour!")
    client_unity = udp_client.SimpleUDPClient(IPaddress_Unity, Port_Unity)
    #client.send_message(osc_camID, "Bonjour!")

    if args.license_key is not None and not wrnchAI.license_check_string(args.license_key) \
       or not wrnchAI.license_check():
        sys.exit('A valid license is required to run the samples')

    params = wrnchAI.PoseParams()
    params.bone_sensitivity = wrnchAI.Sensitivity.high
    params.joint_sensitivity = wrnchAI.Sensitivity.high
    params.enable_tracking = True

    # Default Model resolution
    params.preferred_net_width = model_width
    params.preferred_net_height = model_height

    output_format = wrnchAI.JointDefinitionRegistry.get('j23')

    print('Initializing networks...')
    estimator = wrnchAI.PoseEstimator(models_path= models_dir,
                                      license_string=args.license_key,
                                      params=params,
                                      gpu_id=0,
                                      output_format=output_format)
    estimator.initialize_hands2d(models_dir)
    print('Initialization done!')

    options = wrnchAI.PoseEstimatorOptions()
    options.estimate_all_handboxes = True
    options.estimate_hands = True

    print('Opening webcam...')
    with videocapture_context(args.webcam_index) as cap:
        visualizer = Visualizer()

        joint_definition = estimator.human_2d_output_format()
        bone_pairs = joint_definition.bone_pairs()

        hand_definition = estimator.hand_output_format()
        hand_pairs = hand_definition.bone_pairs()

        def draw_hands(hands):
            for hand in hands:
                joints = hand.joints()

                visualizer.draw_points(joints, joint_size=6)
                visualizer.draw_lines(joints, hand_pairs, bone_width=2)

        while True:
            _, frame = cap.read()
            data_out = []
            human_index = 0

            if frame is not None:
                estimator.process_frame(frame, options)
                humans2d = estimator.humans_2d()

                visualizer.draw_image(frame)

                frame_height = frame.shape[0]
                frame_width = frame.shape[1]

                # Draw skeleton
                for human in humans2d:
                    joints = human.joints()
                    box = human.bounding_box()

                    # Pelv index = 6
                    pelv_x = joints[2 * 6]
                    pelv_y = joints[2 * 6 + 1]
                    # Head index = 8
                    head_x = int(joints[2 * 9] * frame_width)
                    head_y = int(joints[2 * 9 + 1] * frame_height)
                    head_x_offset = head_x - 2

                    #visualizer.draw_box(pelv_x, pelv_y, 0.1, 0.1)

                    # Converts ndnumpy data to list
                    data_out = joints.tolist()
                    #data_out = np.asarray(joints.tolist()) # List to 1D array

                    # Get RGB Value
                    if inFrame(frame, pelv_x, pelv_y, 6):
                        r_val, g_val, b_val = rgb_average_box(frame, pelv_x, pelv_y)
                    else:
                        r_val, g_val, b_val = 0, 0, 0

                    # Add RGB to out data_out
                    data_out.append(r_val)
                    data_out.append(g_val)
                    data_out.append(b_val)

                    osc_addr = osc_camID + str(human_index)

                    # Send OSC
                    client.send_message(osc_addr, data_out) # To prox serv
                    client_unity.send_message(osc_addr, data_out) # To Unity

                    print(osc_addr)
                    print(data_out)                    

                    visualizer.draw_points(joints, colour = userColor[human_index])
                    visualizer.draw_lines(joints, bone_pairs, colour = userColor[human_index])
                    #visualizer.draw_points(joints)
                    #visualizer.draw_lines(joints, bone_pairs)

                    # Draw RBG values
                    rbg_out = "(" + str(r_val) + ";" + str(g_val) + ";" +  str(b_val) + ")"
                    visualizer.draw_text_in_frame(text = rbg_out, x = head_x_offset, y = head_y,
                                                    #color = userColor[human_index], 
                                                    font_scale = 0.5)
        

                    # Increment user
                    human_index += 1
                    

                #print("--------------JointDef----------------")

                #output_format.print_joint_definition()

                print("--------------STOP----------------")

                # Draw hands
                draw_hands(estimator.left_hands())
                draw_hands(estimator.right_hands())
                # Draw box around hands
                '''hand_box_pairs = estimator.hand_boxes()
                for hand_box_pair in hand_box_pairs:
                    left_box = hand_box_pair.left
                    right_box = hand_box_pair.right

                    visualizer.draw_box(left_box.min_x, left_box.min_y,
                                        left_box.width, left_box.height)
                    visualizer.draw_box(right_box.min_x, right_box.min_y,
                                        right_box.width, right_box.height)'''
                
                #r_val, g_val, b_val = rgb_average(frame, 0, 0, temp_width, temp_height)
                # Display text
                

                # Draw border
                cv2.line(frame, ( int(frame_width * 0.3), 0), ( int(frame_width * 0.3), frame_height),
                        red, 2, 16)

                visualizer.show()

            key = cv2.waitKey(1)

            if key & 255 == 27:
                break

def rgb_average(frame, min_x, min_y, width, height):
    frame_width = frame.shape[1]
    frame_height = frame.shape[0]
    # Convert to pixel
    min_x = int(max(0, min_x*frame_width))
    min_y = int(max(0, min_y*frame_height))
    width = int(min(frame_width, min_x + width * frame_width)) - 2
    height = int(min(frame_height, min_y + height * frame_height)) - 2
    r_avg = 0
    g_avg = 0
    b_avg = 0
    total_px = 0

    print("height: " + str(height))
    print("width: " + str(width))

    for y in range(width):
        print("Y: " + str(y))
        for x in range(height):
            print("X: " + str(x))
            b_avg += frame[x, y, 0]
            g_avg += frame[x, y, 1]
            r_avg += frame[x, y, 2]
            total_px += 1

    r_avg = r_avg / total_px
    g_avg = g_avg / total_px
    b_avg = b_avg / total_px
    return (r_avg, g_avg, b_avg)

def rgb_average_box(frame, min_x, min_y):
    frame_width = frame.shape[1]
    frame_height = frame.shape[0]
    box_size = 10
    # Convert to pixel
    '''min_x = int(max(0, min_x*frame_width - 5))
    min_y = int(max(0, min_y*frame_height - 5))
    width = int(min(frame_width, min_x + box_size))
    height = int(min(frame_height, min_y + box_size))'''
    min_x = int(min_x*frame_width - 5)
    min_y = int(min_y*frame_height - 5)
    width = int(min_x + box_size)
    height = int(min_y + box_size)

    r_avg = 0
    g_avg = 0
    b_avg = 0
    total_px = 0

    for y in range(10):
        #print("Y: " + str(y))
        for x in range(10):
            #print("X: " + str(x))
            b_avg += frame[min_y + y, min_x + x, 0]
            g_avg += frame[min_y + y, min_x + x, 1]
            r_avg += frame[min_y + y, min_x + x, 2]
            total_px += 1

    r_avg = r_avg / total_px
    g_avg = g_avg / total_px
    b_avg = b_avg / total_px
    return (r_avg, g_avg, b_avg)


def inFrame(frame, x, y, offset):
    frame_width = frame.shape[1]
    frame_height = frame.shape[0]

    # pixel to ratio
    offset_ratio_x = offset / frame_width
    offset_ratio_y = offset / frame_height
    upperX = x - offset_ratio_x
    lowerX = x + offset_ratio_x
    upperY = y - offset_ratio_x
    lowerY = y + offset_ratio_x
    print("UpX: " + str(upperX) + " LoX: " + str(lowerX) + " UpY: " + str(upperY) + " LoY : " + str(lowerY))

    if upperX < 0 or lowerX > 1 or upperY < 0 or lowerY > 1:
       return False
    else:
        return True

def create_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument('--cam-ID', '-c', type=int, default=0)
    parser.add_argument('--webcam-index', '-i', type=int, default=0)
    parser.add_argument('--license-key', '-k', type=str, default=None)

    return parser


if __name__ == '__main__':
    main(create_parser().parse_args())