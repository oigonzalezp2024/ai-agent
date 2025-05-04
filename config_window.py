import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from cryptography.fernet import Fernet
from api_key_encryptor import ApiKeyEncryptor  # Importamos la nueva clase

# --- Configuración de la Aplicación ---
CONFIG_FILE = 'config.json'
DEFAULT_LANGUAGE = 'es-CO'
DEFAULT_AI_AGENT = 'gemini-pro'
AVAILABLE_LANGUAGES = ['es-CO', 'en-US']
AVAILABLE_AI_AGENTS = ['gemini-pro', 'gemini-2.0-flash']

class ConfigWindow(tk.Toplevel):
    def __init__(self, parent, load_callback):
        super().__init__(parent)
        self.title("Configuración")
        self.geometry("350x200")
        self.resizable(False, False)
        self.parent = parent
        self.load_callback = load_callback
        self.encryptor = ApiKeyEncryptor() # Instancia de la clase de encriptación
        self.current_config = self._load_config()

        self.api_key_label = ttk.Label(self, text="API Key:")
        self.api_key_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.api_key_entry = ttk.Entry(self, width=40)
        self.api_key_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        self.language_label = ttk.Label(self, text="Idioma:")
        self.language_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.language_combo = ttk.Combobox(self, values=AVAILABLE_LANGUAGES)
        self.language_combo.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        self.ai_agent_label = ttk.Label(self, text="Agente AI:")
        self.ai_agent_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.ai_agent_combo = ttk.Combobox(self, values=AVAILABLE_AI_AGENTS)
        self.ai_agent_combo.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        self.save_button = ttk.Button(self, text="Guardar", command=self.save_config)
        self.save_button.grid(row=3, column=0, columnspan=2, padx=10, pady=15, sticky="ew")

        self._load_initial_config()

    def _load_config(self):
        """Carga la configuración desde el archivo."""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'rb') as f:
                    encrypted_data = f.read()
                decrypted_data = self.encryptor.decrypt(encrypted_data)
                return json.loads(decrypted_data) if decrypted_data else {}
            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar la configuración: {e}")
                return {}
        return {}

    def save_config(self):
        config = {
            'api_key': self.api_key_entry.get(),
            'language': self.language_combo.get(),
            'ai_agent': self.ai_agent_combo.get()
        }
        try:
            json_data = json.dumps(config)
            encrypted_data = self.encryptor.encrypt(json_data)
            with open(CONFIG_FILE, 'wb') as f:
                f.write(encrypted_data)
            messagebox.showinfo("Guardado", "Configuración guardada exitosamente.")
            self.load_callback(config)
            self.destroy()
        except Exception as e:
            print("Error", f"Error al guardar la configuración: {e}")
            messagebox.showerror("Error", f"Error al guardar la configuración: {e}")

    def _load_initial_config(self):
        """Carga la configuración inicial en los widgets."""
        self.api_key_entry.insert(0, self.current_config.get('api_key', ''))
        self.language_combo.set(self.current_config.get('language', DEFAULT_LANGUAGE))
        self.ai_agent_combo.set(self.current_config.get('ai_agent', DEFAULT_AI_AGENT))