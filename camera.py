# Name: Motion Detection Camera 
# Developer: Vishnu Unnikrishnan
# Date: 2017-04-22
# Description: Python based motion detection camera

from picamera.array import PiRGBArray
from picamera import PiCamera
import numpy as np
import cv2
import datetime
import imutils
import time
import pickle
import struct
import socket

def main():
	# initialize the camera and grab a reference to the raw camera capture
	camera = PiCamera()
	camera.resolution = (640, 480)
	camera.framerate = 32
	rawCapture = PiRGBArray(camera, size=(640, 480))

	time.sleep(0.25)
	prevFrame = None
	fps_half = 15
	count = 0

	clientsocket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	clientsocket.connect(('10.0.1.16',8089))

	for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
		image = frame.array
		# resize the frame, convert it to grayscale, and blur it
		frame_im = imutils.resize(image, width=500)
		gray = cv2.cvtColor(frame_im, cv2.COLOR_BGR2GRAY)
		gray = cv2.GaussianBlur(gray, (15, 15), 0)
		count = count+1
		if prevFrame != None:
			frameDelta = cv2.absdiff(prevFrame,gray)
			
			thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]
			thresh = cv2.dilate(thresh, None, iterations=10)
			
			if count >= fps_half:
				#Only update prev_frame if half, this effects motion detection sensitivity
				#The lower the more sensitive it is from moment to moment.
				prevFrame = gray
				count = 0
			#cv2.imshow("Threshold", thresh)


			(_,cnts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
			
			motion = "false"
			
			for c in cnts:
			 #if the contour is too small, ignore it
				if cv2.contourArea(c) < 1000:
					continue
				(x, y, w, h) = cv2.boundingRect(c)
				cv2.rectangle(frame_im, (x, y), (x + w, y + h), (0, 255, 0), 2)
				motion = "_true"
			#Send to server
			data = pickle.dumps(frame_im)
			clientsocket.sendall(struct.pack("i", len(data))+data)
			#cv2.imshow("Frame_cli", frame)
			print motion

		else:
			prevFrame = gray

		rawCapture.truncate()
		rawCapture.seek(0)

		if cv2.waitKey(1) & 0xFF == ord('q'):
			break

	# When everything done, release the capture
	cap.release()
	cv2.destroyAllWindows()

if __name__ == "__main__":
	main()
