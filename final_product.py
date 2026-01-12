import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from PIL import Image, ImageTk
import numpy as np

class DigitizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Areometri")

        # --- GUI Setup ---
        # Top frame for controls and coordinate display
        self.right_container = tk.Frame(self.root, padx=5, pady=5)
        self.right_container.pack(side=tk.RIGHT, fill=tk.X)

        # 2. Control Panel (Left side of top container)
        self.controls_frame = tk.Frame(self.right_container)
        self.controls_frame.pack(side=tk.TOP, fill=tk.X, expand=True)

        # Label to display coordinates at the top right
        self.coord_label = tk.Label(self.controls_frame, text="Coordinates: N/A", font=("Courier", 12), bd=1, relief=tk.SUNKEN, width=23, anchor=tk.W, justify='center', compound='center')
        self.coord_label.pack(side=tk.TOP, padx=10, pady=10)

        self.zoom_size = 200 # Size of the square zoom box in pixels
        self.zoom_factor = 3

        self.zoom_canvas = tk.Canvas(self.right_container, width=self.zoom_size, height=self.zoom_size, bg="lightgrey", highlightthickness=1, highlightbackground="black")
        self.zoom_canvas.pack(side=tk.BOTTOM, padx=10)
        
        # Crosshair for the zoom window (static lines in the center)
        mid = self.zoom_size // 2
        self.zoom_canvas.create_line(mid, 0, mid, self.zoom_size, fill="red")
        self.zoom_canvas.create_line(0, mid, self.zoom_size, mid, fill="red")

        # Canvas to display the image and catch mouse events
        self.canvas = tk.Canvas(self.root, bg="grey")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # --- State Variables ---
        self.image = None
        self.photo = None
        self.zoom_photo = None
        self.x_calibration_points = [
            [(103.0, 0),
            (130.0, 0)],
            [(130.0, 0),
            (153.0, 0)],
            [(153.0, 0),
            (173.0, 0)],
            [(173.0, 0),
            (191.0, 0)],
            [(191.0, 0),
            (206.0, 0)],
            [(206.0, 0),
            (220.0, 0)],
            [(220.0, 0),
            (311.0, 0)],
            [(311.0, 0),
            (359.0, 0)],
            [(359.0, 0),
            (396.0, 0)],
            [(396.0, 0),
            (424.0, 0)],
            [(424.0, 0),
            (448.0, 0)],
            [(448.0, 0),
            (467.0, 0)],
            [(467.0, 0),
            (483.0, 0)],
            [(483.0, 0),
            (498.0, 0)],
            [(498.0, 0),
            (512.0, 0)],
            [(512.0, 0),
            (599.0, 0)],
            [(599.0, 0),
            (650.0, 0)],
            [(650.0, 0),
            (686.0, 0)],
            [(686.0, 0),
            (713.0, 0)],
            [(713.0, 0),
            (737.0, 0)],
            [(737.0, 0),
            (756.0, 0)]
] # Stores pixel (x,y) of clicked points
        self.y_calibration_points = [
            [(0, 193.0),
            (0, 207.0)],
            [(0, 207.0),
            (0, 221.0)],
            [(0, 221.0),
            (0, 237.0)],
            [(0, 237.0),
            (0, 252.0)],
            [(0, 252.0),
            (0, 267.0)],
            [(0, 267.0),
            (0, 281.0)],
            [(0, 281.0),
            (0, 296.0)],
            [(0, 296.0),
            (0, 311.0)]
] # Stores pixel (x,y) of clicked points
        self.x_values = [
            [0.0004, 0.0005],
            [0.0005, 0.0006],
            [0.0006, 0.0007],
            [0.0007, 0.0008],
            [0.0008, 0.0009],
            [0.0009, 0.001],
            [0.001, 0.002],
            [0.002, 0.003],
            [0.003, 0.004],
            [0.004, 0.005],
            [0.005, 0.006],
            [0.006, 0.007],
            [0.007, 0.008],
            [0.008, 0.009],
            [0.009, 0.01],
            [0.01, 0.02],
            [0.02, 0.03],
            [0.03, 0.04],
            [0.04, 0.05],
            [0.05, 0.06],
            [0.06, 0.07]
        ]
        self.y_values = [
            [1.000, 1.005],
            [1.005, 1.010],
            [1.010, 1.015],
            [1.015, 1.020],
            [1.020, 1.025],
            [1.025, 1.030],
            [1.030, 1.035],
            [1.035, 1.040]
        ]
        self.calibrating = False
        self.calibration_step = 0
        self.calibration_block = 0
        self.axis = 'y'
        # Transformation parameters
        self.mx, self.cx = [], []
        self.my, self.cy = [], []
        self.is_calibrated = False


        self.canvas.bind("<Motion>", self.display_coordinates)
        self.load_image()

    def load_image(self):
        """Opens a file dialog to load an image, resizes it to fit, and displays it."""
        
        # 1. Open the original image
        original_image = Image.open('./Akseli.png')
        
        # 2. Define maximum dimensions (e.g., fits comfortably on a standard laptop screen)
        max_w = 1000 
        max_h = 600
        
        # 3. Calculate the resize ratio to maintain aspect ratio
        width_ratio = max_w / original_image.width
        height_ratio = max_h / original_image.height
        
        # We take the smaller ratio to ensure it fits both width and height.
        # We also use min(..., 1.0) so we don't stretch small images up.
        scale_factor = min(width_ratio, height_ratio, 1.0)
        
        new_width = int(original_image.width * scale_factor)
        new_height = int(original_image.height * scale_factor)
        
        # 4. Resize using high-quality resampling (LANCZOS)
        # This handles compatibility for both new and old Pillow versions
        try:
            resample_method = Image.Resampling.LANCZOS
        except AttributeError:
            resample_method = Image.ANTIALIAS # For older Pillow versions
            
        self.image = original_image.resize((new_width, new_height), resample_method)
        self.photo = ImageTk.PhotoImage(self.image)
        
        # 5. Update Canvas
        self.canvas.config(width=new_width, height=new_height)
        # Clear previous images if any
        self.canvas.delete("all") 
        self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
        
        # Reset application state
        self.is_calibrated = True
        for i in range(21):
            log_x1 = np.log10(self.x_values[i][0])
            log_x2 = np.log10(self.x_values[i][1])
            self.mx.append((log_x2 - log_x1) / (self.x_calibration_points[i][1][0] - self.x_calibration_points[i][0][0]))
            self.cx.append(log_x1 - self.mx[i] * self.x_calibration_points[i][0][0])
        
        for i in range(8):
            self.my.append((self.y_values[i][1] - self.y_values[i][0]) / (self.y_calibration_points[i][1][1] - self.y_calibration_points[i][0][1]))
            self.cy.append(self.y_values[i][0] - self.my[i] * self.y_calibration_points[i][0][1])

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


    def display_coordinates(self, event):
        """Updates the coordinate label as the mouse moves."""
        # Get canvas coordinates
        px = self.canvas.canvasx(event.x)
        py = self.canvas.canvasy(event.y)
        self.update_zoom(px, py)
        if not self.is_calibrated:
            # Show raw pixel coordinates if not calibrated
            self.coord_label.config(text=f"Pixels: ({px:.0f}, {py:.0f})")
            return

        # Check if mouse is inside the image bounds
        if 0 <= px < self.image.width and 0 <= py < self.image.height:
            # Apply Logarithmic Transformation for X
            if 0 <= px < self.x_calibration_points[0][1][0]: x_index = 0
            for x in range(19):
                if self.x_calibration_points[x][1][0] <= px < self.x_calibration_points[x + 1][1][0]: 
                    x_index = x + 1
                    break
            if self.x_calibration_points[19][1][0] <= px < self.image.width: x_index = 20

            if 0 <= py < self.y_calibration_points[0][1][1]: y_index = 0
            for y in range(6):
                if self.y_calibration_points[y][1][1] <= py < self.y_calibration_points[y + 1][1][1]: 
                    y_index = y + 1
                    break
            if self.y_calibration_points[6][1][1] <= py < self.image.height: y_index = 7

            log_val = self.mx[x_index] * px + self.cx[x_index]
            x_data = np.power(10, log_val)
            
            # Apply Linear Transformation for Y
            y_data = self.my[y_index] * py + self.cy[y_index]

            # Update label with formatted coordinates
            # .4e is scientific notation with 4 decimals (good for log scale)
            # .4f is fixed-point notation with 4 decimals
            self.coord_label.config(text=f"X: {x_data:.6f}, Y: {y_data:.4f}")
        else:
            self.coord_label.config(text="Out of bounds")

if __name__ == "__main__":
    root = tk.Tk()
    # Prevent window from being too small
    root.minsize(600, 400) 
    app = DigitizerApp(root)
    root.mainloop()