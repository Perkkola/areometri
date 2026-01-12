import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from PIL import Image, ImageTk
import numpy as np

class DigitizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Plot Digitizer")

        # --- GUI Layout ---
        # 1. Main container to hold the Control Panel (left) and the Zoom Panel (right)
        self.top_container = tk.Frame(self.root, padx=5, pady=5)
        self.top_container.pack(side=tk.TOP, fill=tk.X)

        # 2. Control Panel (Left side of top container)
        self.controls_frame = tk.Frame(self.top_container)
        self.controls_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.load_btn = tk.Button(self.controls_frame, text="1. Load Image", command=self.load_image)
        self.load_btn.pack(side=tk.LEFT, padx=5)

        self.calibrate_btn = tk.Button(self.controls_frame, text="2. Calibrate Axes", command=self.start_calibration, state=tk.DISABLED)
        self.calibrate_btn.pack(side=tk.LEFT, padx=5)

        self.coord_label = tk.Label(self.controls_frame, text="Coordinates: N/A", font=("Courier", 12), bd=1, relief=tk.SUNKEN, width=35, anchor=tk.W)
        self.coord_label.pack(side=tk.LEFT, padx=10)

        # 3. Zoom Panel (Right side of top container)
        # This canvas will show the magnified view
        self.zoom_size = 150 # Size of the square zoom box in pixels
        self.zoom_factor = 3 # How much to magnify (2x, 3x, etc.)
        
        self.zoom_canvas = tk.Canvas(self.top_container, width=self.zoom_size, height=self.zoom_size, bg="lightgrey", highlightthickness=1, highlightbackground="black")
        self.zoom_canvas.pack(side=tk.RIGHT, padx=10)
        
        # Crosshair for the zoom window (static lines in the center)
        mid = self.zoom_size // 2
        self.zoom_canvas.create_line(mid, 0, mid, self.zoom_size, fill="red")
        self.zoom_canvas.create_line(0, mid, self.zoom_size, mid, fill="red")

        # 4. Main Image Canvas
        self.canvas = tk.Canvas(self.root, cursor="cross", bg="grey")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # --- State Variables ---
        self.image = None       # The PIL Image object (resized)
        self.photo = None       # The PhotoImage for the main canvas
        self.zoom_photo = None  # The PhotoImage for the zoom canvas
        
        self.calibration_points = []
        self.calibrating = False
        self.calibration_step = 0
        self.mx, self.cx = 0, 0
        self.my, self.cy = 0, 0
        self.is_calibrated = False

        # --- Event Bindings ---
        self.canvas.bind("<Motion>", self.on_mouse_move)
        self.canvas.bind("<Button-1>", self.handle_click)

    def load_image(self):
        """Opens, resizes, and displays the image."""
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif")])
        if file_path:
            original_image = Image.open(file_path)
            
            # Resize logic
            max_w, max_h = 1200, 800
            width_ratio = max_w / original_image.width
            height_ratio = max_h / original_image.height
            scale_factor = min(width_ratio, height_ratio, 1.0)
            
            new_width = int(original_image.width * scale_factor)
            new_height = int(original_image.height * scale_factor)
            
            try:
                resample_method = Image.Resampling.LANCZOS
            except AttributeError:
                resample_method = Image.ANTIALIAS

            # Save the resized image as self.image so we can crop from it later
            self.image = original_image.resize((new_width, new_height), resample_method)
            self.photo = ImageTk.PhotoImage(self.image)
            
            self.canvas.config(width=new_width, height=new_height)
            self.canvas.delete("all")
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
            
            self.calibrate_btn.config(state=tk.NORMAL)
            self.is_calibrated = False
            self.calibration_points = []
            self.canvas.delete("calib_mark")

    def update_zoom(self, px, py):
        """Crops a region around (px, py) and displays it magnified in the zoom canvas."""
        if not self.image:
            return

        # 1. Determine the region to crop from the main image
        # We want a region that, when multiplied by zoom_factor, fills the zoom_size.
        crop_radius = (self.zoom_size / self.zoom_factor) / 2
        
        left = px - crop_radius
        top = py - crop_radius
        right = px + crop_radius
        bottom = py + crop_radius
        
        # 2. Crop the image
        cropped = self.image.crop((left, top, right, bottom))
        
        # 3. Resize (magnify) the cropped region
        # Use NEAREST to keep pixels sharp so the user can see exact grid lines
        try:
            resample_zoom = Image.Resampling.NEAREST
        except AttributeError:
            resample_zoom = Image.NEAREST
            
        magnified = cropped.resize((self.zoom_size, self.zoom_size), resample_zoom)
        
        # 4. Display in the zoom canvas
        self.zoom_photo = ImageTk.PhotoImage(magnified)
        # We use itemconfig to update the existing image instead of creating new ones (prevents memory leaks)
        if not hasattr(self, 'zoom_image_id'):
            self.zoom_image_id = self.zoom_canvas.create_image(0, 0, image=self.zoom_photo, anchor=tk.NW)
            # Ensure the crosshair stays on top
            self.zoom_canvas.tag_raise("all")
        else:
            self.zoom_canvas.itemconfig(self.zoom_image_id, image=self.zoom_photo)
            # Keeping the crosshair on top isn't strictly necessary with itemconfig, but good practice
            self.zoom_canvas.tag_raise(self.zoom_image_id) 
            self.zoom_canvas.lower(self.zoom_image_id) # Push image behind red lines

    def on_mouse_move(self, event):
        """Handles both coordinate display and zoom window updates."""
        px = self.canvas.canvasx(event.x)
        py = self.canvas.canvasy(event.y)
        
        # Update the Zoom Window
        self.update_zoom(px, py)

        # Update the Coordinate Label
        if not self.is_calibrated:
            self.coord_label.config(text=f"Pixels: ({px:.0f}, {py:.0f})")
            return

        if 0 <= px < self.image.width and 0 <= py < self.image.height:
            log_val = self.mx * px + self.cx
            x_data = np.power(10, log_val)
            y_data = self.my * py + self.cy
            self.coord_label.config(text=f"X: {x_data:.4e}, Y: {y_data:.4f}")
        else:
            self.coord_label.config(text="Out of bounds")

    # --- Calibration Methods (Same as before) ---
    def start_calibration(self):
        if not self.image: return
        self.calibrating = True
        self.calibration_step = 1
        self.calibration_points = []
        self.is_calibrated = False
        self.canvas.delete("calib_mark")
        messagebox.showinfo("Step 1", "Click on X-axis LEFT known point.")

    def handle_click(self, event):
        if not self.calibrating: return
        px = self.canvas.canvasx(event.x)
        py = self.canvas.canvasy(event.y)
        self.calibration_points.append((px, py))
        self.canvas.create_oval(px-4, py-4, px+4, py+4, outline="red", width=2, tags="calib_mark")

        if self.calibration_step == 1:
            self.calibration_step = 2
            messagebox.showinfo("Step 2", "Click on X-axis RIGHT known point.")
        elif self.calibration_step == 2:
            self.calibration_step = 3
            messagebox.showinfo("Step 3", "Click on Y-axis BOTTOM known point.")
        elif self.calibration_step == 3:
            self.calibration_step = 4
            messagebox.showinfo("Step 4", "Click on Y-axis TOP known point.")
        elif self.calibration_step == 4:
            self.finish_calibration()

    def finish_calibration(self):
        self.calibrating = False
        try:
            x1_d = simpledialog.askfloat("Input", f"Value for X-point 1:")
            x2_d = simpledialog.askfloat("Input", f"Value for X-point 2:")
            y1_d = simpledialog.askfloat("Input", f"Value for Y-point 1:")
            y2_d = simpledialog.askfloat("Input", f"Value for Y-point 2:")

            if None in [x1_d, x2_d, y1_d, y2_d]: return
            
            p1x, p2x = self.calibration_points[0][0], self.calibration_points[1][0]
            p1y, p2y = self.calibration_points[2][1], self.calibration_points[3][1]

            if x1_d <= 0 or x2_d <= 0: raise ValueError("X values must be > 0 for log scale.")

            # Log X Calculation
            self.mx = (np.log10(x2_d) - np.log10(x1_d)) / (p2x - p1x)
            self.cx = np.log10(x1_d) - self.mx * p1x

            # Linear Y Calculation
            self.my = (y2_d - y1_d) / (p2y - p1y)
            self.cy = y1_d - self.my * p1y

            self.is_calibrated = True
            self.canvas.delete("calib_mark")
            messagebox.showinfo("Success", "Calibration complete.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    root.minsize(800, 600)
    app = DigitizerApp(root)
    root.mainloop()