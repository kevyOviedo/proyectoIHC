import cv2
import mediapipe as mp
import pyautogui

def correr_eyetracker(is_running):
    cam = cv2.VideoCapture(0)
    face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)
    screen_w, screen_h = pyautogui.size()
    center_x = screen_w/2
    center_y= screen_h/2
    blink= False
    while is_running():
        _, frame = cam.read()
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        output = face_mesh.process(rgb_frame)
        landmark_points = output.multi_face_landmarks
        frame_h, frame_w, _ = frame.shape
        if landmark_points:
            landmarks = landmark_points[0].landmark
            for id, landmark in enumerate(landmarks[474:478]):
                x = int(landmark.x * frame_w)
                y = int(landmark.y * frame_h)
                cv2.circle(frame, (x, y), 3, (0, 255, 0))
                if id == 1:
                    screen_x = screen_w * landmark.x 
                    screen_y = screen_h * landmark.y
                    
                    ###
                    if screen_x>center_x:
                        screen_x= screen_x+(screen_x-center_x)
                    if screen_x<center_x:
                        screen_x= screen_x-(center_x-screen_x) 
                    if screen_y>center_y:
                        screen_y= screen_y+(screen_y-center_y) 
                    if screen_y<center_y:
                        screen_y= screen_y-(center_y-screen_y)    
                    
                    if screen_x>screen_w:
                        screen_x=screen_w-10
                    if screen_y>screen_h:
                        screen_y=screen_h-10
                    if screen_x<0:
                        screen_x=0
                    if screen_y<0:
                        screen_y=0
                    ###

                    #pyautogui.moveTo(screen_x, screen_y)
                    #print(screen_x,screen_y)	
            left = [landmarks[145], landmarks[159]]
            for landmark in left:
                x = int(landmark.x * frame_w)
                y = int(landmark.y * frame_h)
                
                cv2.circle(frame, (x, y), 3, (0, 255, 255))
            if (left[0].y - left[1].y) < 0.004:
                blink=True
            else:
                blink=False
        else:
            screen_x=-1
            screen_y=-1
            
        
        data = [int(screen_x), int(screen_y), blink]
        #print(data)
        yield data
        #cv2.imshow('Eye Controlled Mouse', frame)
        cv2.waitKey(1)
    cam.release()
    cv2.destroyAllWindows()