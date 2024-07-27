#Optional Shebang for Linux (Might confuse Windows)
#!/usr/bin/env python3

### CONFIG ###

#Pomodero timer
TIME_WORK=10
TIME_PLAY=2

#Doom Clock
MIN_ORANGE=30
MIN_RED=10

### END CONFIG ###

# Table of Contents:
#   CONFIG (see above: the obvious stuff to change)
#   HELP TEXT
#   IMPORTS AND COMPATIBILITY CODE
#   GUI CODE

HELP_TEXT="""
DTimer was designed to be used as a timer for work,
Specifically for Data Annotation Tech.

Created by: John McCabe-Dansted
Version: 0.3

If you want to work for DAT you can use my referral code:
2ZbHGEA

New in 0.3: Tested and fixed install on Ubuntu
New in 0.2: Basic Linux Support and offers to download missing files
  - What works in Linux may depend on your window manager

--------------------------------------------

Features:
- 3 Clocks:
    * Billable Minutes
    * Doom Clock (Countdown to Deadline)
    * Wall Clock (Current Time)
- Pomodoro (Button turns red when work/play time is up)
- Record Time each Windows spends in the Foreground
    * Recorded as IDLE if the user is away for 1+ minutes

---------------------------------------------

Right Click Menu:
- Copy: Foreground Window Times
- Fix Time: Adjust which window titles are billable
- Doom ^A^C: Copy All Text, Initialize Doom Clock from Clipboard
- Doom Picker: Manually set Deadline
--------------------------------------------
- Restart: Set Billable time etc. to Zero
- Quit: Stop This program
--------------------------------------------
- Help: Show This Help
"""

PAUSE_SYMBOL="\u23F8" # Unicode for pause symbol
RECORD_SYMBOL="\u23FA" # Unicode for record symbol

### BEGIN IMPORTS AND COMPATIBILITY CODE ###

import os, sys, re, shutil
from tkinter import Tk;

def restart():
    os.execv(sys.executable, [sys.executable] + sys.argv)

def replace_last_occurrence(s, old, new):
    # Find the last occurrence of the substring
    pos = s.rfind(old)
    if pos == -1:
        return (-1,s)  # Substring not found, return the original string
    # Replace the last occurrence
    return (pos, s[:pos] + new + s[pos + len(old):])

#Define an 'xterm -e' like command.
#WARNING: It doesn't escape double quotes (")
if os.name=='nt':
    def xterm(cmd, confirm=None):
        c=cmd
        if confirm:
            c="set /p DUMMY=" + re.escape(confirm.replace("\n", " ")) + " & " + c
        c="start /wait cmd /k \"" +\
            c + " && set /p DUMMY=Close this window to continue...\""
        os.system(c)
else:
    def xterm(cmd, confirm=None):
        #print(f"'{cmd}' '{confirm}'")

        #c='( '+cmd+' )'
        #if confirm:
            #c="echo " + confirm.replace("\n", " ").replace("'", "\\'").replace("(", "\\()").replace(")", "\\)") + " && read _ && " + c
        #    c="echo " + confirm.translate(str.maketrans("\n'\"()", "     ")) + " && read _ && " + c
        #First we try to start a new $TERM instance. This is the terminal that
        #the user is using now, maybe it is their default terminal.
        #Failing that we try a bunch of random terminals that might be
        #available (Including a number of ones popular on MacOS although
        #we do not suppport MacOS yet). The first one found will be used.
        #If we do not find a terminal the user has, we just use bash. This
        #doesn't allow us to pop up a new window. However it is an OK
        #workaround for things like WSL that may not have an native terminal.

        #c="`which $TERM xfce4-terminal rxvt foot kitty konsole xterm gnome-terminal eterm urxvt gnome-terminal Alacritty alacritty warp hyper iterm2 terminal bash | head -n 1 | sed 's/bash/bash -c'/` -e \"" +\
        #      c + " ; echo Close this window to continue ; read _\""

        #Nah forget it, just use bash for everything

        if confirm:
            print(confirm)
            print("INSTALL COMMAND:" + cmd)
            print("Press Y[Enter] to install, or any other key to quit")
            if input().lower()!='y':
                quit()
        os.system(cmd)

#Try to import modules, offer to install them if it fails
#TODO: Test these actually work on a fresh install
if os.name != 'nt':
    try:
        import tkinter as tk
        import pynput
    except:
        xterm("sudo apt install python3-tk python3-pynput", "DTimer needs tkinter and pynput to run.")
try:

    import tkinter as tk
    from tkinter import BooleanVar, Checkbutton, font, RIGHT, Menu, messagebox
    from collections import defaultdict
    from datetime import datetime

    ### For Doom Clock ###
    #import pyautogui -> Doesn't work
    import time, ctypes, tktimepicker
    from tktimepicker import AnalogPicker, constants

    from pynput.keyboard import Key, Controller
    from time import sleep

except ImportError as e:
    pips='datetime tktimepicker pynput collection'
    if os.name=='nt':
        pips='pynput tkinter pynput ' + pips
    #else:
    #    pips='contextlib ' + pips
    #pip has a stupid default many packages need an alternative timeout. None of the packages we will install, but lets be safe.
    #guess_conda_path=os.path.expandvars(r"%USERPROFILE%\anaconda3\condabin\conda.bat")
    pip1=os.path.expandvars(r"%USERPROFILE%/anaconda3/Scripts/pip.exe")
    (pos2,pip2)=replace_last_occurrence(sys.executable, 'pythonw', 'pip')
    if pos2<0: (pos2,pip2)=replace_last_occurrence(sys.executable, 'python', 'pip')
    msg = repr(e) + "\nWe need all of the following modules:\n" + pips + ".\n"
    #msg =+ " DTimer will quit if any modules are missing.\n"

    #Conda makes it hard to find packages, just use pip
    pip_cmd=''
    for i in range(2):
        if shutil.which('pip'):   pip_cmd="pip" #was x
        elif shutil.which('pip'):    pip_cmd="pip"
        elif shutil.which('pip3'): pip_cmd="pip3"
        elif pos2 >= 0 and os.path.exists(pip2): pip_cmd=pip2
        elif os.path.exists(pip1): pip_cmd=pip1
        #elif shutil.which('conda'):
        #    pip_cmd="conda install " + pips
        #elif os.path.exists(guess_conda_path):
        #    pip_cmd="{guess_conda_path} install" + pips
        else:
            if os.name!='nt' and shutil.which('apt'):
                pip_cmd="sudo add-apt-repository universe && sudo apt-get update && sudo apt-get install python3-pip"
                msg+="\nPress Enter to install pip now, or close the window to quit."
                xterm(pip_cmd, msg)
                continue

            msg +=  "\nWe cannot find Pip. Please install pip or the modules and try again."
            xterm("echo bye", msg)
            quit()
        break

    if os.name != 'nt':
        if os.system("python3 -m venv ~/.virtualenvs/dtimer.venv")==0:
            pip_cmd = "~/.virtualenvs/dtimer.venv/bin/pip"


    msg +=  f" Press Enter to install now({pip_cmd}), or close the window to quit."

    #pip_cmd=pip_cmd+" --default-timeout=100 install " + pips
    pip_cmd=pip_cmd + " install " + pips

    xterm(pip_cmd, msg)

    #Support installing unifont via curl later
    from tkinter.messagebox import askokcancel, showinfo, WARNING
    import tkinter as tk
    root = tk.Tk()
    root.withdraw()
    install = tk.messagebox.askokcancel(
        title='Restart?',
        message="DTimer will need to restart.\nRestart (or quit)?",
        icon=WARNING)
    if not install:
        quit()
    restart()

if os.name!='nt':
    from tkinter.messagebox import askokcancel, showinfo, WARNING
    import tkinter as tk
    def support_symbol(u):
        return os.system(f"fc-list :charset={u}|grep .")==0

    #record
    if   support_symbol("26AB"): RECORD_SYMBOL="\u26AB" # ⚫︎
    elif support_symbol("23FA"): RECORD_SYMBOL="\u23FA" # ⏺︎
    elif support_symbol("25F9"): RECORD_SYMBOL="\u23F9" # ◉︎
    elif support_symbol("25CF"): RECORD_SYMBOL="\u25CF" # ●︎
    elif support_symbol("25CB"): RECORD_SYMBOL="\u25CB" # ○︎
    else: RECORD_SYMBOL="[O]"

    #pause
    if   support_symbol("23F8"): PAUSE_SYMBOL="\u23F8" # ⚫ “⏸” (U+23F8)
    elif support_symbol("9612"): PAUSE_SYMBOL="\u9612\u9612" #  “▌▌” (U+9612)
    #elif support_symbol("9613"): PAUSE_SYMBOL="\u9613\u9613" # ▍ ▍ - &#9613;
    elif support_symbol("2016"): PAUSE_SYMBOL="\u2016" # ⚫ “‖” (U+2016)
    else: PAUSE_SYMBOL="[||]"

def exec_cmd(cmd_string):
    r = os.popen(cmd_string)
    result_string = r.read()
    r.close()
    return result_string

###### Get Window Title ################
if os.name=='nt':
    from ctypes import wintypes, windll, create_unicode_buffer
    def getForegroundWindowTitle():
        hWnd = windll.user32.GetForegroundWindow()
        length = windll.user32.GetWindowTextLengthW(hWnd)
        buf = create_unicode_buffer(length + 1)
        windll.user32.GetWindowTextW(hWnd, buf, length + 1)
        return buf.value

    user32 = windll.user32
    last_hwnd=user32.GetForegroundWindow(None)
    bad_hwnd=0
    def store_fg(bad=False):
        global last_hwnd, bad_hwnd
        if bad:
            bad_hwnd=user32.GetForegroundWindow(None)
        else:
            hwnd = user32.GetForegroundWindow(None)
            if bad_hwnd!=hwnd:
                last_hwnd=user32.GetForegroundWindow(None)
    def unfocus(tk):
        global last_hwnd
        user32.SetForegroundWindow(last_hwnd)
else:

    def unfocus(tk):
            return
            #On X11 we declare the window as being a dock and the WM will unfocus for us
            root=tk.master
            root.withdraw()
            root.deiconify()
            root.attributes("-topmost", True)

    def store_fg(bad=False):
        return

    #Instead of the next hundred odd lines, we could just do this. But it is not "Efficient"
    #def getForegroundWindowTitle():
    #    return exec_cmd("xdotool getwindowfocus getwindowname")

    from contextlib import contextmanager
    import Xlib
    import Xlib.display

    # Connect to the X server and get the root window
    xldisp = Xlib.display.Display()
    xlroot = xldisp.screen().root

    # Prepare the property names we use so they can be fed into X11 APIs
    NET_ACTIVE_WINDOW = xldisp.intern_atom('_NET_ACTIVE_WINDOW')
    NET_WM_NAME = xldisp.intern_atom('_NET_WM_NAME')  # UTF-8
    WM_NAME = xldisp.intern_atom('WM_NAME')           # Legacy encoding

    last_seen = { 'xid': None, 'title': None }

    @contextmanager
    def window_obj(win_id):
        """Simplify dealing with BadWindow (make it either valid or None)"""
        window_obj = None
        if win_id:
            try:
                window_obj = xldisp.create_resource_object('window', win_id)
            except Xlib.error.XError:
                pass
        yield window_obj

    def get_active_window():
        """Return a (window_obj, focus_has_changed) tuple for the active window."""
        win_id = xlroot.get_full_property(NET_ACTIVE_WINDOW,
                                        Xlib.X.AnyPropertyType).value[0]

        focus_changed = (win_id != last_seen['xid'])
        if focus_changed:
            with window_obj(last_seen['xid']) as old_win:
                if old_win:
                    old_win.change_attributes(event_mask=Xlib.X.NoEventMask)

            last_seen['xid'] = win_id
            with window_obj(win_id) as new_win:
                if new_win:
                    new_win.change_attributes(event_mask=Xlib.X.PropertyChangeMask)

        return win_id, focus_changed

    def _get_window_name_inner(win_obj):
        """Simplify dealing with _NET_WM_NAME (UTF-8) vs. WM_NAME (legacy)"""
        for atom in (NET_WM_NAME, WM_NAME):
            try:
                window_name = win_obj.get_full_property(atom, 0)
            except UnicodeDecodeError:  # Apparently a Debian distro package bug
                title = "<could not decode characters>"
            else:
                if window_name:
                    win_name = window_name.value
                    if isinstance(win_name, bytes):
                        # Apparently COMPOUND_TEXT is so arcane that this is how
                        # tools like xprop deal with receiving it these days
                        win_name = win_name.decode('latin1', 'replace')
                    return win_name
                else:
                    title = "<unnamed window>"

        return "{} (XID: {})".format(title, win_obj.id)

    def get_window_name(win_id):
        """Look up the window name for a given X11 window ID"""
        if not win_id:
            last_seen['title'] = "<no window id>"
            return last_seen['title']

        title_changed = False
        with window_obj(win_id) as wobj:
            if wobj:
                win_title = _get_window_name_inner(wobj)
                title_changed = (win_title != last_seen['title'])
                last_seen['title'] = win_title

        return last_seen['title'], title_changed

    def getForegroundWindowTitle():
        try:
            return (get_window_name(get_active_window()[0])[0])
        except:
            #Doesn't seem to work in LXDE
            return "ERROR"

######### IDLE TIME ##################
if os.name == 'nt':
    from ctypes import Structure, windll, c_uint, sizeof, byref
    class LASTINPUTINFO(Structure):
        _fields_ = [
            ('cbSize', c_uint),
            ('dwTime', c_uint),
        ]

    def get_idle_duration():
        lastInputInfo = LASTINPUTINFO()
        lastInputInfo.cbSize = sizeof(lastInputInfo)
        windll.user32.GetLastInputInfo(byref(lastInputInfo))
        millis = windll.kernel32.GetTickCount() - lastInputInfo.dwTime
        return millis / 1000.0
else:

    class XScreenSaverInfo( ctypes.Structure):
        """ typedef struct { ... } XScreenSaverInfo; """
        _fields_ = [('window',      ctypes.c_ulong), # screen saver window
                    ('state',       ctypes.c_int),   # off,on,disabled
                    ('kind',        ctypes.c_int),   # blanked,internal,external
                    ('since',       ctypes.c_ulong), # milliseconds
                    ('idle',        ctypes.c_ulong), # milliseconds
                    ('event_mask',  ctypes.c_ulong)] # events

    try:
        xlib = ctypes.cdll.LoadLibrary( 'libX11.so')
    except:
        xlib = ctypes.cdll.LoadLibrary( 'libX11.so.6')
    xlib.XOpenDisplay.argtypes = [ctypes.c_char_p]
    xlib.XOpenDisplay.restype = ctypes.c_void_p  # Actually, it's a Display pointer, but since the Display structure definition is not known (nor do we care about it), make it a void pointer

    xlib.XDefaultRootWindow.argtypes = [ctypes.c_void_p]
    xlib.XDefaultRootWindow.restype = ctypes.c_uint32

    xss = ctypes.cdll.LoadLibrary( 'libXss.so.1')
    xss.XScreenSaverQueryInfo.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.POINTER(XScreenSaverInfo)]
    xss.XScreenSaverQueryInfo.restype = ctypes.c_int

    DISPLAY=os.environ['DISPLAY']
    xdpy = xlib.XOpenDisplay(None)
    xroot = xlib.XDefaultRootWindow( xdpy)
    xss.XScreenSaverAllocInfo.restype = ctypes.POINTER(XScreenSaverInfo)
    xss_info = xss.XScreenSaverAllocInfo()
    def get_idle_duration():
        global xss, xroot, xss_info
        xss.XScreenSaverQueryInfo( xdpy, xroot, xss_info)
        millis = xss_info.contents.idle
        #millis = int(exec_cmd("xprintidle"))
        return millis / 1000.0


########### END IDLE TIME ################

### END IMPORTS AND COMPATIBILITY CODE ###


### GUI CODE ###


def copy_all():
    if os.name!='nt':
        #pynput should work in Linux, but it doesn't seem to
        #You may have to play a bit with this to get it to work with your window manager.
        if os.system("sleep 0.1 && xdotool key ctrl+a && sleep 0.1 && xdotool key ctrl+c")==0:
            return
    print("D2")
    kc=Controller()
    def s(): sleep(0.1)
    def p(k):
        print(k)
        s()
        kc.press(k)
    def r(k):
        s()
        kc.release(k)
    p(Key.ctrl_l)
    p('a')
    r('a')
    p('c')
    r('c')
    r(Key.ctrl_l)
    s()

class TimeTrackerApp(tk.Tk):
    def __init__(self, master):
        self.master = master
        self.master.title("Time Tracker")
        self.master.overrideredirect(True)
        if os.name != 'nt':
            self.master.wm_attributes("-type", "dock")

        self.recording = False
        self.last_time = time.time()
        self.toggle_time = self.last_time
        self.doom_time = 0
        self.elapsed_time = 0

        ft = font.Font(family='Arial', size=16)
        self.button = tk.Button(master, text=RECORD_SYMBOL, font=ft, command=self.toggle_recording)
        self.button.pack(side=RIGHT)

        ft = font.Font(family='Arial', size=16)
        self.time_label = tk.Label(master, text="00:00:00", font=ft)
        self.time_label.pack(padx=1,pady=0,side=tk.TOP)

        tl_h=self.time_label.winfo_height()
        ft = font.Font(family='Arial', size=9)
        self.doom_label = tk.Label(master, text="00:00:00", font=ft)
        self.doom_label.pack(padx=1,pady=0,side=tk.LEFT)
        self.doom_label.place(x=0,y=24)
        self.wall_clock = tk.Label(master, text="00:00", font=ft)
        self.wall_clock.place(x=53,y=24)

        self.title_times = defaultdict(float)
        self.pause_times = defaultdict(float)

        self.master.bind("<ButtonPress-1>", self.start_move)
        self.master.bind("<ButtonRelease-1>", self.stop_move)
        self.master.bind("<B1-Motion>", self.do_move)
        self.master.bind("<Button-3>", self.do_popup)

        m = Menu(root, tearoff=0)
        m.add_command(label="Copy", command=self.do_copy)
        m.add_command(label="Fix Time", command=self.fix_time)
        m.add_command(label="Doom ^A^C", command=self.do_doom)
        m.add_command(label="Doom Picker", command=self.get_time)
        m.add_separator()
        m.add_command(label="Restart", command=restart)
        m.add_command(label="Quit", command=self.master.destroy)
        m.add_separator()
        m.add_command(label="Help", command=self.do_help)
        self.popup_menu = m

        self.update_time()

        self.master.after(1, lambda: store_fg(bad=True)) #store_fg(bad=True)
        self.master.after(10, lambda: unfocus(self))

    def do_about(self):
        tk.messagebox.showinfo(
            title="About DTimer",
            message=ABOUT_TEXT)

    def do_help(self):
        tk.messagebox.showinfo(
            title="DTimer HELP",
            message=HELP_TEXT)

    def updateTime(self,t):
        (a,b,c)=t
        self.doom_time=time.time()+a*3600+b*60

    def get_time(self):
        root=self.master
        top = tk.Toplevel(root)
        top.title("Set Deadline")

        time_picker = AnalogPicker(top, type=constants.HOURS24)
        time_picker.setHours(1)
        time_picker.setMinutes(0)
        time_picker.pack(expand=True, fill="both")
        ok_btn = tk.Button(top, text="Set Doom Clock", command=lambda: self.updateTime(time_picker.time()))
        ok_btn.pack()

    def fix_time(self):

        top = tk.Toplevel(self.master)
        top.title('Fix Billable Time')

        def add(key,value,default,prefix=""):
             self.category_values.append(BooleanVar())
             self.category_values[-1].set(default)
             m=value/60
             self.category_mins.append(m)
             l=Checkbutton(top, text=f"{prefix} {key} ({m:.2f})", variable=self.category_values[-1], command=lambda: self.fix_time_recalc())
             l.pack(anchor=tk.W)
        self.category_values = []
        self.category_mins = []
        for k, v in self.title_times.items(): add(k,v,1,RECORD_SYMBOL)
        for k, v in self.pause_times.items(): add(k,v,0,PAUSE_SYMBOL)

        self.fix_time_label=tk.Label(top, text="")
        self.fix_time_recalc()
        self.fix_time_label.pack(anchor=tk.W)


    def fix_time_recalc(self):
        t=0
        for i in range(len(self.category_mins)):
            t+=self.category_values[i].get()*self.category_mins[i]
        self.fix_time_label.config(text=f"Minutes: {t:.2f}")


    def do_doom(self):
        r=re.compile(r".*\nExpires in: (\d+) hours? (\d+) minutes?\n[$]\d.*",re.MULTILINE|re.DOTALL)
        print("D1")
        unfocus(self)
        copy_all()
        s=self.master.clipboard_get()
        print(s)
        m=r.match(s)
        if m:
            h,m=m.groups()
            self.doom_time=time.time()+int(h)*3600+int(m)*60

    def do_copy(self):
        s=''
        for key,value in self.title_times.items():
            min=value/60
            s+=f"+\t{min:7.3f}\t{key}\n"
        for key,value in self.pause_times.items():
            min=value/60
            s+=f"P\t{min:7.3f}\t{key}\n"
        self.master.clipboard_clear()
        self.master.clipboard_append(s)

    def do_popup(self, event):
        m=self.popup_menu
        try:
            m.tk_popup(event.x_root, event.y_root)
        finally:
            m.grab_release()
        #unfocus(self)

    def start_move(self, event):
        store_fg(bad=True)
        self.x = event.x
        self.y = event.y

    def stop_move(self, event):
        self.x = None
        self.y = None
        unfocus(self)

    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.master.winfo_x() + deltax
        y = self.master.winfo_y() + deltay
        self.master.geometry(f"+{x}+{y}")


    def toggle_recording(self):
        store_fg(bad=True)
        self.update_time()
        self.toggle_time=time.time()
        self.recording = not self.recording
        if self.recording:
            self.button.config(text=PAUSE_SYMBOL)
        else:
            self.button.config(text=RECORD_SYMBOL)
        unfocus(self)

    def time2str(self,secs):
        minutes, seconds = divmod(secs, 60)
        hours, minutes = divmod(minutes, 60)
        return "%02d:%02d:%02d" % (hours, minutes, seconds)

    def update_time(self):
        from datetime import datetime
        dt = datetime.now()
        self.wall_clock.config(text=dt.strftime("%H:%M"))

        store_fg()

        ctime=dt.timestamp()

        addtime = ctime - self.last_time
        window = getForegroundWindowTitle()
        title = window if window else "NONE"

        fg='green'
        if self.doom_time > ctime:
            self.doom_label.config(text=self.time2str(self.doom_time-ctime))
            mins=(self.doom_time - ctime)/60
            if mins < MIN_ORANGE:
                fg='orange'
                if mins < MIN_RED:
                    fg='red'
        else:
            self.doom_label.config(text="00:00:00")
        self.doom_label.config(fg=fg)
        if get_idle_duration() > 60:
            title = "IDLE"

        if self.recording:
            wanted_mins=TIME_WORK
            self.elapsed_time += addtime
            self.title_times[title] += addtime
            minutes, seconds = divmod(self.elapsed_time, 60)
            hours, minutes = divmod(minutes, 60)
            self.time_label.config(text=self.time2str(self.elapsed_time))
        else:
            wanted_mins=TIME_PLAY
            self.pause_times[title] += addtime
        period_mins=(ctime-self.toggle_time)/60
        if wanted_mins>period_mins:
            bg='lightgrey'
        else:
            bg='red'
        if TIME_WORK*TIME_PLAY:
            self.button.configure(bg=bg)

        self.master.after(1000, self.update_time)  # Update every 1000 milliseconds
        self.last_time = ctime

root = tk.Tk()
app = TimeTrackerApp(root)
root.call('wm', 'attributes', '.', '-topmost', '1')
root.mainloop()