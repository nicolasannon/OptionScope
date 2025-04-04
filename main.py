import customtkinter as ctk
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import mplcursors
import greek_functions as gf
from PIL import Image

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class OptionScopeApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("optionScope")
        self.geometry("1400x800")
        self.S_range = np.linspace(1, 200, 200)
        self.params = {"K": 100.0, "sigma": 0.2, "r": 0.05, "T": 1.0}
        self.selected_param = "K"
        self.option_type = "PUT"
        self.first_greek = "Delta"
        self.second_greek = "Gamma"
        self.cursor = None
        self.create_widgets()
        self.plot_graph()

    def create_widgets(self):
        left_frame = ctk.CTkFrame(self)
        left_frame.pack(side="left", fill="y", padx=10, pady=10)
        try:
            logo_image = ctk.CTkImage(Image.open("optionScopeLogo.png"), size=(150, 150))
            logo_label = ctk.CTkLabel(left_frame, image=logo_image, text="")
            logo_label.image = logo_image
            logo_label.pack(pady=10)
        except Exception as e:
            print("Could not load logo:", e)
        call_put_frame = ctk.CTkFrame(left_frame)
        call_put_frame.pack(pady=10)
        self.call_button = ctk.CTkButton(call_put_frame, text="CALL", command=lambda: self.set_option("CALL"))
        self.call_button.pack(side="left", padx=5)
        self.put_button = ctk.CTkButton(call_put_frame, text="PUT", command=lambda: self.set_option("PUT"))
        self.put_button.pack(side="left", padx=5)
        self.highlight_call_put()
        ctk.CTkLabel(left_frame, text="Paramètres :").pack(pady=5)
        self.param_entries = {}
        limits = {"K": (1, 200), "sigma": (0.01, 1), "r": (0.0, 0.2), "T": (0.1, 10)}
        for name in ["K", "sigma", "r", "T"]:
            frame = ctk.CTkFrame(left_frame)
            frame.pack(pady=2, fill="x", padx=5)
            btn = ctk.CTkButton(frame, text=name, width=50, command=lambda n=name: self.select_param(n))
            btn.pack(side="left")
            entry = ctk.CTkEntry(frame, width=100)
            entry.insert(0, str(self.params[name]))
            entry.pack(side="right")
            self.param_entries[name] = (entry, btn)
        self.highlight_param()
        self.slider = ctk.CTkSlider(self, from_=limits["K"][0], to=limits["K"][1], command=self.update_slider_param)
        self.slider.set(self.params["K"])
        self.slider.pack(fill="x", padx=10, pady=10)
        self.greek_buttons = {}
        for num, label in enumerate(["Choisir Greek 1 :", "Choisir Greek 2 :"], start=1):
            ctk.CTkLabel(left_frame, text=label).pack(pady=5)
            for greek in ["Delta", "Gamma", "Vega", "Theta", "Rho"]:
                btn = ctk.CTkButton(left_frame, text=greek, command=lambda g=greek, n=num: self.set_greek(g, n))
                btn.pack(pady=2)
                self.greek_buttons[(greek, num)] = btn
        self.highlight_greeks()
        self.clear_button = ctk.CTkButton(left_frame, text="Effacer commentaire", command=self.clear_comments)
        self.clear_button.pack(pady=10)
        self.fig, self.ax1 = plt.subplots()
        self.ax2 = self.ax1.twinx()
        self.fig.tight_layout(pad=3)
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.get_tk_widget().pack(side="right", fill="both", expand=True)

    def highlight_call_put(self):
        self.call_button.configure(fg_color="green" if self.option_type == "CALL" else "gray")
        self.put_button.configure(fg_color="green" if self.option_type == "PUT" else "gray")

    def highlight_greeks(self):
        for (greek, num), btn in self.greek_buttons.items():
            selected = (num == 1 and greek == self.first_greek) or (num == 2 and greek == self.second_greek)
            btn.configure(fg_color="green" if selected else "gray")

    def highlight_param(self):
        for name, (_, btn) in self.param_entries.items():
            btn.configure(fg_color="green" if name == self.selected_param else "gray")

    def select_param(self, name):
        self.selected_param = name
        self.highlight_param()
        limits = {"K": (1, 200), "sigma": (0.01, 1), "r": (0.0, 0.2), "T": (0.1, 10)}
        self.slider.configure(from_=limits[name][0], to=limits[name][1])
        self.slider.set(self.params[name])

    def set_option(self, opt):
        self.option_type = opt
        self.highlight_call_put()
        self.plot_graph()

    def set_greek(self, greek, num):
        if num == 1:
            self.first_greek = greek
        else:
            self.second_greek = greek
        self.highlight_greeks()
        self.plot_graph()

    def update_slider_param(self, value):
        self.params[self.selected_param] = float(value)
        entry, _ = self.param_entries[self.selected_param]
        entry.delete(0, 'end')
        entry.insert(0, f"{float(value):.4f}")
        self.plot_graph()

    def plot_graph(self):
        self.ax1.clear()
        self.ax2.clear()
        funcs_put = {"Delta": gf.delta_put, "Gamma": gf.gamma, "Vega": gf.vega, "Theta": gf.theta_put, "Rho": gf.rho_put}
        funcs_call = {
            "Delta": lambda S, K, T, r, sigma: gf.delta_put(S, K, T, r, sigma) + 1,
            "Gamma": gf.gamma,
            "Vega": gf.vega,
            "Theta": lambda S, K, T, r, sigma: gf.theta_put(S, K, T, r, sigma) + r * K * np.exp(-r * T),
            "Rho": lambda S, K, T, r, sigma: gf.rho_put(S, K, T, r, sigma) + K * T * np.exp(-r * T)
        }
        funcs = funcs_call if self.option_type == "CALL" else funcs_put
        greek1_vals = funcs[self.first_greek](self.S_range, self.params["K"], self.params["T"], self.params["r"], self.params["sigma"])
        line1, = self.ax1.plot(self.S_range, greek1_vals, "b", label=self.first_greek)
        self.ax1.set_ylabel(self.first_greek, color="blue")
        greek2_vals = funcs[self.second_greek](self.S_range, self.params["K"], self.params["T"], self.params["r"], self.params["sigma"])
        line2, = self.ax2.plot(self.S_range, greek2_vals, "orange", label=self.second_greek)
        self.ax2.set_ylabel(self.second_greek, color="orange")
        self.ax2.relim()
        self.ax2.autoscale_view()
        self.ax2.margins(0.1)
        if self.option_type == "CALL":
            price = gf.put_price(100, self.params["K"], self.params["T"], self.params["r"], self.params["sigma"]) + 100 - self.params["K"] * np.exp(-self.params["r"] * self.params["T"])
        else:
            price = gf.put_price(100, self.params["K"], self.params["T"], self.params["r"], self.params["sigma"])
        greek1_100 = funcs[self.first_greek](100, self.params["K"], self.params["T"], self.params["r"], self.params["sigma"])
        greek2_100 = funcs[self.second_greek](100, self.params["K"], self.params["T"], self.params["r"], self.params["sigma"])
        self.ax1.set_title(f"Prix du {self.option_type} (S=100): {price:.4f}\n{self.first_greek}: {greek1_100:.4f}, {self.second_greek}: {greek2_100:.4f}")
        self.ax1.set_xlabel("Prix du sous-jacent (S)")
        self.ax1.grid(True)
        self.cursor = mplcursors.cursor([line1, line2], hover=True)
        self.cursor.connect("add", lambda sel: self.update_annotation(sel, funcs))
        self.canvas.draw_idle()

    def update_annotation(self, sel, funcs):
        S_value = sel.target[0]
        text = (f"S = {S_value:.2f}\n{self.first_greek} = {funcs[self.first_greek](S_value, self.params['K'], self.params['T'], self.params['r'], self.params['sigma']):.4f}\n{self.second_greek} = {funcs[self.second_greek](S_value, self.params['K'], self.params['T'], self.params['r'], self.params['sigma']):.4f}")
        sel.annotation.set_text(text)

    def clear_comments(self):
        if self.cursor is not None:
            self.cursor.clear()
        self.canvas.draw_idle()

if __name__ == "__main__":
    app = OptionScopeApp()
    app.mainloop()
