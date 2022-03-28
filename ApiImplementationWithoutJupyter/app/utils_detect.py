import os
import cv2
import math
MIN_DIST=80


#Below code is the utility functions which will be used as a part of video detection  

# given a dataframe of all the detected object coordinates in a frame, put them in a list of tuples 
def get_coordinates(df):
    objects = []
    for index, row in df.iterrows():
        objects.append( ( int(row[0]), int(row[1]), int(row[2]), int(row[3]) ) )

    return objects


# Takes frame and the model that got initialized. Then, process that frame and detects the desired objects and returns the coorindates, confidence and class label.
# However, we are only taking the coordinates of the detected objects and returning that as a list of tuples.
def detect(model, img):
    results = model(img)
    
    df = results.pandas().xyxy[0]
    
    detect_info = get_coordinates(df)
    return detect_info

# Given the coordinates of the detected objects, return the centroids of those objects as a list of centroids.
def get_centroid(detect_info):
    # object --> (top-left) x1,y1, (bottom-right) x2,y2
    centroids = []
    for object in detect_info:
        centroid_x = (object[0] + object[2]) // 2
        centroid_y = (object[1] + object[3]) // 2
        bboxHeight = object[3] - object[1]
        centroids.append([centroid_x, centroid_y, bboxHeight])
    return centroids

# returns the distance between two centroids 
def get_distance(centroid1, centroid2):
    distance = math.sqrt((centroid1[0] - centroid2[0]) ** 2 + (centroid1[1] - centroid2[1]) ** 2)
    return distance

# Given the centroids of the detected objects, computes  the distance between each centroids and those centroids which have less than MIN_DIST threshold will be marked as a violated people.
def get_violated_distance_people_test(centroids, MIN_DIST=80):
    violated_people = []
    for i in range(len(centroids)):
        for j in range(i + 1, len(centroids)):
            if get_distance(centroids[i], centroids[j]) <= MIN_DIST:
                violated_people.append((i, j))
    return violated_people

# Draws the rectangle around the detected objects with red color for violated people along with arrows and  
def draw_arrows(image, detect_info, centroids, violated_people):
    if len(detect_info) > 0:
        for idx, object in enumerate(detect_info):
            if list(filter(lambda x: x.count(idx) > 0, violated_people)):
                temp = list(filter(lambda x: x.count(idx) > 0, violated_people))  # [(),()] temp - violated people index
                color = (0, 0, 255)
                label = 'Alert'
                for i in range(len(temp)):
                    # image = cv2.circle(image, (centroids[temp[i][0]][0], centroids[temp[i][0]][1]), 10, color, -1)
                    # image = cv2.circle(image, (centroids[temp[i][1]][0], centroids[temp[i][1]][1]), 10, color, -1)
                    image = cv2.arrowedLine(image, (centroids[temp[i][0]][0], centroids[temp[i][0]][1]),
                                     (centroids[temp[i][1]][0], centroids[temp[i][1]][1]), color, 2)
                    image = cv2.arrowedLine(image, (centroids[temp[i][1]][0], centroids[temp[i][1]][1]),(centroids[temp[i][0]][0], centroids[temp[i][0]][1]), color, 2)
            else:
                color = (0, 255, 0)
                label = 'Safe'
            image = cv2.rectangle(image, (object[0], object[1]), (object[2], object[3]), color, 2)
            image = cv2.putText(image, label, (object[0], object[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2,cv2.LINE_AA)

    text = "Social Distancing Violations: {}".format(len(set([item  for tup in violated_people for item in tup])))
    image = cv2.putText(image, text, (20, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (0, 0, 255), 3)
    return image

