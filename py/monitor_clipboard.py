import os
import hashlib
import shutil
from PIL import ImageGrab, Image, ImageTk, ImageDraw, ImageFont
import time
import filetype
import PIL
import ctypes
import tkinter as tk
from tkinter import Canvas
import math

OUTPUT_DIR = "F:\\pics"

DEBUG = False
# Constants for timer intervals
TIMER_INTERVAL_SHORT = 100  # milliseconds
TIMER_INTERVAL_LONG = 2000  # milliseconds
MAX_CACHE_FILES = 99 #number of files to check in the cache
INACTIVITY_THRESHOLD = 60  # seconds
BRAVE_CACHE_PATH = r"%LocalAppData%\BraveSoftware\Brave-Browser\User Data\Default\Cache\Cache_Data"
BRAVE_CACHE_PATH = os.path.expandvars(BRAVE_CACHE_PATH)
HASH_FILE = os.path.join(OUTPUT_DIR, "sha256.txt")

# Animation constants
ANIMATION_DURATION = 0.2  # seconds
ANIMATION_FPS = 60
FLOPPY_ICON_SIZE = 256
FLOPPY_ICON_POSITION = (50, 50)  # Bottom-right corner offset

# Ensure paths exist
if not os.path.exists(BRAVE_CACHE_PATH):
    print(f"Error: {BRAVE_CACHE_PATH} does not exist")
    exit(1)

if not os.path.exists(OUTPUT_DIR):
    print(f"Error: {OUTPUT_DIR} does not exist")
    exit(1)

def create_floppy_icon(size=256):
    """Create a floppy disk icon using Unicode symbol."""
    icon = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(icon)
    
    floppy_symbol = "💾"  # U+1F4BE
    
    try:
        font_size = int(size * 0.8)
        font_names = ["seguiemj.ttf", "NotoColorEmoji.ttf", "AppleColorEmoji.ttc", "arial.ttf"]
        
        font = None
        for font_name in font_names:
            try:
                font = ImageFont.truetype(font_name, font_size)
                break
            except (OSError, IOError):
                continue
        
        if font is None:
            font = ImageFont.load_default()
        
        bbox = draw.textbbox((0, 0), floppy_symbol, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (size - text_width) // 2
        y = (size - text_height) // 2
        
        draw.text((x, y), floppy_symbol, fill=(30, 100, 200, 255), font=font)
        
    except Exception:
        # Fallback: simple blue square
        margin = size // 8
        draw.rectangle([margin, margin, size-margin, size-margin], fill=(30, 100, 200, 255))
        inner_margin = size // 3
        draw.rectangle([inner_margin, inner_margin, size-inner_margin, size-inner_margin], 
                      fill=(255, 255, 255, 255))
    
    return icon

class SaveAnimationWindow:
    """Creates an overlay window to show save animation using pure timer events."""
    
    def __init__(self, main_root):
        self.main_root = main_root
        self.animation_window = None
        self.canvas = None
        self.is_animating = False
        self.animation_timer = None
        
    def get_mouse_position(self):
        """Get current mouse cursor position."""
        try:
            from ctypes import wintypes
            point = wintypes.POINT()
            ctypes.windll.user32.GetCursorPos(ctypes.byref(point))
            return (point.x, point.y)
        except Exception:
            screen_width = self.main_root.winfo_screenwidth()
            screen_height = self.main_root.winfo_screenheight()
            return (screen_width // 2, screen_height // 2)

    def get_monitor_from_mouse(self, mouse_x, mouse_y):
        """Get monitor information for the monitor containing the mouse cursor."""
        try:
            from ctypes import wintypes
            
            point = wintypes.POINT(mouse_x, mouse_y)
            monitor = ctypes.windll.user32.MonitorFromPoint(point, 2)
            
            class MONITORINFO(ctypes.Structure):
                _fields_ = [
                    ('cbSize', ctypes.c_ulong),
                    ('rcMonitor', wintypes.RECT),
                    ('rcWork', wintypes.RECT),
                    ('dwFlags', ctypes.c_ulong)
                ]
            
            monitor_info = MONITORINFO()
            monitor_info.cbSize = ctypes.sizeof(MONITORINFO)
            
            if ctypes.windll.user32.GetMonitorInfoW(monitor, ctypes.byref(monitor_info)):
                rect = monitor_info.rcMonitor
                return {
                    'x': rect.left,
                    'y': rect.top,
                    'width': rect.right - rect.left,
                    'height': rect.bottom - rect.top
                }
        except Exception:
            pass
        
        return {
            'x': 0,
            'y': 0,
            'width': self.main_root.winfo_screenwidth(),
            'height': self.main_root.winfo_screenheight()
        }

    def animate_save(self, image):
        """Animate the image shrinking into a floppy icon."""
        if self.is_animating:
            return
        
        start_position = self.get_mouse_position()
        monitor = self.get_monitor_from_mouse(start_position[0], start_position[1])
        
        target_position = (monitor['x'] + monitor['width'] - FLOPPY_ICON_POSITION[0] - FLOPPY_ICON_SIZE, 
                         monitor['y'] + monitor['height'] - FLOPPY_ICON_POSITION[1] - FLOPPY_ICON_SIZE)
        
        self._start_animation(image, target_position, start_position, monitor)

    def _start_animation(self, image, target_position, start_position, monitor):
        """Initialize and start the animation window."""
        try:
            self.is_animating = True
            
            self.animation_window = tk.Toplevel(self.main_root)
            self.animation_window.withdraw()
            self.animation_window.attributes('-topmost', True)
            self.animation_window.overrideredirect(True)
            
            self.animation_window.geometry(f"{monitor['width']}x{monitor['height']}+{monitor['x']}+{monitor['y']}")
            
            self.canvas = Canvas(self.animation_window, width=monitor['width'], height=monitor['height'], 
                               highlightthickness=0, bg='black')
            self.canvas.pack()
            
            # Make transparent
            self.animation_window.attributes('-transparentcolor', 'black')
            
            # Prepare images
            max_start_size = min(400, image.width, image.height)
            start_image = image.copy()
            start_image.thumbnail((max_start_size, max_start_size), Image.Resampling.LANCZOS)
            
            floppy_icon = create_floppy_icon(FLOPPY_ICON_SIZE)
            
            # Calculate positions relative to monitor
            start_x = start_position[0] - monitor['x'] - start_image.width // 2
            start_y = start_position[1] - monitor['y'] - start_image.height // 2
            
            target_x = target_position[0] - monitor['x']
            target_y = target_position[1] - monitor['y']
            monitor_relative_target = (target_x, target_y)
            
            # Show window
            self.animation_window.deiconify()
            self.animation_window.lift()
            
            # Animation state
            animation_state = {
                'frame': 0,
                'frames': int(ANIMATION_DURATION * ANIMATION_FPS),
                'start_image': start_image,
                'floppy_icon': floppy_icon,
                'start_x': start_x,
                'start_y': start_y,
                'target_position': monitor_relative_target,
                'frame_interval': int(1000 / ANIMATION_FPS)
            }
            
            self._animate_frame(animation_state)
            
        except Exception:
            self._cleanup_animation()

    def _animate_frame(self, state):
        """Animate a single frame."""
        try:
            if not self.is_animating or not self.animation_window:
                return
                
            if state['frame'] >= state['frames']:
                self.animation_timer = self.main_root.after(300, self._cleanup_animation)
                return
            
            progress = state['frame'] / state['frames']
            eased_progress = 0.5 * (1 - math.cos(progress * math.pi))
            
            # Calculate current size and position
            current_scale = 1.0 - (0.9 * eased_progress)
            current_width = max(1, int(state['start_image'].width * current_scale))
            current_height = max(1, int(state['start_image'].height * current_scale))
            
            current_x = int(state['start_x'] + (state['target_position'][0] - state['start_x']) * eased_progress)
            current_y = int(state['start_y'] + (state['target_position'][1] - state['start_y']) * eased_progress)
            
            opacity = max(0.2, 1.0 - eased_progress)
            
            self.canvas.delete("all")
            
            # Draw shrinking image
            if current_width > 1 and current_height > 1:
                resized_image = state['start_image'].resize((current_width, current_height), Image.Resampling.LANCZOS)
                
                if resized_image.mode != 'RGBA':
                    resized_image = resized_image.convert('RGBA')
                
                alpha = resized_image.split()[-1]
                alpha = alpha.point(lambda p: int(p * opacity))
                resized_image.putalpha(alpha)
                
                photo = ImageTk.PhotoImage(resized_image)
                self.canvas.create_image(current_x, current_y, anchor=tk.NW, image=photo)
                self.canvas.image = photo
            
            # Draw floppy icon
            floppy_opacity = min(1.0, eased_progress * 2)
            if floppy_opacity > 0:
                floppy_with_opacity = state['floppy_icon'].copy()
                alpha = floppy_with_opacity.split()[-1]
                alpha = alpha.point(lambda p: int(p * floppy_opacity))
                floppy_with_opacity.putalpha(alpha)
                
                floppy_photo = ImageTk.PhotoImage(floppy_with_opacity)
                self.canvas.create_image(state['target_position'][0], state['target_position'][1], 
                                       anchor=tk.NW, image=floppy_photo)
                self.canvas.floppy_image = floppy_photo
            
            state['frame'] += 1
            self.animation_timer = self.main_root.after(state['frame_interval'], lambda: self._animate_frame(state))
            
        except Exception:
            self._cleanup_animation()

    def _cleanup_animation(self):
        """Clean up animation resources."""
        try:
            if self.animation_timer:
                self.main_root.after_cancel(self.animation_timer)
                self.animation_timer = None
                
            if self.animation_window:
                self.animation_window.destroy()
                self.animation_window = None
                
            self.canvas = None
        except Exception:
            pass
        finally:
            self.is_animating = False

class ClipboardMonitor:
    """Timer-based clipboard monitor."""
    
    def __init__(self, root):
        self.root = root
        self.last_clipboard_hash = None
        self.last_clipboard_sequence_number = None
        self.last_action_time = time.time()
        self.timer_id = None
        self.is_running = False
        self.save_animator = SaveAnimationWindow(root)
        self.cached_hashes = {}
        
    def get_clipboard_sequence_number(self):
        return ctypes.windll.user32.GetClipboardSequenceNumber()

    def get_clipboard_image(self):
        try:
            return ImageGrab.grabclipboard()
        except Exception:
            return None

    def get_last_files_in_cache(self, n=99):
        try:
            files = sorted(os.listdir(BRAVE_CACHE_PATH), 
                         key=lambda x: os.path.getmtime(os.path.join(BRAVE_CACHE_PATH, x)), 
                         reverse=True)
            return files[:n]
        except Exception:
            return []

    def calculate_image_hash(self, file_path):
        if file_path in self.cached_hashes:
            return self.cached_hashes[file_path]
        try:
            with Image.open(file_path) as image:
                hash_val = hashlib.sha256(image.tobytes()).hexdigest()
                self.cached_hashes[file_path] = hash_val
                return hash_val
        except Exception:
            return None

    def save_image_with_animation(self, file_path, clipboard_hash, clipboard_image):
        """Save image file and trigger animation."""
        try:
            kind = filetype.guess(file_path)
            if not kind:
                return False
                
            ext = kind.extension
            new_file_path = os.path.join(OUTPUT_DIR, f"{clipboard_hash}.{ext}")
            
            shutil.copyfile(file_path, new_file_path)
            
            with open(HASH_FILE, "a") as hash_file:
                hash_file.write(f"{clipboard_hash} {new_file_path}\n")
                
            print(f"Copied {os.path.basename(file_path)} to {new_file_path}")
            
            if clipboard_image:
                self.save_animator.animate_save(clipboard_image)
            
            return True
            
        except Exception as e:
            print(f"Error saving image: {e}")
            return False

    def check_clipboard(self):
        """Timer callback to check clipboard."""
        try:
            clipboard_sequence_number = self.get_clipboard_sequence_number()
            
            if clipboard_sequence_number != self.last_clipboard_sequence_number:
                self.last_clipboard_sequence_number = clipboard_sequence_number
                clipboard_image = self.get_clipboard_image()
                
                if clipboard_image:
                    clipboard_hash = hashlib.sha256(clipboard_image.tobytes()).hexdigest()
                    
                    if clipboard_hash != self.last_clipboard_hash:
                        self.last_clipboard_hash = clipboard_hash

                        last_files = self.get_last_files_in_cache(MAX_CACHE_FILES)
                        for file_name in last_files:
                            if not file_name.startswith("f_"):
                                continue
                            file_path = os.path.join(BRAVE_CACHE_PATH, file_name)
                            if os.path.isfile(file_path):
                                file_hash = self.calculate_image_hash(file_path)
                                if file_hash == clipboard_hash:
                                    with open(HASH_FILE, "a+") as hash_file:
                                        hash_file.seek(0)
                                        if f"{clipboard_hash} " not in hash_file.read():
                                            if self.save_image_with_animation(file_path, clipboard_hash, clipboard_image):
                                                self.last_action_time = time.time()
                                    break
            
            # Schedule next check
            interval = TIMER_INTERVAL_LONG if time.time() - self.last_action_time > INACTIVITY_THRESHOLD else TIMER_INTERVAL_SHORT
            
            if self.is_running:
                self.timer_id = self.root.after(interval, self.check_clipboard)
                
        except Exception:
            if self.is_running:
                self.timer_id = self.root.after(TIMER_INTERVAL_LONG, self.check_clipboard)

    def start(self):
        """Start clipboard monitoring."""
        print("Starting clipboard monitor...")
        self.is_running = True
        self.last_action_time = time.time()
        self.timer_id = self.root.after(TIMER_INTERVAL_SHORT, self.check_clipboard)

    def stop(self):
        """Stop clipboard monitoring."""
        print("Stopping clipboard monitor...")
        self.is_running = False
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None
        if self.save_animator.is_animating:
            self.save_animator._cleanup_animation()

def main():
    root = tk.Tk()
    root.withdraw()
    root.title("Clipboard Monitor")
    
    monitor = ClipboardMonitor(root)
    
    def on_closing():
        monitor.stop()
        root.quit()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    monitor.start()
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\nKeyboard interrupt received")
        monitor.stop()

if __name__ == "__main__":
    main()