import tkinter as tk
from tkinter import ttk, font, messagebox, Toplevel
import json

# --- NUEVO: Paleta de Colores Personalizada ---
COLORS = {
    "dark_blue": "#2C3D55",
    "independence": "#3E4C5E",
    "charcoal": "#536271",
    "old_lavender": "#6A687A",
    "wenge": "#84828F",
    "white": "#FFFFFF",
    "light_gray": "#CCCCCC"
}

# --- Datos del Plan de Entrenamiento (Ahora es el plan por defecto) ---
default_training_plan = {
    "Lunes": {"focus": "Entrenamiento técnico de Muay Thai.", "exercises": []},
    "Martes": {
        "focus": "Fuerza y Potencia (Striking y Brazos).",
        "exercises": [
            {"name": "Sentadilla Goblet con Mancuerna", "description": "Series: 4\nRepeticiones: 8-10"},
            {"name": "Remo Renegado (Renegade Row)", "description": "Series: 3\nRepeticiones: 8 por brazo"}
        ]
    },
    # ... (el resto del plan sigue igual) ...
}


class TrainingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Plan de Entrenamiento Semanal (Beta v3)")
        self.root.geometry("850x650")
        
        # MODIFICADO: Aplicamos el color de fondo principal
        self.root.configure(bg=COLORS["independence"])
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self.plan_file = "plan.json"
        self.training_plan = self.load_plan()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # --- Estilos y Fuentes ---
        self.title_font = font.Font(family="Helvetica", size=18, weight="bold")
        self.subtitle_font = font.Font(family="Helvetica", size=12)
        self.text_font = font.Font(family="Helvetica", size=10)
        
        # MODIFICADO: Configuramos los estilos con la paleta de colores
        style = ttk.Style()
        style.theme_use("clam")
        
        # Estilo para los botones
        style.configure("TButton", 
                        padding=6, 
                        relief="flat", 
                        background=COLORS["charcoal"], 
                        foreground=COLORS["white"], 
                        font=self.subtitle_font)
        style.map("TButton", background=[('active', COLORS["old_lavender"])])
        
        # Estilo para el PanedWindow
        style.configure("TPanedwindow", background=COLORS["independence"])
        
        self.create_widgets()

    def load_plan(self):
        try:
            with open(self.plan_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return default_training_plan

    def save_plan(self):
        with open(self.plan_file, 'w', encoding='utf-8') as f:
            json.dump(self.training_plan, f, ensure_ascii=False, indent=4)

    def on_closing(self):
        self.save_plan()
        self.root.destroy()

    def create_widgets(self):
        main_frame = tk.Frame(self.root, bg=COLORS["independence"], padx=20, pady=20)
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.grid_rowconfigure(3, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        title_label = tk.Label(main_frame, text="Tu Plan de Entrenamiento", font=self.title_font, bg=COLORS["independence"], fg=COLORS["white"])
        title_label.grid(row=0, column=0, pady=(0, 20))

        days_frame = tk.Frame(main_frame, bg=COLORS["independence"])
        days_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        
        days = list(self.training_plan.keys())
        for i, day in enumerate(days):
            days_frame.grid_columnconfigure(i, weight=1)
            button = ttk.Button(days_frame, text=day, command=lambda d=day: self.show_day_plan(d))
            button.grid(row=0, column=i, sticky="ew", padx=2)

        self.focus_label = tk.Label(main_frame, text="Selecciona un día para comenzar", font=self.subtitle_font, bg=COLORS["independence"], fg=COLORS["light_gray"])
        self.focus_label.grid(row=2, column=0, pady=10)

        paned_window = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned_window.grid(row=3, column=0, sticky="nsew", pady=(10,0))

        # --- Panel Izquierdo (Lista y Botones) ---
        left_panel = tk.Frame(paned_window, bg=COLORS["dark_blue"])
        paned_window.add(left_panel, weight=1)
        left_panel.grid_rowconfigure(0, weight=1)
        left_panel.grid_columnconfigure(0, weight=1)
        
        self.exercise_listbox = tk.Listbox(left_panel, font=self.text_font, bg=COLORS["dark_blue"], fg=COLORS["white"], 
                                           selectbackground=COLORS["wenge"], borderwidth=0, highlightthickness=0)
        self.exercise_listbox.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.exercise_listbox.bind("<<ListboxSelect>>", self.show_exercise_description)
        
        button_frame = tk.Frame(left_panel, bg=COLORS["dark_blue"])
        button_frame.grid(row=1, column=0, pady=10)

        add_btn = ttk.Button(button_frame, text="Agregar", command=self.add_exercise)
        add_btn.pack(side=tk.LEFT, padx=5)
        edit_btn = ttk.Button(button_frame, text="Editar", command=self.edit_exercise)
        edit_btn.pack(side=tk.LEFT, padx=5)
        delete_btn = ttk.Button(button_frame, text="Eliminar", command=self.delete_exercise)
        delete_btn.pack(side=tk.LEFT, padx=5)

        # --- Panel Derecho (Descripción) ---
        desc_frame = tk.Frame(paned_window, bg=COLORS["dark_blue"])
        paned_window.add(desc_frame, weight=2)
        desc_frame.grid_rowconfigure(0, weight=1)
        desc_frame.grid_columnconfigure(0, weight=1)
        
        self.description_text = tk.Text(desc_frame, wrap=tk.WORD, font=self.text_font, bg=COLORS["dark_blue"], 
                                        fg=COLORS["white"], borderwidth=0, highlightthickness=0)
        self.description_text.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
        self.description_text.config(state=tk.DISABLED)

    def show_day_plan(self, day):
        self.current_day = day
        plan = self.training_plan[day]
        self.focus_label.config(text=f"Foco: {plan['focus']}")
        self.exercise_listbox.delete(0, tk.END)
        self.description_text.config(state=tk.NORMAL)
        self.description_text.delete("1.0", tk.END)
        
        if plan["exercises"]:
            for exercise in plan["exercises"]:
                self.exercise_listbox.insert(tk.END, exercise["name"])
            self.exercise_listbox.select_set(0)
            self.show_exercise_description(None)
        else:
            self.description_text.insert("1.0", "Hoy es día de entrenamiento técnico o descanso.")
        
        self.description_text.config(state=tk.DISABLED)

    def show_exercise_description(self, event):
        selected_indices = self.exercise_listbox.curselection()
        if not selected_indices:
            self.description_text.config(state=tk.NORMAL)
            self.description_text.delete("1.0", tk.END)
            self.description_text.config(state=tk.DISABLED)
            return
        
        selected_index = selected_indices[0]
        exercise_name = self.exercise_listbox.get(selected_index)
        
        description = "Descripción no encontrada."
        for ex in self.training_plan[self.current_day]["exercises"]:
            if ex["name"] == exercise_name:
                description = ex["description"]
                break
        
        self.description_text.config(state=tk.NORMAL)
        self.description_text.delete("1.0", tk.END)
        self.description_text.insert("1.0", description)
        self.description_text.config(state=tk.DISABLED)

    def add_exercise(self):
        if not hasattr(self, 'current_day'):
            messagebox.showwarning("Advertencia", "Por favor, selecciona un día primero.")
            return
        self.show_editor_window(mode="add")

    def edit_exercise(self):
        selected_indices = self.exercise_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Advertencia", "Por favor, selecciona un ejercicio para editar.")
            return
        self.show_editor_window(mode="edit", selected_index=selected_indices[0])

    def delete_exercise(self):
        selected_indices = self.exercise_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Advertencia", "Por favor, selecciona un ejercicio para eliminar.")
            return
        exercise_name = self.exercise_listbox.get(selected_indices[0])
        confirm = messagebox.askyesno("Confirmar Eliminación", f"¿Estás seguro de que quieres eliminar '{exercise_name}'?")
        if confirm:
            del self.training_plan[self.current_day]["exercises"][selected_indices[0]]
            self.show_day_plan(self.current_day)

    # MODIFICADO: Ventana de edición ahora usa la paleta de colores
    def show_editor_window(self, mode, selected_index=None):
        editor = Toplevel(self.root)
        editor.title(f"{'Editar' if mode == 'edit' else 'Agregar'} Ejercicio")
        editor.geometry("400x300")
        editor.configure(bg=COLORS["independence"])

        tk.Label(editor, text="Nombre:", bg=COLORS["independence"], fg=COLORS["white"]).pack(pady=(10,0))
        name_entry = tk.Entry(editor, width=50, bg=COLORS["dark_blue"], fg=COLORS["white"], insertbackground=COLORS["white"])
        name_entry.pack(pady=5, padx=10)

        tk.Label(editor, text="Descripción:", bg=COLORS["independence"], fg=COLORS["white"]).pack(pady=(10,0))
        desc_text = tk.Text(editor, width=50, height=10, wrap=tk.WORD, bg=COLORS["dark_blue"], fg=COLORS["white"], insertbackground=COLORS["white"])
        desc_text.pack(pady=5, padx=10)

        if mode == "edit":
            exercise = self.training_plan[self.current_day]["exercises"][selected_index]
            name_entry.insert(0, exercise["name"])
            desc_text.insert("1.0", exercise["description"])
        
        def save_changes():
            new_name = name_entry.get()
            new_desc = desc_text.get("1.0", tk.END).strip()
            if not new_name:
                messagebox.showerror("Error", "El nombre no puede estar vacío.")
                return
            new_exercise = {"name": new_name, "description": new_desc}
            if mode == "edit":
                self.training_plan[self.current_day]["exercises"][selected_index] = new_exercise
            else:
                self.training_plan[self.current_day]["exercises"].append(new_exercise)
            self.show_day_plan(self.current_day)
            editor.destroy()

        save_button = ttk.Button(editor, text="Guardar", command=save_changes)
        save_button.pack(pady=10)


if __name__ == "__main__":
    root = tk.Tk()
    app = TrainingApp(root)
    root.mainloop()