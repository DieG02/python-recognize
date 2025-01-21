import csv
import copy
import itertools
import cv2 as cv
import numpy as np

def select_mode(key, mode):
  number = -1
  if 48 <= key <= 57:  # 0 ~ 9
    number = key - 48
  if key == 110:  # n
    mode = 0
  if key == 107:  # k
    mode = 1
  if key == 104:  # h
    mode = 2
  return number, mode


def calc_bounding_rect(image, landmarks):
  image_width, image_height = image.shape[1], image.shape[0]

  landmark_array = np.empty((0, 2), int)

  for _, landmark in enumerate(landmarks.landmark):
    landmark_x = min(int(landmark.x * image_width), image_width - 1)
    landmark_y = min(int(landmark.y * image_height), image_height - 1)

    landmark_point = [np.array((landmark_x, landmark_y))]

    landmark_array = np.append(landmark_array, landmark_point, axis=0)

  x, y, w, h = cv.boundingRect(landmark_array)

  return [x, y, x + w, y + h]


def calc_landmark_list(image, landmarks):
  image_width, image_height = image.shape[1], image.shape[0]

  landmark_point = []

  # Keypoint
  for _, landmark in enumerate(landmarks.landmark):
    landmark_x = min(int(landmark.x * image_width), image_width - 1)
    landmark_y = min(int(landmark.y * image_height), image_height - 1)
    # landmark_z = landmark.z

    landmark_point.append([landmark_x, landmark_y])

  return landmark_point


def pre_process_landmark(landmark_list):
  temp_landmark_list = copy.deepcopy(landmark_list)

  # Convert to relative coordinates
  base_x, base_y = 0, 0
  for index, landmark_point in enumerate(temp_landmark_list):
    if index == 0:
      base_x, base_y = landmark_point[0], landmark_point[1]

    temp_landmark_list[index][0] = temp_landmark_list[index][0] - base_x
    temp_landmark_list[index][1] = temp_landmark_list[index][1] - base_y

  # Convert to a one-dimensional list
  temp_landmark_list = list(
    itertools.chain.from_iterable(temp_landmark_list))

  # Normalization
  max_value = max(list(map(abs, temp_landmark_list)))

  def normalize_(n):
    return n / max_value

  temp_landmark_list = list(map(normalize_, temp_landmark_list))

  return temp_landmark_list


def pre_process_point_history(image, point_history):
  image_width, image_height = image.shape[1], image.shape[0]

  temp_point_history = copy.deepcopy(point_history)

  # Convert to relative coordinates
  base_x, base_y = 0, 0
  for index, point in enumerate(temp_point_history):
    if index == 0:
      base_x, base_y = point[0], point[1]

    temp_point_history[index][0] = (temp_point_history[index][0] - base_x) / image_width
    temp_point_history[index][1] = (temp_point_history[index][1] - base_y) / image_height

  # Convert to a one-dimensional list
  temp_point_history = list(
    itertools.chain.from_iterable(temp_point_history))

  return temp_point_history


def logging_csv(number, mode, landmark_list, point_history_list):
  if mode == 0:
    pass
  if mode == 1 and (0 <= number <= 9):
    csv_path = 'model/keypoint_classifier/keypoint.csv'
    with open(csv_path, 'a', newline="") as f:
      writer = csv.writer(f)
      writer.writerow([number, *landmark_list])
  if mode == 2 and (0 <= number <= 9):
    csv_path = 'model/point_history_classifier/point_history.csv'
    with open(csv_path, 'a', newline="") as f:
      writer = csv.writer(f)
      writer.writerow([number, *point_history_list])
  return
