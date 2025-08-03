#!python
#!C:\Users\s_pam\AppData\Local\Microsoft\WindowsApps\python.exe
#!/usr/bin/env python3
"""
Mouse Tracker - Displays 4 translucent yellow triangles pointing at the mouse cursor
on the edges of the screen.
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
        self.root = tk.Tk()
        self.root.title("Mouse Tracker")
        
        # Make window fullscreen and transparent
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-alpha', 0.3)  # 30% opacity
        self.root.attributes('-topmost', True)
        
        # Remove window decorations
        self.root.overrideredirect(True)
        
        # Create canvas for drawing with transparent background
        self.canvas = tk.Canvas(
            self.root,
            width=self.root.winfo_screenwidth(),
            height=self.root.winfo_screenheight(),
            bg='#000000',  # Black background
            highlightthickness=0
        )
        self.canvas.pack()
        
        # Make the window background transparent by setting it to black with alpha
        self.root.configure(bg='#000000')
        # The alpha attribute on the root window will make the black transparent
        
        # Make canvas background transparent by using a very dark color
        # that will be nearly invisible with the alpha setting
        self.canvas.configure(bg='#000000')
        
        # Get screen dimensions
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        
        # Triangle properties
        self.triangle_size = 30
        self.triangle_color = '#FFFF00'  # Yellow
        
        # Store triangle objects
        self.triangles = []
        
        # Create initial triangles
        self.create_triangles()
        
        # Start mouse tracking thread
        self.running = True
        self.track_thread = threading.Thread(target=self.track_mouse, daemon=True)
        self.track_thread.start()
        
        # Bind escape key to exit
        self.root.bind('<Escape>', lambda e: self.quit())
        
        # Start the GUI
        self.root.mainloop()
    
    def create_triangles(self):
        """Create 4 triangles pointing inward from screen edges"""
        # Clear existing triangles
        for triangle in self.triangles:
            self.canvas.delete(triangle)
        self.triangles.clear()
        
        # Top triangle (pointing down)
        top_triangle = self.canvas.create_polygon(
            self.screen_width // 2 - self.triangle_size, 0,
            self.screen_width // 2 + self.triangle_size, 0,
            self.screen_width // 2, self.triangle_size,
            fill=self.triangle_color, outline='', tags='triangle'
        )
        self.triangles.append(top_triangle)
        
        # Bottom triangle (pointing up)
        bottom_triangle = self.canvas.create_polygon(
            self.screen_width // 2 - self.triangle_size, self.screen_height,
            self.screen_width // 2 + self.triangle_size, self.screen_height,
            self.screen_width // 2, self.screen_height - self.triangle_size,
            fill=self.triangle_color, outline='', tags='triangle'
        )
        self.triangles.append(bottom_triangle)
        
        # Left triangle (pointing right)
        left_triangle = self.canvas.create_polygon(
            0, self.screen_height // 2 - self.triangle_size,
            0, self.screen_height // 2 + self.triangle_size,
            self.triangle_size, self.screen_height // 2,
            fill=self.triangle_color, outline='', tags='triangle'
        )
        self.triangles.append(left_triangle)
        
        # Right triangle (pointing left)
        right_triangle = self.canvas.create_polygon(
            self.screen_width, self.screen_height // 2 - self.triangle_size,
            self.screen_width, self.screen_height // 2 + self.triangle_size,
            self.screen_width - self.triangle_size, self.screen_height // 2,
            fill=self.triangle_color, outline='', tags='triangle'
        )
        self.triangles.append(right_triangle)
    
    def update_triangle_positions(self, mouse_x, mouse_y):
        """Update triangle positions to point at mouse cursor"""
        # Calculate distances from mouse to each edge
        dist_to_top = mouse_y
        dist_to_bottom = self.screen_height - mouse_y
        dist_to_left = mouse_x
        dist_to_right = self.screen_width - mouse_x
        
        # Find closest edge
        min_dist = min(dist_to_top, dist_to_bottom, dist_to_left, dist_to_right)
        
        # Update triangle positions based on mouse position
        if min_dist == dist_to_top:
            # Mouse is closest to top edge - move top triangle
            new_x = max(self.triangle_size, min(self.screen_width - self.triangle_size, mouse_x))
            self.canvas.coords(self.triangles[0],
                new_x - self.triangle_size, 0,
                new_x + self.triangle_size, 0,
                new_x, self.triangle_size
            )
        elif min_dist == dist_to_bottom:
            # Mouse is closest to bottom edge - move bottom triangle
            new_x = max(self.triangle_size, min(self.screen_width - self.triangle_size, mouse_x))
            self.canvas.coords(self.triangles[1],
                new_x - self.triangle_size, self.screen_height,
                new_x + self.triangle_size, self.screen_height,
                new_x, self.screen_height - self.triangle_size
            )
        elif min_dist == dist_to_left:
            # Mouse is closest to left edge - move left triangle
            new_y = max(self.triangle_size, min(self.screen_height - self.triangle_size, mouse_y))
            self.canvas.coords(self.triangles[2],
                0, new_y - self.triangle_size,
                0, new_y + self.triangle_size,
                self.triangle_size, new_y
            )
        elif min_dist == dist_to_right:
            # Mouse is closest to right edge - move right triangle
            new_y = max(self.triangle_size, min(self.screen_height - self.triangle_size, mouse_y))
            self.canvas.coords(self.triangles[3],
                self.screen_width, new_y - self.triangle_size,
                self.screen_width, new_y + self.triangle_size,
                self.screen_width - self.triangle_size, new_y
            )
    
    def track_mouse(self):
        """Track mouse position in a separate thread"""
        while self.running:
            try:
                # Get mouse position
                cursor = win32gui.GetCursorPos()
                mouse_x, mouse_y = cursor
                
                # Update triangle positions on main thread
                self.root.after(0, self.update_triangle_positions, mouse_x, mouse_y)
                
                # Small delay to prevent excessive updates
                time.sleep(0.05)  # 20 FPS
                
            except Exception as e:
                print(f"Error tracking mouse: {e}")
                time.sleep(0.1)
    
    def quit(self):
        """Clean up and exit"""
        self.running = False
        self.root.quit()

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