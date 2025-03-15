import time
import asyncio
from array import array
from time import sleep
import pygame

title = "Amateur Radio Communications"

tone_freq_hz = 600
dit_time_sec = .05
dah_time_sec = .1
pause_time_sec = .05

black = (0, 0, 0)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
gray = (200, 200, 200)
yellow = (255, 255, 0)
orange = (255,140,0)

class Note(pygame.mixer.Sound):

    def __init__(self, frequency, volume=.1):
        self.frequency = frequency
        pygame.mixer.Sound.__init__(self, self.build_samples())
        self.set_volume(volume)

    def build_samples(self):
        period = int(round(pygame.mixer.get_init()[0] / self.frequency))
        samples = array("h", [0] * period)
        amplitude = 2 ** (abs(pygame.mixer.get_init()[1]) - 1) - 1
        for time in range(period):
            if time < period / 2:
                samples[time] = amplitude
            else:
                samples[time] = -amplitude
        return samples

code = {"A": ".-",     "B": "-...",   "C": "-.-.", 
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

code_reverse = {v: k for k, v in code.items()}

pygame.init()

infoObject = pygame.display.Info()
screen = pygame.display.set_mode((infoObject.current_w, infoObject.current_h))
clock = pygame.time.Clock()
running = True
pygame.mixer.pre_init(44100, -16, 1, 1024)

timer = 0
morse = []
input = ""
symbol = ""

while running:

    dt = clock.tick(30) / 1000
    timer += dt
    pygame.display.flip()

    screen.fill("black")
    font = pygame.font.SysFont(None, 84)
    center = screen.get_rect().center

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.unicode.isalpha() or event.unicode.isnumeric():
                input += event.unicode.upper()
                symbol = code[event.unicode.upper()]
                morse.append(symbol)

                for char in symbol:
                    if char == ".":
                        Note(tone_freq_hz).play(-1,maxtime=int(dit_time_sec*1000))
                        time.sleep(.1)
                    else:
                        Note(tone_freq_hz).play(-1,maxtime=int(dah_time_sec*1000))
                        time.sleep(.1)
                    time.sleep(pause_time_sec)
                    
            elif event.key == pygame.K_SPACE:
                input += " "
                symbol = ""
            elif event.key == pygame.K_BACKSPACE:
                input = input[:-1]
                morse = morse[:-1]
            elif event.key == pygame.K_RETURN:
                input = ""
                symbol = ""
            if (input == ""):
                symbol = ""
       
    title_img = font.render(title, True, orange)
    input_img = font.render(input, True, yellow)
    morse_img = font.render(" ".join(morse), True, yellow)

    last_char_img = font.render(input[-1] if len(input) else "", True, yellow)
    last_morse_img = font.render(symbol, True, yellow) 

    screen.blit(title_img, title_img.get_rect(center = (center[0],center[1]-350)))
    screen.blit(last_morse_img, last_morse_img.get_rect(center = (center[0],center[1]-250)))
    screen.blit(last_char_img, last_char_img.get_rect(center = (center[0],center[1]-150)))
    screen.blit(input_img, input_img.get_rect(center = (center[0],center[1]+150)))
    screen.blit(morse_img, morse_img.get_rect(center = (center[0],center[1]+250)))