import tkinter as tk
from tkinter import ttk, font, messagebox, Toplevel
import json
from datetime import date

# --- Paleta de Colores ---
COLORS = {
    "dark_blue": "#2C3D55",
    "independence": "#3E4C5E",
    "charcoal": "#536271",
    "old_lavender": "#6A687A",
    "wenge": "#84828F",
    "white": "#FFFFFF",
    "light_gray": "#CCCCCC",
    "completed_green": "#66BB6A"
}

# --- Plan de Entrenamiento por Defecto ---
# MODIFICADO: Se restauraron todos los ejercicios de Martes y Jueves
default_training_plan = {
    "Lunes": {"focus": "Entrenamiento técnico de Muay Thai.", "activity": "Clase de Muay Thai", "exercises": []},
    "Martes": {"focus": "Fuerza y Potencia (Striking y Brazos).", "activity": None, "exercises": [
        {"name": "Sentadilla Goblet con Mancuerna", "description": "Fundamental para la potencia de tus patadas. Sujeta una mancuerna en vertical contra tu pecho. Baja profundo manteniendo la espalda recta y sube de forma explosiva.\n\nSeries: 4\nRepeticiones: 8-10"},
        {"name": "Remo Renegado (Renegade Row)", "description": "Fortalece la espalda para jalar en el clinch y el core para la estabilidad. En posición de plancha con mancuernas, rema con un brazo sin girar las caderas.\n\nSeries: 3\nRepeticiones: 8 por brazo"},
        {"name": "Flexiones a Máxima Velocidad", "description": "Desarrolla la potencia de empuje para tus puños. Baja de forma controlada y sube con la mayor velocidad posible, sin despegar las manos del suelo.\n\nSeries: 4\nRepeticiones: Tantas como puedas"},
        {"name": "Curl de Bíceps con Mancuerna", "description": "Fortalece los bíceps para la fuerza de tracción en el clinch. De pie, con una mancuerna en cada mano, flexiona los codos para llevar las pesas hacia los hombros.\n\nSeries: 3\nRepeticiones: 10-12 por brazo"},
        {"name": "Extensión de Tríceps sobre la Cabeza", "description": "Añade potencia a la extensión final de tus puñetazos. Sostén una mancuerna con ambas manos sobre tu cabeza y flexiona los codos para bajarla por detrás de la nuca. Extiende los brazos para volver a subir.\n\nSeries: 3\nRepeticiones: 10-12"}
    ]},
    "Miércoles": {"focus": "Ciclismo de Resistencia.", "activity": "Ruta Plana Mapocho 42k", "exercises": []},
    "Jueves": {"focus": "Resistencia Muscular y Fuerza de Clinch.", "activity": None, "exercises": [
        {"name": "Zancadas con Pausa", "description": "Construye resistencia en las piernas. Sostén las mancuernas, haz una zancada y aguanta 2 segundos en la posición más baja antes de subir. Alterna piernas.\n\nSeries: 3\nRepeticiones: 10 por pierna"},
        {"name": "Press de Hombro de Rodillas", "description": "Para la resistencia de los hombros al golpear. Arrodillado para proteger la espalda, empuja las mancuernas hacia arriba de forma controlada.\n\nSeries: 3\nRepeticiones: 12-15"},
        {"name": "Remo con Banda", "description": "Simula el agarre y jale constante del clinch. Siéntate, pasa la banda por tus pies y rema llevando los codos hacia atrás, apretando la espalda.\n\nSeries: 3\nRepeticiones: 20"},
        {"name": "Fortalecimiento de Cuello (Isométricos)", "description": "Coloca la palma de tu mano en tu frente y empuja suavemente con la cabeza contra la mano, sin que la cabeza se mueva. Mantén la tensión por 10-15 segundos. Repite en los lados y en la nuca.\n\nSeries: 2\nRepeticiones: 3 por cada lado (frente, nuca, izquierda, derecha)"},
        {"name": "Elevaciones de Mentón", "description": "Acostado boca arriba en el suelo, levanta ligeramente la cabeza y lleva tu mentón hacia el pecho. Mantén la contracción por un segundo y baja lentamente.\n\nSeries: 3\nRepeticiones: 15-20"},
        {"name": "Plancha (Plank)", "description": "Un core fuerte es la base de todo. Mantén una línea recta desde la cabeza a los talones, apretando abdomen y glúteos.\n\nSeries: 3\nTiempo: 60 segundos"},
        {"name": "Giro Ruso (Russian Twist)", "description": "Fortalece los oblicuos para la rotación en golpes y rodillas. Sentado, inclínate hacia atrás y gira el torso de lado a lado con una mancuerna.\n\nSeries: 3\nRepeticiones: 20 giros totales"}
    ]},
    "Viernes": {"focus": "Entrenamiento técnico de Muay Thai.", "activity": "Clase de Muay Thai", "exercises": []},
    "Sábado": {"focus": "Ciclismo de Intensidad.", "activity": "Ascenso al Cerro San Cristóbal", "exercises": []},
    "Domingo": {"focus": "Movilidad y Recuperación Activa.", "activity": "Sesión de Estiramientos y Movilidad", "exercises": []}
}

class TrainingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Plan de Entrenamiento Semanal (Beta v6)")
        self.root.geometry("950x650")
        self.root.configure(bg=COLORS["independence"])
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self.data_file = "training_data.json"
        self.load_data()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # --- Estilos y Fuentes ---
        self.title_font = font.Font(family="Helvetica", size=18, weight="bold")
        self.subtitle_font = font.Font(family="Helvetica", size=12)
        self.text_font = font.Font(family="Helvetica", size=10)
        
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton", padding=6, relief="flat", background=COLORS["charcoal"], foreground=COLORS["white"], font=self.subtitle_font)
        style.map("TButton", background=[('active', COLORS["old_lavender"])])
        style.configure("TPanedwindow", background=COLORS["independence"])
        
        style.configure("Days.TButton", font=("Helvetica", 9), padding=(0, 6))

        self.create_widgets()

    def load_data(self):
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.training_plan = data.get("plan", default_training_plan)
                self.completion_status = data.get("completion", {})
            
            for day, details in default_training_plan.items():
                if day not in self.training_plan:
                    self.training_plan[day] = details
                elif "activity" not in self.training_plan[day]:
                    self.training_plan[day]["activity"] = details["activity"]

        except (FileNotFoundError, json.JSONDecodeError):
            self.training_plan = default_training_plan
            self.completion_status = {}

    def save_data(self):
        data_to_save = {"plan": self.training_plan, "completion": self.completion_status}
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=4)

    def on_closing(self):
        self.save_data()
        self.root.destroy()

    def create_widgets(self):
        main_frame = tk.Frame(self.root, bg=COLORS["independence"], padx=20, pady=20)
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.grid_rowconfigure(3, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        title_label = tk.Label(main_frame, text="Tu Plan de Entrenamiento", font=self.title_font, bg=COLORS["independence"], fg=COLORS["white"])
        title_label.grid(row=0, column=0, pady=(0, 20), columnspan=2)

        days_frame = tk.Frame(main_frame, bg=COLORS["independence"])
        days_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        days = list(self.training_plan.keys())
        for i, day in enumerate(days):
            days_frame.grid_columnconfigure(i, weight=1)
            button = ttk.Button(days_frame, text=day, style="Days.TButton", command=lambda d=day: self.show_day_plan(d))
            button.grid(row=0, column=i, sticky="ew", padx=2)

        self.focus_label = tk.Label(main_frame, text="Selecciona un día para comenzar", font=self.subtitle_font, bg=COLORS["independence"], fg=COLORS["light_gray"])
        self.focus_label.grid(row=2, column=0, pady=10)

        paned_window = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned_window.grid(row=3, column=0, sticky="nsew", pady=(10,0))

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

        complete_btn = ttk.Button(button_frame, text="Completado ✓", command=self.toggle_completion)
        complete_btn.pack(side=tk.LEFT, padx=5)
        add_btn = ttk.Button(button_frame, text="Agregar", command=self.add_exercise)
        add_btn.pack(side=tk.LEFT, padx=5)
        edit_btn = ttk.Button(button_frame, text="Editar", command=self.edit_exercise)
        edit_btn.pack(side=tk.LEFT, padx=5)
        delete_btn = ttk.Button(button_frame, text="Eliminar", command=self.delete_exercise)
        delete_btn.pack(side=tk.LEFT, padx=5)

        desc_frame = tk.Frame(paned_window, bg=COLORS["dark_blue"])
        paned_window.add(desc_frame, weight=2)
        desc_frame.grid_rowconfigure(0, weight=1)
        desc_frame.grid_columnconfigure(0, weight=1)
        
        self.description_text = tk.Text(desc_frame, wrap=tk.WORD, font=self.text_font, bg=COLORS["dark_blue"], fg=COLORS["white"], borderwidth=0, highlightthickness=0, insertbackground=COLORS["white"])
        self.description_text.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
        self.description_text.config(state=tk.DISABLED)

    def show_day_plan(self, day):
        self.current_day = day
        plan = self.training_plan.get(day, {})
        self.focus_label.config(text=f"Foco: {plan.get('focus', 'N/A')}")
        
        self.exercise_listbox.delete(0, tk.END)
        self.description_text.config(state=tk.NORMAL)
        self.description_text.delete("1.0", tk.END)
        self.description_text.config(state=tk.DISABLED)

        today_str = str(date.today())
        todays_progress = self.completion_status.get(today_str, {})

        items_to_show = []
        if plan.get("activity"):
            items_to_show.append(plan["activity"])
        for exercise in plan.get("exercises", []):
            items_to_show.append(exercise["name"])

        if not items_to_show:
            self.description_text.config(state=tk.NORMAL)
            self.description_text.insert("1.0", "Día de descanso o sin planificar.")
            self.description_text.config(state=tk.DISABLED)
        else:
            for i, item_name in enumerate(items_to_show):
                self.exercise_listbox.insert(tk.END, item_name)
                if todays_progress.get(item_name, False):
                    self.exercise_listbox.itemconfig(i, {'fg': COLORS["completed_green"]})
            
            self.exercise_listbox.select_set(0)
            self.show_exercise_description(None)

    def toggle_completion(self):
        selected_indices = self.exercise_listbox.curselection()
        if not selected_indices or not hasattr(self, 'current_day'):
            messagebox.showwarning("Advertencia", "Selecciona un ejercicio o actividad primero.")
            return

        selected_index = selected_indices[0]
        item_name = self.exercise_listbox.get(selected_index)
        today_str = str(date.today())
        
        if today_str not in self.completion_status:
            self.completion_status[today_str] = {}
            
        current_status = self.completion_status[today_str].get(item_name, False)
        self.completion_status[today_str][item_name] = not current_status
        
        new_color = COLORS["completed_green"] if not current_status else COLORS["white"]
        self.exercise_listbox.itemconfig(selected_index, {'fg': new_color})

    def show_exercise_description(self, event):
        selected_indices = self.exercise_listbox.curselection()
        if not selected_indices: return
        
        item_name = self.exercise_listbox.get(selected_indices[0])
        plan_today = self.training_plan[self.current_day]
        description = ""

        if item_name == plan_today.get("activity"):
            description = f"Actividad principal de hoy:\n\n{plan_today['focus']}"
        else:
            for ex in plan_today.get("exercises", []):
                if ex["name"] == item_name:
                    description = ex.get("description", "Sin descripción.")
                    break
        
        self.description_text.config(state=tk.NORMAL)
        self.description_text.delete("1.0", tk.END)
        self.description_text.insert("1.0", description)
        self.description_text.config(state=tk.DISABLED)

    def add_exercise(self):
        if not hasattr(self, 'current_day'):
            messagebox.showwarning("Advertencia", "Por favor, selecciona un día primero.")
            return
        if self.training_plan[self.current_day].get("activity"):
             messagebox.showinfo("Información", "No se pueden agregar ejercicios a un día con una actividad principal definida.")
             return
        self.show_editor_window(mode="add")

    def edit_exercise(self):
        if not hasattr(self, 'current_day') or not self.exercise_listbox.curselection():
            messagebox.showwarning("Advertencia", "Selecciona un ejercicio para editar.")
            return
        
        item_name = self.exercise_listbox.get(self.exercise_listbox.curselection()[0])
        if item_name == self.training_plan[self.current_day].get("activity"):
            messagebox.showinfo("Información", "Las actividades principales no se editan desde aquí.")
            return
        
        exercise_index = -1
        for i, ex in enumerate(self.training_plan[self.current_day]["exercises"]):
            if ex["name"] == item_name:
                exercise_index = i
                break
        
        if exercise_index != -1:
            self.show_editor_window(mode="edit", selected_index=exercise_index)

    def delete_exercise(self):
        if not hasattr(self, 'current_day') or not self.exercise_listbox.curselection():
            messagebox.showwarning("Advertencia", "Selecciona un ejercicio para eliminar.")
            return
        
        item_name = self.exercise_listbox.get(self.exercise_listbox.curselection()[0])
        if item_name == self.training_plan[self.current_day].get("activity"):
            messagebox.showinfo("Información", "Las actividades principales no se pueden eliminar.")
            return

        if messagebox.askyesno("Confirmar Eliminación", f"¿Eliminar '{item_name}'?"):
            exercises = self.training_plan[self.current_day]["exercises"]
            self.training_plan[self.current_day]["exercises"] = [ex for ex in exercises if ex['name'] != item_name]
            self.show_day_plan(self.current_day)

    def show_editor_window(self, mode, selected_index=None):
        editor = Toplevel(self.root)
        editor.title(f"{'Editar' if mode == 'edit' else 'Agregar'} Ejercicio")
        editor.geometry("400x350")
        editor.configure(bg=COLORS["independence"])
        editor.transient(self.root)
        editor.grab_set()

        tk.Label(editor, text="Nombre:", bg=COLORS["independence"], fg=COLORS["white"]).pack(pady=(10,0))
        name_entry = tk.Entry(editor, width=50, bg=COLORS["dark_blue"], fg=COLORS["white"], insertbackground=COLORS["white"])
        name_entry.pack(pady=5, padx=10)

        tk.Label(editor, text="Descripción:", bg=COLORS["independence"], fg=COLORS["white"]).pack(pady=(10,0))
        desc_text = tk.Text(editor, width=50, height=12, wrap=tk.WORD, bg=COLORS["dark_blue"], fg=COLORS["white"], insertbackground=COLORS["white"])
        desc_text.pack(pady=5, padx=10)

        if mode == "edit" and selected_index is not None:
            exercise = self.training_plan[self.current_day]["exercises"][selected_index]
            name_entry.insert(0, exercise["name"])
            desc_text.insert("1.0", exercise["description"])
        
        def save_changes():
            new_name, new_desc = name_entry.get().strip(), desc_text.get("1.0", tk.END).strip()
            if not new_name:
                messagebox.showerror("Error", "El nombre no puede estar vacío.", parent=editor)
                return
            
            new_exercise = {"name": new_name, "description": new_desc}
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