import tkinter as tk
from tkinter import messagebox, filedialog
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from datetime import datetime
import os
import sys
import threading
from PIL import Image, ImageTk

# --- PATH SETUP (Safe for .deb and Linux Installs) ---
if getattr(sys, 'frozen', False):
    APP_PATH = os.path.dirname(sys.executable)
else:
    APP_PATH = os.path.dirname(os.path.abspath(__file__))

# Point to the 'assets' folder correctly
PROJECT_ROOT = os.path.abspath(os.path.join(APP_PATH, '..'))

# ALWAYS save logs to the user's home folder
USER_HOME = os.path.expanduser("~")
LOG_DIR = os.path.join(USER_HOME, "GamesAssistant_Logs")

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

MASTER_LOG_FILE = os.path.join(LOG_DIR, "master_history.log")

# --- LOGIC SETTINGS ---
FIB_SEQUENCE = [1, 1, 2, 3, 5, 8, 13, 21]
CHAOS_SEQUENCES = {
    "Alpha": ["Big", "Small", "Big", "Big", "Small", "Big", "Small"],
    "Beta": ["Small", "Small", "Big", "Small", "Big", "Big", "Small"],
    "Gamma": ["Big", "Big", "Small", "Small", "Small", "Big", "Big"]
}
THEMES = ["cyborg", "superhero", "darkly", "solar", "cosmo", "flatly"]

class BettingApp(ttk.Window):
    def __init__(self):
        super().__init__(themename="cyborg")
        
        # --- ICON SETUP ---
        try:
            icon_path = "/usr/share/gamesassistant/assets/icon.png"
            if not os.path.exists(icon_path):
                icon_path = os.path.join(PROJECT_ROOT, 'assets', 'icon.png')
            if not os.path.exists(icon_path):
                icon_path = os.path.join(APP_PATH, 'assets', 'icon.png')

            if os.path.exists(icon_path):
                pil_image = Image.open(icon_path)
                pil_image = pil_image.resize((32, 32), Image.LANCZOS)
                icon_image = ImageTk.PhotoImage(pil_image)
                self.iconphoto(True, icon_image)
            else:
                print(f"Icon warning: Could not find icon at {icon_path}")
        except Exception as e:
            print(f"Icon error: {e}")

        self.title("GamesAssistant v1.6")
        self.geometry("900x650")
        
        self.current_life_step = 0
        self.base_unit = tk.IntVar(value=3)
        self.current_prediction_index = 0
        
        # --- UI LAYOUT ---
        main_container = ttk.Frame(self)
        main_container.pack(fill=BOTH, expand=True)

        left_panel = ttk.Frame(main_container)
        left_panel.pack(side=LEFT, fill=BOTH, expand=True)

        self.right_panel = ttk.Labelframe(main_container, text="Session Log", padding=10)
        self.right_panel.pack(side=RIGHT, fill=Y, padx=10, pady=10)
        
        self.log_box = tk.Text(self.right_panel, width=30, height=20, font=("Courier", 10), state='disabled', bg="#1a1a1a", fg="#00ff00")
        self.log_box.pack(fill=BOTH, expand=True)

        ttk.Button(self.right_panel, text="💾 Export Log", command=self.export_log_to_file, bootstyle="info-outline").pack(fill=X, pady=5)

        self.create_header(left_panel)
        
        self.notebook = ttk.Notebook(left_panel)
        self.notebook.pack(expand=True, fill=BOTH, padx=10, pady=10)
        
        self.static_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.static_frame, text="Static Mode")
        self.build_static_tab()
        
        self.time_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.time_frame, text="Time Mode")
        self.build_time_tab()

        self.settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_frame, text="Settings")
        self.build_settings_tab()
        
        self.create_controls(left_panel)

    def play_sound(self, sound_type):
        """Plays sound in a separate thread"""
        def _play():
            try:
                # 1. Standard Linux Path (Installed)
                sound_path = f"/usr/share/gamesassistant/assets/sounds/{sound_type}.wav"
                
                # 2. Local Dev Path (Fallback)
                if not os.path.exists(sound_path):
                    sound_path = os.path.join(PROJECT_ROOT, 'assets', 'sounds', f"{sound_type}.wav")
                
                # 3. Binary Relative Path (Fallback)
                if not os.path.exists(sound_path):
                     sound_path = os.path.join(APP_PATH, 'assets', 'sounds', f"{sound_type}.wav")

                if os.path.exists(sound_path):
                    os.system(f"aplay -q {sound_path}")
                else:
                    print(f"Sound missing: {sound_path}")
            except Exception as e:
                print(f"Sound error: {e}")
        
        threading.Thread(target=_play, daemon=True).start()

    def build_settings_tab(self):
        frm = ttk.Frame(self.settings_frame, padding=20)
        frm.pack(fill=BOTH, expand=True)
        ttk.Label(frm, text="App Appearance", font=("Helvetica", 16, "bold")).pack(pady=10)
        ttk.Label(frm, text="Select Theme:").pack(pady=5)
        self.theme_var = tk.StringVar(value="cyborg")
        theme_combo = ttk.Combobox(frm, textvariable=self.theme_var, values=THEMES, state="readonly")
        theme_combo.pack(pady=5)
        theme_combo.bind("<<ComboboxSelected>>", self.change_theme)

    def change_theme(self, event):
        new_theme = self.theme_var.get()
        self.style.theme_use(new_theme)
        if new_theme in ["cosmo", "flatly"]:
            self.log_box.config(bg="white", fg="black")
        else:
            self.log_box.config(bg="#1a1a1a", fg="#00ff00")

    def add_to_log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.log_box.config(state='normal')
        self.log_box.insert(tk.END, log_entry)
        self.log_box.see(tk.END)
        self.log_box.config(state='disabled')
        try:
            with open(MASTER_LOG_FILE, "a") as f: f.write(log_entry)
        except Exception as e:
            print(f"Logging error: {e}")

    def export_log_to_file(self):
        content = self.log_box.get("1.0", tk.END)
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", initialfile=f"session_{datetime.now().strftime('%Y%m%d')}.txt")
        if file_path:
            with open(file_path, "w") as f: f.write(content)
            messagebox.showinfo("Success", f"Saved to {file_path}")

    def create_header(self, parent):
        header_frame = ttk.Frame(parent, padding=10)
        header_frame.pack(fill=X)
        ttk.Label(header_frame, text="Base Unit (₹):", font=("Helvetica", 12)).pack(side=LEFT, padx=5)
        ttk.Entry(header_frame, textvariable=self.base_unit, width=5).pack(side=LEFT)
        ttk.Button(header_frame, text="New Life", command=self.reset_life, bootstyle="danger-outline").pack(side=RIGHT)

    def build_static_tab(self):
        frm = ttk.Frame(self.static_frame, padding=20)
        frm.pack(fill=BOTH, expand=True)
        self.seq_var = tk.StringVar(value="Alpha")
        ttk.Combobox(frm, textvariable=self.seq_var, values=list(CHAOS_SEQUENCES.keys())).pack(pady=5)
        self.static_pred_lbl = ttk.Label(frm, text="READY", font=("Helvetica", 24, "bold"), anchor="center", bootstyle="inverse-info")
        self.static_pred_lbl.pack(pady=20, fill=X)
        ttk.Button(frm, text="Get Next Prediction", command=self.update_static_prediction, bootstyle="success").pack(pady=10)

    def build_time_tab(self):
        frm = ttk.Frame(self.time_frame, padding=20)
        frm.pack(fill=BOTH, expand=True)
        self.time_pred_lbl = ttk.Label(frm, text="WAITING", font=("Helvetica", 24, "bold"), anchor="center", bootstyle="inverse-warning")
        self.time_pred_lbl.pack(pady=20, fill=X)
        ttk.Button(frm, text="Sync Time & Predict", command=self.predict_by_time, bootstyle="warning").pack(pady=10)

    def create_controls(self, parent):
        control_frame = ttk.Labelframe(parent, text="Result Tracker", padding=10)
        control_frame.pack(fill=X, padx=10, pady=10)
        self.bet_display = ttk.Label(control_frame, text="Next Bet: ₹3", font=("Helvetica", 16, "bold"))
        self.bet_display.pack(pady=5)
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(fill=X)
        ttk.Button(btn_frame, text="WIN", command=self.record_win, bootstyle="success", width=10).pack(side=LEFT, padx=20, expand=True)
        ttk.Button(btn_frame, text="LOSS", command=self.record_loss, bootstyle="danger", width=10).pack(side=RIGHT, padx=20, expand=True)

    def update_static_prediction(self):
        seq = CHAOS_SEQUENCES[self.seq_var.get()]
        pred = seq[self.current_prediction_index]
        self.static_pred_lbl.config(text=f"Bet: {pred.upper()}")
        self.current_prediction_index = (self.current_prediction_index + 1) % len(seq)

    def predict_by_time(self):
        now = datetime.now()
        outcome = "BIG" if now.second % 2 == 0 else "SMALL"
        self.time_pred_lbl.config(text=f"{outcome}")

    def update_bet_display(self):
        fib_val = FIB_SEQUENCE[min(self.current_life_step, len(FIB_SEQUENCE)-1)]
        amount = fib_val * self.base_unit.get()
        self.bet_display.config(text=f"Next Bet: ₹{amount}")

    def record_win(self):
        self.play_sound("win")
        self.add_to_log(f"WIN at Step {self.current_life_step + 1}")
        self.current_life_step = max(0, self.current_life_step - 2)
        self.update_bet_display()

    def record_loss(self):
        self.play_sound("loss")
        self.add_to_log(f"LOSS at Step {self.current_life_step + 1}")
        self.current_life_step += 1
        if self.current_life_step >= len(FIB_SEQUENCE):
            self.add_to_log("!!! LIFE DEPLETED !!!")
            messagebox.showwarning("Stop", "Life Depleted. Reset.")
            self.reset_life()
        else:
            self.update_bet_display()

    def reset_life(self):
        self.add_to_log("--- NEW LIFE STARTED ---")
        self.current_life_step = 0
        self.update_bet_display()

if __name__ == "__main__":
    app = BettingApp()
    app.mainloop()
