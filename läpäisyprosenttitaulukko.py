import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox, ttk
from PIL import Image, ImageTk
import numpy as np
from scipy.interpolate import make_interp_spline

class DigitizerApp:
    def __init__(self, root, width, height):
        self.root = root
        self.root.title("Läpäisyprosenttitaulukko")

        self.right_container = tk.Frame(self.root, padx=5, pady=5)
        self.right_container.pack(side=tk.RIGHT, fill=tk.X)

        self.controls_frame = tk.Frame(self.right_container)
        self.controls_frame.pack(side=tk.TOP, fill=tk.X, expand=True)


        self.calculator_frame = tk.Frame(self.right_container)
        self.calculator_frame.pack(side=tk.BOTTOM, fill=tk.X, expand=True, pady=10)
  

        tk.Label(self.calculator_frame, text="Kohde lämpötila (°C):", bg="#f0f0f0").pack(anchor=tk.W, padx=10)
        self.ent_temp = tk.Entry(self.calculator_frame)
        self.ent_temp.pack(padx=10, fill=tk.X)
        self.ent_temp.insert(0, "21.5")

        tk.Label(self.calculator_frame, text="Kohde X (Lukema):", bg="#f0f0f0").pack(anchor=tk.W, padx=10)
        self.ent_y = tk.Entry(self.calculator_frame)
        self.ent_y.pack(padx=10, fill=tk.X)
        self.ent_y.insert(0, "1.020")

        self.calc_btn = tk.Button(self.calculator_frame, text="Laske Y (Läpäisyprosentti)", command=self.calculate_interpolation, bg="lightgreen", font=("Arial", 10, "bold"))
        self.calc_btn.pack(padx=10, pady=10, fill=tk.X)

        self.result_label = tk.Label(self.calculator_frame, text="Tulos:\n---", bg="#f0f0f0", font=("Arial", 12), fg="blue")
        self.result_label.pack(pady=10)

        self.canvas = tk.Canvas(self.root, bg="grey")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        if width >= 1500 and height >= 900:
            self.max_w = 1200
            self.max_h = 800
        else:
            self.max_w = 1000
            self.max_h = 600

        self.load_image()

        self.x_23 = [1.000,1.0291238738503619]
        self.y_23 = [0.04, 1.0]

        self.x_14 = [1.0035, 1.031]
        self.y_14 = [0.1, 1.0]
        


    def load_image(self):

        original_image = Image.open('./kuva_2.png')
        
        width_ratio = self.max_w / original_image.width
        height_ratio = self.max_h / original_image.height

        scale_factor = min(width_ratio, height_ratio, 1.0)
        
        new_width = int(original_image.width * scale_factor)
        new_height = int(original_image.height * scale_factor)

        
        try:
            resample_method = Image.Resampling.LANCZOS
        except AttributeError:
            resample_method = Image.ANTIALIAS
            
        self.image = original_image.resize((new_width, new_height), resample_method)
        self.photo = ImageTk.PhotoImage(self.image)
        
        self.canvas.config(width=new_width, height=new_height)
        self.canvas.delete("all") 
        self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)

    def calculate_interpolation(self):
        try:
            target_temp = float(self.ent_temp.get())
            target_y = float(self.ent_y.get())

            get_diameter = self.create_temperature_interpolator(self.x_23, self.y_23 ,self.x_14, self.y_14)
                
            result = get_diameter(target_y, target_temp)

            if result > 1: result = 1
            if result < 0: result = 0
            self.result_label.config(text=f"Y = {result:.5f}")
        except ValueError as e:
            messagebox.showerror("Error", f"Virheellinen numero: {e}.")
        except Exception as e:
            messagebox.showerror("Error", f"Lasku epäonnistui: {str(e)}")

    def create_temperature_interpolator(self, y_1, x_1, y_2, x_2, ub = 23, lb = 14):
        idx_23 = np.argsort(y_1)
        spline_23 = make_interp_spline(y_1, x_1, k=1)
        
        idx_14 = np.argsort(y_2)
        spline_14 = make_interp_spline(y_2, x_2, k=1)

        def predict(reading, temperature):
            if not (14 <= temperature <= 23):
                print("Warning: Temperature outside calibrated range (14-23C). Extrapolating.")
                
            d_23 = spline_23(reading)
            d_14 = spline_14(reading)
            
            w = (temperature - lb) / (ub - lb)
            d_target = d_14 + w * (d_23 - d_14)
            
            return d_target
            
        return predict


    # get_diameter = create_temperature_interpolator(y_vals_23, x_vals_23, y_vals_14, x_vals_14, ub, lb)
    # result = get_diameter(1.020, 21.5)


if __name__ == "__main__":
    root = tk.Tk()
    root.minsize(600, 400) 
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    app = DigitizerApp(root, screen_width, screen_height)
    root.mainloop()