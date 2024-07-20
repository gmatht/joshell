import tkinter as tk
from tkinter import font, LEFT, RIGHT, Menu
import time
from collections import defaultdict
import platform
import os

### CONFIG ###
TIME_WORK=10
TIME_PLAY=2


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
else:
    def getForegroundWindowTitle():
        return exec_cmd("xdotool getwindowfocus getwindowname")

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
        self.elapsed_time = 0

        ft = font.Font(family='Arial', size=16)
        self.time_label = tk.Label(master, text="00:00:00", font=ft)
        self.time_label.pack(padx=1,side=LEFT)

        pause_symbol = "\u23FA"  # Unicode for record symbol
        self.button = tk.Button(master, text=pause_symbol, font=ft, command=self.toggle_recording)
        self.button.pack(side=RIGHT)
        self.title_times = defaultdict(float)
        self.pause_times = defaultdict(float)

        self.time_label.bind("<ButtonPress-1>", self.start_move)
        self.time_label.bind("<ButtonRelease-1>", self.stop_move)
        self.time_label.bind("<B1-Motion>", self.do_move)
        self.time_label.bind("<Button-3>", self.do_popup)

        m = Menu(root, tearoff=0)
        m.add_command(label="Copy", command=self.do_copy)
        #m.add_command(label="Reload")
        m.add_separator()
        m.add_command(label="Restart", command=self.do_restart)
        m.add_command(label="Quit", command=self.master.destroy)
        self.popup_menu = m

        self.update_time()
        #self.floater = FloatingWindow(self)

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

    def do_popup(self, event):
        m=self.popup_menu
        try:
            m.tk_popup(event.x_root, event.y_root)
        finally:
            m.grab_release()
    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def stop_move(self, event):
        self.x = None
        self.y = None

    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.master.winfo_x() + deltax
        y = self.master.winfo_y() + deltay
        self.master.geometry(f"+{x}+{y}")


    def toggle_recording(self):
        self.update_time()
        self.toggle_time=time.time()
        self.recording = not self.recording
        if self.recording:
            self.button.config(text="\u23F8")  # Unicode for pause symbol
        else:
            self.button.config(text="\u23FA")  # Unicode for record symbol

    def update_time(self):
        ctime=time.time()
        addtime = ctime - self.last_time
        window = getForegroundWindowTitle()
        title = window if window else "NONE"

        if get_idle_duration() > 60:
            title = "IDLE"
        if self.recording:
            wanted_mins=TIME_WORK
            self.elapsed_time += addtime
            self.title_times[title] += addtime
            minutes, seconds = divmod(self.elapsed_time, 60)
            hours, minutes = divmod(minutes, 60)
            self.time_label.config(text="%02d:%02d:%02d" % (hours, minutes, seconds))
        else:
            wanted_mins=TIME_PLAY
            self.pause_times[title] += addtime
        period_mins=(ctime-self.toggle_time)/60
        if wanted_mins>period_mins:
            bg='lightgrey'
        else:
            bg='red'
        if TIME_WORK*TIME_PLAY:
            self.master.configure(bg=bg)

        self.master.after(1000, self.update_time)  # Update every 1000 milliseconds
        self.last_time = ctime

root = tk.Tk()
app = TimeTrackerApp(root)
root.call('wm', 'attributes', '.', '-topmost', '1')
root.mainloop()