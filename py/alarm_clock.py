#!/bin/env python3
from datetime import datetime
import os
import sys
import random
import select
import tty
import termios
import pygame


ALARM_TIME=730 # 7:30am
BLUE_BLOCK_TIME=1700 # 5:00pm
ANTI_BURNIN_WIDTH=9 # Max x-shift used to reduce burn-in
LINES=113 #tput lines
COLS=34   #tput cols
COLS=113
LINES=34
WHITE_CHAR='\u2588'

#To list possible colours
#for i in `seq 0 7`; do tput setaf $i ; echo $i ; done
SLEEP_COLOR=3 #Sleepy Brown
WAKE_COLOR=6  #Energetic Cyan

class _GetchUnix:
    """This code snippet defines a `__call__` method that takes an optional
    argument `wait_seconds` with a default value of 0.1.

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

    def __call__(self, wait_seconds=0.1):
        fd = sys.stdin.fileno()

        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            r, w, e = select.select([ fd ], [], [], wait_seconds)
            if fd in r:
                ch = sys.stdin.read(1)
            else:
                ch = ''
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


def make_text_font():
    """
    Generates a dictionary of characters and their corresponding ASCII representations.

    This function iterates over a set of characters and generates a dictionary where each
    character is mapped to its corresponding ASCII representation. The characters are
    obtained from the string " :0123456789". For each character, a font is created using
    the "Loma.ttf" font file with a size of 44. The character is then rendered onto a
    black image using the white font. The resulting image is converted to a numpy array
    and the pixels are mapped to either a space (' ') or a hash ('#'). The resulting
    characters are then flattened into a list of lines and stored in the dictionary.

    The function trips the top of the characters until a non-blank character is found.
    If a non-blank character is found, the function prints the dictionary and exits.

    If you want to add more characters, simply add them to the string " :0123456789".

    Returns:
        None
    """
    from PIL import Image, ImageDraw, ImageFont
    import numpy as np

    char_dict={}
    for char in " 0123456789":
        myfont = ImageFont.truetype("Loma.ttf", 44)
        size = myfont.getbbox(char)[2:]
        img = Image.new("1",size,"black")
        draw = ImageDraw.Draw(img)
        draw.text((0, 0), char, "white", font=myfont)
        pixels = np.array(img, dtype=np.uint8)
        #white_char='\u2588'
        chars = np.array([' ','#'], dtype="U1")[pixels]
        #chars = np.array([' ','#'], dtype="U1")[pixels]
        strings = chars.view('U' + str(chars.shape[1])).flatten()
        char_dict[char]=[str(x) for x in strings] #.join(strings)
    found_nonblank = False
    while True:
        for key, val in char_dict.items():
            #print(val[0])
            if val[0].strip()!='':
                found_nonblank = True
                break
        if found_nonblank:
            break
        for key, val in char_dict.items():
            char_dict[key]=val[1:]
    print(f"text_font={char_dict}".replace(",",",\n").replace("[","[\n "))
    sys.exit()

text_font={' ': [
 '               ',
 '               ',
 '               ',
 '               ',
 '               ',
 '               ',
 '               ',
 '               ',
 '               ',
 '               ',
 '               ',
 '               ',
 '               ',
 '               ',
 '               ',
 '               ',
 '               ',
 '               ',
 '               ',
 '               ',
 '               ',
 '               ',
 '               ',
 '               ',
 '               ',
 '               ',
 '               ',
 '               ',
 '               ',
 '               ',
 '               '],
 '0': [
 '         ######         ',
 '       ##########       ',
 '      ############      ',
 '     ##############     ',
 '    ######    ######    ',
 '    ####       #####    ',
 '   #####        #####   ',
 '   ####          ####   ',
 '   ####          ####   ',
 '  #####          #####  ',
 '  ####            ####  ',
 '  ####            ####  ',
 '  ####            ####  ',
 '  ####            ####  ',
 '  ####            ####  ',
 '  ####            ####  ',
 '  ####            ####  ',
 '  ####            ####  ',
 '  ####            ####  ',
 '  ####            ####  ',
 '  ####            ####  ',
 '  #####          #####  ',
 '   ####          ####   ',
 '   ####          ####   ',
 '   #####        #####   ',
 '    #####      #####    ',
 '    ######    ######    ',
 '     ##############     ',
 '      ############      ',
 '       ##########       ',
 '         ######         '],
 '1': [
 '             ####       ',
 '            #####       ',
 '            #####       ',
 '           ######       ',
 '          #######       ',
 '         ########       ',
 '        #########       ',
 '      ###########       ',
 '     ####### ####       ',
 '     ######  ####       ',
 '     ####    ####       ',
 '     ##      ####       ',
 '             ####       ',
 '             ####       ',
 '             ####       ',
 '             ####       ',
 '             ####       ',
 '             ####       ',
 '             ####       ',
 '             ####       ',
 '             ####       ',
 '             ####       ',
 '             ####       ',
 '             ####       ',
 '             ####       ',
 '             ####       ',
 '             ####       ',
 '             ####       ',
 '             ####       ',
 '             ####       ',
 '             ####       '],
 '2': [
 '         #######        ',
 '      ############      ',
 '     ##############     ',
 '    ################    ',
 '   ######      ######   ',
 '   ####          ####   ',
 '  #####          #####  ',
 '  ####            ####  ',
 '  ####            ####  ',
 '                  ####  ',
 '                  ####  ',
 '                 #####  ',
 '                 ####   ',
 '                #####   ',
 '               #####    ',
 '              #####     ',
 '             #####      ',
 '           ######       ',
 '          ######        ',
 '         ######         ',
 '        #####           ',
 '       #####            ',
 '      #####             ',
 '     #####              ',
 '     ####               ',
 '    ####                ',
 '   ####                 ',
 '   ###################  ',
 '  ####################  ',
 '  ####################  ',
 '  ####################  '],
 '3': [
 '        #######         ',
 '      ###########       ',
 '     #############      ',
 '    ###############     ',
 '   ######     ######    ',
 '   #####        #####   ',
 '  #####          ####   ',
 '  ####           ####   ',
 '  ####           ####   ',
 '                 ####   ',
 '                ####    ',
 '              ######    ',
 '         ##########     ',
 '         ########       ',
 '         ##########     ',
 '         ############   ',
 '               #######  ',
 '                 #####  ',
 '                  ##### ',
 '                   #### ',
 '                   #### ',
 '                   #### ',
 '  ####             #### ',
 '  ####            ##### ',
 '  #####           ####  ',
 '   #####         #####  ',
 '   ######      ######   ',
 '    #################   ',
 '     ##############     ',
 '      ############      ',
 '        #######         '],
 '4': [
 '              ####      ',
 '             #####      ',
 '             #####      ',
 '            ######      ',
 '           #######      ',
 '           #######      ',
 '          ########      ',
 '         #########      ',
 '         #########      ',
 '        ##### ####      ',
 '       #####  ####      ',
 '       #####  ####      ',
 '      #####   ####      ',
 '     #####    ####      ',
 '     #####    ####      ',
 '    #####     ####      ',
 '   #####      ####      ',
 '   ####       ####      ',
 '  #####       ####      ',
 ' #####        ####      ',
 ' #####################  ',
 ' #####################  ',
 ' #####################  ',
 ' #####################  ',
 '              ####      ',
 '              ####      ',
 '              ####      ',
 '              ####      ',
 '              ####      ',
 '              ####      ',
 '              ####      '],
 '5': [
 '      ###############   ',
 '      ###############   ',
 '     ################   ',
 '     ################   ',
 '     ####               ',
 '     ####               ',
 '     ####               ',
 '    #####               ',
 '    ####                ',
 '    ####  ######        ',
 '    #### #########      ',
 '    ################    ',
 '    #################   ',
 '   #######     ######   ',
 '   #####         #####  ',
 '    ###           ####  ',
 '                  ##### ',
 '                   #### ',
 '                   #### ',
 '                   #### ',
 '                   #### ',
 '                   #### ',
 '  ####             #### ',
 '  ####            ####  ',
 '  #####           ####  ',
 '   #####         #####  ',
 '   ######      ######   ',
 '    ################    ',
 '     ##############     ',
 '      ############      ',
 '         ######         '],
 '6': [
 '          ######        ',
 '       ###########      ',
 '      ##############    ',
 '     ###############    ',
 '    ######     ######   ',
 '    #####        #####  ',
 '   #####         #####  ',
 '   ####           ####  ',
 '   ####                 ',
 '   ###                  ',
 '  ####    ######        ',
 '  ####  ##########      ',
 '  #### #############    ',
 '  ###################   ',
 '  ########     ######   ',
 '  #######        #####  ',
 '  ######          ####  ',
 '  #####           ##### ',
 '  #####            #### ',
 '  #####            #### ',
 '  #####            #### ',
 '  #####            #### ',
 '   ####            #### ',
 '   ####           ##### ',
 '   #####          ####  ',
 '    #####        #####  ',
 '    ######     ######   ',
 '     ###############    ',
 '      ##############    ',
 '       ###########      ',
 '         #######        '],
 '7': [
 '   ###################  ',
 '   ###################  ',
 '   ###################  ',
 '   ###################  ',
 '                #####   ',
 '                #####   ',
 '               #####    ',
 '              #####     ',
 '              #####     ',
 '             #####      ',
 '             ####       ',
 '            #####       ',
 '            ####        ',
 '           #####        ',
 '           ####         ',
 '          #####         ',
 '          ####          ',
 '          ####          ',
 '         ####           ',
 '         ####           ',
 '         ####           ',
 '        ####            ',
 '        ####            ',
 '        ####            ',
 '        ####            ',
 '       ####             ',
 '       ####             ',
 '       ####             ',
 '       ####             ',
 '       ####             ',
 '       ####             '],
 '8': [
 '         #######        ',
 '       ###########      ',
 '     ###############    ',
 '    #################   ',
 '    ######     ######   ',
 '   #####         #####  ',
 '   ####           ####  ',
 '   ####           ####  ',
 '   ####           ####  ',
 '   ####           ####  ',
 '    ####         ####   ',
 '    ######     ######   ',
 '     ###############    ',
 '       ###########      ',
 '      #############     ',
 '    #################   ',
 '   ######      ######   ',
 '   #####         #####  ',
 '  #####           ##### ',
 '  ####             #### ',
 '  ####             #### ',
 '  ####             #### ',
 '  ####             #### ',
 '  ####             #### ',
 '  #####           ##### ',
 '   #####         #####  ',
 '   #######      ######  ',
 '    #################   ',
 '     ###############    ',
 '       ############     ',
 '         #######        '],
 '9': [
 '         #######        ',
 '       ###########      ',
 '     ##############     ',
 '    ################    ',
 '    ######     ######   ',
 '   #####        #####   ',
 '   ####          #####  ',
 '  #####           ####  ',
 '  ####            ####  ',
 '  ####            ##### ',
 '  ####            ##### ',
 '  ####            ##### ',
 '  ####            ##### ',
 '  #####           ##### ',
 '   ####          ###### ',
 '   #####        ####### ',
 '    ######     ######## ',
 '    ################### ',
 '     ############# #### ',
 '       ##########  #### ',
 '         ######    #### ',
 '                   ###  ',
 '                  ####  ',
 '   ####           ####  ',
 '   #####         ####   ',
 '   #####         ####   ',
 '    ######     #####    ',
 '    ################    ',
 '     ##############     ',
 '       ###########      ',
 '         #######        ']}


for key,val in text_font.items():
    text_font[key]=[line.replace("#",WHITE_CHAR) for line in val]

#We can run this on old dodgy laptops, but they may have dodgy BIOS clock too.
if datetime.now().year < 2024:
    os.system('ntpdate pool.ntp.org')

pygame.init()

getch=_GetchUnix()
#def getch(timeout):
    #result = subprocess.run(['bash', '-c', f'read -s -n 1 -t {timeout} key; printf "%s" "$key"'], capture_output=True, text=True)
    #return result.stdout
def replace_first_char_if_zero(s):
    """
    Replaces the first character of a string with a space if it is a zero.

    Parameters:
        s (str): The input string.

    Returns:
        str: The modified string with the first character replaced by a space if it is a zero.
    """
    if s.startswith('0'):
        return ' ' + s[1:]
    return s
if not os.path.exists('idx'):
    print("""idx not found. It is meant to have one FLAC/MP3/OGG etc. per line. Run something like:
    locate *.mp3 > idx
to create it""")
    sys.exit()
lines=[]
with open('idx', 'r', encoding='utf-8') as file:
    # Read all lines into a list
    #lines = [line.rstrip() for line in file]
    ratings={}
    if os.path.exists('idx.review'):
        with open('idx.review', 'r', encoding='utf-8') as review_file:
            for line in review_file:
                line = line.rstrip()
                rating=int(line[0])
                if rating==0:
                    rating=10
                fname=line[2:]
                ratings[fname]=rating
    for line in file:
        line = line.rstrip()
        if not line in ratings or ratings[line]>3:
            lines.append(line)
i=0
idx={}
for line in lines:
    idx[i]=line
    i=i+1
VOICE=pygame.mixer.Channel(0)
MUSIC=pygame.mixer.Channel(1)

playing=""
playing_rot=0
MUSIC.set_volume(0.2)

LOG=open("banner.log", "a", encoding="utf-8");

def play():
    """
    Plays a random sound from the `idx` dictionary using the `MUSIC` channel.

    This function selects a random sound file from the `idx` dictionary and attempts to play it using the `MUSIC` channel. If an exception occurs during the playback, the error message is logged to the `LOG` file.

    Parameters:
        None

    Returns:
        None
    """
    global playing
    choice=random.choice(idx)
    try:
        MUSIC.play(pygame.mixer.Sound(choice))
        playing=choice
    except Exception as e:
        LOG.write(f"{choice} -- {e}\n")
#def queue():
#    choice=random.choice(idx)
#    try:
#        MUSIC.queue(pygame.mixer.Sound(choice))
#    except Exception as e:
#        os.system(f"printf '%s' '{choice} -- {e}' >> banner.log")

def verbose(now):
    """
    Returns a string representing the current time in a verbose format.

    Parameters:
        now (datetime): The current datetime object.

    Returns:
        str: A string representing the current time in the format "The time is X minutes past Y", where X is the minute of the hour and Y is the hour of the day. If the minute is 0, it is replaced with a space. If the hour is 0, it is replaced with "midnight".
    """
    verbose=now.strftime("The time is %M minutes past %H o'clock")
    verbose=verbose.replace(" 0"," ")
    verbose=verbose.replace(" 0 o'clock"," midnight")
    return verbose

def precache(now):
    """
    Pre-caches the Google Text To Speech (GTTS) MP3 file for the given time.

    This function takes a datetime object `now` as input and generates an MP3 file for the given time. The file is saved in the "tts" directory with the filename in the format "HHMM.mp3", where HH is the hour of the day and MM is the minute of the hour. If the file already exists, it is not re-generated.

    Parameters:
        now (datetime): The current datetime object.

    Returns:
        str: The filename of the generated MP3 file.

    Raises:
        Exception: If an error occurs while generating the MP3 file. The error message is logged to the "idx.log" file.
    """
    from gtts import gTTS # Takes 2s to load on my old 32bit machine
    hhmm_=now.strftime("%H%M")
    fname=f"tts/{hhmm_}.mp3"
    #print (str)
    if not os.path.exists(fname):
        try:
            myobj = gTTS(text=verbose(now), lang='en', slow=False)
            myobj.save(fname)
        except Exception as e:
            os.system(f"printf '%s' '{hhmm_}:{verbose(now)} -- {e}' >> idx.log")
    return fname

tput_cmds={"cup 0 0": "[1;1H",
            "clear": "[H[J[3J",
            'setaf 0': '[30m',
            'setaf 1': '[31m',
            'setaf 2': '[32m',
            'setaf 3': '[33m',
            'setaf 4': '[34m',
            'setaf 5': '[35m',
            'setaf 6': '[36m',
            'setaf 7': '[37m'
}
def tput(cmd):
    """
    Emulates the `tput` terminal control utility command.

    Args:
        cmd (str): The terminal control command to be executed.

    Returns:
        None

    This function retrieves the corresponding terminal control command from the `tput_cmds` dictionary and prints it to the standard output. The command is printed without a newline character at the end.

    Note:
        The `tput` utility is not called directly in this function. Uncomment the line `os.system("tput "+cmd)` to execute the command using the `os.system` function.
    """
    print(tput_cmds[cmd],end='')
    #    os.system("tput "+cmd)
tput (f'setaf {SLEEP_COLOR}') # Set terminal fg to brown


def setterm_blank(mins):
    """
    Set the terminal blank time to the specified number of minutes.
    Use `setterm_blank(0)` to prevent the terminal from blanking

    Args:
        mins (int): The number of minutes to set the blank time to. Must be between 0 and 60.

    Raises:
        SystemExit: If the value of `mins` is not between 0 and 60.

    Returns:
        None

    This function prints the terminal control command to set the blank time to the specified number of minutes. The command is printed without a newline character at the end.

    Note:
        The `os.system` function is commented out in this function. Uncomment the line `os.system (f"setterm -blank {mins}")` to execute the command using the `os.system` function.
    """
    if mins < 0 or mins > 60:
        print("mins in setterm(mins) must be in 0..60")
        print("Invalid value {mins} found. Quitting")
        sys.exit()
    print(f"[9;{mins}]",end='')
    #os.system (f"setterm -blank {mins}")

last_hh='9999'
alarm=False
indent=9

def alarm_on():
    """
    Turns on the alarm and sets the terminal blank time to 0.
    Sets the terminal foreground color to the WAKE_COLOR (cyan), plays music,
    and reads out the current time every minute.

    Parameters:
        None

    Returns:
        None
    """
    global alarm
    alarm=True
    setterm_blank(0)
    tput(f'setaf {WAKE_COLOR}') # Set terminal fg to cyan
    play()

if not os.path.exists("tts/"):
    os.system("mkdir tts")
if len(sys.argv)>1:
    if sys.argv[1]=="--precache":
        for hour in range(0,24):
            for minute in range(0,60):
                print(
                    precache(datetime(2000,1,1,hour,minute))
                )
    elif sys.argv[1]=="--alarm":
        alarm_on()
    elif sys.argv[1]=="--make_text_font" or sys.argv[1]=="--make_font":
        make_text_font()

REVIEW=open("idx.review", "a", encoding="utf-8")

tput('clear')
while True:
    tput("cup 0 0")
    now = datetime.now()
    wait = 61 - now.second # Wait until one second past the start of the next minute
    hhmm_=now.strftime("%H%M")
    hhmm=replace_first_char_if_zero(hhmm_)
    if int(last_hh) < ALARM_TIME and int(hhmm) >= ALARM_TIME:
        alarm_on()
    if int(last_hh) < BLUE_BLOCK_TIME and int(hhmm) >= BLUE_BLOCK_TIME:
        tput(f'setaf {SLEEP_COLOR}') # Set terminal fg to brown
    last_hh=hhmm
    lines = []
    for tuple in zip(text_font[hhmm[0]],text_font[hhmm[1]],text_font[hhmm[2]],text_font[hhmm[3]]):
        lines.append((' '*indent + ''.join(tuple) + ' '*(ANTI_BURNIN_WIDTH-indent)).ljust(COLS-1) )

    while len(lines)<LINES-2:
        lines.append(' '*(COLS-1))

    indent += random.randint(0,1)
    if indent > ANTI_BURNIN_WIDTH:
        indent = 0
    #print()
    print(playing.ljust(COLS-1)+"\n"+("\n".join(lines)))
    tput("cup 0 0")
    user_ch=""
    if alarm:
        MUSIC.pause()
        fn=precache(now)
        if os.path.exists(fn):
            VOICE.play(pygame.mixer.Sound(fn))
        else:
            os.system(f"printf '%s' '{verbose(now)}' | espeak -a 200")
        user_ch=getch(4).lower()
        MUSIC.unpause()
        last_second=now.second
        while not user_ch:
            now=datetime.now()
            if now.second < last_second:
                break
            last_second=now.second
            if not MUSIC.get_busy():
                play()
            else:
                rot_str=(f"  [{now.second}] "+playing).ljust(COLS-1)
                if playing_rot>len(rot_str):
                    playing_rot=0
                else:
                    playing_rot+=1
                tput("cup 0 0")
                print((rot_str[playing_rot:]+rot_str[0:playing_rot])[0:COLS-1])
            user_ch=getch(0.25).lower()
            if user_ch.isdigit():
                REVIEW.write(f"{user_ch} {playing}\n")
                if user_ch < '6':
                    play()
                user_ch=''
    elif not user_ch:
        user_ch=getch(wait).lower()

    print(f"Got Ch '{user_ch}'")
    if user_ch == 'q':
        print("Quit")
        break
    elif user_ch == 'w':
        alarm=False
        for i in [0, 1]:
            pygame.mixer.Channel(i).stop()
        setterm_blank(5)
        tput(f'setaf {SLEEP_COLOR}') # Set terminal fg to brown
    elif user_ch == 'a':
        alarm_on()
