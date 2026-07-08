#---------------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Admin
#
# Created:     07-07-2026
# Copyright:   (c) Admin 2026
# Licence:     <your licence>
#---------------------------------------------------------------------------------------
import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# PORTABLE DESKTOP ROUTING AUTOMATION
DESKTOP_PATH = os.path.join(os.path.expanduser("~"), "Desktop", "PerformanceTracker_Data")
os.makedirs(DESKTOP_PATH, exist_ok=True)
DATA_FILE = os.path.join(DESKTOP_PATH, "universal_performance_db.json")

def load_raw_database():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {"config": {}, "logs": {}}
    return {"config": {}, "logs": {}}

def save_raw_database(data):
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)
        return True
    except Exception as e:
        messagebox.showerror("Local Save Failure", f"Failed to write data to Desktop:\n{str(e)}")
        return False

class CommercialTelemetryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("STUDY TRACKER STUDIO v4.0")
        self.root.geometry("1340x840") # GEOMETRY SPECIFIER FIX APPLIED HERE
        self.root.configure(bg="#0b0f17")

        self.db = load_raw_database()
        if "config" not in self.db: self.db["config"] = {}
        if "logs" not in self.db: self.db["logs"] = {}

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure(".", background="#0b0f17", foreground="#ffffff")
        self.style.configure("TCombobox", fieldbackground="#161b26", background="#111622", foreground="#ffffff")

        # ----------------- LEFT SIDE PANEL (INPUT MATRIX) -----------------
        self.left_panel = tk.Frame(root, bg="#111622", width=480, bd=0)
        self.left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=15, pady=15)
        self.left_panel.pack_propagate(False)

        lbl_brand = tk.Label(self.left_panel, text="STUDY METRICS ENGINE", font=("Segoe UI", 16, "bold"), bg="#111622", fg="#00e5ff")
        lbl_brand.pack(side=tk.TOP, pady=15)

        # --- INLINE EASY CONFIGURATION HUB ---
        config_hub = tk.LabelFrame(self.left_panel, text=" ADD EXAMS & SUBJECTS ", bg="#161b26", fg="#39ff14", font=("Segoe UI", 10, "bold"), bd=1)
        config_hub.pack(side=tk.TOP, fill=tk.X, padx=15, pady=5, ipady=8)

        # Row 1: Exam Selection / Dropdown
        r1 = tk.Frame(config_hub, bg="#161b26")
        r1.pack(fill=tk.X, padx=10, pady=4)
        tk.Label(r1, text="EXAM TARGET:", font=("Segoe UI", 10, "bold"), bg="#161b26", fg="#ffffff", width=14, anchor="w").pack(side=tk.LEFT)
        self.cb_exam = ttk.Combobox(r1, values=["NDA", "KCET", "NEET", "BOARDS"], font=("Segoe UI", 10))
        self.cb_exam.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        self.cb_exam.set("NDA")

        # Row 2: Subject Input
        r2 = tk.Frame(config_hub, bg="#161b26")
        r2.pack(fill=tk.X, padx=10, pady=4)
        tk.Label(r2, text="SUBJECT NAME:", font=("Segoe UI", 10, "bold"), bg="#161b26", fg="#ffffff", width=14, anchor="w").pack(side=tk.LEFT)
        self.ent_subject = tk.Entry(r2, bg="#111622", fg="#ffffff", insertbackground="white", font=("Segoe UI", 10), bd=1)
        self.ent_subject.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        # Row 3: Daily Limit Spinner + Save Button
        r3 = tk.Frame(config_hub, bg="#161b26")
        r3.pack(fill=tk.X, padx=10, pady=4)
        tk.Label(r3, text="DAILY GOAL CAP:", font=("Segoe UI", 10, "bold"), bg="#161b26", fg="#ffffff", width=14, anchor="w").pack(side=tk.LEFT)
        self.spin_cap = tk.Spinbox(r3, from_=1, to=100, bg="#111622", fg="#ffffff", buttonbackground="#161b26", font=("Segoe UI", 10, "bold"), width=5)
        self.spin_cap.pack(side=tk.LEFT)

        btn_add = tk.Button(r3, text="+ ADD SUBJECT", bg="#39ff14", fg="#0b0f17", font=("Segoe UI", 9, "bold"), bd=0, padx=15, command=self.inline_add_subject)
        btn_add.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))

        # Bottom Core Save Button
        btn_frame = tk.Frame(self.left_panel, bg="#111622")
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=15, padx=20)

        btn_log = tk.Button(btn_frame, text="SAVE TODAY'S PERFORMANCE", bg="#00e5ff", fg="#0b0f17", font=("Segoe UI", 12, "bold"), bd=0, height=2, command=self.commit_daily_telemetry)
        btn_log.pack(fill=tk.X)

        # Middle Scrollable Window Framework
        self.scroll_container = tk.Frame(self.left_panel, bg="#111622")
        self.scroll_container.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=10)

        self.canvas = tk.Canvas(self.scroll_container, bg="#111622", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.scroll_container, orient="vertical", command=self.canvas.yview)
        self.scroll_content = tk.Frame(self.canvas, bg="#111622")

        self.scroll_content.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.scroll_content.bind_all("<MouseWheel>", lambda e: self.canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        self.canvas.create_window((0, 0), window=self.scroll_content, anchor="nw", width=430)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.input_object_registry = {}
        self.rebuild_dynamic_input_grid()

        # ----------------- RIGHT SIDE PANEL (DASHBOARD) -----------------
        self.right_panel = tk.Frame(root, bg="#0b0f17")
        self.right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=15, pady=15)

        search_bar = tk.Frame(self.right_panel, bg="#111622", height=65)
        search_bar.pack(side=tk.TOP, fill=tk.X, pady=(0, 15), ipady=5)
        search_bar.pack_propagate(False)

        lbl_search = tk.Label(search_bar, text="View Performance History Sunday (YYYY-MM-DD):", bg="#111622", fg="#ffffff", font=("Segoe UI", 11, "bold"))
        lbl_search.pack(side=tk.LEFT, padx=15)

        self.search_entry = tk.Entry(search_bar, bg="#161b26", fg="#ffffff", insertbackground="white", width=15, font=("Segoe UI", 11, "bold"), bd=2)
        self.search_entry.pack(side=tk.LEFT, padx=5)

        btn_search = tk.Button(search_bar, text="LOAD CHARTS", bg="#1b2234", fg="#00e5ff", font=("Segoe UI", 10, "bold"), bd=0, padx=20, command=self.trigger_historical_query)
        btn_search.pack(side=tk.LEFT, padx=15)

        self.chart_container = tk.Frame(self.right_panel, bg="#0b0f17")
        self.chart_container.pack(fill=tk.BOTH, expand=True)

        self.update_combobox_list()
        self.render_dashboard_view()

    def update_combobox_list(self):
        existing_exams = list(self.db["config"].keys())
        default_options = ["NDA", "KCET", "NEET", "BOARDS"]
        combined = list(set(existing_exams + default_options))
        self.cb_exam['values'] = combined

    def rebuild_dynamic_input_grid(self):
        for widget in self.scroll_content.winfo_children():
            widget.destroy()
        self.input_object_registry.clear()

        if not self.db["config"]:
            lbl_hint = tk.Label(self.scroll_content, text="[TRACKER IS EMPTY]\nUse the panel above to add your custom\nExams and Subjects instantly.", bg="#111622", fg="#8a99ad", font=("Segoe UI", 11, "italic"))
            lbl_hint.pack(pady=40, padx=20)
            return

        for exam, subjects in self.db["config"].items():
            box_frame = tk.LabelFrame(self.scroll_content, text=f"  {exam.upper()} TARGETS  ", bg="#111622", fg="#00e5ff", font=("Segoe UI", 11, "bold"), bd=1, labelanchor="nw")
            box_frame.pack(fill=tk.X, padx=10, pady=10, ipady=6)
            self.input_object_registry[exam] = {}

            for subject, limit in subjects.items():
                row = tk.Frame(box_frame, bg="#111622")
                row.pack(fill=tk.X, padx=15, pady=4)

                # DELETE ACCIDENT RED BUTTON
                btn_del = tk.Button(row, text="✕", bg="#111622", fg="#ff3366", activebackground="#ff3366", activeforeground="#ffffff", font=("Segoe UI", 9, "bold"), bd=0, padx=5, command=lambda e=exam, s=subject: self.delete_individual_subject(e, s))
                btn_del.pack(side=tk.LEFT, padx=(0, 5))

                lbl = tk.Label(row, text=f"{subject} (Goal: {limit})", bg="#111622", fg="#ffffff", width=16, anchor="w", font=("Segoe UI", 11))
                lbl.pack(side=tk.LEFT)

                spin = tk.Spinbox(row, from_=0, to=limit, width=5, bg="#161b26", fg="#ffffff", buttonbackground="#111622", font=("Segoe UI", 11, "bold"), bd=1)
                spin.pack(side=tk.RIGHT)
                self.input_object_registry[exam][subject] = spin

    def inline_add_subject(self):
        exam = self.cb_exam.get().strip().upper()
        subject = self.ent_subject.get().strip()
        try:
            lim = int(self.spin_cap.get())
        except ValueError:
            return

        if not exam or not subject:
            messagebox.showwarning("Missing Data", "Please write an Exam name and a Subject name first!")
            return

        # FIXED MULTI-SUBJECT INJECTION
        if exam not in self.db["config"]:
            self.db["config"][exam] = {}
        self.db["config"][exam][subject] = lim

        if save_raw_database(self.db):
            self.ent_subject.delete(0, tk.END)
            self.update_combobox_list()
            self.rebuild_dynamic_input_grid()
            self.render_dashboard_view()

    def delete_individual_subject(self, exam, subject):
        if exam in self.db["config"] and subject in self.db["config"][exam]:
            del self.db["config"][exam][subject]
            if not self.db["config"][exam]:
                del self.db["config"][exam]

            if save_raw_database(self.db):
                self.update_combobox_list()
                self.rebuild_dynamic_input_grid()
                self.render_dashboard_view()

    def commit_daily_telemetry(self):
        today_str = datetime.now().strftime("%Y-%m-%d")
        day_entry = {}

        for exam, sub_dict in self.input_object_registry.items():
            day_entry[exam] = {}
            for subject, spinbox in sub_dict.items():
                day_entry[exam][subject] = int(spinbox.get())

        self.db["logs"][today_str] = day_entry
        if save_raw_database(self.db):
            messagebox.showinfo("Saved!", "Your scores have been logged safely on your Desktop!")
        self.render_dashboard_view()

    def trigger_historical_query(self):
        target_str = self.search_entry.get().strip()
        try:
            target_date = datetime.strptime(target_str, "%Y-%m-%d")
            if target_date.weekday() != 6:
                messagebox.showwarning("Warning", "Charts compile on Sundays! Please enter a Sunday date.")
                return
            self.render_dashboard_view(forced_sunday_str=target_str)
        except ValueError:
            messagebox.showerror("Error", "Use format: YYYY-MM-DD")

    def render_dashboard_view(self, forced_sunday_str=None):
        for widget in self.chart_container.winfo_children():
            widget.destroy()

        today = datetime.now()
        is_sunday = (today.weekday() == 6)

        if forced_sunday_str:
            target_sunday_str = forced_sunday_str
            title_tag = f"WEEKLY HISTORY OVERVIEW: {target_sunday_str}"
        elif is_sunday:
            target_sunday_str = today.strftime("%Y-%m-%d")
            title_tag = f"WEEKLY REPORT FOR: {target_sunday_str}"
        else:
            lbl_wait = tk.Label(self.chart_container,
                                text=f"[WAITING FOR SUNDAY ARCHIVE]\n\nToday is {today.strftime('%A')}.\nWeekly stats generate automatically every Sunday night.\n\nTo look at old records, type a past Sunday date above.",
                                bg="#0b0f17", fg="#8a99ad", font=("Segoe UI", 13, "italic"))
            lbl_wait.pack(expand=True)
            return

        target_sunday_date = datetime.strptime(target_sunday_str, "%Y-%m-%d")
        week_dates = [(target_sunday_date - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]

        flat_averages = {}
        total_gained, total_possible = 0, 0
        data_found = False

        for exam, subjects in self.db["config"].items():
            for subject in subjects.keys():
                flat_averages[f"{exam}\n{subject}"] = {"gained": 0, "possible": 0}

        for date in week_dates:
            if date in self.db["logs"]:
                data_found = True
                for exam, subjects in self.db["config"].items():
                    for subject, max_val in subjects.items():
                        logged_val = self.db["logs"][date].get(exam, {}).get(subject, 0)
                        key = f"{exam}\n{subject}"
                        if key in flat_averages:
                            flat_averages[key]["gained"] += logged_val
                            flat_averages[key]["possible"] += max_val

        if not data_found:
            lbl_none = tk.Label(self.chart_container, text=f"[NO DATA CHRONICLED]\nNo updates saved for the week ending {target_sunday_str}.", bg="#0b0f17", fg="#ff3366", font=("Segoe UI", 13, "bold"))
            lbl_none.pack(expand=True)
            return

        labels = list(flat_averages.keys())
        scores = [(v["gained"]/v["possible"])* 100 if v["possible"] > 0 else 0 for v in flat_averages.values()]

        for v in flat_averages.values():
            total_gained += v["gained"]
            total_possible += v["possible"]

        overall_efficiency = (total_gained / total_possible) * 100 if total_possible > 0 else 0

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5), facecolor="#0b0f17")
        fig.suptitle(title_tag, color='#00e5ff', fontsize=14, fontweight='bold')

        bars = ax1.bar(labels, scores, color="#161b26", edgecolor="#00e5ff", linewidth=1.5)
        ax1.set_title("Subject Score Output (%)", color='#ffffff', fontsize=11, pad=12)
        ax1.set_facecolor("#111622")
        ax1.set_ylim(0, 115)
        ax1.tick_params(colors='#8a99ad', labelsize=8)
        ax1.grid(axis='y', color='#161b26', linestyle='--', alpha=0.7)

        for bar in bars:
            height = bar.get_height()
            ax1.annotate(f'{height:.1f}%', xy=(bar.get_x() + bar.get_width() / 2, height),
                         xytext=(0, 4), textcoords="offset points", ha='center', va='bottom', color='#39ff14', fontsize=8, fontweight='bold')

        ax2.pie([overall_efficiency, 100 - overall_efficiency], labels=['Syllabus Mastered', 'Remaining'], autopct='%1.1f%%', startangle=140,
                colors=['#39ff14', '#ff3366'], textprops={'color': '#ffffff', 'fontsize': 10, 'weight': 'bold'},
                wedgeprops={'edgecolor': '#0b0f17', 'linewidth': 3})
        ax2.set_title(f"Total Weekly Efficiency: {overall_efficiency:.1f}%", color='#ffffff', fontsize=11, pad=12)

        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=self.chart_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = CommercialTelemetryApp(root)
    root.mainloop()