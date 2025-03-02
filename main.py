
import pygame
from pygame.mixer import Sound, get_init, pre_init

import time

from array import array
from time import sleep

class Note(Sound):

    def __init__(self, frequency, volume=.1):
        self.frequency = frequency
        Sound.__init__(self, self.build_samples())
        self.set_volume(volume)

    def build_samples(self):
        period = int(round(get_init()[0] / self.frequency))
        samples = array("h", [0] * period)
        amplitude = 2 ** (abs(get_init()[1]) - 1) - 1
        for time in range(period):
            if time < period / 2:
                samples[time] = amplitude
            else:
                samples[time] = -amplitude
        return samples

BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (200, 200, 200)

CODE = {"A": ".-",     "B": "-...",   "C": "-.-.", 
        "D": "-..",    "E": ".",      "F": "..-.",
        "G": "--.",    "H": "....",   "I": "..",
        "J": ".---",   "K": "-.-",    "L": ".-..",
        "M": "--",     "N": "-.",     "O": "---",
        "P": ".--.",   "Q": "--.-",   "R": ".-.",
     	"S": "...",    "T": "-",      "U": "..-",
        "V": "...-",   "W": ".--",    "X": "-..-",
        "Y": "-.--",   "Z": "--..",
        
        "0": "-----",  "1": ".----",  "2": "..---",
        "3": "...--",  "4": "....-",  "5": ".....",
        "6": "-....",  "7": "--...",  "8": "---..",
        "9": "----.", " ": " "
        }

pygame.init()
screen = pygame.display.set_mode((1920, 1080))
clock = pygame.time.Clock()
running = True

input = ""
morse = ""

pre_init(44100, -16, 1, 1024)


while running:

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.unicode.isalpha():
                input += event.unicode.upper()
                code = CODE[event.unicode.upper()]
                for char in code:
                    if char == ".":
                        Note(200).play(-1,maxtime=50)
                        time.sleep(.1)
                    else:
                        Note(200).play(-1,maxtime=100)
                        time.sleep(.1)
                    time.sleep(.05)

                    
            elif event.key == pygame.K_SPACE:
                input += " "
            elif event.key == pygame.K_BACKSPACE:
                input = input[:-1]
            elif event.key == pygame.K_RETURN:
                input = ""
            elif event.type == pygame.QUIT:
                running = False

    morse = [CODE[c] + " " for c in input]
    morse = "".join(morse)
    screen.fill("black")
    font = pygame.font.SysFont(None, 84)
    
    input_img = font.render(input, True, GREEN)
    morse_img = font.render(morse, True, GREEN)
    screen.blit(input_img, (20, 20))
    screen.blit(morse_img, (20, 100))

    dt = clock.tick(30) / 1000

    pygame.display.flip()

