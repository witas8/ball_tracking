import cv2
import numpy as np
import imutils
import argparse
from collections import deque

camera = cv2.VideoCapture(0)

ap = argparse.ArgumentParser()
ap.add_argument("-b", "--buffer", type=int, default=128, help="max buffer size")
args = vars(ap.parse_args())

pts = deque(maxlen=args["buffer"])
counter = 0
position = []
time = []

while True:
    ret, frame = camera.read()
    cv2. imshow("Frame", frame)
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    low_blue = np.array([94, 80, 2])
    high_blue = np.array([126, 255, 255])
    blue_mask = cv2.inRange(hsv_frame, low_blue, high_blue)
    blue = cv2.bitwise_and(frame, frame, mask=blue_mask)

    cnts = cv2.findContours(blue_mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    center = None

    if len(cnts) > 0:
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        if M["m00"] > 0:
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

            if radius > 15:
                cv2.circle(frame, (int(x), int(y)), int(radius),(0, 255, 255), 2)
                cv2.circle(frame, center, 5, (0, 0, 255), -1)

                position.append(center)

                if len(position) < 2:
                   p1 = position[-1]
                else:
                   p1 = position[-2] #previous
                diff = np.subtract(position[-1], p1)

                print  "Previous center: {}".format(p1)
                print  "Now center {}".format(position[-1])
                print  "Difference: {}".format(diff)

                pts.appendleft(center)

                for i in range(1, len(pts)):
                    thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)
                    cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), thickness)
                    counter = counter + 1
                    time.append(counter)
                    #print "Time: {}".format(time[-1])

                    if len(time) < 2:
                        t1 = time[-1]
                        delta_t = 0
                    else:
                        delta_t = time[-1] - time[-2]
                        velocity = float(diff[-1]/delta_t)
                        print  "Delta time: {}".format(delta_t)
                        print  "Velocity: {}".format(velocity)

            else:
                pts.clear()
                counter = 0

            print "Time: {}".format(counter)
            #compute: velocity = (center - previous_center)/counter

        else:
            pass

    cv2.imshow("Frame", frame)
    #cv2.imshow("Uncolored Mask", blue_mask) #no color
    cv2.imshow("Colored mask", blue) #with color

    key = cv2.waitKey(1)
    if key == 27:
        break