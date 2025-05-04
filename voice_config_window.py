import tkinter as tk
from tkinter import ttk, messagebox
import pyttsx3

class VoiceConfigWindow(tk.Toplevel):
    def __init__(self, parent, current_voice_id, current_rate, save_callback):
        super().__init__(parent)
        self.title("Configuración de Voz")
        self.geometry("400x300")
        self.parent = parent
        self.save_callback = save_callback  # Guardamos la función callback
        self.engine = pyttsx3.init()
        self.current_voice_id = current_voice_id
        self.current_rate = current_rate

        self.voices = self.engine.getProperty('voices')
        self._create_widgets()

        self.protocol("WM_DELETE_WINDOW", self._on_closing) # Manejar el cierre de la ventana

    def _create_widgets(self):
        ttk.Label(self, text="Seleccionar Voz:").pack(padx=10, pady=(10, 5), anchor="w")
        self.voice_labels = [f"[{i}] {v.name}" for i, v in enumerate(self.voices)]
        self.voice_var = tk.StringVar(self)
        self.voice_var.set(self._get_voice_name_from_id(self.current_voice_id) if self.current_voice_id else (self.voice_labels[0] if self.voice_labels else ""))

        self.voice_list = tk.Listbox(self, listvariable=tk.StringVar(value=self.voice_labels), height=5)
        self._set_initial_voice_selection()
        self.voice_list.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        ttk.Label(self, text="Velocidad de la voz (ejemplo: 150):").pack(pady=(10, 5))
        self.velocidad_entry = ttk.Entry(self)
        self.velocidad_entry.insert(0, self.current_rate if self.current_rate is not None else 125)
        self.velocidad_entry.pack(padx=10, pady=5, fill=tk.X)

        guardar_button = ttk.Button(self, text="Guardar Configuración de Voz", command=self._guardar_configuracion)
        guardar_button.pack(pady=15)

    def _get_voice_name_from_id(self, voice_id):
        for voice in self.voices:
            if voice.id == voice_id:
                return voice.name
        return None

    def _get_voice_id_from_selection(self):
        seleccion_indices = self.voice_list.curselection()
        if seleccion_indices:
            seleccion_indice = seleccion_indices[0]
            return self.voices[seleccion_indice].id
        return None

    def _set_initial_voice_selection(self):
        if self.current_voice_id:
            for i, voice in enumerate(self.voices):
                if voice.id == self.current_voice_id:
                    self.voice_list.select_set(i)
                    break

    def _guardar_configuracion(self):
        voice_id = self._get_voice_id_from_selection()
        velocidad_str = self.velocidad_entry.get()
        velocidad = None
        if velocidad_str.isdigit():
            velocidad = int(velocidad_str)
        elif velocidad_str:
            messagebox.showerror("Error", "La velocidad debe ser un número entero.")
            return

        self.save_callback({'voice_id': voice_id, 'voice_rate': velocidad})
        self.destroy()

    def _on_closing(self):
        """Función que se llama al cerrar la ventana."""
        voice_id = self._get_voice_id_from_selection()
        velocidad_str = self.velocidad_entry.get()
        velocidad = None
        if velocidad_str.isdigit():
            velocidad = int(velocidad_str)

        self.save_callback({'voice_id': voice_id, 'voice_rate': velocidad})
        self.destroy()