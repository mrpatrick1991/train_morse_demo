
import time
import asyncio
from array import array
from time import sleep
import pygame

from pygame.mixer import Sound, get_init, pre_init

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
YELLOW = (255, 255, 0)
ORANGE = (255,140,0)

title = "Amateur Radio Communications"

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

CODE_REVERSE = {v: k for k, v in CODE.items()}

pygame.init()

infoObject = pygame.display.Info()
screen = pygame.display.set_mode((infoObject.current_w, infoObject.current_h))
clock = pygame.time.Clock()
running = True

input = ""
morse = ""
code = ""
key = ""

key_timer_ms = 0
last_action_timer_s = 0

pre_init(44100, -16, 1, 1024)

while running:

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.unicode.isalpha() or event.unicode.isnumeric():
                input += event.unicode.upper()
                code = CODE[event.unicode.upper()]
                for char in code:
                    if char == ".":
                        Note(400).play(-1,maxtime=50)
                        time.sleep(.1)
                    else:
                        Note(400).play(-1,maxtime=100)
                        time.sleep(.1)
                    time.sleep(.05)
                    
            elif event.key == pygame.K_SPACE:
                input += " "
            elif event.key == pygame.K_BACKSPACE:
                input = input[:-1]
                if (input == ""):
                    code = ""
            elif event.key == pygame.K_RETURN:
                input = ""
                code = ""
            elif event.key == pygame.K_RSHIFT:
                key_timer_ms = 0
                last_action_timer_ms = 0
                Note(400).play(-1,maxtime=60000)

            elif event.type == pygame.QUIT:
                running = False

        if event.type == pygame.KEYUP and event.key == pygame.K_RSHIFT:
            last_action_timer_ms = 0
            print("key down time is: ", key_timer_ms)
            pygame.mixer.stop()
            if (key_timer_ms < 0.1):
                print(".")
                key+="."
            elif (key_timer_ms >= 0.1 and key_timer_ms < 3.0):
                print("-")
                key+="_"

        if (last_action_timer_s > 5.0):
                try:
                    input += CODE_REVERSE[key]
                    key = ""
                except KeyError:
                    print("no decode on: ", key)
                    key = ""
                    
                


    morse = [CODE[c] + " " for c in input]
    morse = "".join(morse)

    screen.fill("black")
    font = pygame.font.SysFont(None, 84)
    center = screen.get_rect().center
    title_img = font.render(title, True, ORANGE)


    input_img = font.render(input, True, YELLOW)
    morse_img = font.render(morse, True, YELLOW)

    last_char_img = font.render(input[-1] if len(input) else "", True, YELLOW)
    last_morse_img = font.render(code, True, YELLOW)

    screen.blit(title_img, title_img.get_rect(center = (center[0],center[1]-350)))

    screen.blit(last_morse_img, last_morse_img.get_rect(center = (center[0],center[1]-250)))
    screen.blit(last_char_img, last_char_img.get_rect(center = (center[0],center[1]-150)))

    screen.blit(input_img, input_img.get_rect(center = (center[0],center[1]+150)))
    screen.blit(morse_img, morse_img.get_rect(center = (center[0],center[1]+250)))

    dt = clock.tick(30) / 1000
    key_timer_ms += dt
    last_action_timer_s += dt

    pygame.display.flip()

