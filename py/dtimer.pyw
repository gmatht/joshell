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

HELP_TEXT="""
DTimer was designed to be used as a timer for work,
Specifically for Data Annotation Tech.

Created by: John McCabe-Dansted
Version: 0.2

If you want to work for DAT you can use my referral code:
2ZbHGEA

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

import os, sys, re;

#Define an 'xterm -e' like command.
#WARNING: It doesn't escape double quotes (")
if os.name=='nt':
    def xterm(cmd, confirm=None):
        c=cmd
        if confirm:
            c="set /p DUMMY=" + confirm + " && " + c
        c="start cmd /k \"" +\
            c + " && set /p DUMMY=Close this window to continue...\""
        os.system(c)
else:
    def xterm(cmd, confirm=None):
        c=cmd
        if confirm:
            c="echo" + confirm + " && read _ && " + c
        c="`which $TERM xfce4-terminal rxvt foot kitty konsole xterm gnome-terminal eterm urxvt gnome-terminal Alacritty alacritty warp hyper iterm2 terminal | head -n 1` -e \"" +\
              c + " && echo Close this window to continue && read _\""
        os.system(c)

#Try to import modules, offer to install them if it fails
#TODO: Test these actually work on a fresh install
try:
    import tkinter as tk
    from tkinter import BooleanVar, Checkbutton, font, RIGHT, Menu, messagebox
    from collections import defaultdict
    from datetime import datetime

    ### For Doom Clock ###
    #import pyautogui
    import time, ctypes, tktimepicker
    from tktimepicker import AnalogPicker, constants

    from pynput.keyboard import Key, Controller
    from time import sleep

except ImportError:
    pips='datetime tk time tktimepicker pynput ctypes collection'
    if os.name!='nt':
        pips='Xlib contextlib ' + pips
    pip_cmd="pip install " + pips
    msg = "DTimer will quit if any modules are missing. "
    msg = "We need all of the following modules:" + pips + "."
    msg += "Press Enter to install now, or close the window to quit."

    #Support installing unifont via curl later
    from tkinter.messagebox import askokcancel, showinfo, WARNING
    root = tk.Tk()
    root.title('Restart?')
    install = askokcancel(
        title='Restart?',
        message="DTimer will need to restart.\nRestart (or quit)?",
        icon=WARNING)
    if not install:
        quit()
    os.execv(sys.argv[0], sys.argv)

if os.name!='nt':
    if os.system("fc-list :charset=23F8,93FA|grep ."):
        install = askokcancel(
            title='Install GNU Unifont?',
            message="""DTimer uses unicode symbols, but you don't have a font installed with those symbols.

            If you don't install such a font, DTimer will use ugly ascii symbols instead. :(

            Would you like us to install GNU Unifont now? (26 MB download; 86 MB untarred; 589 MB when built with font files)""",
            icon=WARNING)
        if install:
            xterm("mkdir -p ~/.fonts && cd ~/.fonts && curl -O https://unifoundry.com/pub/unifont/unifont-15.1.05/unifont-15.1.05.tar.gz && tar -xf unifont-15.1.05.tar.gz && fc-cache -f -v")
        else:
            PAUSE_SYMBOL="[*]" # Ascii pause symbol
            RECORD_SYMBOL="[||]" # Ascii record symbol


def copy_all():
    if os.name!='nt':
        #pynput should work in Linux, but it doesn't seem to
        #You may have to play a bit with this to get it to work with your window manager.
        if os.system("sleep 0.1 && xdotool key ctrl+a && sleep 0.1 && xdotool key ctrl+c")==0:
            return
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

    xlib = ctypes.cdll.LoadLibrary( 'libX11.so')
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

def restart():
    os.execv(sys.executable, [sys.executable] + sys.argv)

########### END IDLE TIME ################

### END IMPORTS AND COMPATIBILITY CODE ###

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
        #pause_symbol = "\u23FA"  # Unicode for record symbol
        self.button = tk.Button(master, text=RECORD_SYMBOL, font=ft, command=self.toggle_recording)
        self.button.pack(side=RIGHT)

        ft = font.Font(family='Arial', size=16)
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
        m.add_command(label="Restart", command=restart)
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
        os.execv(sys.argv[0], sys.argv)
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
        #if platform.system() != 'Windows':
        #    self.master.wm_attributes("-type", "normal")
        store_fg(bad=True)
        self.x = event.x
        self.y = event.y

    def stop_move(self, event):
        #if platform.system() != 'Windows':
        #    self.master.wm_attributes("-type", "dock")
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