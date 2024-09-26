import cv2
import cvzone
from cvzone.HandTrackingModule import HandDetector
import numpy as np
import time
import pygame

# Initialize pygame mixer
pygame.mixer.init()

# Load sound
hit_sound = pygame.mixer.Sound("sonds/sonun.mp3")

cap = cv2.VideoCapture(0)
cap.set(3, 1920)  # Set width 
cap.set(4, 1080)  # Set height #

# Import images
imgBackground = cv2.imread("img/3.png")
imgGameOver = cv2.imread("img/5.png", cv2.IMREAD_UNCHANGED)
imgBoll = cv2.imread("img/12-111.png", cv2.IMREAD_UNCHANGED)
imgBat1 = cv2.imread("img/12-1111.png", cv2.IMREAD_UNCHANGED)
imgBat2 = cv2.imread("img/12-1111 copy.png", cv2.IMREAD_UNCHANGED)

imgBackground = cv2.resize(imgBackground, (1920, 1080))
imgGameOver = cv2.resize(imgGameOver, (1920, 1080))
imgBoll = cv2.resize(imgBoll, (90, 90))  # Adjusted size
imgBat1 = cv2.resize(imgBat1, (75, 271))  # Adjusted size
imgBat2 = cv2.resize(imgBat2, (75, 271))  # Adjusted size

detector = HandDetector(staticMode=False, maxHands=2, modelComplexity=1, detectionCon=0.8, minTrackCon=0.5)

bollPos = [100, 100]
speedx = 12
speedy = 12
gameOver = False
score = [0, 0]
misses = 0  # Initialize misses counter

# Game duration in seconds
GAME_DURATION = 180  # 3 minutes

# Interval for speed increase in seconds
SPEED_INCREASE_INTERVAL = 4
last_speed_increase_time = time.time()

# Maximum speed
MAX_SPEED = 50

# Record the start time
start_time = time.time()

while True:
    _, img = cap.read()
    img = cv2.flip(img, 1)

    # The 'flipType' parameter flips the image, making it easier for some detections
    hands, img = detector.findHands(img, draw=True, flipType=False)

    # Overlay background
    img = cv2.addWeighted(img, 0.0, imgBackground, 0.8, 0)

    # Check for hands
    if hands:
        for hand in hands:
            x, y, w, h = hand['bbox']
            h1, w1, _ = imgBat1.shape
            y1 = int(y - h1 / 2)
            y1 = np.clip(y1, 20, 780)

            if hand['type'] == "Left":
                img = cvzone.overlayPNG(img, imgBat1, (100, y1))  # Adjusted position
                if 100 < bollPos[0] < 100 + w1 and y1 < bollPos[1] < y1 + h1:
                    speedx = -speedx
                    bollPos[0] += 30
                    score[0] += 1
                    hit_sound.play()  # Play sound when ball hits left bat

            if hand['type'] == "Right":
                img = cvzone.overlayPNG(img, imgBat2, (1825, y1))  # Adjusted position
                if 1825 - 100 < bollPos[0] < 1825 + w1 and y1 < bollPos[1] < y1 + h1:
                    speedx = -speedx
                    bollPos[0] -= 30
                    score[1] += 1
                    hit_sound.play()  # Play sound when ball hits right bat

    # Check for game over
    if bollPos[0] < 40 or bollPos[0] > 1880:  # Adjusted positions
        misses += 1
        if misses >= 3:
            gameOver = True
        else:
            bollPos = [100, 100]  # Reset ball position
            speedx = 12  # Reset speed
            speedy = 12

    # Check for timer
    elapsed_time = time.time() - start_time
    remaining_time = int(GAME_DURATION - elapsed_time)
    minutes = remaining_time // 60
    seconds = remaining_time % 60
    timer_text = f" {minutes:02}:{seconds:02}"
    if remaining_time <= 0:
        gameOver = True

    if gameOver:
        img = imgGameOver
        
        cv2.putText(img, str(score[0] + score[1]).zfill(2), (870, 660), cv2.FONT_HERSHEY_COMPLEX, 5, (204, 255, 153), 8)  # Adjusted position
        
    else:
        # Increase speed periodically
        if time.time() - last_speed_increase_time > SPEED_INCREASE_INTERVAL:
            speedx = min(speedx * 1.0, MAX_SPEED)  # Smaller increment
            speedy = min(speedy * 1.0, MAX_SPEED)  # Smaller increment
            last_speed_increase_time = time.time()
           # print(f"Speed increased: speedx={speedx}, speedy={speedy}")  # Log speed increases

        # Move ball
        if bollPos[1] >= 800 or bollPos[1] <= 10:  # Adjusted positions
            speedy = -speedy
            hit_sound.play()  # Play sound when ball hits top or bottom side
        bollPos[0] += int(speedx)
        bollPos[1] += int(speedy)

        # Overlay ball
        img = cvzone.overlayPNG(img, imgBoll, bollPos)
        cv2.putText(img, str(score[0]), (450, 1000), cv2.FONT_HERSHEY_COMPLEX, 3, (255, 255, 255), 5)  # Adjusted position
        cv2.putText(img, str(score[1]), (1375, 1000), cv2.FONT_HERSHEY_COMPLEX, 3, (255, 255, 255), 5)  # Adjusted position
        cv2.putText(img, timer_text, (790, 1000), cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 255, 255), 5)  # Display timer
        cv2.putText(img, f" {misses}/3", (50, 1000), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 5)

    cv2.imshow("Image", img)
    key = cv2.waitKey(1)
    if key == ord('r'):
        bollPos = [100, 100]
        speedx = 12
        speedy = 12
        gameOver = False
        score = [0, 0]
        misses = 0  # Reset misses
        start_time = time.time()  # Reset the timer
        last_speed_increase_time = time.time()  # Reset speed increase time
    if key == ord('q'):
        break


cap.release()
cv2.destroyAllWindows()
