import cv2
import mediapipe as mp
import numpy as np
import pygame
import time

# Initialize pygame mixer
pygame.mixer.init()

# Load sound
hit_sound = pygame.mixer.Sound("sonun.mp3")

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)  # Set width to 1280 pixels (720p width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)  # Set height to 720 pixels (720p height)

# Game variables
bollPos = [640, 360]
speedx = 20
speedy = 25
gameOver = False
score = [0, 0]
misses = 0  # Initialize misses counter

# Game duration in seconds
GAME_DURATION = 180  # 3 minutes

# Interval for speed increase in seconds
SPEED_INCREASE_INTERVAL = 30
last_speed_increase_time = time.time()

# Maximum speed
MAX_SPEED = 50

# Record the start time
start_time = time.time()

# Function to draw hands
def draw_hand_landmarks(image, hand_landmarks):
    if hand_landmarks:
        for landmarks in hand_landmarks:
            mp_drawing.draw_landmarks(image, landmarks, mp_hands.HAND_CONNECTIONS)

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    result = hands.process(img_rgb)

    hand_landmarks = result.multi_hand_landmarks
    draw_hand_landmarks(img, hand_landmarks)

    if hand_landmarks:
        for hand in hand_landmarks:
            x_min, y_min = 1280, 720
            x_max, y_max = 0, 0
            for lm in hand.landmark:
                x, y = int(lm.x * 1280), int(lm.y * 720)
                x_min = min(x, x_min)
                y_min = min(y, y_min)
                x_max = max(x, x_max)
                y_max = max(y, y_max)

            hand_type = "Left" if hand.landmark[0].x < hand.landmark[9].x else "Right"
            if hand_type == "Left":
                if 50 < bollPos[0] < 50 + (x_max - x_min) and y_min < bollPos[1] < y_max:
                    speedx = -speedx
                    bollPos[0] += 30
                    score[0] += 1
                    hit_sound.play()  # Play sound when ball hits left bat

            if hand_type == "Right":
                if 1155 - 50 < bollPos[0] < 1155 + (x_max - x_min) and y_min < bollPos[1] < y_max:
                    speedx = -speedx
                    bollPos[0] -= 30
                    score[1] += 1
                    hit_sound.play()  # Play sound when ball hits right bat

    # Check for game over
    if bollPos[0] < 40 or bollPos[0] > 1240:  # Adjusted positions for 720p
        misses += 1
        if misses >= 3:
            gameOver = True
        else:
            bollPos = [640, 360]  # Reset ball position to the center
            speedx = 20  # Reset speed
            speedy = 25

    # Check for timer
    elapsed_time = time.time() - start_time
    remaining_time = int(GAME_DURATION - elapsed_time)
    minutes = remaining_time // 60
    seconds = remaining_time % 60
    timer_text = f"Time: {minutes:02}:{seconds:02}"
    if remaining_time <= 0:
        gameOver = True

    if gameOver:
        img = np.zeros((720, 1280, 3), np.uint8)
        cv2.putText(img, "Game Over", (450, 360), cv2.FONT_HERSHEY_COMPLEX, 2, (204, 255, 153), 4)
        cv2.putText(img, f"Score: {score[0] + score[1]}", (450, 460), cv2.FONT_HERSHEY_COMPLEX, 2, (204, 255, 153), 4)
    else:
        # Increase speed periodically
        if time.time() - last_speed_increase_time > SPEED_INCREASE_INTERVAL:
            speedx = min(speedx * 1.05, MAX_SPEED)  # Smaller increment
            speedy = min(speedy * 1.05, MAX_SPEED)  # Smaller increment
            last_speed_increase_time = time.time()
            print(f"Speed increased: speedx={speedx}, speedy={speedy}")  # Log speed increases

        # Move ball
        if bollPos[1] >= 670 or bollPos[1] <= 10:  # Adjusted positions for 720p
            speedy = -speedy
            hit_sound.play()  # Play sound when ball hits top or bottom side
        bollPos[0] += int(speedx)
        bollPos[1] += int(speedy)

        # Draw ball
        cv2.circle(img, tuple(bollPos), 20, (0, 255, 255), -1)
        cv2.putText(img, str(score[0]), (225, 680), cv2.FONT_HERSHEY_COMPLEX, 1.5, (255, 255, 255), 3)  # Adjusted position
        cv2.putText(img, str(score[1]), (1055, 680), cv2.FONT_HERSHEY_COMPLEX, 1.5, (255, 255, 255), 3)  # Adjusted position
        cv2.putText(img, timer_text, (25, 25), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)  # Display timer
        cv2.putText(img, f"Misses: {misses}/3", (25, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)  # Display misses

    cv2.imshow("Image", img)
    key = cv2.waitKey(1)
    if key == ord('r'):
        bollPos = [640, 360]
        speedx = 20
        speedy = 25
        gameOver = False
        score = [0, 0]
        misses = 0  # Reset misses
        start_time = time.time()  # Reset the timer
        last_speed_increase_time = time.time()  # Reset speed increase time
    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
