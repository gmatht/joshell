#Optional Shebang for Linux
#!/usr/bin/env python3

### CONFIG ###
#Pomodero timer
TIME_WORK=10
TIME_PLAY=2
#Doom Clock
MIN_ORANGE=30
MIN_RED=10
### END CONFIG ###

ABOUT_TEXT="""
- About: Show About
"""

HELP_TEXT="""
DTimer was designed to be used as a timer for work,
Specifically for Data Annotation Tech.

Created by: John McCabe-Dansted
Version: 0.1

If you want to work for DAT you can use my referral code:
2ZbHGEA

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
- Doom Picker: Manually set time to Deadline
--------------------------------------------
- Restart: Set Billable time etc. to Zero
- Quit: Stop This program
--------------------------------------------
- Help: Show This Help
"""

PAUSE_SYMBOL="\u23F8" # Unicode for pause symbol
RECORD_SYMBOL="\u23FA" # Unicode for record symbol

import re
import sys
import tkinter as tk
from tkinter import BooleanVar, Checkbutton, font, RIGHT, Menu, messagebox
import time
from collections import defaultdict
import platform
import os
from datetime import datetime

### For Doom Clock ###
#import pyautogui
import tktimepicker
from tktimepicker import AnalogPicker, constants



from pynput.keyboard import Key, Controller
from time import sleep

from ctypes import windll




def copy_all():
    kc=Controller()
    def s(): sleep(0.1)
    def p(k):
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

def exec_cmd(cmd_string):
    r = os.popen(cmd_string)
    result_string = r.read()
    r.close()
    return result_string

###### Get Window Title ################
if platform.system() == 'Windows':
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
    def getForegroundWindowTitle():
        return exec_cmd("xdotool getwindowfocus getwindowname")
    def unfocus(tk):
            root=tk.master
            root.withdraw()
            root.deiconify()
            root.attributes("-topmost", True)

    def store_fg():
        return

######### IDLE TIME ##################
if platform.system() == 'Windows':
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


    def get_idle_duration():
        millis = int(exec_cmd("xprintidle"))
        os.system('clear')
        return millis / 1000.0

########### END IDLE TIME ################

class TimeTrackerApp(tk.Tk):
    def __init__(self, master):
        self.master = master
        self.master.title("Time Tracker")
        self.master.overrideredirect(True)

        self.recording = False
        self.last_time = time.time()
        self.toggle_time = self.last_time
        self.doom_time = 0
        self.elapsed_time = 0

        ft = font.Font(family='Arial', size=16)
        #pause_symbol = "\u23FA"  # Unicode for record symbol
        self.button = tk.Button(master, text=RECORD_SYMBOL, font=ft, command=self.toggle_recording)
        self.button.pack(side=RIGHT)

        self.time_label = tk.Label(master, text="00:00:00", font=ft)
        self.time_label.pack(padx=1,pady=0,side=tk.TOP)

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
        #m.add_command(label="Reload")
        m.add_separator()
        m.add_command(label="Restart", command=self.do_restart)
        m.add_command(label="Quit", command=self.master.destroy)
        m.add_separator()
        m.add_command(label="Help", command=self.do_help)
        #m.add_command(label="About", command=self.do_about)
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
        copy_all()
        s=self.master.clipboard_get()
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

    def do_restart(self):
        self.elapsed_time = 0
        self.title_times = defaultdict(float)
        self.pause_times = defaultdict(float)
        self.time_label.config(text="00:00:00")

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