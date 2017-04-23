# Name: Motion Detection Camera 
# Developer: Vishnu Unnikrishnan
# Date: 2017-04-22
# Description: Python based motion detection camera

import numpy as np
import cv2
import datetime
import imutils
import time

def main():
	cap = cv2.VideoCapture(0)

	time.sleep(0.25)
	prevFrame = None
	fps_half = 15
	count = 0
	while(True):
		#Capture frames
		ret, frame = cap.read()
		
		# resize the frame, convert it to grayscale, and blur it
		frame = imutils.resize(frame, width=500)
		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		gray = cv2.GaussianBlur(gray, (15, 15), 0)
		count = count+1
		if prevFrame != None:
			frameDelta = cv2.absdiff(prevFrame,gray)
			
			thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]
			thresh = cv2.dilate(thresh, None, iterations=10)
			
			if count >= fps_half:
				prevFrame = gray
				count = 0
			cv2.imshow("Threshold", thresh)


			(cnts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
			
			for c in cnts:
			 #if the contour is too small, ignore it
				if cv2.contourArea(c) < 1000:
					continue
				(x, y, w, h) = cv2.boundingRect(c)
				cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
				
			cv2.imshow("Frame", frame)

		else:
			prevFrame = gray

		if cv2.waitKey(1) & 0xFF == ord('q'):
			break

	# When everything done, release the capture
	cap.release()
	cv2.destroyAllWindows()

if __name__ == "__main__":
	main()
