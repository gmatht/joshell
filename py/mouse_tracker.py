#!python
#!C:\Users\s_pam\AppData\Local\Microsoft\WindowsApps\python.exe
#!/usr/bin/env python3
"""
Mouse Tracker - Displays 4 small translucent windows that hide when the mouse cursor is over them.
"""

import tkinter as tk
import win32api
import win32gui
import win32con
import threading
import time
import math

class MouseTracker:
    def __init__(self):
        # Get screen dimensions
        self.screen_width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
        self.screen_height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
        
        # Window properties
        self.window_size = 60
        self.window_color = '#FFFF00'  # Yellow
        self.alpha = 0.7  # 70% opacity
        
        # Store window objects
        self.windows = []
        self.window_positions = []
        
        # Create 4 small windows
        self.create_windows()
        
        # Start mouse tracking thread
        self.running = True
        self.track_thread = threading.Thread(target=self.track_mouse, daemon=True)
        self.track_thread.start()
        
        # Start the GUI for the first window (others will be managed separately)
        if self.windows:
            self.windows[0].mainloop()
    
    def create_windows(self):
        """Create 4 small windows positioned at screen corners"""
        # Define positions for the 4 windows (corners)
        positions = [
            (0, 0),  # Top-left
            (self.screen_width - self.window_size, 0),  # Top-right
            (0, self.screen_height - self.window_size),  # Bottom-left
            (self.screen_width - self.window_size, self.screen_height - self.window_size)  # Bottom-right
        ]
        
        for i, (x, y) in enumerate(positions):
            window = self.create_single_window(x, y, i)
            self.windows.append(window)
            self.window_positions.append((x, y))
    
    def create_single_window(self, x, y, window_id):
        """Create a single small window"""
        window = tk.Toplevel()
        window.title(f"Mouse Tracker {window_id}")
        
        # Set window properties
        window.geometry(f"{self.window_size}x{self.window_size}+{x}+{y}")
        window.attributes('-alpha', self.alpha)
        window.attributes('-topmost', True)
        window.overrideredirect(True)  # Remove window decorations
        
        # Create canvas for drawing
        canvas = tk.Canvas(
            window,
            width=self.window_size,
            height=self.window_size,
            bg=self.window_color,
            highlightthickness=0
        )
        canvas.pack()
        
        # Create static triangle based on window position
        self.create_static_triangle(canvas, window_id)
        
        # Store canvas reference in window object
        window.canvas = canvas
        window.window_id = window_id
        
        # Bind escape key to exit (only for first window)
        if window_id == 0:
            window.bind('<Escape>', lambda e: self.quit())
        
        return window
    
    def create_static_triangle(self, canvas, window_id):
        """Create a static triangle pointing in the appropriate direction based on window position"""
        center_x = self.window_size // 2
        center_y = self.window_size // 2
        triangle_size = 20
        
        # Create triangles pointing inward from each corner
        if window_id == 0:  # Top-left - point down-right
            points = [
                center_x - triangle_size, center_y - triangle_size,
                center_x + triangle_size, center_y - triangle_size,
                center_x + triangle_size, center_y + triangle_size
            ]
        elif window_id == 1:  # Top-right - point down-left
            points = [
                center_x - triangle_size, center_y - triangle_size,
                center_x + triangle_size, center_y - triangle_size,
                center_x - triangle_size, center_y + triangle_size
            ]
        elif window_id == 2:  # Bottom-left - point up-right
            points = [
                center_x - triangle_size, center_y - triangle_size,
                center_x + triangle_size, center_y - triangle_size,
                center_x + triangle_size, center_y + triangle_size
            ]
        else:  # Bottom-right - point up-left
            points = [
                center_x - triangle_size, center_y - triangle_size,
                center_x + triangle_size, center_y - triangle_size,
                center_x - triangle_size, center_y + triangle_size
            ]
        
        canvas.create_polygon(
            points[0], points[1],
            points[2], points[3],
            points[4], points[5],
            fill='#FF4400', outline='#CC2200', width=2
        )
    
    def update_window_positions(self, mouse_x, mouse_y):
        """Move windows to point toward mouse cursor"""
        for i, window in enumerate(self.windows):
            try:
                # Calculate new position based on mouse location
                new_x, new_y = self.calculate_window_position(i, mouse_x, mouse_y)
                
                # Update window position
                window.geometry(f"{self.window_size}x{self.window_size}+{new_x}+{new_y}")
            except:
                pass
    
    def calculate_window_position(self, window_id, mouse_x, mouse_y):
        """Calculate optimal window position to point toward mouse"""
        # Define base positions (corners)
        base_positions = [
            (0, 0),  # Top-left
            (self.screen_width - self.window_size, 0),  # Top-right
            (0, self.screen_height - self.window_size),  # Bottom-left
            (self.screen_width - self.window_size, self.screen_height - self.window_size)  # Bottom-right
        ]
        
        base_x, base_y = base_positions[window_id]
        
        # Calculate offset based on mouse position
        # Move window slightly toward mouse while staying near the corner
        offset_x = int((mouse_x - self.screen_width // 2) * 0.1)
        offset_y = int((mouse_y - self.screen_height // 2) * 0.1)
        
        # Apply offset while keeping window in appropriate corner
        if window_id == 0:  # Top-left
            new_x = max(0, min(self.screen_width // 2 - self.window_size, base_x + offset_x))
            new_y = max(0, min(self.screen_height // 2 - self.window_size, base_y + offset_y))
        elif window_id == 1:  # Top-right
            new_x = max(self.screen_width // 2, min(self.screen_width - self.window_size, base_x + offset_x))
            new_y = max(0, min(self.screen_height // 2 - self.window_size, base_y + offset_y))
        elif window_id == 2:  # Bottom-left
            new_x = max(0, min(self.screen_width // 2 - self.window_size, base_x + offset_x))
            new_y = max(self.screen_height // 2, min(self.screen_height - self.window_size, base_y + offset_y))
        else:  # Bottom-right
            new_x = max(self.screen_width // 2, min(self.screen_width - self.window_size, base_x + offset_x))
            new_y = max(self.screen_height // 2, min(self.screen_height - self.window_size, base_y + offset_y))
        
        return new_x, new_y
    
    def is_mouse_over_window(self, window, mouse_x, mouse_y):
        """Check if mouse cursor is over a specific window"""
        try:
            # Get window position and size
            window_x = window.winfo_x()
            window_y = window.winfo_y()
            window_width = window.winfo_width()
            window_height = window.winfo_height()
            
            # Check if mouse is within window bounds
            return (window_x <= mouse_x <= window_x + window_width and
                    window_y <= mouse_y <= window_y + window_height)
        except:
            return False
    
    def update_window_visibility(self, mouse_x, mouse_y):
        """Show/hide windows based on mouse position"""
        for window in self.windows:
            try:
                if self.is_mouse_over_window(window, mouse_x, mouse_y):
                    # Hide window if mouse is over it
                    window.withdraw()
                else:
                    # Show window if mouse is not over it
                    window.deiconify()
            except:
                pass
    
    def track_mouse(self):
        """Track mouse position in a separate thread"""
        while self.running:
            try:
                # Get mouse position
                cursor = win32gui.GetCursorPos()
                mouse_x, mouse_y = cursor
                
                # Update window visibility and triangles on main thread
                if self.windows:
                    self.windows[0].after(0, self.update_window_visibility, mouse_x, mouse_y)
                    self.windows[0].after(0, self.update_window_positions, mouse_x, mouse_y)
                
                # Small delay to prevent excessive updates
                time.sleep(0.05)  # 20 FPS
                
            except Exception as e:
                print(f"Error tracking mouse: {e}")
                time.sleep(0.1)
    
    def quit(self):
        """Clean up and exit"""
        self.running = False
        # Close all windows
        for window in self.windows:
            try:
                window.destroy()
            except:
                pass
        # Exit the main loop
        if self.windows:
            self.windows[0].quit()

def main():
    """Main function"""
    try:
        print("Starting Mouse Tracker...")
        print("Press ESC to exit")
        tracker = MouseTracker()
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main() 