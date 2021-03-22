#Importing Packages
import cv2
import time
import argparse
import imutils
from directkeys import  W, A, S, D, PressKey, ReleaseKey

# Setting the Upper and Lower boundaries for object color 
#Note: The values must be taken from HSV color space only
Lower_threshold = ( 29, 86, 6 ) #(36, 0 ,0)      
Upper_threshold = (70, 255, 255) #( 64, 255, 255 )    

#Start capturing video input
video_input = cv2.VideoCapture(0)


# Delay to open game window(manually) in order to sync 
time.sleep(2.0)
current_key_pressed = set()

#For continous tracking, we are looping the code
while True:
    keyPressed = False                              
    keyPressed_lr = False
    # Get the current frame
    _, frame = video_input.read()
    frame = cv2.flip(frame, 1)
 
    # Resizing the image to the specified width size
    frame = imutils.resize(frame, width=600)   
    #To remove noise, applying a 7*7 gaussian filter mask
    blurred = cv2.GaussianBlur(frame, (7, 7), 0)
    #Converting captured image to hsv image
    hsv_image = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    #To detect the objects with color in the threshold ranges
    #Note: In this case, this is green color
    mask = cv2.inRange(hsv_image, Lower_threshold, Upper_threshold)
    #To remove small dots present in the masked image
    mask = cv2.erode(mask, None, iterations = 2)
    #Dilating the image
    mask = cv2.dilate(mask, None, iterations = 2)
 
    #Dividing the 2 contours into right and left for [UP, DOWN] and [LEFT, RIGHT]
    limit = 300 #int(width/2)
    right_contour = mask[:,limit:,]            
    left_contour = mask[:,0:limit,]

    
    #Finds the contours on the left side of the image
    cnts_left = cv2.findContours(left_contour.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts_left = imutils.grab_contours(cnts_left)
    #Finds the contours on the right side of the image
    cnts_right = cv2.findContours(right_contour.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts_right = imutils.grab_contours(cnts_right)
    center_left = None
    center_right = None 
    #Parameters for text format on the screen
    font = cv2.FONT_HERSHEY_SIMPLEX
    fontScale = 1
    color = (255, 0 ,0)
    thickness = 2
        
    #************************************   Detection for KEYS - [W,A,S,D] *********************************
    #Continue only if both contours(left and right) are detected
    if len(cnts_left) > 0:
        left_value = max(cnts_left, key = cv2.contourArea)
        ((x_left, y_left), radius_left) = cv2.minEnclosingCircle(left_value)
        left_moment = cv2.moments(left_value)
        center_left = (int(left_moment["m10"] / left_moment["m00"]) , int(left_moment["m01"] / left_moment["m00"]))

        #Continue only if the radius of both contours are greater than 10
        #Note: This value size can be changed according to application
        if int(radius_left) > 8:
            #Draws a circle around the object and its center on the left side 
            cv2.circle(frame, (int(x_left), int(y_left)), int(radius_left), (0, 255, 255), 2)
            cv2.circle(frame, center_left, 5, (255, 0, 0), -1)

            #Checking condition for 'UP' condition
            if center_left[1] < 160:
                cv2.putText(frame,'UP',(20,50), font, fontScale,color  ) #, thickness)
                print('UP')
                PressKey(W)
                current_key_pressed.add(W)
                keyPressed = True
                keyPressed_lr = True
            #Checking condition for 'DOWN' condition
            elif center_left[1] > 320:
                cv2.putText(frame,'DOWN',(20,50),font, fontScale,color ) #, thickness)
                print('DOWN')
                PressKey(S)
                current_key_pressed.add(S)
                keyPressed = True
                keyPressed_lr = True

    if len(cnts_right) > 0:                       
        #Finds the contour with the largest size
        right_value = max(cnts_right, key = cv2.contourArea)
        #Finds the radius and center of the largest contour
        ((x_right, y_right), radius_right) = cv2.minEnclosingCircle(right_value)
        right_moment = cv2.moments(right_value)
        center_right = (int(right_moment["m10"] / right_moment["m00"]), int(right_moment["m01"] / right_moment["m00"]))
        center_right = ( int(center_right[0] + limit ) ,center_right[1]) 

        if int(radius_right) > 8:
            #Draws a circle aroudn the object and its center on the right side
            cv2.circle(frame, (int(x_right)+ limit , int(y_right)), int(radius_right), (0, 255, 255), 2)
            cv2.circle(frame, center_right, 5, (255, 0, 0), -1)

            #Checking condition for 'LEFT' condition
            if center_right[0] < 365 :                        
                cv2.putText(frame,'LEFT',(200,50),font, fontScale,color )#, thickness)
                print('LEFT')
                PressKey(A)
                keyPressed = True
                current_key_pressed.add(A)
            #Checking concdition for 'RIGHT' condition
            elif center_right[0] > 515:
                cv2.putText(frame,'RIGHT',(200,50),font, fontScale,color ) #, thickness)
                print('RIGHT')
                PressKey(D)
                keyPressed = True
                current_key_pressed.add(D)

        #*************************  End of direction detection ****************************
        
    #Dividing left half into 'UP' and 'DOWN' or 'W' and 'S'.
    cv2.line(frame,(0,160),( 240 ,160),(0,224,19),2)
    cv2.line(frame,(0,320),( 240 ,320),(0,224,19),2)

    #Dividing right half into 'LEFT' and 'RIGHT'  or  'A' or 'S'
    cv2.line(frame, (240,0), (240,480), (0,224,19),2)
    cv2.line(frame, (365,0), (365,480), (0,224,19),2)
    cv2.line(frame, (515,0),(515,480),(0,224,19),2)
    cv2.line(frame, (640,0),(640,480),(0,224,19),2)
    #Displays the frame 
    cv2.imshow("Frame", frame)


    #If key is pressed, then releasing the key
    #For 'W' and 'S' keys
    if not keyPressed and len(current_key_pressed) != 0:
        for key in current_key_pressed:
            ReleaseKey(key)
        current_key_pressed = set()

    #If key is pressed, then releasing the key
    #For 'A' and 'D' keys, with keys 'UP' or 'DOWN' pressed down
    if not keyPressed_lr and ((D in current_key_pressed) or (A in current_key_pressed)):
        if A in current_key_pressed:
            ReleaseKey(A)
            current_key_pressed.remove(A)
        elif D in current_key_pressed:
            ReleaseKey(D)
            current_key_pressed.remove(D)

    key = cv2.waitKey(1) & 0xFF
 

    #Exits the program if the key 'e' is pressed
    if key == ord("e"):
        break
 
# closes all windows
video_input.release()
cv2.destroyAllWindows()