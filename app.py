#!/usr/bin/env python
# -*- coding: utf-8 -*-
import csv
import copy
import argparse
from collections import deque
from collections import Counter

import mediapipe as mp
import cv2 as cv
import time

import src.helpers as Helper
import src.drawers as Drawer
import src.controllers as Controller

from utils import CvFpsCalc
from model import KeyPointClassifier
from model import PointHistoryClassifier


def get_args():
	parser = argparse.ArgumentParser()

	parser.add_argument("--device", type=int, default=0)
	parser.add_argument("--width", help='cap width', type=int, default=960)
	parser.add_argument("--height", help='cap height', type=int, default=540)

	parser.add_argument('--use_static_image_mode', action='store_true')
	parser.add_argument("--min_detection_confidence",
											help='min_detection_confidence',
											type=float,
											default=0.7)
	parser.add_argument("--min_tracking_confidence",
											help='min_tracking_confidence',
											type=int,
											default=0.5)

	args = parser.parse_args()

	return args


def main():
	# Argument parsing #################################################################
	args = get_args()

	cap_device = args.device
	cap_width = args.width
	cap_height = args.height

	use_static_image_mode = args.use_static_image_mode
	min_detection_confidence = args.min_detection_confidence
	min_tracking_confidence = args.min_tracking_confidence

	use_brect = True

	# Camera preparation ###############################################################
	cap = cv.VideoCapture(cap_device)
	cap.set(cv.CAP_PROP_FRAME_WIDTH, cap_width)
	cap.set(cv.CAP_PROP_FRAME_HEIGHT, cap_height)

	# Model load #############################################################
	mp_hands = mp.solutions.hands
	hands = mp_hands.Hands(
		static_image_mode=use_static_image_mode,
		max_num_hands=2,
		min_detection_confidence=min_detection_confidence,
		min_tracking_confidence=min_tracking_confidence,
	)

	keypoint_classifier = KeyPointClassifier()
	point_history_classifier = PointHistoryClassifier()

	# Read labels ###########################################################
	with open(
  	'model/keypoint_classifier/keypoint_classifier_label.csv',
   	encoding='utf-8-sig') as file:
			keypoint_classifier_labels = csv.reader(file)
			keypoint_classifier_labels = [
				row[0] for row in keypoint_classifier_labels
			]
	with open(
		'model/point_history_classifier/point_history_classifier_label.csv',
		encoding='utf-8-sig') as file:
			point_history_classifier_labels = csv.reader(file)
			point_history_classifier_labels = [
				row[0] for row in point_history_classifier_labels
			]

	# FPS Measurement ########################################################
	cvFpsCalc = CvFpsCalc(buffer_len=10)

	# Coordinate history #################################################################
	history_length = 16
	point_history = deque(maxlen=history_length)

	# Finger gesture history ################################################
	finger_gesture_history = deque(maxlen=history_length)

	#  ########################################################################
	mode = 0
	
	gestures_map = {
		"no-gesture": None,
		"zoom-in": "zoom-in",
		"zoom-out": "zoom-out",
		"slide-up": "slide-up",
		"slide-down": "slide-down",
		"swipe-left": "swipe-left",
		"swipe-right": "swipe-right",
		"expand": "expand",
		"contract": "contract",
	}
		
	last_gesture_time = 0
	DEBOUNCE_DELAY = 0.15
    
    
	while True:
		fps = cvFpsCalc.get()

		# Process Key (ESC: end) #################################################
		key = cv.waitKey(10)
		if key == 27:  # ESC
			break
		number, mode = Helper.select_mode(key, mode)

		# Camera capture #####################################################
		ret, image = cap.read()
		if not ret:
			break
		image = cv.flip(image, 1)  # Mirror display
		debug_image = copy.deepcopy(image)

		# Detection implementation #############################################################
		image = cv.cvtColor(image, cv.COLOR_BGR2RGB)

		image.flags.writeable = False
		results = hands.process(image)
		image.flags.writeable = True

		#  ####################################################################
		if results.multi_hand_landmarks is not None:
			for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
				# Bounding box calculation
				brect = Helper.calc_bounding_rect(debug_image, hand_landmarks)
				# Landmark calculation
				landmark_list = Helper.calc_landmark_list(debug_image, hand_landmarks)

				# Conversion to relative coordinates / normalized coordinates
				pre_processed_landmark_list = Helper.pre_process_landmark(landmark_list)
				pre_processed_point_history_list = Helper.pre_process_point_history(debug_image, point_history)
				# Write to the dataset file
				Helper.logging_csv(number, mode, pre_processed_landmark_list, pre_processed_point_history_list)

				# Hand sign classification
				hand_sign_id = keypoint_classifier(pre_processed_landmark_list)
				if hand_sign_id == 2:  # Point gesture
					point_history.append(landmark_list[8])
				else:
					point_history.append([0, 0])
		
  
				gesture = gestures_map.get(keypoint_classifier_labels[hand_sign_id])
				
				# Handle gesture changes with debounce
				if gesture in gestures_map:
					current_time = time.time()
					
					if current_time - last_gesture_time >= DEBOUNCE_DELAY:
						if gesture is not None:
							if gesture == "zoom-in":
								Controller.zoom_in()
							elif gesture == "zoom-out":
								Controller.zoom_out()
							elif gesture == "slide-up":
								Controller.scroll_up()
							elif gesture == "slide-down":
								Controller.scroll_down()
							elif gesture == "swipe-left": 
								Controller.previous_tab()
							elif gesture == "swipe-right":
								Controller.next_tab()
							print(f"Pressed {gesture}")
									
					last_gesture_time = current_time
     

				# Finger gesture classification
				finger_gesture_id = 0
				point_history_len = len(pre_processed_point_history_list)
				if point_history_len == (history_length * 2):
					finger_gesture_id = point_history_classifier(pre_processed_point_history_list)

				# Calculates the gesture IDs in the latest detection
				finger_gesture_history.append(finger_gesture_id)
				most_common_fg_id = Counter(finger_gesture_history).most_common()

				# Drawing part
				debug_image = Drawer.bounding_rect(use_brect, debug_image, brect)
				debug_image = Drawer.landmarks(debug_image, landmark_list)
				debug_image = Drawer.info_text(
					debug_image,
					brect,
					handedness,
					keypoint_classifier_labels[hand_sign_id],
					point_history_classifier_labels[most_common_fg_id[0][0]],
				)
		else:
			point_history.append([0, 0])

		debug_image = Drawer.point_history(debug_image, point_history)
		debug_image = Drawer.info(debug_image, fps, mode, number)

		# Screen reflection #############################################################
		cv.imshow('Hand Gesture Recognition', debug_image)


	cap.release()
	cv.destroyAllWindows()


if __name__ == '__main__':
	main()
