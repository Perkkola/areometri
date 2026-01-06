import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from PIL import Image, ImageTk
import numpy as np

class DigitizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Plot Digitizer")

        # --- GUI Setup ---
        # Top frame for controls and coordinate display
        self.controls_frame = tk.Frame(self.root, padx=5, pady=5)
        self.controls_frame.pack(side=tk.TOP, fill=tk.X)

        self.load_btn = tk.Button(self.controls_frame, text="1. Load Image", command=self.load_image)
        self.load_btn.pack(side=tk.LEFT, padx=5)

        self.calibrate_btn = tk.Button(self.controls_frame, text="2. Calibrate Axes", command=self.start_calibration, state=tk.DISABLED)
        self.calibrate_btn.pack(side=tk.LEFT, padx=5)

        # Label to display coordinates at the top right
        self.coord_label = tk.Label(self.controls_frame, text="Coordinates: N/A", font=("Courier", 12), bd=1, relief=tk.SUNKEN, width=35, anchor=tk.E)
        self.coord_label.pack(side=tk.RIGHT, padx=10)

        # Canvas to display the image and catch mouse events
        self.canvas = tk.Canvas(self.root, cursor="cross", bg="grey")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # --- State Variables ---
        self.image = None
        self.photo = None
        self.calibration_points = [] # Stores pixel (x,y) of clicked points
        self.calibrating = False
        self.calibration_step = 0
        # Transformation parameters
        self.mx, self.cx = 0, 0
        self.my, self.cy = 0, 0
        self.is_calibrated = False

        # --- Event Bindings ---
        # Track mouse movement to update coordinates
        self.canvas.bind("<Motion>", self.display_coordinates)
        # Handle clicks for calibration
        self.canvas.bind("<Button-1>", self.handle_click)

    def load_image(self):
        """Opens a file dialog to load an image, resizes it to fit, and displays it."""
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif")])
        if file_path:
            # 1. Open the original image
            original_image = Image.open(file_path)
            
            # 2. Define maximum dimensions (e.g., fits comfortably on a standard laptop screen)
            max_w = 1200 
            max_h = 900 
            
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
            self.calibrate_btn.config(state=tk.NORMAL)
            self.is_calibrated = False
            self.calibration_points = []

    def start_calibration(self):
        """Starts the 4-step calibration process."""
        if not self.image:
            return
        self.calibrating = True
        self.calibration_step = 1
        self.calibration_points = []
        self.is_calibrated = False
        self.canvas.delete("calib_mark")
        messagebox.showinfo("Calibration Step 1/4", "Click on a known point on the **left** side of the X-axis.")

    def handle_click(self, event):
        """Handles mouse clicks during the calibration process."""
        if not self.calibrating:
            return

        # Get coordinates relative to the canvas, accounting for scrolling if added later
        px = self.canvas.canvasx(event.x)
        py = self.canvas.canvasy(event.y)
        
        self.calibration_points.append((px, py))
        # Draw a red marker where clicked
        self.canvas.create_oval(px-4, py-4, px+4, py+4, outline="red", width=2, tags="calib_mark")

        # Guide user through the 4 steps
        if self.calibration_step == 1:
            self.calibration_step = 2
            messagebox.showinfo("Calibration Step 2/4", "Click on a known point on the **right** side of the X-axis.")
        elif self.calibration_step == 2:
            self.calibration_step = 3
            messagebox.showinfo("Calibration Step 3/4", "Click on a known point near the **bottom** of the Y-axis.")
        elif self.calibration_step == 3:
            self.calibration_step = 4
            messagebox.showinfo("Calibration Step 4/4", "Click on a known point near the **top** of the Y-axis.")
        elif self.calibration_step == 4:
            self.finish_calibration()

    def finish_calibration(self):
        """Prompts for data values and calculates transformation parameters."""
        self.calibrating = False
        
        try:
            # Prompt user for the data values corresponding to the clicked points
            x1_d = simpledialog.askfloat("Input", f"Enter value for X-point 1 (pixel x={self.calibration_points[0][0]:.0f}):")
            x2_d = simpledialog.askfloat("Input", f"Enter value for X-point 2 (pixel x={self.calibration_points[1][0]:.0f}):")
            y1_d = simpledialog.askfloat("Input", f"Enter value for Y-point 1 (pixel y={self.calibration_points[2][1]:.0f}):")
            y2_d = simpledialog.askfloat("Input", f"Enter value for Y-point 2 (pixel y={self.calibration_points[3][1]:.0f}):")

            if None in [x1_d, x2_d, y1_d, y2_d]:
                 messagebox.showwarning("Cancelled", "Calibration cancelled.")
                 self.canvas.delete("calib_mark")
                 return
            
            # Get pixel coordinates from stored points
            p1x = self.calibration_points[0][0]
            p2x = self.calibration_points[1][0]
            p1y = self.calibration_points[2][1]
            p2y = self.calibration_points[3][1]

            print(f"p1x: {p1x}")
            print(f"p2x: {p2x}")
            print(f"p1y: {p1y}")
            print(f"p2y: {p2y}")

            # Basic validation
            if p1x == p2x: raise ValueError("X-points must have different horizontal positions.")
            if p1y == p2y: raise ValueError("Y-points must have different vertical positions.")
            if x1_d <= 0 or x2_d <= 0: raise ValueError("For logarithmic X-axis, values must be positive.")

            # --- Calculate Logarithmic X-axis Transformation ---
            # log10(x_data) = mx * x_pixel + cx
            log_x1 = np.log10(x1_d)
            log_x2 = np.log10(x2_d)
            self.mx = (log_x2 - log_x1) / (p2x - p1x)
            self.cx = log_x1 - self.mx * p1x

            # --- Calculate Linear Y-axis Transformation ---
            # y_data = my * y_pixel + cy
            self.my = (y2_d - y1_d) / (p2y - p1y)
            self.cy = y1_d - self.my * p1y

            self.is_calibrated = True
            self.canvas.delete("calib_mark") # Clean up markers
            messagebox.showinfo("Success", "Calibration complete! Move your mouse over the image to read coordinates.")

        except (ValueError, TypeError) as e:
            messagebox.showerror("Calibration Error", str(e))
            self.canvas.delete("calib_mark")

    def display_coordinates(self, event):
        """Updates the coordinate label as the mouse moves."""
        # Get canvas coordinates
        px = self.canvas.canvasx(event.x)
        py = self.canvas.canvasy(event.y)

        if not self.is_calibrated:
            # Show raw pixel coordinates if not calibrated
            self.coord_label.config(text=f"Pixels: ({px:.0f}, {py:.0f})")
            return

        # Check if mouse is inside the image bounds
        if 0 <= px < self.image.width and 0 <= py < self.image.height:
            # Apply Logarithmic Transformation for X
            log_val = self.mx * px + self.cx
            x_data = np.power(10, log_val)
            
            # Apply Linear Transformation for Y
            y_data = self.my * py + self.cy

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