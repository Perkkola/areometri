import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox, ttk
from PIL import Image, ImageTk
import numpy as np
from scipy.interpolate import make_interp_spline

class DigitizerApp:
    def __init__(self, root, width, height):
        self.root = root
        self.root.title("Areometri")

        self.right_container = tk.Frame(self.root, padx=5, pady=5)
        self.right_container.pack(side=tk.RIGHT, fill=tk.X)

        self.controls_frame = tk.Frame(self.right_container)
        self.controls_frame.pack(side=tk.TOP, fill=tk.X, expand=True)

        self.coord_label = tk.Label(self.controls_frame, text="Coordinates: N/A", font=("Courier", 12), bd=1, relief=tk.SUNKEN, width=23, anchor=tk.W, justify='center', compound='center')
        self.coord_label.pack(side=tk.TOP, padx=10, pady=10)

        self.calculator_frame = tk.Frame(self.right_container)
        self.calculator_frame.pack(side=tk.BOTTOM, fill=tk.X, expand=True, pady=10)
        tk.Label(self.calculator_frame, text="Valitse aika:", bg="#f0f0f0").pack(anchor=tk.W, padx=10)
        self.time_var = tk.StringVar(value="6min")
        self.time_dropdown = ttk.Combobox(self.calculator_frame, textvariable=self.time_var, values=["1min", "6min", "1h", "5h", "1vrk"], state="readonly")
        self.time_dropdown.pack(side=tk.TOP, pady=10)

        tk.Label(self.calculator_frame, text="Kohde lämpötila (°C):", bg="#f0f0f0").pack(anchor=tk.W, padx=10)
        self.ent_temp = tk.Entry(self.calculator_frame)
        self.ent_temp.pack(padx=10, fill=tk.X)
        self.ent_temp.insert(0, "21.5")

        tk.Label(self.calculator_frame, text="Kohde Y (Lukema):", bg="#f0f0f0").pack(anchor=tk.W, padx=10)
        self.ent_y = tk.Entry(self.calculator_frame)
        self.ent_y.pack(padx=10, fill=tk.X)
        self.ent_y.insert(0, "1.020")

        self.calc_btn = tk.Button(self.calculator_frame, text="Laske X", command=self.calculate_interpolation, bg="lightgreen", font=("Arial", 10, "bold"))
        self.calc_btn.pack(padx=10, pady=10, fill=tk.X)

        self.result_label = tk.Label(self.calculator_frame, text="Tulos:\n---", bg="#f0f0f0", font=("Arial", 12), fg="blue")
        self.result_label.pack(pady=10)

        self.zoom_size = 200
        self.zoom_factor = 3

        self.zoom_canvas = tk.Canvas(self.right_container, width=self.zoom_size, height=self.zoom_size, bg="lightgrey", highlightthickness=1, highlightbackground="black")
        self.zoom_canvas.pack(side=tk.BOTTOM, padx=10)
        
        mid = self.zoom_size // 2
        self.zoom_canvas.create_line(mid, 0, mid, self.zoom_size, fill="red")
        self.zoom_canvas.create_line(0, mid, self.zoom_size, mid, fill="red")

        self.canvas = tk.Canvas(self.root, bg="grey")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.image = None
        self.photo = None
        self.zoom_photo = None

        self.y = np.array([1.000, 1.010, 1.020, 1.030, 1.040])
        self.m1 = np.array([[0.063506, 0.061478, 0.059505, 0.056761, 0.054556],
                    [0.061478, 0.060000, 0.057565, 0.05499, 0.052853],
                    [0.059056, 0.057090, 0.054772, 0.052853, 0.050799],
                    [0.056313, 0.054320, 0.052549, 0.050799, 0.049209]])

        self.m6 = np.array([[0.02559, 0.024789, 0.023823, 0.023077, 0.022178],
                    [0.024789, 0.024013, 0.023261, 0.022355, 0.021483],
                    [0.024013, 0.023261, 0.022355, 0.021655, 0.020811],
                    [0.023077, 0.022355, 0.021483, 0.020977, 0.020000]])

        self.t1 = np.array([[0.008000, 0.007753, 0.007454, 0.00728, 0.00700],
                    [0.007692, 0.007454, 0.007223, 0.00700, 0.006722],
                    [0.007454, 0.007223, 0.006943, 0.006732, 0.006507],
                    [0.007167, 0.007000, 0.006667, 0.006507, 0.006198]])

        self.t5 = np.array([[0.003548, 0.003464, 0.003302, 0.003198, 0.003071],
                    [0.003464, 0.003302, 0.003173, 0.003073, 0.003000],
                    [0.003276, 0.003173, 0.003048, 0.002951, 0.002852],
                    [0.003147, 0.003048, 0.002975, 0.002855, 0.002757]])

        self.vrk1 = np.array([[0.001657, 0.001595, 0.001536, 0.001491, 0.001425],
                    [0.001595, 0.001536, 0.001491, 0.001436, 0.001372],
                    [0.001525, 0.001491, 0.001425, 0.001372, 0.001321],
                    [0.001480, 0.001414, 0.001372, 0.001321, 0.001273]])

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

        if width >= 1500 and height >= 900:
            self.max_w = 1200
            self.max_h = 800
            self.grid_points = [
                [(140.0, 257.0),
                (140.0, 276.0),
                (139.0, 295.0),
                (139.0, 316.0),
                (139.0, 336.0),
                (139.0, 356.0),
                (139.0, 374.0),
                (139.0, 395.0),
                (139.0, 415.0)],
                [(176.0, 257.0),
                (176.0, 276.0),
                (176.0, 295.0),
                (176.0, 316.0),
                (176.0, 337.0),
                (176.0, 356.0),
                (176.0, 374.0),
                (176.0, 395.0),
                (176.0, 415.0)],
                [(207.0, 257.0),
                (207.0, 276.0),
                (207.0, 295.0),
                (207.0, 316.0),
                (206.0, 337.0),
                (206.0, 356.0),
                (206.0, 375.0),
                (206.0, 395.0),
                (206.0, 415.0)],
                [(234.0, 257.0),
                (234.0, 276.0),
                (234.0, 295.0),
                (234.0, 316.0),
                (233.0, 337.0),
                (233.0, 356.0),
                (233.0, 374.0),
                (233.0, 395.0),
                (233.0, 415.0)],
                [(256.0, 257.0),
                (256.0, 276.0),
                (256.0, 295.0),
                (256.0, 316.0),
                (256.0, 337.0),
                (256.0, 356.0),
                (256.0, 374.0),
                (256.0, 395.0),
                (256.0, 415.0)],
                [(277.0, 257.0),
                (277.0, 277.0),
                (276.0, 295.0),
                (276.0, 316.0),
                (276.0, 337.0),
                (276.0, 356.0),
                (276.0, 375.0),
                (276.0, 395.0),
                (276.0, 415.0)],
                [(295.0, 258.0),
                (295.0, 278.0),
                (295.0, 297.0),
                (295.0, 317.0),
                (295.0, 338.0),
                (295.0, 357.0),
                (295.0, 375.0),
                (295.0, 396.0),
                (295.0, 416.0)],
                [(417.0, 259.0),
                (417.0, 278.0),
                (417.0, 297.0),
                (417.0, 317.0),
                (417.0, 338.0),
                (417.0, 357.0),
                (417.0, 375.0),
                (417.0, 396.0),
                (417.0, 416.0)],
                [(482.0, 258.0),
                (482.0, 278.0),
                (482.0, 297.0),
                (482.0, 317.0),
                (482.0, 338.0),
                (482.0, 358.0),
                (482.0, 376.0),
                (482.0, 396.0),
                (482.0, 416.0)],
                [(530.0, 258.0),
                (530.0, 278.0),
                (530.0, 297.0),
                (530.0, 317.0),
                (530.0, 338.0),
                (530.0, 357.0),
                (530.0, 376.0),
                (530.0, 396.0),
                (530.0, 416.0)],
                [(567.0, 258.0),
                (567.0, 278.0),
                (567.0, 296.0),
                (567.0, 317.0),
                (567.0, 338.0),
                (568.0, 357.0),
                (568.0, 376.0),
                (568.0, 396.0),
                (568.0, 416.0)],
                [(599.0, 258.0),
                (599.0, 278.0),
                (599.0, 297.0),
                (599.0, 317.0),
                (599.0, 338.0),
                (599.0, 357.0),
                (599.0, 376.0),
                (599.0, 396.0),
                (599.0, 416.0)],
                [(625.0, 258.0),
                (625.0, 278.0),
                (625.0, 297.0),
                (625.0, 317.0),
                (625.0, 338.0),
                (625.0, 357.0),
                (625.0, 375.0),
                (625.0, 396.0),
                (624.0, 416.0)],
                [(647.0, 258.0),
                (647.0, 278.0),
                (647.0, 296.0),
                (647.0, 317.0),
                (647.0, 337.0),
                (647.0, 356.0),
                (647.0, 375.0),
                (647.0, 396.0),
                (647.0, 416.0)],
                [(667.0, 258.0),
                (667.0, 278.0),
                (667.0, 297.0),
                (667.0, 317.0),
                (667.0, 338.0),
                (667.0, 356.0),
                (667.0, 375.0),
                (667.0, 396.0),
                (667.0, 416.0)],
                [(685.0, 258.0),
                (685.0, 278.0),
                (685.0, 296.0),
                (685.0, 317.0),
                (685.0, 337.0),
                (685.0, 357.0),
                (685.0, 375.0),
                (685.0, 396.0),
                (685.0, 416.0)],
                [(801.0, 259.0),
                (801.0, 279.0),
                (801.0, 298.0),
                (801.0, 318.0),
                (801.0, 338.0),
                (801.0, 357.0),
                (801.0, 376.0),
                (801.0, 396.0),
                (801.0, 416.0)],
                [(868.0, 259.0),
                (868.0, 279.0),
                (868.0, 298.0),
                (868.0, 318.0),
                (868.0, 338.0),
                (868.0, 357.0),
                (869.0, 376.0),
                (869.0, 396.0),
                (869.0, 416.0)],
                [(917.0, 259.0),
                (917.0, 278.0),
                (917.0, 297.0),
                (917.0, 318.0),
                (917.0, 338.0),
                (917.0, 357.0),
                (917.0, 375.0),
                (917.0, 396.0),
                (917.0, 416.0)],
                [(953.0, 259.0),
                (953.0, 278.0),
                (953.0, 297.0),
                (954.0, 317.0),
                (954.0, 338.0),
                (954.0, 356.0),
                (954.0, 375.0),
                (954.0, 395.0),
                (954.0, 415.0)],
                [(983.0, 259.0),
                (983.0, 278.0),
                (983.0, 297.0),
                (983.0, 317.0),
                (984.0, 337.0),
                (984.0, 356.0),
                (984.0, 375.0),
                (984.0, 395.0),
                (985.0, 415.0)],
                [(1008.0, 259.0),
                (1008.0, 278.0),
                (1008.0, 297.0),
                (1008.0, 317.0),
                (1008.0, 338.0),
                (1008.0, 356.0),
                (1008.0, 375.0),
                (1009.0, 395.0),
                (1009.0, 415.0)]
]
        else:
            self.max_w = 1000
            self.max_h = 600
            self.grid_points = [
            [(105.0, 193.0),
            (105.0, 207.0),
            (105.0, 222.0),
            (104.0, 237.0),
            (104.0, 252.0),
            (104.0, 267.0),
            (104.0, 281.0),
            (104.0, 296.0),
            (104.0, 311.0)],
            [(132.0, 193.0),
            (132.0, 207.0),
            (132.0, 221.0),
            (132.0, 237.0),
            (132.0, 252.0),
            (132.0, 267.0),
            (132.0, 281.0),
            (132.0, 296.0),
            (132.0, 311.0)],
            [(155.0, 193.0),
            (155.0, 207.0),
            (155.0, 222.0),
            (155.0, 237.0),
            (155.0, 253.0),
            (155.0, 267.0),
            (155.0, 281.0),
            (155.0, 296.0),
            (155.0, 311.0)],
            [(175.0, 193.0),
            (175.0, 207.0),
            (175.0, 221.0),
            (175.0, 237.0),
            (175.0, 253.0),
            (174.0, 267.0),
            (175.0, 281.0),
            (174.0, 296.0),
            (174.0, 311.0)],
            [(192.0, 193.0),
            (192.0, 207.0),
            (192.0, 221.0),
            (192.0, 237.0),
            (192.0, 253.0),
            (192.0, 267.0),
            (192.0, 281.0),
            (192.0, 296.0),
            (192.0, 311.0)],
            [(207.0, 193.0),
            (207.0, 208.0),
            (207.0, 221.0),
            (207.0, 237.0),
            (207.0, 253.0),
            (207.0, 267.0),
            (207.0, 281.0),
            (207.0, 296.0),
            (207.0, 311.0)],
            [(221.0, 194.0),
            (221.0, 208.0),
            (221.0, 223.0),
            (221.0, 238.0),
            (221.0, 254.0),
            (221.0, 268.0),
            (221.0, 282.0),
            (221.0, 297.0),
            (221.0, 312.0)],
            [(313.0, 194.0),
            (313.0, 209.0),
            (313.0, 223.0),
            (313.0, 238.0),
            (313.0, 254.0),
            (313.0, 268.0),
            (313.0, 282.0),
            (313.0, 297.0),
            (313.0, 312.0)],
            [(362.0, 194.0),
            (362.0, 209.0),
            (362.0, 223.0),
            (362.0, 238.0),
            (362.0, 254.0),
            (362.0, 268.0),
            (362.0, 282.0),
            (361.0, 297.0),
            (361.0, 312.0)],
            [(398.0, 194.0),
            (398.0, 208.0),
            (398.0, 222.0),
            (398.0, 238.0),
            (398.0, 254.0),
            (398.0, 268.0),
            (398.0, 282.0),
            (398.0, 297.0),
            (398.0, 312.0)],
            [(425.0, 194.0),
            (425.0, 208.0),
            (425.0, 222.0),
            (425.0, 238.0),
            (425.0, 254.0),
            (425.0, 268.0),
            (425.0, 282.0),
            (425.0, 297.0),
            (425.0, 312.0)],
            [(449.0, 194.0),
            (449.0, 208.0),
            (449.0, 222.0),
            (449.0, 238.0),
            (449.0, 253.0),
            (449.0, 268.0),
            (449.0, 282.0),
            (449.0, 297.0),
            (449.0, 312.0)],
            [(468.0, 194.0),
            (468.0, 208.0),
            (468.0, 222.0),
            (468.0, 238.0),
            (468.0, 253.0),
            (468.0, 267.0),
            (468.0, 281.0),
            (468.0, 297.0),
            (468.0, 312.0)],
            [(485.0, 194.0),
            (485.0, 209.0),
            (485.0, 222.0),
            (485.0, 238.0),
            (485.0, 253.0),
            (485.0, 267.0),
            (485.0, 281.0),
            (485.0, 297.0),
            (485.0, 312.0)],
            [(500.0, 194.0),
            (500.0, 208.0),
            (500.0, 222.0),
            (500.0, 238.0),
            (500.0, 253.0),
            (500.0, 267.0),
            (500.0, 281.0),
            (500.0, 297.0),
            (500.0, 312.0)],
            [(513.0, 194.0),
            (513.0, 208.0),
            (513.0, 222.0),
            (513.0, 238.0),
            (513.0, 253.0),
            (513.0, 267.0),
            (513.0, 281.0),
            (513.0, 297.0),
            (513.0, 312.0)],
            [(600.0, 194.0),
            (600.0, 209.0),
            (600.0, 223.0),
            (600.0, 238.0),
            (600.0, 254.0),
            (600.0, 268.0),
            (600.0, 282.0),
            (600.0, 297.0),
            (600.0, 312.0)],
            [(651.0, 194.0),
            (651.0, 209.0),
            (651.0, 223.0),
            (651.0, 239.0),
            (651.0, 254.0),
            (651.0, 268.0),
            (651.0, 282.0),
            (651.0, 297.0),
            (651.0, 312.0)],
            [(687.0, 194.0),
            (687.0, 209.0),
            (687.0, 223.0),
            (687.0, 238.0),
            (687.0, 253.0),
            (687.0, 268.0),
            (687.0, 281.0),
            (687.0, 297.0),
            (687.0, 312.0)],
            [(714.0, 194.0),
            (715.0, 209.0),
            (715.0, 223.0),
            (715.0, 238.0),
            (715.0, 253.0),
            (715.0, 267.0),
            (715.0, 281.0),
            (715.0, 297.0),
            (715.0, 312.0)],
            [(737.0, 194.0),
            (737.0, 209.0),
            (737.0, 223.0),
            (737.0, 238.0),
            (737.0, 253.0),
            (738.0, 267.0),
            (738.0, 281.0),
            (738.0, 296.0),
            (738.0, 311.0)],
            [(756.0, 194.0),
            (756.0, 209.0),
            (756.0, 223.0),
            (756.0, 238.0),
            (756.0, 253.0),
            (756.0, 267.0),
            (756.0, 281.0),
            (756.0, 296.0),
            (756.0, 311.0)]
]
    
        self.mx, self.cx = [[] for _ in range(21)], [[] for _ in range(21)]
        self.my, self.cy = [[] for _ in range(21)], [[] for _ in range(21)]

        self.canvas.bind("<Motion>", self.display_coordinates)
        self.load_image()

    def calculate_interpolation(self):
        try:
            time_block = self.time_var.get()
            target_temp = float(self.ent_temp.get())
            target_y = float(self.ent_y.get())

            if 14 <= target_temp < 17: ub, lb, x_1, x_2 = 17, 14, 0, 1
            elif 17 <= target_temp < 20: ub, lb, x_1, x_2  = 20, 17, 1, 2
            elif 20 <= target_temp <= 23: ub, lb, x_1, x_2  = 23, 20, 2, 3


            match time_block:
                case "1min":
                    get_diameter = self.create_temperature_interpolator(self.y, self.m1[x_2], self.y ,self.m1[x_1], ub, lb)
                case "6min":
                    get_diameter = self.create_temperature_interpolator(self.y, self.m6[x_2], self.y ,self.m6[x_1], ub, lb)
                case "1h":
                    get_diameter = self.create_temperature_interpolator(self.y, self.t1[x_2], self.y ,self.t1[x_1], ub, lb)
                case "5h":
                    get_diameter = self.create_temperature_interpolator(self.y, self.t5[x_2], self.y ,self.t5[x_1], ub, lb)
                case "1vrk":
                    get_diameter = self.create_temperature_interpolator(self.y, self.vrk1[x_2], self.y ,self.vrk1[x_1], ub, lb)
                
            result = get_diameter(target_y, target_temp)
            self.result_label.config(text=f"X = {result:.5f}")
        except ValueError:
            messagebox.showerror("Error", "Virheellinen numero.")
        except Exception as e:
            messagebox.showerror("Error", f"Lasku epäonnistui: {str(e)}")

    def create_temperature_interpolator(self, y_1, x_1, y_2, x_2, ub, lb):
        idx_23 = np.argsort(y_1)
        spline_23 = make_interp_spline(y_1[idx_23], x_1[idx_23], k=3)
        
        idx_14 = np.argsort(y_2)
        spline_14 = make_interp_spline(y_2[idx_14], x_2[idx_14], k=3)

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

    def load_image(self):

        original_image = Image.open('./kuva.png')
        
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
        
        self.is_calibrated = True

        for i in range(21):
            for j in range(8):
                log_x1 = np.log10(self.x_values[i][0])
                log_x2 = np.log10(self.x_values[i][1])
                self.mx[i].append((log_x2 - log_x1) / (self.grid_points[i + 1][j][0] - self.grid_points[i][j][0]))
                self.cx[i].append(log_x1 - self.mx[i][j] * self.grid_points[i][j][0])
        

                self.my[i].append((self.y_values[j][1] - self.y_values[j][0]) / (self.grid_points[i][j + 1][1] - self.grid_points[i][j][1]))
                self.cy[i].append(self.y_values[j][0] - self.my[i][j] * self.grid_points[i][j][1])

    def update_zoom(self, px, py):
        if not self.image:
            return

        crop_radius = (self.zoom_size / self.zoom_factor) / 2
        
        left = px - crop_radius
        top = py - crop_radius
        right = px + crop_radius
        bottom = py + crop_radius
        
        cropped = self.image.crop((left, top, right, bottom))

        try:
            resample_zoom = Image.Resampling.NEAREST
        except AttributeError:
            resample_zoom = Image.NEAREST
            
        magnified = cropped.resize((self.zoom_size, self.zoom_size), resample_zoom)
        
        self.zoom_photo = ImageTk.PhotoImage(magnified)
        if not hasattr(self, 'zoom_image_id'):
            self.zoom_image_id = self.zoom_canvas.create_image(0, 0, image=self.zoom_photo, anchor=tk.NW)
            self.zoom_canvas.tag_raise("all")
        else:
            self.zoom_canvas.itemconfig(self.zoom_image_id, image=self.zoom_photo)
            self.zoom_canvas.tag_raise(self.zoom_image_id) 
            self.zoom_canvas.lower(self.zoom_image_id)


    def display_coordinates(self, event):
        px = self.canvas.canvasx(event.x)
        py = self.canvas.canvasy(event.y)
        self.update_zoom(px, py)

        if 0 <= px < self.image.width and 0 <= py < self.image.height:
            found = False

            if 0 <= py < self.grid_points[1][1][1] and 0 <= px < self.grid_points[1][1][0]:
                self.x_index = 0
                self.y_index = 0
                found = True

            if 0 <= py < self.grid_points[1][1][1] and self.grid_points[20][1][0] <= px < self.image.width:
                self.x_index = 20
                self.y_index = 0
                found = True

            if self.grid_points[1][7][1] <= py < self.image.height and 0 <= px < self.grid_points[1][7][0]:
                self.x_index = 0
                self.y_index = 7
                found = True

            if self.grid_points[1][7][1] <= py < self.image.height and self.grid_points[20][1][0] <= px < self.image.width:
                self.x_index = 20
                self.y_index = 7
                found = True

            if not found: 
                for i in range(1, 20):
                    if 0 <= py < self.grid_points[i + 1][1][1] and self.grid_points[i][1][0] <= px < self.grid_points[i + 1][1][0]:
                        self.x_index = i
                        self.y_index = 0
                        found = True
                        break
                    if self.grid_points[i + 1][7][1] <= py < self.image.height and self.grid_points[i][1][0] <= px < self.grid_points[i + 1][1][0]:
                        self.x_index = i
                        self.y_index = 7
                        found = True
                        break

            if not found:
                for j in range(1, 7):
                    if 0 <= px < self.grid_points[1][j + 1][0] and self.grid_points[1][j][1] <= py < self.grid_points[1][j + 1][1]:
                        self.x_index = 0
                        self.y_index = j
                        found = True
                        break

                    if self.grid_points[20][j + 1][0] <= px < self.image.width and self.grid_points[20][j][1] <= py < self.grid_points[20][j + 1][1]:
                        self.x_index = 20
                        self.y_index = j
                        found = True
                        break

            if not found:
                for i in range(1, 20):
                    if found: break

                    for j in range(1, 7):
                        if self.grid_points[i][j][0] <= px < self.grid_points[i + 1][j][0] and self.grid_points[i][j][1] <= py < self.grid_points[i][j + 1][1]:
                            self.x_index = i
                            self.y_index = j
                            found = True
                            break
            
            log_val = self.mx[self.x_index][self.y_index] * px + self.cx[self.x_index][self.y_index] 
            x_data = np.power(10, log_val)
            
            y_data = self.my[self.x_index][self.y_index] * py + self.cy[self.x_index][self.y_index]

            self.coord_label.config(text=f"X: {x_data:.6f}, Y: {y_data:.4f}")
        else:
            self.coord_label.config(text="Out of bounds")

if __name__ == "__main__":
    root = tk.Tk()
    root.minsize(600, 400) 
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    app = DigitizerApp(root, screen_width, screen_height)
    root.mainloop()