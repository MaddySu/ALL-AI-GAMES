import random
import cv2
import cvzone
from cvzone.HandTrackingModule import HandDetector
import time
import pygame  # Import pygame

# Initialize pygame mixer
pygame.mixer.init()

# Load the sounds
sound_start = pygame.mixer.Sound("assest/SPS/sounds/sound.mp3")
sound_ai_win = pygame.mixer.Sound("assest/SPS/sounds/AIwin.mp3")
sound_player_win = pygame.mixer.Sound("assest/SPS/sounds/Pwin.mp3")
sound_Drow = pygame.mixer.Sound("assest/SPS/sounds/Drow.mp3")

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

detector = HandDetector(maxHands=1)

timer = 0
stateResult = False
startGame = False
scores = [0, 0]  # [AI, Player]

while True:
    imgBG = cv2.imread("assest/SPS/img/BG.png")
    success, img = cap.read()

    # Resize the image to 598x630
    imgScaled = cv2.resize(img, (598, 630))

    # Find Hands
    hands, img = detector.findHands(imgScaled)  # with draw

    if startGame:
        if stateResult is False:
            timer = time.time() - initialTime
            cv2.putText(imgBG, str(int(timer)), (900, 650), cv2.FONT_HERSHEY_PLAIN, 9, (255, 0, 255), 6)

            if timer > 3:
                stateResult = True
                timer = 0

                if hands:
                    playerMove = None
                    hand = hands[0]
                    fingers = detector.fingersUp(hand)
                    if fingers == [0, 0, 0, 0, 0]:
                        playerMove = 1
                    elif fingers == [1, 1, 1, 1, 1]:
                        playerMove = 2
                    elif fingers == [0, 1, 1, 0, 0]:
                        playerMove = 3

                    randomNumber = random.randint(1, 3)
                    imgAI = cv2.imread(f'assest/SPS/img/{randomNumber}.png', cv2.IMREAD_UNCHANGED)
                    imgBG = cvzone.overlayPNG(imgBG, imgAI, (288, 456))

                    # Player Wins
                    if (playerMove == 1 and randomNumber == 3) or \
                            (playerMove == 2 and randomNumber == 1) or \
                            (playerMove == 3 and randomNumber == 2):
                        scores[1] += 1
                        sound_player_win.play()  # Play player win sound

                    # AI Wins
                    elif (playerMove == 3 and randomNumber == 1) or \
                            (playerMove == 1 and randomNumber == 2) or \
                            (playerMove == 2 and randomNumber == 3):
                        scores[0] += 1
                        sound_ai_win.play()  # Play AI win sound
                   
                    elif(playerMove == 3 and randomNumber == 3) or \
                            (playerMove == 2 and randomNumber == 2) or \
                            (playerMove == 1 and randomNumber == 1):
                       
                        cv2.putText(imgBG, "Draw", (869, 459), cv2.FONT_HERSHEY_PLAIN, 9, (255, 0, 255), 6)
                        sound_Drow.play()  # Play AI win sound

    # Update the position of imgScaled on imgBG at coordinates (1198, 355)
    imgBG[355:355+630, 1198:1198+598] = imgScaled

    if stateResult:
        imgBG = cvzone.overlayPNG(imgBG, imgAI, (288, 456))

    # Ensure scores are always printed on top of other elements
    cv2.putText(imgBG, str(scores[0]), (633, 320), cv2.FONT_HERSHEY_PLAIN, 6, (0, 255, 255), 6)  # (633, 320)
    cv2.putText(imgBG, str(scores[1]), (1690, 320), cv2.FONT_HERSHEY_PLAIN, 6, (0, 255, 255), 6)

    # Display the images
    cv2.imshow("BG", imgBG)
    
    # Debugging statements to print scores in the console
    #print(f"AI Score: {scores[0]}, Player Score: {scores[1]}")

    key = cv2.waitKey(1)
    if key == ord('s') or key == ord('S') :
        startGame = True
        initialTime = time.time()
        stateResult = False
        sound_start.play()  # Play the start game sound when the 's' key is pressed
    if key == ord('q') or key == ord('Q') :
        break


cap.release()
cv2.destroyAllWindows()
