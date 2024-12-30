# importing the tkinter module and PIL
# that is pillow module
from tkinter import *
from PIL import ImageTk, Image
import sys
import math
import glob
import threading
import shutil
import os


#CONFIG
view_width=1970
view_height=1000
GEOM="1977x1020" # Main Window
DEST='~/good_pics'
SRC='~/Downloads/*.jpg'
SRC='/mnt/z/BLOB/FromUSB/32GBmini/3D/DCIM/104_FUJI/*.JPG'
#END CONFIG


DEST=os.path.expanduser(DEST)
SRC=os.path.expanduser(SRC)

img_no=1

def update():
    global img_no
    global label
    global button_forward
    global button_back
    global button_exit
    global root
    global image_reference
    global list_images
    #label.grid_forget()

    print("IMG: ", img_no)
    sys.stdout.flush()

    init_cache(img_no-1)
    img_cache[img_no-4]=None
    img_cache[img_no+4]=None
    preload(img_no)
    preload(img_no+1)
    root.title('Image Selector: ' + list_images[img_no-1] )

    #if img_no <= 1:
    #    button_back.status=DISABLED
    #else:
    #    button_back.status=NORMAL

    with lock:
        sys.stdout.flush()
        img=ImageTk.PhotoImage(img_cache[img_no-1])
        image_reference = img
        label = Label(image=img, width=view_width, height=view_height)
        label.grid(row=5, column=0, columnspan=3)

def back():
    global img_no
    img_no-=1
    update()

def forward():
    global img_no
    img_no+=1
    update()

root = Tk()
root.title("Image Viewer")
root.geometry("1977x1020")

list_images = glob.glob(SRC)
img_cache = [None]*len(list_images)

lock = threading.Lock()


def init_cache(i):
    global img_cache

    _preload(i)
    return

    with lock:
        img = img_cache[i]

    if img is None:
        preload(i)
    while True:
        with lock:
            if not isinstance(img_cache[i], threading.Thread):
                break
        img_cache[i].join()

def preload(i):
    with lock:
        if img_cache[i] is not None:
            return
        t=threading.Thread(target=_preload, args=[i])
        img_cache[i]=t
    img_cache[i].start()

def _preload(i):
    global list_images
    global img_cache
    #with lock:
    #    if img_cache[i] is not None and img_cache[i] != "Loading":
    #        return
    img=Image.open(list_images[i])
    img_cache[i] = img

    w = view_width

    h = math.ceil(img.height * (w / img.width))
    if h > view_height:
        h = view_height
        w = math.ceil(img.width * (h / img.height))

    result = img.resize((w,h),Image.Resampling.LANCZOS)
    with lock:
        img_cache[i] = result
    sys.stdout.flush()

sys.stdout.flush()

def save():
    if not os.path.exists(DEST):
        os.makedirs(DEST)
    print("SAVING: " + list_images[img_no-1]) 
    sys.stdout.flush()
    shutil.copy2(list_images[img_no-1], DEST)


init_cache(0)
image_no_1 = ImageTk.PhotoImage(img_cache[0])

label = Label(image=image_no_1, width=view_width, height=view_height)
label.grid(row=5, column=0, columnspan=4)

button_back = Button(root, text="Back", command=back,
                     state=DISABLED)

button_exit = Button(root, text="Exit",
                     command=root.quit)

button_forward = Button(root, text="Forward",
                        command=lambda: forward(1))

button_save = Button(root, text="Save (S)", command=save)

button_back.grid(row=1, column=0)
button_exit.grid(row=1, column=1)
button_forward.grid(row=1, column=2)
button_save.grid(row=1, column=3)

def key(event):
    sys.stdout.flush()
    k=event.keysym.lower()
    if k=='s':
        save()
    if k=='d':
        forward()
    if k=='a':
        back()
    if k=='escape':
        root.quit()

root.bind("<KeyRelease>", key)


root.mainloop()
