from __future__ import division
import cv2
import numpy as np
import time
import math
from PIL import Image

protoFile = "Model/pose_deploy.prototxt"
weightsFile = "Model/pose_iter_102000.caffemodel"
nPoints = 22

POSE_PAIRS = [ [0,1],[1,2],[2,3],[3,4],[0,5],[5,6],[6,7],[7,8],[0,9],[9,10],[10,11],[11,12],[0,13],[13,14],[14,15],[15,16],[0,17],[17,18],[18,19],[19,20] ]
net = cv2.dnn.readNetFromCaffe(protoFile, weightsFile)

frame = cv2.imread("Image/00.jpg")
frame_handlandmark = np.copy(frame)
color_frame = np.copy(frame)
frameCopy = np.copy(frame)
frameWidth = frame.shape[1]
frameHeight = frame.shape[0]
aspect_ratio = frameWidth/frameHeight

threshold = 0.1

t = time.time()
# input image dimensions for the network
inHeight = 368
inWidth = int(((aspect_ratio*inHeight)*8)//8)
inpBlob = cv2.dnn.blobFromImage(frame, 1.0 / 255, (inWidth, inHeight), (0, 0, 0), swapRB=False, crop=False)

net.setInput(inpBlob)

output = net.forward()

print("time taken by network : {:.3f}".format(time.time() - t))

points = []

for i in range(nPoints):
    # confidence map of corresponding body's part.
    probMap = output[0, i, :, :]
    probMap = cv2.resize(probMap, (frameWidth, frameHeight))
    # Find global maxima of the probMap.
    minVal, prob, minLoc, point = cv2.minMaxLoc(probMap)

    if prob > threshold :
        cv2.circle(frameCopy, (int(point[0]), int(point[1])), 2, (0, 255, 255), thickness=-1, lineType=cv2.FILLED)
        cv2.putText(frameCopy, "{}".format(i), (int(point[0]), int(point[1])), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, lineType=cv2.LINE_AA)

        points.append((int(point[0]), int(point[1])))
    else :
        points.append(None)

for pair in POSE_PAIRS:
    partA = pair[0]
    partB = pair[1]
    # print(partA,partB)
    # print(points[partA], points[partB])

    if points[partA] and points[partB]:
        cv2.line(frame_handlandmark, points[partA], points[partB], (0, 255, 255), 2)
        cv2.circle(frame_handlandmark, points[partA], 2, (0, 0, 255), thickness=-1, lineType=cv2.FILLED)
        cv2.circle(frame_handlandmark, points[partB], 2, (0, 0, 255), thickness=-1, lineType=cv2.FILLED)

finger = [points[20],points[16],points[12],points[8],points[4]]
finger_second = [points[19],points[15],points[11],points[7],points[3]]

if None in finger:
    finger.remove(None)

if None in finger_second:
    finger_second.remove(None)


print(finger)
print(finger_second)



for i in range(len(finger)):

    fingerprint_X = int((finger[i][0] + finger_second[i][0]) / 2)
    fingerprint_Y = int((finger[i][1] + finger_second[i][1]) / 2)
    print(fingerprint_X,fingerprint_Y)
    circle_size = finger[i][0] - fingerprint_X +  fingerprint_Y - finger[i][1]
    print(circle_size)
    # cv2.circle(frame_handlandmark, (fingerprint_X, fingerprint_Y), circle_size, (255, 255, 0), thickness=1)
    first_X =finger[i][0]
    first_Y = finger[i][1]
    second_X = finger_second[i][0]
    second_Y = finger_second[i][1]

    X = first_X - second_X
    Y = first_Y - second_Y


    B = math.sqrt(math.pow(X,2) + math.pow(Y,2))
    print(B)
    radius = int(B / 2)
    half_radius = int(radius / 2)
    acos = math.acos( X/B ) * 57.3 # 1 radian 곱
    print('acos : ',acos)
    # cos = math.acos()
    cv2.ellipse(frame_handlandmark,(fingerprint_X, fingerprint_Y),(radius,half_radius),-acos,0,360,(255,255,125),1)
    cv2.ellipse(color_frame,(fingerprint_X, fingerprint_Y),(radius,half_radius),-acos,0,360,(0,0,0),-1)

img = cv2.bitwise_xor(color_frame,frame)

# blue_threshold = 0
# green_threshold = 0
# red_threshold = 0
# bgr_threshold = [blue_threshold, green_threshold, red_threshold]
#
# thresholds = (color_frame[:,:,0] <= bgr_threshold[0]) \
#             | (color_frame[:,:,1] <= bgr_threshold[1]) \
#             | (color_frame[:,:,2] <= bgr_threshold[2])
#
# img[thresholds] = [255,255,255]
img = cv2.medianBlur(img,3)
cv2.imshow('test',img)



img = cv2.bitwise_or(img,frame)
print(img.shape)
# img = cv2.bitwise_or(img,frame2)
# frame = cv2.bitwise_and(frame,color_frame)


# cv2.circle(frame,finger[1])

# ycrcb = cv2.cvtColor(frame,cv2.COLOR_BGR2YCrCb)
# mask_hand = cv2.inRange(ycrcb, np.array([0,133,77]), np.array([255,173,127]))

# cv2.imshow('hands',mask_hand)
# frame = cv2.resize(frame,(480,680))
# cv2.imshow('Output-Keypoints', frameCopy)
frame_handlandmark = cv2.medianBlur(frame_handlandmark,15)
cv2.imshow('frame_handlandmark',frame_handlandmark)
cv2.imshow('color_frame',color_frame)
cv2.imshow('Output', img)
# 20 , 16, 12, 8,  4
print("Total time taken : {:.3f}".format(time.time() - t))

cv2.waitKey(0)