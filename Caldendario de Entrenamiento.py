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
default_training_plan = {
    "Lunes": {"focus": "Entrenamiento técnico de Muay Thai.", "activity": "Clase de Muay Thai", "exercises": []},
    "Martes": {"focus": "Fuerza y Potencia (Striking y Brazos).", "activity": None, "exercises": [
        {"name": "Sentadilla Goblet con Mancuerna", "series": 4, "description": "Fundamental para la potencia de tus patadas..."},
        {"name": "Remo Renegado (Renegade Row)", "series": 3, "description": "Fortalece la espalda para jalar en el clinch..."},
        {"name": "Flexiones a Máxima Velocidad", "series": 4, "description": "Desarrolla la potencia de empuje para tus puños..."},
        {"name": "Curl de Bíceps con Mancuerna", "series": 3, "description": "Fortalece los bíceps para la fuerza de tracción..."},
        {"name": "Extensión de Tríceps sobre la Cabeza", "series": 3, "description": "Añade potencia a la extensión final de tus puñetazos..."}
    ]},
    "Miércoles": {"focus": "Ciclismo de Resistencia.", "activity": "Ruta Plana Mapocho 42k", "exercises": []},
    "Jueves": {"focus": "Resistencia Muscular y Fuerza de Clinch.", "activity": None, "exercises": [
        {"name": "Zancadas con Pausa", "series": 3, "description": "Construye resistencia en las piernas..."},
        {"name": "Press de Hombro de Rodillas", "series": 3, "description": "Para la resistencia de los hombros al golpear..."},
        {"name": "Remo con Banda", "series": 3, "description": "Simula el agarre y jale constante del clinch..."},
        {"name": "Fortalecimiento de Cuello (Isométricos)", "series": 2, "description": "Fortalece el cuello de forma segura..."},
        {"name": "Elevaciones de Mentón", "series": 3, "description": "Fortalece la parte frontal del cuello..."},
        {"name": "Plancha (Plank)", "series": 3, "description": "Un core fuerte es la base de todo..."},
        {"name": "Giro Ruso (Russian Twist)", "series": 3, "description": "Fortalece los oblicuos para la rotación..."}
    ]},
    "Viernes": {"focus": "Entrenamiento técnico de Muay Thai.", "activity": "Clase de Muay Thai", "exercises": []},
    "Sábado": {"focus": "Ciclismo de Intensidad.", "activity": "Ascenso al Cerro San Cristóbal", "exercises": []},
    "Domingo": {"focus": "Movilidad y Recuperación Activa.", "activity": "Sesión de Estiramientos y Movilidad", "exercises": []}
}

class SeriesTracker(tk.Frame):
    def __init__(self, parent, total_series, completed_series=0, on_series_change=None):
        super().__init__(parent, bg=COLORS["dark_blue"])
        self.total_series = total_series
        self.completed_series = completed_series
        self.on_series_change = on_series_change
        self.series_labels = []
        self._create_widgets()
        self.update_display()

    def _create_widgets(self):
        tk.Label(self, text="Series:", font=("Helvetica", 10), bg=COLORS["dark_blue"], fg=COLORS["light_gray"]).pack(side=tk.LEFT, padx=(0, 10))
        for i in range(self.total_series):
            lbl = tk.Label(self, text="●", font=("Helvetica", 20), bg=COLORS["dark_blue"], fg=COLORS["circle_bg"])
            lbl.pack(side=tk.LEFT, padx=3)
            lbl.bind("<Button-1>", lambda e, index=i: self._on_circle_click(index))
            self.series_labels.append(lbl)

    def _on_circle_click(self, index):
        self.completed_series = index + 1 if (index + 1) != self.completed_series else index
        self.update_display()
        if self.on_series_change: self.on_series_change(self.completed_series)
            
    def update_display(self):
        for i, lbl in enumerate(self.series_labels):
            lbl.config(fg=COLORS["completed_green"] if i < self.completed_series else COLORS["circle_bg"])

class TrainingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Plan de Entrenamiento Semanal (Beta v9)")
        self.root.geometry("1050x700")
        self.root.configure(bg=COLORS["independence"])

        self.plan_file = "plan.json"
        self.progress_file = "progress.csv"
        
        self.load_plan()
        self.load_progress()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.title_font = font.Font(family="Helvetica", size=18, weight="bold")
        self.subtitle_font = font.Font(family="Helvetica", size=12)
        self.text_font = font.Font(family="Helvetica", size=10)
        
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton", padding=6, relief="flat", background=COLORS["charcoal"], foreground=COLORS["white"], font=self.subtitle_font)
        style.map("TButton", background=[('active', COLORS["old_lavender"])])
        style.configure("TPanedwindow", background=COLORS["independence"])
        style.configure("Days.TButton", font=("Helvetica", 9), padding=(0, 6))

        # NUEVO: Diccionario para traducir el día de la semana
        self.days_map = {
            'Monday': 'Lunes', 'Tuesday': 'Martes', 'Wednesday': 'Miércoles',
            'Thursday': 'Jueves', 'Friday': 'Viernes', 'Saturday': 'Sábado', 'Sunday': 'Domingo'
        }
        
        self.create_widgets()

    def load_plan(self):
        try:
            with open(self.plan_file, 'r', encoding='utf-8') as f:
                self.training_plan = json.load(f)
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
        # Configuración de la ventana principal para que sea expansible
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        main_frame = tk.Frame(self.root, bg=COLORS["independence"], padx=20, pady=20)
        main_frame.grid(row=0, column=0, sticky="nsew")
        # Le damos peso a la fila 3 (donde vive el contenido principal)
        main_frame.grid_rowconfigure(3, weight=1) 
        # Le damos peso a la columna 0 (la única que usamos)
        main_frame.grid_columnconfigure(0, weight=1)

        title_label = tk.Label(main_frame, text="Tu Plan de Entrenamiento", font=self.title_font, bg=COLORS["independence"], fg=COLORS["white"])
        title_label.grid(row=0, column=0, pady=(0, 20))

        # --- Contenedor de los Botones de Días ---
        days_frame = tk.Frame(main_frame, bg=COLORS["independence"])
        # Hacemos que el contenedor se estire horizontalmente (east-west)
        days_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        
        days = list(self.training_plan.keys())
        for i, day in enumerate(days):
            # LA CLAVE ESTÁ AQUÍ: Le damos peso a cada una de las 7 columnas dentro del contenedor
            days_frame.grid_columnconfigure(i, weight=1)
            button = ttk.Button(days_frame, text=day, style="Days.TButton", command=lambda d=day: self.show_day_plan(d))
            # Hacemos que cada botón se estire para llenar su columna
            button.grid(row=0, column=i, sticky="ew", padx=2)

        self.focus_label = tk.Label(main_frame, text="Selecciona un día para comenzar", font=self.subtitle_font, bg=COLORS["independence"], fg=COLORS["light_gray"])
        self.focus_label.grid(row=2, column=0, pady=10)

        paned_window = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned_window.grid(row=3, column=0, sticky="nsew", pady=(10,0))

        # --- Panel Izquierdo (Lista y Botones de Acción) ---
        left_panel = tk.Frame(paned_window, bg=COLORS["dark_blue"])
        paned_window.add(left_panel, weight=1)
        left_panel.grid_rowconfigure(0, weight=1)
        left_panel.grid_columnconfigure(0, weight=1)
        
        self.exercise_listbox = tk.Listbox(left_panel, font=self.text_font, bg=COLORS["dark_blue"], fg=COLORS["white"], 
                                           selectbackground=COLORS["wenge"], borderwidth=0, highlightthickness=0, selectforeground=COLORS["white"])
        self.exercise_listbox.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.exercise_listbox.bind("<<ListboxSelect>>", self.show_exercise_description)
        
        button_frame = tk.Frame(left_panel, bg=COLORS["dark_blue"])
        button_frame.grid(row=1, column=0, pady=10)
        
        complete_btn = ttk.Button(button_frame, text="Completar Todo ✓", command=self.complete_all_series)
        complete_btn.pack(side=tk.LEFT, padx=5)
        add_btn = ttk.Button(button_frame, text="Agregar", command=self.add_exercise)
        add_btn.pack(side=tk.LEFT, padx=5)
        edit_btn = ttk.Button(button_frame, text="Editar", command=self.edit_exercise)
        edit_btn.pack(side=tk.LEFT, padx=5)
        delete_btn = ttk.Button(button_frame, text="Eliminar", command=self.delete_exercise)
        delete_btn.pack(side=tk.LEFT, padx=5)

        # --- Panel Derecho (Descripción y Series Tracker) ---
        self.desc_panel = tk.Frame(paned_window, bg=COLORS["dark_blue"])
        paned_window.add(self.desc_panel, weight=2)
        self.desc_panel.grid_rowconfigure(1, weight=1)
        self.desc_panel.grid_columnconfigure(0, weight=1)
        
        self.series_tracker_frame = tk.Frame(self.desc_panel, bg=COLORS["dark_blue"])
        self.series_tracker_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=(15,0))

        self.description_text = tk.Text(self.desc_panel, wrap=tk.WORD, font=self.text_font, bg=COLORS["dark_blue"], 
                                        fg=COLORS["white"], borderwidth=0, highlightthickness=0, insertbackground=COLORS["white"])
        self.description_text.grid(row=1, column=0, sticky="nsew", padx=15, pady=15)
        self.description_text.config(state=tk.DISABLED)

    # MODIFICADO: Esta función ahora comprueba si el día seleccionado es hoy
    def show_day_plan(self, day):
        self.current_day = day
        plan = self.training_plan.get(day, {})
        self.focus_label.config(text=f"Foco: {plan.get('focus', 'N/A')}")
        self.exercise_listbox.delete(0, tk.END)

        # Limpiar panel derecho
        for widget in self.series_tracker_frame.winfo_children(): widget.destroy()
        self.description_text.config(state=tk.NORMAL)
        self.description_text.delete("1.0", tk.END)
        self.description_text.config(state=tk.DISABLED)

        # Comprobar si el día seleccionado es el día actual de la semana
        today_name = self.days_map[date.today().strftime('%A')]
        is_today = (self.current_day == today_name)
        
        today_str = str(date.today())
        todays_progress = self.completion_status.get(today_str, {})
        
        items_to_show = []
        if plan.get("activity"): items_to_show.append(plan["activity"])
        for exercise in plan.get("exercises", []): items_to_show.append(exercise["name"])

        if not items_to_show:
            self.description_text.config(state=tk.NORMAL)
            self.description_text.insert("1.0", "Día de descanso o sin planificar.")
            self.description_text.config(state=tk.DISABLED)
        else:
            for i, item_name in enumerate(items_to_show):
                self.exercise_listbox.insert(tk.END, item_name)
                # Solo aplicar color de completado si estamos viendo el día de hoy
                if is_today:
                    progress = todays_progress.get(item_name, {})
                    series_completed = progress.get("series_completed", 0)
                    total_series = 1
                    exercise_data = next((ex for ex in plan.get("exercises", []) if ex["name"] == item_name), None)
                    if exercise_data and "series" in exercise_data: total_series = exercise_data["series"]
                    if series_completed >= total_series: self.exercise_listbox.itemconfig(i, {'fg': COLORS["completed_green"]})
            
            self.exercise_listbox.select_set(0)
            self.show_exercise_description(None)

    def show_exercise_description(self, event):
        if not self.exercise_listbox.curselection(): return
        item_name = self.exercise_listbox.get(self.exercise_listbox.curselection()[0])
        plan_today = self.training_plan[self.current_day]
        description, total_series = "", 0
        exercise_data = next((ex for ex in plan_today.get("exercises", []) if ex["name"] == item_name), None)
        if exercise_data:
            description, total_series = exercise_data.get("description", ""), exercise_data.get("series", 0)
        elif item_name == plan_today.get("activity"):
            description, total_series = f"Actividad principal de hoy:\n\n{plan_today['focus']}", 1
        self.description_text.config(state=tk.NORMAL)
        self.description_text.delete("1.0", tk.END)
        self.description_text.insert("1.0", description)
        self.description_text.config(state=tk.DISABLED)
        
        for widget in self.series_tracker_frame.winfo_children(): widget.destroy()
        
        today_name = self.days_map[date.today().strftime('%A')]
        is_today = (self.current_day == today_name)

        if total_series > 0 and is_today:
            today_str = str(date.today())
            progress = self.completion_status.get(today_str, {}).get(item_name, {})
            completed_series = progress.get("series_completed", 0)
            def on_series_change(new_completed_count): self.update_series_progress(item_name, new_completed_count)
            tracker = SeriesTracker(self.series_tracker_frame, total_series, completed_series, on_series_change)
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
        
        today_str = str(date.today())
        todays_progress = self.completion_status.get(today_str, {})
        plan_today = self.training_plan[self.current_day]
        for i in range(self.exercise_listbox.size()):
            item_name = self.exercise_listbox.get(i)
            progress = todays_progress.get(item_name, {})
            series_completed = progress.get("series_completed", 0)
            total_series = 1
            exercise_data = next((ex for ex in plan_today.get("exercises", []) if ex["name"] == item_name), None)
            if exercise_data: total_series = exercise_data.get("series", 1)
            if series_completed >= total_series: self.exercise_listbox.itemconfig(i, {'fg': COLORS["completed_green"]})
            else: self.exercise_listbox.itemconfig(i, {'fg': COLORS["white"]})
    
    def complete_all_series(self):
        today_name = self.days_map[date.today().strftime('%A')]
        if self.current_day != today_name:
            messagebox.showinfo("Información", "Solo puedes registrar el progreso para el día de hoy.")
            return
        if not self.exercise_listbox.curselection(): return
        item_name = self.exercise_listbox.get(self.exercise_listbox.curselection()[0])
        plan_today = self.training_plan[self.current_day]
        total_series = 1
        exercise_data = next((ex for ex in plan_today.get("exercises", []) if ex["name"] == item_name), None)
        if exercise_data: total_series = exercise_data.get("series", 1)
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
        editor.geometry("400x400")
        editor.configure(bg=COLORS["independence"])
        editor.transient(self.root); editor.grab_set()
        # ... (código de la ventana de edición sin cambios) ...
        tk.Label(editor, text="Nombre:", bg=COLORS["independence"], fg=COLORS["white"]).pack(pady=(10,0))
        name_entry = tk.Entry(editor, width=50, bg=COLORS["dark_blue"], fg=COLORS["white"], insertbackground=COLORS["white"])
        name_entry.pack(pady=5, padx=10)
        tk.Label(editor, text="Series:", bg=COLORS["independence"], fg=COLORS["white"]).pack(pady=(10,0))
        series_entry = tk.Entry(editor, width=10, bg=COLORS["dark_blue"], fg=COLORS["white"], insertbackground=COLORS["white"])
        series_entry.pack(pady=5, padx=10)
        tk.Label(editor, text="Descripción:", bg=COLORS["independence"], fg=COLORS["white"]).pack(pady=(10,0))
        desc_text = tk.Text(editor, width=50, height=10, wrap=tk.WORD, bg=COLORS["dark_blue"], fg=COLORS["white"], insertbackground=COLORS["white"])
        desc_text.pack(pady=5, padx=10)
        if mode == "edit" and selected_index is not None:
            exercise = self.training_plan[self.current_day]["exercises"][selected_index]
            name_entry.insert(0, exercise["name"])
            series_entry.insert(0, exercise.get("series", 1))
            desc_text.insert("1.0", exercise["description"])
        def save_changes():
            new_name, new_desc = name_entry.get().strip(), desc_text.get("1.0", tk.END).strip()
            try:
                new_series = int(series_entry.get().strip())
                if new_series < 1: raise ValueError
            except ValueError:
                messagebox.showerror("Error", "El número de series debe ser un número entero positivo.", parent=editor); return
            if not new_name:
                messagebox.showerror("Error", "El nombre no puede estar vacío.", parent=editor); return
            new_exercise = {"name": new_name, "series": new_series, "description": new_desc}
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