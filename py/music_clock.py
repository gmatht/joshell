#!/bin/env python3
"""
Talking Musical Console Alarm Clock

When Alarm Time is reached, this clock will read out the current time every
minute and play a random song.

This doesn't use X11 or a GUI.  It's meant to be run from the command line.
You should be able to run this on a very old Laptop without any problems.
E.g. Slackware 14 + music_clock.py uses about (120+40=160) MB of RAM.
It will move the text around to avoid burn-in.

Created by: John McCabe-Dansted
Version: 1.4 (2024-08-13) Fix bug preventing alarm triggering + fix voice
Version: 1.3 (2024-08-10) Rename to music_clock.py (Unique & short)
Version: 1.2 (2024-08-08) Fixed bug with snooze and tidy up.
Version: 1.1 (2024-08-08) Now warn need python3 and name change.

Usage:
    python3 music_clock.py
            OR
    chmod +x music_clock.py && ./music_clock.py

Arguments:
    --precache (Pre-cache the 22/44MB of MP3 speech files)
           #### DEBUGGING OPTIONS ####
    --alarm    (Start with the alarm enabled, mainly for debugging)
    --snooze   (Start in Snoozed state)
    --play     (Just start the play thread without UI or clock)

Keys:
    q/Escape/Ctrl-C: Quit
    w: Wake (Silence alarm, allow screen to blank on idle, brown color)
    a: Alarm (Start alarm, disables screen blanking, energetic cyan color)
    s: Snooze (Snoozes alarm for 20 minutes)
    1, 2, ..., 9, 0: Rate the current song, 1..2 will not be played next time
    n/./>: Next Song (Moves to the next song without rating this one)
    p/,/<: Previous Song (Moves to the previous song without rating this one)
    h: Help
"""

from datetime import datetime
import os
import signal
import subprocess
import sys
import random
import select
import threading
import shutil
from PIL import Image, ImageDraw, ImageFont


### BEGIN CONFIGURATION ###
ALARM_TIME = 730  # 7:30am

SNOOZE_SECS = 1200  # 20 minutes

WAKE_BLANK_MINS = 20

MIN_ANTI_BURNIN_WIDTH = 3  # Mininum x-shift reserved for moving clock face
MIN_ANTI_BURNIN_HEIGHT = 1  # Mininum y-shift ... (to reduce burn-in)
WHITE_CHAR = "\u2588"  # U+2588 is full block character, used for large text

VISUAL_24_HOUR_CLOCK = True
AUDIO_24_HOUR_CLOCK = False

SHUFFLE_SONGS = True

# To list possible colours
# for i in `seq 0 7`; do tput setaf $i ; echo $i ; done
SLEEP_COLOR = 3  # Sleepy Brown
WAKE_COLOR = 6  # Energetic Cyan

MIN_PLAY_RATING = 3  # Minimum rating for rated song (or will not be play song)
### END CONFIGURATION ###

f'' # YOU NEED PYTHON 3. TRY: python3 music_clock.py

if VISUAL_24_HOUR_CLOCK:
    VISUAL_H = "H"
else:
    VISUAL_H = "I"

if AUDIO_24_HOUR_CLOCK:
    AUDIO_H = "H"
else:
    AUDIO_H = "I"

ffplay_exe="ffplay"
if not shutil.which(ffplay_exe):
    ffplay_exe=None
    for f in [r"C:\ProgramData\chocolatey\lib\ffmpeg\tools\ffmpeg\bin\ffplay.exe"]:
        if os.path.isfile(f):
            ffplay_exe=f
            break
    if not ffplay_exe:
        print("ffplay not found")
        os.exit()
    
       
#win32
#if subprocess.call(["which", "ffplay"]) != 0:
#    print("ffplay not found")
#    sys.exit(1)
# Get terminal size

#try:
#    LINES, COLS = [int(i) for i in os.popen("tput lines cols", "r").read().split()]
#except:
#    #This may fail, e.g. on Win32. Just use some sensible defaults.
#    LINES=24
#    COLS=78

COLS, LINES = os.get_terminal_size()

lock = threading.RLock()


try:
    import termios
    import tty
    class _GetchUnix:
       """This code snippet defines a `__call__` method that takes an optional
       argument `wait_seconds` with a default value of None (wait forever).
   
       Inside the method, it retrieves the file descriptor of the standard input
       (`sys.stdin.fileno()`), saves the current terminal settings
       (`termios.tcgetattr(fd)`), and then sets the terminal to raw mode
       (`tty.setraw(sys.stdin.fileno())`).
   
       Next, it uses the `select.select()` function to wait for input from the
       standard input for the specified `wait_seconds`. If there is input
       available, it reads a single character from the standard input
       (`sys.stdin.read(1)`), otherwise it assigns an empty string to the variable `ch`.
   
       Finally, it restores the original terminal settings
           (`termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)`)
       and returns the value of `ch`."""
   
       def __call__(self, wait_seconds=None):
           fd = sys.stdin.fileno()
   
           old_settings = termios.tcgetattr(fd)
           try:
               tty.setraw(sys.stdin.fileno())
               r, w, e = select.select([fd], [], [], wait_seconds)
               if fd in r:
                   ch = sys.stdin.read(1)
               else:
                   ch = ""
           finally:
               termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
           return ch


    getch = _GetchUnix()
except:
    import msvcrt
    import time
    #import bytes
    def getch(wait):

        while wait > 0 and not msvcrt.kbhit():
            mysleep = min(wait,1)
            time.sleep(mysleep)
            wait -= mysleep
        if msvcrt.kbhit():
            return bytes.decode(msvcrt.getch())
        return '\0'
    #getch = msvcrt._getch
   

def make_font_size(font_size, char_list):
    """
    Generates a dictionary of characters and their corresponding ASCII representations.

    This function iterates over a set of characters and generates a dictionary
    where each character is mapped to its corresponding ASCII representation.
    The characters are obtained from the string char_list. For each
    character, a font is created using the "DejaVuSans-Bold.ttf" font file with
    the given size The character is then rendered onto a black image using the
    white font. The pixels are mapped to either a space (' ') or WHITE_CHAR. The
    resulting characters are then added to a list of lines and stored in the
    dictionary.

    The function trips the top of the characters until a non-blank character is found.
    If a non-blank character is found, the function prints the dictionary and exits.

    Returns:
        None
    """

    char_dict = {}
    for char in char_list:
        myfont = ImageFont.truetype("DejaVuSans-Bold.ttf", font_size)
        size = myfont.getbbox(char)[2:]  # calc the size of text in pixels
        image = Image.new("1", size, 1)  # create a b/w image
        draw = ImageDraw.Draw(image)
        draw.text((0, 0), char, font=myfont)  # render the text to the bitmap
        strings = []
        for rownum in range(size[1]):
            line = ""
            for colnum in range(size[0]):
                if image.getpixel((colnum, rownum)):
                    line += " "
                else:
                    line += WHITE_CHAR
            strings.append(line)
        char_dict[char] = strings

    found_nonblank = False
    while True:
        for key, val in char_dict.items():
            if val[0].strip() != "":
                found_nonblank = True
                break
        if found_nonblank:
            break
        for key, val in char_dict.items():
            char_dict[key] = val[1:]
    return char_dict


def make_font():
    """
    Find the optimal font size based on the
    available screen space.

    Returns:
        A dictionary of characters and their corresponding ASCII
        representations.
    """
    made = make_font_size(100, "8")
    x_factor = COLS / (len(made["8"][0])*4+4)
    y_factor = LINES / len(made["8"])
    factor = min(x_factor, y_factor)
    size = int(factor * 100)-1
    made = make_font_size(size, "8")
    while len(made["8"][0]) * 4 > COLS - 3 or len(made["8"]) > LINES - 3:
        size -= 1
        made = make_font_size(size, "8")
    return make_font_size(size, " 0123456789")


text_font = make_font()
# Max x-shift used to reduce burn-in
ANTI_BURNIN_WIDTH = COLS - 3 - len(text_font["8"][0] * 4)
font_h = len(text_font["8"])
ANTI_BURNIN_HEIGHT = LINES - 1 - font_h
COLON = ["  "] * font_h
COLON[font_h * 1 // 3] = WHITE_CHAR + WHITE_CHAR
COLON[font_h * 2 // 3] = WHITE_CHAR + WHITE_CHAR

# We can run this on old dodgy laptops, but they may have dodgy BIOS clock too.
if datetime.now().year < 2024:
    os.system("ntpdate pool.ntp.org")




def replace_first_char_if_zero(s):
    """
    Replaces the first character of a string with a space if it is a zero.

    Parameters:
        s (str): The input string.

    Returns:
        str: The modified string with the first character replaced by a space if
        it is a zero.
    """
    if s.startswith("0"):
        return " " + s[1:]
    return s


if not os.path.exists("idx"):
    print(
        """idx not found. It is meant to have one FLAC/MP3/OGG etc. per line.
        Run something like:
            locate *.mp3 > idx
        to create it"""
    )
    sys.exit()
lines = []

ffplay = None
playing = ""
voice = None
command = ""


def playable_rating(char):
    """
    Converts the given character to an integer rating and checks if it is
    greater than or equal to the minimum play rating.

    Parameters:
        char (str): A character representing a rating.

    Returns:
        bool: True if rating is at least MINIMUM_PLAY_RATING, False otherwise.
    """
    rating = int(char)
    if rating == 0:
        rating = 10
    return rating >= MIN_PLAY_RATING


def play_music():
    """
    Play music from a list of songs.

    This function reads the songs from the 'idx' file and filters out the songs
    that have a rating less than the minimum play rating. It then shuffles the
    list of songs if the 'SHUFFLE_SONGS' flag is set. The function then plays
    each song in the list, one after the other. If the main thread sets the 'q'
    command, the program exits. If main sets the 'p' command, the previous song
    is played. Otherwise, the next song in the list is played. The volume of the
    music is set to 0.2.

    Parameters:
        None

    Returns:
        None
    """
    global ffplay
    global playing
    global command

    to_play = []
    with open("idx", "r", encoding="utf-8") as file:
        # Read all lines into a list
        # lines = [line.rstrip() for line in file]
        ratings = {}
        if os.path.exists("idx.review"):
            with open("idx.review", "r", encoding="utf-8") as review_file:
                for line in review_file:
                    line = line.rstrip()
                    rating = int(line[0])
                    if rating == 0:
                        rating = 10
                    fname = line[2:]
                    ratings[fname] = rating
        for line in file:
            line = line.rstrip()
            if not line in ratings or ratings[line] >= MIN_PLAY_RATING:
                to_play.append(line)
    if SHUFFLE_SONGS:
        random.shuffle(to_play)
    playing = to_play.pop()
    played = []

    while True:
        with lock:
            #if os.name == 'nt' and not nt_playing:
            #    continue
            if command == "q":  # QUIT
                sys.exit()
            if command == "p":  # Previous
                if played:
                    to_play.append(playing)
                    playing = played.pop()
            else:  # Play next song
                if command != "d":  # Delete Current Song from List
                    played.append(playing)
                if not to_play:
                    if SHUFFLE_SONGS:
                        random.shuffle(played)
                    to_play = played
                    played = []
                playing = to_play.pop()
            command = ""
            ffplay = subprocess.Popen(
                [
                    ffplay_exe,
                    "-nodisp",
                    "-autoexit",
                    "-af",
                    "volume=0.2",
                    playing,
                ],
                shell=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        time.sleep(99)
        if ffplay:
            ffplay.wait()
        

#quitting = False
playing_rot = 0

LOG = open("idx.log", "a", encoding="utf-8")

music_player = None

nt_playing = 0

def sigterm(o):
    o.send_signal(signal.SIGTERM)

if os.name=='nt':
    def sigcont(o):
        pass
    sigkill=sigterm
    sigstop=sigterm
    sigint=sigterm
else:
    def sigint(o):
        o.send_signal(signal.SIGINT)
    def sigkill(o):
        o.send_signal(signal.SIGKILL)
    def sigcont(o):
        o.send_signal(signal.SIGCONT)
    def sigstop(o):
        o.send_signal(signal.SIGSTOP)    
        
def signal_handler(sig, frame):
    """
    Handles the signal received by the program.

    Args:
        sig (signal.Signals): The signal received by the program.
        frame (types.FrameType): The current stack frame.

    Returns:
        None

    This function is called when the program receives a signal.
     It prints a message indicating that the user pressed Ctrl+C.
     It then acquires the lock and sends a SIGINT signal to the
     ffplay and voice processes (if they exist).
     Finally, it exits the program with a status code of 0.

    Note:
        This function should be registered as a signal handler using the
        `signal.signal()` function.

    """
    print("You pressed Ctrl+C!")
    with lock:
        if ffplay:
            sigkill(ffplay)
            ffplay.wait()
        if voice:
            sigkill(voice)
            voice.wait()
    sys.exit(0)


#signal.signal(signal.SIGINT, signal_handler)


def play():
    """
    Starts playing music if the music player is not already running. If the
    music player is already running, it waits for the music player to be
    available before sending a SIGCONT signal to resume playback.

    Parameters:
        None

    Returns:
        None
    """
    global music_player
    if music_player is None:
        music_player = threading.Thread(target=play_music)
        music_player.start()
    else:
        while True:
            getch(0.1)
            with lock:
                if ffplay:
                    sigcont(ffplay)
                    if os.name=='nt':
                       nt_playing=1
                    break


#def pause():
#    with lock:
#        ffplay.send_signal(signal.SIGSTOP)


def verbose(now):
    """
    Returns a string representing the current time in a verbose format.

    Parameters:
        now (datetime): The current datetime object.

    Returns:
        str: A string representing the current time in the format "The time
             is X minutes past Y", where X is the minute of the hour and Y is
             the hour of the day. The minute is printed without the leading
             zero. If the hour is 0, it is replaced with "midnight".
    """
    txt=now.strftime(f"The time is %M minutes past %{AUDIO_H} o'clock")
    return (txt.replace(" 0", " ").replace(" 0 o'clock", " midnight"))


def precache(now):
    """
    Pre-caches the Google Text To Speech (GTTS) MP3 file for the given time.

    This function takes a datetime object `now` as input and generates an
    MP3 file for the given time. The file is saved in the "tts" directory
    with the filename in the format "HHMM.mp3", where HH is the hour of the
    day and MM is the minute of the hour. If the file already exists, it is
    not re-generated.

    Parameters:
        now (datetime): The current datetime object.

    Returns:
        str: The filename of the generated MP3 file.

    Raises:
        Exception: If an error occurs while generating the MP3 file,
        The error message is logged to the "idx.log" file.
    """
    from gtts import gTTS  # Takes 2s to load on my old 32bit machine

    hhmm_ = now.strftime(f"%{AUDIO_H}%M")
    fname = f"tts/{hhmm_}.mp3"
    # print (str)
    if not os.path.exists(fname):
        try:
            myobj = gTTS(text=verbose(now), lang="en", slow=False)
            myobj.save(fname)
        except Exception as e:
            LOG.write(f"{hhmm_}:{verbose(now)} -- {e}\n")
    return fname


tput_cmds = {
    "cup 0 0": "\x1B[1;1H",
    "clear": "\x1B[H\x1B[J\x1B[3J",
    "setaf 0": "\x1B[30m",
    "setaf 1": "\x1B[31m",
    "setaf 2": "\x1B[32m",
    "setaf 3": "\x1B[33m",
    "setaf 4": "\x1B[34m",
    "setaf 5": "\x1B[35m",
    "setaf 6": "\x1B[36m",
    "setaf 7": "\x1B[37m",
}


def tput(cmd):
    """
    Emulates the `tput` terminal control utility command.

    Args:
        cmd (str): The terminal control command to be executed.

    Returns:
        None

    This function retrieves the corresponding terminal control command from the
    `tput_cmds` dictionary and prints it to the standard output.
     The command is printed without a newline character at the end.

    Note:
        The `tput` utility is not called directly in this function.
         Uncomment the line `os.system("tput "+cmd)` to execute the command
         using the `os.system` function.
    """
    print(tput_cmds[cmd], end="")
    # This should be equivalent to:)
    #    os.system("tput "+cmd)


tput(f"setaf {SLEEP_COLOR}")  # Set terminal fg to brown


def setterm_blank(mins):
    """
    Set the terminal blank time to the specified number of minutes. Use
    `setterm_blank(0)` to prevent the terminal from blanking

    Args:
        mins (int): The number of minutes to set the blank time to. Must be
        between 0 and 60.

    Raises:
        SystemExit: If the value of `mins` is not between 0 and 60.

    Returns:
        None

    This function prints the terminal control command to set the blank time to
    the specified number of minutes. The command is printed without a newline
    character at the end.

    Note:
        The `os.system` function is commented out in this function. Uncomment
        the line `os.system (f"setterm -blank {mins}")` to execute the command
        using the `os.system` function.
    """
    if not 0 <= mins <= 60:
        print("mins in setterm(mins) must be in 0..60")
        print("Invalid value {mins} found. Quitting")
        sys.exit()
    print(f"\x1B[9;{mins}]", end="")
    # This should be equivalent to:
    # os.system (f"setterm -blank {mins}")


last_h24 = 9999
alarm = False
indent = random.randint(0, ANTI_BURNIN_WIDTH)
v_indent = random.randint(0, ANTI_BURNIN_HEIGHT)


def alarm_on():
    """
    Turns on the alarm and sets the terminal blank time to 0. Sets the terminal
    foreground color to the WAKE_COLOR (cyan), plays music, and reads out the
    current time every minute.

    Parameters:
        None

    Returns:
        None
    """
    global alarm
    alarm = True
    setterm_blank(0)
    tput(f"setaf {WAKE_COLOR}")  # Set terminal fg to cyan
    if os.name == 'nt':
        with lock:
            nt_playing=1
    play()

snooze_now = None

if not os.path.exists("tts/"):
    os.system("mkdir tts")
if len(sys.argv) > 1:
    if sys.argv[1] == "--precache":
        for hour in range(0, 24):
            for minute in range(0, 60):
                print(precache(datetime(2000, 1, 1, hour, minute)))
    elif sys.argv[1] == "--alarm":
        alarm_on()
    elif sys.argv[1] == "--play":
        play_music()
        sys.exit()
    elif sys.argv[1] == "--snooze":
        snooze_now = datetime.now()

REVIEW = open("idx.review", "a", encoding="utf-8")

tput("clear")
while True:
    tput("cup 0 0")
    loop_now = datetime.now()
    wait = (
        61 - loop_now.second
    )  # Wait until one second past the start of the next minute
    hhmm_ = loop_now.strftime(f"%{VISUAL_H}%M")
    hhmm = replace_first_char_if_zero(hhmm_)
    hour24=int(loop_now.strftime(f"%H%M"))
    if int(hour24) >= ALARM_TIME > last_h24:
        alarm_on()
    lines = []
    for i in range(0, v_indent):
        lines.append(" " * (COLS - 1))
    tf = text_font
    for quad in zip(tf[hhmm[0]], tf[hhmm[1]], COLON, tf[hhmm[2]], tf[hhmm[3]]):
        lines.append(
            (" " * indent + "".join(quad) + " " * (ANTI_BURNIN_WIDTH - indent)).ljust(
                COLS - 1
            )
        )

    while len(lines) < LINES - 2:
        lines.append(" " * (COLS - 1))

    indent += random.randint(0, 1)
    v_indent += random.randint(0, 1)
    if indent > ANTI_BURNIN_WIDTH:
        indent = 0
    if v_indent > ANTI_BURNIN_HEIGHT:
        v_indent = 0

    if snooze_now:
        snooze_in_secs = (SNOOZE_SECS - (loop_now - snooze_now).seconds)
        if snooze_in_secs < 1:
            alarm_on()
            snooze_now = None
        else:
            wait = max(1,snooze_in_secs)
        print(
            (
                " " * indent
                + f"Snoozing for {snooze_in_secs/60:.2f} minutes"
            ).ljust(COLS - 1),
            end="",
        )
    elif not alarm:
        print(" " * (COLS - 1), end="")
    print("\n" + ("\n".join(lines)))
    tput("cup 0 0")
    user_ch = ""
    if alarm:
        fn = precache(loop_now)
        if last_h24 != int(hour24):
            if os.path.exists(fn):
                # It can take a few seconds for audio to start
                # Add adelay so those seconds don't go missing
                if voice:
                    sigint(voice)
                    voice.wait()
                voice = subprocess.Popen(
                    [ffplay_exe, "-nodisp", "-autoexit", "-af", "adelay=3000", fn],
                    shell=False,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            else:
                os.system(f"""printf '%s' "{verbose(loop_now)}" | espeak -a 200""")
        play()
        last_second = loop_now.second
        user_ch = ""
        while not user_ch:
            loop_now = datetime.now()
            if loop_now.second < last_second:
                break
            last_second = loop_now.second
            with lock:
                rot_str = (f"  [{loop_now.second}] " + playing).ljust(COLS - 1)
            if playing_rot > len(rot_str):
                playing_rot = 0
            else:
                playing_rot += 1
            tput("cup 0 0")
            print((rot_str[playing_rot:] + rot_str[0:playing_rot])[0 : COLS - 1])
            user_ch = getch(0.2).lower()
            if user_ch.isdigit():
                REVIEW.write(f"{user_ch} {playing}\n")
                if not playable_rating(user_ch):
                    with lock:
                        command='d' # Don't play again
                        sigint(ffplay)
                        sigcont(ffplay)
                        ffplay.wait()
                user_ch = ""
            elif not user_ch:
                pass
            elif user_ch in "n.>p,<":
                with lock:
                    if user_ch in "p,<":
                        command='p'
                    sigint(ffplay)
                    sigcont(ffplay) 
                    if os.name=='nt':
                        with lock:
                            nt_playing=1  
                    
                    ffplay.wait()
                user_ch = ""

    elif not user_ch:
        user_ch = getch(wait).lower()

    last_h24 = hour24

    if not user_ch:
        continue
    asc = ord(user_ch)
    print(f"Got Ch '{user_ch}' --  '{asc}")


    if user_ch == "q" or asc in [3, 27]:
        print("Quit")
        with lock:
            command = "q"
        if ffplay:
           sigcont(ffplay)
           sigint(ffplay)
           ffplay.wait()
        if voice:
           sigint(voice)
           voice.wait()
        break
    if user_ch in "ws":
        alarm = False
        with lock:
            if ffplay:
                if os.name=='nt':
                    #sigstop(music_player)
                    #music_player=None
                    nt_playing=0
                    sigstop(ffplay)
                    ffplay.wait()
                    ffplay=None
                else:
                    sigstop(ffplay)
        if voice:
            sigint(voice)
            voice.wait()
        setterm_blank(WAKE_BLANK_MINS)  # Let terminal go blank after inactivity
        tput(f"setaf {SLEEP_COLOR}")  # Set terminal fg to brown
        if user_ch == "s":
            snooze_now = datetime.now()
        else:
            snooze_now = None
    elif user_ch == "a":
        alarm_on()
        snooze_now = None
    if user_ch == "h":
        tput("clear")
        print(__doc__)
        getch(None)
