import tkinter as tk
from tkinter import ttk, font, messagebox, Toplevel
import json
import csv
import os
from datetime import date

# --- Paleta de Colores ---
COLORS = {
    "dark_blue": "#2C3D55", "independence": "#3E4C5E", "charcoal": "#536271",
    "old_lavender": "#6A687A", "wenge": "#84828F", "white": "#FFFFFF",
    "light_gray": "#CCCCCC", "completed_green": "#66BB6A", "circle_bg": "#4A4A4A"
}

# --- Plan de Entrenamiento por Defecto ---
# VERSIÓN CORREGIDA con descripciones completas
default_training_plan = {
    "Lunes": {"focus": "Entrenamiento técnico de Muay Thai.", "activity": "Clase de Muay Thai", "exercises": []},
    "Martes": {"focus": "Fuerza y Potencia (Striking y Brazos).", "activity": None, "exercises": [
        {"name": "Sentadilla Goblet con Mancuerna", "series": 4, "reps": "8-10", "description": "Fundamental para la potencia de tus patadas. Sujeta una mancuerna en vertical contra tu pecho. Baja profundo manteniendo la espalda recta y sube de forma explosiva."},
        {"name": "Remo Renegado (Renegade Row)", "series": 3, "reps": "8 p/brazo", "description": "Fortalece la espalda para jalar en el clinch y el core para la estabilidad. En posición de plancha con mancuernas, rema con un brazo sin girar las caderas."},
        {"name": "Flexiones a Máxima Velocidad", "series": 4, "reps": "AMRAP", "description": "Desarrolla la potencia de empuje para tus puños. Baja de forma controlada y sube con la mayor velocidad posible, sin despegar las manos del suelo."},
        {"name": "Curl de Bíceps con Mancuerna", "series": 3, "reps": "10-12", "description": "Fortalece los bíceps para la fuerza de tracción en el clinch. De pie, con una mancuerna en cada mano, flexiona los codos para llevar las pesas hacia los hombros."},
        {"name": "Extensión de Tríceps sobre la Cabeza", "series": 3, "reps": "10-12", "description": "Añade potencia a la extensión final de tus puñetazos. Sostén una mancuerna con ambas manos sobre tu cabeza y flexiona los codos para bajarla por detrás de la nuca."}
    ]},
    "Miércoles": {"focus": "Ciclismo de Resistencia.", "activity": "Ruta Plana Mapocho 42k", "exercises": []},
    "Jueves": {"focus": "Resistencia Muscular y Fuerza de Clinch.", "activity": None, "exercises": [
        {"name": "Zancadas con Pausa", "series": 3, "reps": "10 p/pierna", "description": "Construye resistencia en las piernas. Sostén las mancuernas, haz una zancada y aguanta 2 segundos en la posición más baja antes de subir. Alterna piernas."},
        {"name": "Press de Hombro de Rodillas", "series": 3, "reps": "12-15", "description": "Para la resistencia de los hombros al golpear. Arrodillado para proteger la espalda, empuja las mancuernas hacia arriba de forma controlada."},
        {"name": "Remo con Banda", "series": 3, "reps": "20", "description": "Simula el agarre y jale constante del clinch. Siéntate, pasa la banda por tus pies y rema llevando los codos hacia atrás, apretando la espalda."},
        {"name": "Fortalecimiento de Cuello (Isométricos)", "series": 2, "reps": "10-15 seg.", "description": "Coloca la palma de tu mano en tu frente y empuja suavemente con la cabeza contra la mano, sin que la cabeza se mueva. Repite en los lados y en la nuca."},
        {"name": "Elevaciones de Mentón", "series": 3, "reps": "15-20", "description": "Acostado boca arriba en el suelo, levanta ligeramente la cabeza y lleva tu mentón hacia el pecho. Mantén la contracción por un segundo y baja lentamente. No uses impulso."},
        {"name": "Plancha (Plank)", "series": 3, "reps": "60 seg.", "description": "Un core fuerte es la base de todo. Mantén una línea recta desde la cabeza a los talones, apretando abdomen y glúteos."},
        {"name": "Giro Ruso (Russian Twist)", "series": 3, "reps": "20 giros", "description": "Fortalece los oblicuos para la rotación en golpes y rodillas. Sentado, inclínate hacia atrás y gira el torso de lado a lado con una mancuerna."}
    ]},
    "Viernes": {"focus": "Entrenamiento técnico de Muay Thai.", "activity": "Clase de Muay Thai", "exercises": []},
    "Sábado": {"focus": "Ciclismo de Intensidad.", "activity": "Ascenso al Cerro San Cristóbal", "exercises": []},
    "Domingo": {"focus": "Movilidad y Recuperación Activa.", "activity": "Sesión de Estiramientos y Movilidad", "exercises": []}
}

# --- Widget Personalizado para los Círculos de Series ---
class SeriesTracker(tk.Frame):
    def __init__(self, parent, total_series, completed_series=0, on_series_change=None, interactive=True):
        super().__init__(parent, bg=COLORS["dark_blue"])
        self.total_series = total_series
        self.completed_series = completed_series
        self.on_series_change = on_series_change
        self.interactive = interactive
        self.series_labels = []
        self._create_widgets()
        self.update_display()

    def _create_widgets(self):
        tk.Label(self, text="Series:", font=("Helvetica", 10), bg=COLORS["dark_blue"], fg=COLORS["light_gray"]).pack(side=tk.LEFT, padx=(0, 10))
        for i in range(self.total_series):
            lbl = tk.Label(self, text="●", font=("Helvetica", 20), bg=COLORS["dark_blue"], fg=COLORS["circle_bg"])
            lbl.pack(side=tk.LEFT, padx=3)
            if self.interactive:
                lbl.config(cursor="hand2")
                lbl.bind("<Button-1>", lambda e, index=i: self._on_circle_click(index))
            self.series_labels.append(lbl)

    def _on_circle_click(self, index):
        self.completed_series = index + 1 if (index + 1) != self.completed_series else index
        self.update_display()
        if self.on_series_change: self.on_series_change(self.completed_series)
            
    def update_display(self):
        for i, lbl in enumerate(self.series_labels):
            lbl.config(fg=COLORS["completed_green"] if i < self.completed_series else COLORS["circle_bg"])

# --- Clase Principal de la Aplicación ---
class TrainingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Plan de Entrenamiento Semanal")
        self.root.geometry("1050x700")
        self.root.configure(bg=COLORS["independence"])

        self.plan_file = "plan.json"
        self.progress_file = "progress.csv"
        
        self.load_plan()
        self.load_progress()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # --- Estilos y Fuentes ---
        self.title_font = font.Font(family="Helvetica", size=18, weight="bold")
        self.subtitle_font = font.Font(family="Helvetica", size=12)
        self.text_font = font.Font(family="Helvetica", size=10)
        self.reps_font = font.Font(family="Helvetica", size=12, weight="bold")
        
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton", padding=6, relief="flat", background=COLORS["charcoal"], foreground=COLORS["white"], font=self.subtitle_font)
        style.map("TButton", background=[('active', COLORS["old_lavender"])])
        style.configure("TPanedwindow", background=COLORS["independence"])
        style.configure("Days.TButton", font=("Helvetica", 9), padding=(0, 6))

        self.days_map = {'Monday': 'Lunes', 'Tuesday': 'Martes', 'Wednesday': 'Miércoles', 'Thursday': 'Jueves', 'Friday': 'Viernes', 'Saturday': 'Sábado', 'Sunday': 'Domingo'}
        
        self.create_widgets()

    def load_plan(self):
        try:
            with open(self.plan_file, 'r', encoding='utf-8') as f:
                self.training_plan = json.load(f)
            # Bucle de migración para asegurar compatibilidad con versiones antiguas del plan.json
            for day_name, day_content in self.training_plan.items():
                for i, ex in enumerate(day_content.get("exercises", [])):
                    default_ex = next((item for item in default_training_plan.get(day_name, {}).get("exercises", []) if item["name"] == ex["name"]), None)
                    if default_ex:
                        if "series" not in ex: self.training_plan[day_name]["exercises"][i]["series"] = default_ex["series"]
                        if "reps" not in ex: self.training_plan[day_name]["exercises"][i]["reps"] = default_ex["reps"]
        except (FileNotFoundError, json.JSONDecodeError):
            self.training_plan = default_training_plan

    def load_progress(self):
        self.completion_status = {}
        if not os.path.exists(self.progress_file): return
        with open(self.progress_file, mode='r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                date_str, item_name, series_completed = row['Date'], row['Item'], int(row['SeriesCompleted'])
                if date_str not in self.completion_status: self.completion_status[date_str] = {}
                self.completion_status[date_str][item_name] = {"series_completed": series_completed}

    def save_plan(self):
        with open(self.plan_file, 'w', encoding='utf-8') as f:
            json.dump(self.training_plan, f, ensure_ascii=False, indent=4)

    def save_progress(self):
        with open(self.progress_file, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Date', 'Item', 'SeriesCompleted'])
            for date_str, items in self.completion_status.items():
                for item_name, progress in items.items():
                    writer.writerow([date_str, item_name, progress.get("series_completed", 0)])

    def on_closing(self):
        self.save_plan()
        self.save_progress()
        self.root.destroy()

    def create_widgets(self):
        self.root.grid_rowconfigure(0, weight=1); self.root.grid_columnconfigure(0, weight=1)
        main_frame = tk.Frame(self.root, bg=COLORS["independence"], padx=20, pady=20)
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.grid_rowconfigure(3, weight=1); main_frame.grid_columnconfigure(0, weight=1)
        title_label = tk.Label(main_frame, text="Tu Plan de Entrenamiento", font=self.title_font, bg=COLORS["independence"], fg=COLORS["white"])
        title_label.grid(row=0, column=0, pady=(0, 20))
        days_frame = tk.Frame(main_frame, bg=COLORS["independence"])
        days_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        for i, day in enumerate(self.training_plan.keys()):
            days_frame.grid_columnconfigure(i, weight=1)
            ttk.Button(days_frame, text=day, style="Days.TButton", command=lambda d=day: self.show_day_plan(d)).grid(row=0, column=i, sticky="ew", padx=2)
        self.focus_label = tk.Label(main_frame, text="Selecciona un día para comenzar", font=self.subtitle_font, bg=COLORS["independence"], fg=COLORS["light_gray"])
        self.focus_label.grid(row=2, column=0, pady=10)
        paned_window = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned_window.grid(row=3, column=0, sticky="nsew", pady=(10,0))
        left_panel = tk.Frame(paned_window, bg=COLORS["dark_blue"])
        paned_window.add(left_panel, weight=1)
        left_panel.grid_rowconfigure(0, weight=1); left_panel.grid_columnconfigure(0, weight=1)
        self.exercise_listbox = tk.Listbox(left_panel, font=self.text_font, bg=COLORS["dark_blue"], fg=COLORS["white"], 
                                           selectbackground=COLORS["wenge"], borderwidth=0, highlightthickness=0, selectforeground=COLORS["white"])
        self.exercise_listbox.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.exercise_listbox.bind("<<ListboxSelect>>", self.show_exercise_description)
        button_frame = tk.Frame(left_panel, bg=COLORS["dark_blue"])
        button_frame.grid(row=1, column=0, pady=10)
        ttk.Button(button_frame, text="Completar Todo ✓", command=self.complete_all_series).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Agregar", command=self.add_exercise).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Editar", command=self.edit_exercise).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Eliminar", command=self.delete_exercise).pack(side=tk.LEFT, padx=5)
        self.desc_panel = tk.Frame(paned_window, bg=COLORS["dark_blue"])
        paned_window.add(self.desc_panel, weight=2)
        self.desc_panel.grid_rowconfigure(2, weight=1); self.desc_panel.grid_columnconfigure(0, weight=1)
        self.tracker_reps_frame = tk.Frame(self.desc_panel, bg=COLORS["dark_blue"])
        self.tracker_reps_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 5))
        self.series_tracker_frame = tk.Frame(self.tracker_reps_frame, bg=COLORS["dark_blue"])
        self.series_tracker_frame.pack(side=tk.LEFT)
        self.reps_label = tk.Label(self.tracker_reps_frame, text="", font=self.reps_font, bg=COLORS["dark_blue"], fg=COLORS["wenge"])
        self.reps_label.pack(side=tk.RIGHT, padx=20)
        self.description_text = tk.Text(self.desc_panel, wrap=tk.WORD, font=self.text_font, bg=COLORS["dark_blue"], 
                                        fg=COLORS["white"], borderwidth=0, highlightthickness=0, insertbackground=COLORS["white"], height=10)
        self.description_text.grid(row=1, column=0, sticky="nsew", padx=15, pady=15)
        self.description_text.config(state=tk.DISABLED)

    def show_day_plan(self, day):
        self.current_day = day
        plan = self.training_plan.get(day, {})
        self.focus_label.config(text=f"Foco: {plan.get('focus', 'N/A')}")
        self.exercise_listbox.delete(0, tk.END)
        self.reps_label.config(text="")
        for widget in self.series_tracker_frame.winfo_children(): widget.destroy()
        self.description_text.config(state=tk.NORMAL); self.description_text.delete("1.0", tk.END); self.description_text.config(state=tk.DISABLED)
        items_to_show = [plan["activity"]] if plan.get("activity") else [ex["name"] for ex in plan.get("exercises", [])]
        if not items_to_show:
            self.description_text.config(state=tk.NORMAL); self.description_text.insert("1.0", "Día de descanso."); self.description_text.config(state=tk.DISABLED)
        else:
            today_name, today_str, todays_progress = self.days_map[date.today().strftime('%A')], str(date.today()), self.completion_status.get(str(date.today()), {})
            is_today = (self.current_day == today_name)
            for i, item_name in enumerate(items_to_show):
                self.exercise_listbox.insert(tk.END, item_name)
                if is_today:
                    series_completed = todays_progress.get(item_name, {}).get("series_completed", 0)
                    total_series = 1
                    ex_data = next((ex for ex in plan.get("exercises",[]) if ex["name"] == item_name), None)
                    if ex_data: total_series = ex_data.get("series", 1)
                    if series_completed >= total_series: self.exercise_listbox.itemconfig(i, {'fg': COLORS["completed_green"]})
            self.exercise_listbox.select_set(0)
            self.show_exercise_description(None)

    def show_exercise_description(self, event):
        if not self.exercise_listbox.curselection(): return
        item_name = self.exercise_listbox.get(self.exercise_listbox.curselection()[0])
        plan_today = self.training_plan[self.current_day]
        description, total_series, reps = "", 0, ""
        exercise_data = next((ex for ex in plan_today.get("exercises", []) if ex["name"] == item_name), None)
        if exercise_data:
            description, total_series, reps = exercise_data.get("description", ""), exercise_data.get("series", 0), exercise_data.get("reps", "")
        elif item_name == plan_today.get("activity"):
            description, total_series = f"Actividad principal de hoy:\n\n{plan_today['focus']}", 1
        self.description_text.config(state=tk.NORMAL); self.description_text.delete("1.0", tk.END); self.description_text.insert("1.0", description); self.description_text.config(state=tk.DISABLED)
        self.reps_label.config(text=f"Reps: {reps}" if reps else "")
        for widget in self.series_tracker_frame.winfo_children(): widget.destroy()
        today_name = self.days_map[date.today().strftime('%A')]
        is_today = (self.current_day == today_name)
        if total_series > 0:
            completed_series = 0
            if is_today:
                progress = self.completion_status.get(str(date.today()), {}).get(item_name, {})
                completed_series = progress.get("series_completed", 0)
            def on_series_change(new_count): self.update_series_progress(item_name, new_count)
            tracker = SeriesTracker(self.series_tracker_frame, total_series, completed_series, on_series_change, interactive=is_today)
            tracker.pack()

    def update_series_progress(self, item_name, completed_count):
        today_str = str(date.today())
        if today_str not in self.completion_status: self.completion_status[today_str] = {}
        if item_name not in self.completion_status[today_str]: self.completion_status[today_str][item_name] = {}
        self.completion_status[today_str][item_name]["series_completed"] = completed_count
        self.refresh_list_colors()

    def refresh_list_colors(self):
        today_name = self.days_map[date.today().strftime('%A')]
        if self.current_day != today_name: return
        today_str, todays_progress = str(date.today()), self.completion_status.get(str(date.today()), {})
        plan_today = self.training_plan[self.current_day]
        for i in range(self.exercise_listbox.size()):
            item_name = self.exercise_listbox.get(i)
            series_completed = todays_progress.get(item_name, {}).get("series_completed", 0)
            total_series = 1
            ex_data = next((ex for ex in plan_today.get("exercises", []) if ex["name"] == item_name), None)
            if ex_data: total_series = ex_data.get("series", 1)
            if series_completed >= total_series: self.exercise_listbox.itemconfig(i, {'fg': COLORS["completed_green"]})
            else: self.exercise_listbox.itemconfig(i, {'fg': COLORS["white"]})
    
    def complete_all_series(self):
        if not self.exercise_listbox.curselection(): return
        today_name = self.days_map[date.today().strftime('%A')]
        if self.current_day != today_name: messagebox.showinfo("Información", "Solo puedes registrar el progreso para el día de hoy."); return
        item_name = self.exercise_listbox.get(self.exercise_listbox.curselection()[0])
        plan_today = self.training_plan[self.current_day]
        total_series = 1
        ex_data = next((ex for ex in plan_today.get("exercises", []) if ex["name"] == item_name), None)
        if ex_data: total_series = ex_data.get("series", 1)
        self.update_series_progress(item_name, total_series)
        self.show_exercise_description(None)

    def add_exercise(self):
        if not hasattr(self, 'current_day'): messagebox.showwarning("Advertencia", "Por favor, selecciona un día primero."); return
        if self.training_plan[self.current_day].get("activity"): messagebox.showinfo("Información", "No se pueden agregar ejercicios a un día con una actividad principal."); return
        self.show_editor_window(mode="add")

    def edit_exercise(self):
        if not hasattr(self, 'current_day') or not self.exercise_listbox.curselection(): messagebox.showwarning("Advertencia", "Selecciona un ejercicio para editar."); return
        item_name = self.exercise_listbox.get(self.exercise_listbox.curselection()[0])
        if item_name == self.training_plan[self.current_day].get("activity"): messagebox.showinfo("Información", "Las actividades principales no se editan."); return
        exercise_index = next((i for i, ex in enumerate(self.training_plan[self.current_day]["exercises"]) if ex["name"] == item_name), -1)
        if exercise_index != -1: self.show_editor_window(mode="edit", selected_index=exercise_index)

    def delete_exercise(self):
        if not hasattr(self, 'current_day') or not self.exercise_listbox.curselection(): messagebox.showwarning("Advertencia", "Selecciona un ejercicio para eliminar."); return
        item_name = self.exercise_listbox.get(self.exercise_listbox.curselection()[0])
        if item_name == self.training_plan[self.current_day].get("activity"): messagebox.showinfo("Información", "Las actividades principales no se pueden eliminar."); return
        if messagebox.askyesno("Confirmar Eliminación", f"¿Eliminar '{item_name}'?"):
            self.training_plan[self.current_day]["exercises"] = [ex for ex in self.training_plan[self.current_day]["exercises"] if ex['name'] != item_name]
            self.show_day_plan(self.current_day)

    def show_editor_window(self, mode, selected_index=None):
        editor = Toplevel(self.root)
        editor.title(f"{'Editar' if mode == 'edit' else 'Agregar'} Ejercicio")
        editor.geometry("400x450")
        editor.configure(bg=COLORS["independence"])
        editor.transient(self.root); editor.grab_set()
        tk.Label(editor, text="Nombre:", bg=COLORS["independence"], fg=COLORS["white"]).pack(pady=(10,0))
        name_entry = tk.Entry(editor, width=50, bg=COLORS["dark_blue"], fg=COLORS["white"], insertbackground=COLORS["white"])
        name_entry.pack(pady=5, padx=10)
        tk.Label(editor, text="Series:", bg=COLORS["independence"], fg=COLORS["white"]).pack(pady=(10,0))
        series_entry = tk.Entry(editor, width=10, bg=COLORS["dark_blue"], fg=COLORS["white"], insertbackground=COLORS["white"])
        series_entry.pack(pady=5, padx=10)
        tk.Label(editor, text="Repeticiones/Objetivo:", bg=COLORS["independence"], fg=COLORS["white"]).pack(pady=(10,0))
        reps_entry = tk.Entry(editor, width=50, bg=COLORS["dark_blue"], fg=COLORS["white"], insertbackground=COLORS["white"])
        reps_entry.pack(pady=5, padx=10)
        tk.Label(editor, text="Descripción:", bg=COLORS["independence"], fg=COLORS["white"]).pack(pady=(10,0))
        desc_text = tk.Text(editor, width=50, height=8, wrap=tk.WORD, bg=COLORS["dark_blue"], fg=COLORS["white"], insertbackground=COLORS["white"])
        desc_text.pack(pady=5, padx=10)
        if mode == "edit" and selected_index is not None:
            exercise = self.training_plan[self.current_day]["exercises"][selected_index]
            name_entry.insert(0, exercise["name"])
            series_entry.insert(0, exercise.get("series", 1))
            reps_entry.insert(0, exercise.get("reps", ""))
            desc_text.insert("1.0", exercise["description"])
        def save_changes():
            new_name, new_desc, new_reps = name_entry.get().strip(), desc_text.get("1.0", tk.END).strip(), reps_entry.get().strip()
            try:
                new_series = int(series_entry.get().strip())
                if new_series < 1: raise ValueError
            except ValueError:
                messagebox.showerror("Error", "El número de series debe ser un número entero positivo.", parent=editor); return
            if not new_name:
                messagebox.showerror("Error", "El nombre no puede estar vacío.", parent=editor); return
            new_exercise = {"name": new_name, "series": new_series, "reps": new_reps, "description": new_desc}
            if mode == "edit" and selected_index is not None:
                self.training_plan[self.current_day]["exercises"][selected_index] = new_exercise
            else:
                self.training_plan[self.current_day]["exercises"].append(new_exercise)
            self.show_day_plan(self.current_day)
            editor.destroy()
        save_button = ttk.Button(editor, text="Guardar", command=save_changes)
        save_button.pack(pady=10)
        self.root.wait_window(editor)

if __name__ == "__main__":
    root = tk.Tk()
    app = TrainingApp(root)
    root.mainloop()