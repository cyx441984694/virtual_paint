import cv2 
import mediapipe as mp 
import os
import time 
import numpy as np


def color_switch(event,x,y,flags,param):
    # get mouse x position to detect which color to choose
    global col,header 
    if 142 < x < 213:
        header = overlist[6]
        col = (226, 43, 138) # purple
        print("the col is: purple")
    elif 213 < x < 284:
        header = overlist[5]
        col = (255,255,255) #white
        print("the col is: white")
    elif 355 < x < 426:
        header = overlist[3]
        col = (255, 255, 0)
        print("the col is: yellow")
    elif 497 < x < 568:
        header = overlist[1]
        col = (0,0,255)
        print("the col is: red")
    # can add more 


def initiate_color_imglist():
    # Load images from the folder and append them to the list
    folder = 'colors'
    mylist = os.listdir(folder)
    print(mylist)
    overlist = []
    for i in range(1,len(mylist)):
        image = cv2.imread(f'{folder}/{i}.png')
        try:
            overlist.append(image)
        except AttributeError:
            print("shape not found")
    return overlist


if __name__ == '__main__':
        
    # Initialize webcam video capture
    cap = cv2.VideoCapture(0)
    cap.set(3, 640)  # Set width
    cap.set(4, 500)  # Set height
    cap.set(10, 150)  # Set brightness
    
    # Initialize mediapipe Hands object for hand tracking
    mpHands = mp.solutions.hands
    hands = mpHands.Hands()
    mpdraw = mp.solutions.drawing_utils
    
    pasttime = 0
    col = [0, 0, 255]  # Default color (red)
    xp, yp = 0, 0
    
    overlist = initiate_color_imglist()
    # Set the initial header image from the first image in the list
    header = overlist[1]
    
    # Create a blank canvas to draw on
    canvas = np.zeros((640, 1000, 3), np.uint8)
    
    while cap.isOpened():
        # Read a frame from the webcam and flip it horizontally
        success, frame = cap.read()
        frame = cv2.flip(frame, 1)
        
        # Convert the frame to RGB color space for hand tracking
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
        # Process the frame to detect hand landmarks
        results = hands.process(img)
        lanmark = []
    
        if results.multi_hand_landmarks:
            for hn in results.multi_hand_landmarks:
                for id, lm in enumerate(hn.landmark):
                    h, w, c = frame.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lanmark.append([id, cx, cy])
                mpdraw.draw_landmarks(frame, hn, mpHands.HAND_CONNECTIONS)
    
        
        if len(lanmark) != 0:
            # Check if the hand is in "selection mode" or "drawing mode"
            x1, y1 = lanmark[8][1], lanmark[8][2]
            x2, y2 = lanmark[12][1], lanmark[12][2]
    
            cv2.setMouseCallback('cam',color_switch)
    
            if lanmark[8][2] < lanmark[6][2] and lanmark[12][2] < lanmark[10][2]:
                xp, yp = 0, 0
                print('Selection mode')
                    
                # Draw a rectangle representing the qselected color
                cv2.rectangle(frame, (x1, y1), (x2, y2), col, cv2.FILLED)
    
            elif lanmark[8][2] < lanmark[6][2]:
                print('Drawing mode')
                if xp == 0 and yp == 0:
                    xp, yp = x1, y1
    
                # Draw lines on the canvas when in "drawing mode"
                cv2.line(frame, (xp,yp), (x1, y1), col, 5, cv2.FILLED)
                # TBC? - to add pause and delay 
                cv2.line(canvas, (xp,yp), (x1, y1), col, 5, cv2.FILLED)
                xp, yp = x1, y1
    
        # Prepare the canvas for blending with the frame
        imgGray = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
        _, imgInv = cv2.threshold(imgGray, 50, 255, cv2.THRESH_BINARY_INV)
        imgInv = cv2.cvtColor(imgInv, cv2.COLOR_GRAY2BGR)
    
        # Use bitwise operations to blend the frame with the canvas
        frame = cv2.bitwise_and(frame, frame, imgInv)
        frame = cv2.bitwise_or(frame,frame, canvas)
    
        # Add the header (color selection) at the top of the frame
        frame[0:100, 0:640] = header
    
        # Calculate and display the frames per second (FPS) on the frame
        ctime = time.time()
        fps = 1 / (ctime - pasttime)
        pasttime = ctime
        cv2.putText(frame, f'FPS: {int(fps)}', (490, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 3)
    
        # Show the webcam frame and the canvas
        cv2.imshow('cam', frame)
        cv2.imshow('canvas', canvas)
    
        # clear or quite
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("exiting...")
            break
        if cv2.waitKey(1) & 0xFF == ord('d'):
            print("resetting to blank...")
            canvas = np.zeros((640, 1000, 3), np.uint8)
    
            
