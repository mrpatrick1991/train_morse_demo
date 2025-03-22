import time
import asyncio
from array import array
from time import sleep
import pygame
import socket
import threading
import json
import RPi.GPIO as GPIO 


title = "Amateur Radio Communications"


MULTICAST_GROUP = "224.1.1.1"
PORT = 5007

tone_freq_hz = 500
dit_time_sec = .05
dah_time_sec = .1
pause_time_sec = .05
key_fudge_factor = 1.5      # make the manual keydown less sensitive, i.e. symbols are expected to be longer.
key_guard_period_sec = 0.40 # assume that the character is done being keyed if there is no keyer activity in this many seconds. 
key_min_time_sec = 0.01     # if key pressed for less than this, don't record it as a dit (or a dah). 

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

GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
GPIO.setup(11, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

infoObject = pygame.display.Info()
screen = pygame.display.set_mode((infoObject.current_w, infoObject.current_h))
clock = pygame.time.Clock()
running = True
pygame.mixer.pre_init(44100, -16, 1, 1024)

timer = 0
morse = []
keyer_dit_dah = []
input = ""
symbol = ""

send_flag = False
mouse_down_time = 0
mouse_down = False

def udp_send(message):
    """Sends dictionary messages over UDP multicast."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
    json_data = json.dumps(message)  # Serialize dict to JSON
    sock.sendto(json_data.encode(), (MULTICAST_GROUP, PORT))


def udp_receive():
    """Receives dictionary messages over UDP multicast."""
    global morse
    global input
    global symbol

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("", PORT))

    mreq = socket.inet_aton(MULTICAST_GROUP) + socket.inet_aton("0.0.0.0")
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    print(f"Listening for messages on {MULTICAST_GROUP}:{PORT}...")

    while True:
        data, addr = sock.recvfrom(4096)
        try:
            message = json.loads(data.decode())  # Deserialize JSON to dict
            print(f"Received from {addr}: {message}")
            morse[:] = message["morse"]  # Update in place
            input = message["input"]
            symbol = message["symbol"]

        except json.JSONDecodeError:
            pass

threading.Thread(target=udp_receive, daemon=True).start()

while running:

    dt = clock.tick(30) / 1000
    timer += dt
    pygame.display.flip()

    screen.fill("black")
    font = pygame.font.SysFont(None, 84)
    center = screen.get_rect().center

    if GPIO.input(11) == GPIO.HIGH:
        print("high")
    

    for event in pygame.event.get():

        if event.type == pygame.QUIT:  # Handles window close
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN and not mouse_down:
            mouse_down = True
            mouse_down_time = timer
            Note(tone_freq_hz).play(-1,maxtime=int(10*1000))

        if event.type == pygame.MOUSEBUTTONUP and mouse_down:
            mouse_down = False
            mouse_down_sec = timer - mouse_down_time
            pygame.mixer.stop()
            print("mouse clicked for: ", str(mouse_down_sec))

            if (mouse_down_sec <= dit_time_sec*key_fudge_factor and mouse_down_sec > key_min_time_sec):
                print("DIT ")
                keyer_dit_dah.append(".")

            elif (mouse_down_sec >= dit_time_sec*key_fudge_factor):
                print("DAH ")
                keyer_dit_dah.append("-")
                

        if timer - mouse_down_time >= key_guard_period_sec and len(keyer_dit_dah) and not mouse_down:
            print("guard period timeout")

            if (len(keyer_dit_dah) > 5):
                keyer_dit_dah = []
                print("".join(keyer_dit_dah))
                print("morse symbol is too long (>5 dits or dahs), ignoring.")

            try:
                input += code_reverse["".join(keyer_dit_dah)]
                symbol = "".join(keyer_dit_dah)
                morse.append(symbol)
                print("keyed symbol is: ", input)
                keyer_dit_dah = []
                send_flag = True
            except KeyError:
                print("no valid morse symbol for: ", str("".join(keyer_dit_dah)), " ignoring.")
                keyer_dit_dah = []
            print("".join(keyer_dit_dah))
            keyer_dit_dah = []

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:  # Exit when ESC is pressed
                running = False

            if (event.unicode.isalpha() or event.unicode.isnumeric()) and not mouse_down:
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
                if input:
                    input = input[:-1]  # Remove last character
                if morse:
                    morse.pop()  # Remove last Morse code entry
            elif event.key == pygame.K_RETURN:
                input = ""
                symbol = ""
                morse = []
            if (input == ""):
                symbol = ""
            
            send_flag = True

       
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

    if (send_flag):
        send_flag = False
        udp_send({"morse":morse, "input": input, "symbol": symbol})

    