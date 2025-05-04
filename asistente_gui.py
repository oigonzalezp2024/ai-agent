import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import locale
import speech_recognition as sr
import pyttsx3
import google.generativeai as genai
from datetime import datetime
from config_window import ConfigWindow
from voice_config_window import VoiceConfigWindow
from cryptography.fernet import Fernet  # Importar Fernet aquí

# --- Configuración de la Aplicación ---
NOMBRE_ARCHIVO_JSON = 'agente_ai.json'
DEFAULT_LANGUAGE = 'es-CO'
DEFAULT_AI_AGENT = 'gemini-2.0-flash'
CONFIG_FILE = 'config.json'
KEY_FILE = 'encryption.key'

class AsistenteGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Asistente de Voz Moderno")
        self.geometry("600x450")
        self.configure(bg="#f0f0f0")

        self.api_key = None
        self.ai_agent = None
        self.language = None
        self.selected_voice_id = None  # Inicializar selected_voice_id
        self.voice_rate = 125          # Inicializar voice_rate
        self._load_initial_config()

        self.r = sr.Recognizer()
        self.engine = pyttsx3.init()
        self.registro_interacciones = self.cargar_interacciones()

        self.historial_text = tk.Text(self, height=10, state=tk.DISABLED, wrap=tk.WORD, font=('Segoe UI', 12), bg="#e0e0e0")
        self.historial_text.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 10), sticky="nsew")

        self.entrada_label = ttk.Label(self, text="Di algo:")
        self.entrada_label.grid(row=1, column=0, padx=20, pady=(10, 5), sticky="w")

        self.entrada_texto = ttk.Entry(self)
        self.entrada_texto.grid(row=2, column=0, padx=20, pady=(5, 10), sticky="ew")
        self.entrada_texto.bind("<Return>", self.procesar_entrada_manual)

        self.hablar_button = ttk.Button(self, text="Hablar", command=self.iniciar_escucha)
        self.hablar_button.grid(row=2, column=1, padx=20, pady=(5, 10), sticky="e")

        self.configurar_voz_button = ttk.Button(self, text="Configurar Voz", command=self.mostrar_configuracion_voz)
        self.configurar_voz_button.grid(row=3, column=0, columnspan=2, padx=20, pady=(10, 10), sticky="ew")

        self.configurar_app_button = ttk.Button(self, text="Configurar App", command=self.mostrar_configuracion_app)
        self.configurar_app_button.grid(row=4, column=0, columnspan=2, padx=20, pady=(5, 20), sticky="ew")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)

        if self.language:
            try:
                locale.setlocale(locale.LC_ALL, '')
            except locale.Error:
                print(f"Advertencia: No se pudo establecer la configuración regional del sistema. Intentando con {self.language}")
                try:
                    locale.setlocale(locale.LC_ALL, self.language)
                except locale.Error:
                    print(f"Error: No se pudo establecer el idioma a {self.language}. Usando la configuración predeterminada.")

        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model_gemini = genai.GenerativeModel('models/'+self.ai_agent)
            self.hablar(f"Hola. El asistente está configurado en idioma {self.language}.")
        else:
            pass

    def _get_encryption_key(self):
            """Obtiene la clave de encriptación."""
            KEY_FILE = 'encryption.key'
            key = None  # Inicializamos key fuera del if
            if not os.path.exists(KEY_FILE):
                key = Fernet.generate_key()
                with open(KEY_FILE, 'wb') as key_file:
                    key_file.write(key)
            with open(KEY_FILE, 'rb') as key_file:
                key = key_file.read()  # Leemos la clave existente
            return key

    def _load_config(self):
        """Carga la configuración desde el archivo."""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'rb') as f:
                    encrypted_data = f.read()
                decrypted_data = Fernet(self._get_encryption_key()).decrypt(encrypted_data).decode()
                return json.loads(decrypted_data)
            except Exception as e:
                print(f"Error al cargar la configuración: {e}")
                return {}
        return {}

    def _save_config(self, config):
        """Guarda la configuración en el archivo."""
        try:
            json_data = json.dumps(config)
            encrypted_data = Fernet(self._get_encryption_key()).encrypt(json_data.encode())
            with open(CONFIG_FILE, 'wb') as f:
                f.write(encrypted_data)
            print("Configuración guardada exitosamente.")
        except Exception as e:
            print(f"Error al guardar la configuración: {e}")

    def _load_initial_config(self):
        """Carga la configuración inicial."""
        config = self._load_config()
        self.api_key = config.get('api_key')
        self.language = config.get('language', DEFAULT_LANGUAGE)
        self.ai_agent = config.get('ai_agent', DEFAULT_AI_AGENT)
        self.selected_voice_id = config.get('voice_id')
        voice_rate = config.get('voice_rate')
        if isinstance(voice_rate, str) and voice_rate.isdigit():
            self.voice_rate = int(voice_rate)
        elif isinstance(voice_rate, int):
            self.voice_rate = voice_rate
        else:
            self.voice_rate = 125

        self.engine = pyttsx3.init()
        if self.selected_voice_id:
            try:
                self.engine.setProperty('voice', self.selected_voice_id)
            except Exception as e:
                print(f"Error al establecer la voz: {e}")
        self.engine.setProperty('rate', self.voice_rate)

    def mostrar_configuracion_app(self):
        ConfigWindow(self, self.update_app_config)

    def update_app_config(self, config):
        self.api_key = config.get('api_key')
        self.language = config.get('language', DEFAULT_LANGUAGE)
        self.ai_agent = config.get('ai_agent', DEFAULT_AI_AGENT)

        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model_gemini = genai.GenerativeModel('models/'+self.ai_agent)
        else:
            self.model_gemini = None

    def hablar(self, texto):
        """Reproduce el texto por voz usando pyttsx3."""
        self.engine.say(texto)
        self.engine.runAndWait()

    def obtener_respuesta_gemini(self, prompt):
        """Obtiene una respuesta de texto del modelo Gemini Pro."""
        if self.model_gemini:
            try:
                response = self.model_gemini.generate_content(prompt)
                return response.text
            except Exception as e:
                return f"Error al generar la respuesta: {e}"
        else:
            return "La API Key no ha sido configurada."

    def cargar_interacciones(self):
        """Carga las interacciones desde el archivo JSON si existe."""
        if os.path.exists(NOMBRE_ARCHIVO_JSON):
            with open(NOMBRE_ARCHIVO_JSON, 'r') as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    print("Error al decodificar el archivo JSON. Se iniciará con un nuevo registro.")
                    return {"interacciones": []}
        else:
            return {"interacciones": []}

    def guardar_interacciones(self, data):
        """Guarda las interacciones en el archivo JSON."""
        with open(NOMBRE_ARCHIVO_JSON, 'w') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def agregar_al_historial(self, texto, es_usuario=True):
        """Agrega texto al historial de la interfaz."""
        self.historial_text.config(state=tk.NORMAL)
        tag = "usuario" if es_usuario else "asistente"
        font_style = ('Segoe UI', 12, 'bold') if es_usuario else ('Segoe UI', 12)
        self.historial_text.tag_config(tag, foreground="#333" if es_usuario else "#007bff", font=font_style)
        self.historial_text.insert(tk.END, f"{'Tú:' if es_usuario else 'Asistente:'} {texto}\n", tag)
        self.historial_text.config(state=tk.DISABLED)
        self.historial_text.see(tk.END)

    def iniciar_escucha(self):
        """Inicia la escucha de voz."""
        if not self.api_key:
            messagebox.showerror("Error", "La API Key no ha sido configurada. Por favor, ve a 'Configurar App'.")
            return

        self.agregar_al_historial("Escuchando...", es_usuario=True)
        self.update_idletasks()

        with sr.Microphone() as source:
            print("Di algo...")
            self.r.adjust_for_ambient_noise(source)
            try:
                audio = self.r.listen(source, timeout=20, phrase_time_limit=20)
                print("Procesando...")
                texto_entrada = self.r.recognize_google(audio, language=self.language)
                print(f"Has dicho: {texto_entrada}")
                self.agregar_al_historial(texto_entrada)
                self.procesar_respuesta(texto_entrada)
            except sr.UnknownValueError:
                self.agregar_al_historial("No pude entender lo que dijiste.", es_usuario=False)
                self.hablar("No pude entender lo que dijiste.")
            except sr.RequestError as e:
                error_msg = f"No se pudo solicitar resultados del servicio de reconocimiento de voz; {e}"
                self.agregar_al_historial(error_msg, es_usuario=False)
                self.hablar(error_msg)
            except sr.WaitTimeoutError:
                self.agregar_al_historial("No se detectó audio. Intenta de nuevo.", es_usuario=False)
                self.hablar("No se detectó audio. Intenta de nuevo.")
            except Exception as e:
                error_msg = f"Ocurrió un error inesperado: {e}"
                self.agregar_al_historial(error_msg, es_usuario=False)
                self.hablar(error_msg)

    def procesar_entrada_manual(self, event):
        """Procesa la entrada de texto manual."""
        if not self.api_key:
            messagebox.showerror("Error", "La API Key no ha sido configurada. Por favor, ve a 'Configurar App'.")
            return

        texto_entrada = self.entrada_texto.get()
        if texto_entrada:
            self.agregar_al_historial(texto_entrada)
            self.entrada_texto.delete(0, tk.END)
            self.procesar_respuesta(texto_entrada)

    def procesar_respuesta(self, texto_entrada):
        """Obtiene la respuesta de la IA y la muestra."""
        if not self.model_gemini:
            self.agregar_al_historial("La API Key no ha sido configurada.", es_usuario=False)
            self.hablar("La API Key no ha sido configurada.")
            return

        historial_interacciones = json.dumps(self.registro_interacciones, ensure_ascii=False)
        ajuste = "no des muchos detalles solo da tu respuesta y nunca hagas mas que una pregunta a la vez. "
        prompt_con_historial = f"Historial de interacciones: {historial_interacciones}\n\nPregunta del usuario: {texto_entrada} {ajuste}"
        respuesta_ai = self.obtener_respuesta_gemini(prompt_con_historial)
        print(f"Respuesta de la IA: {respuesta_ai}")
        self.agregar_al_historial(respuesta_ai, es_usuario=False)
        self.hablar(respuesta_ai)

        interaccion = {
            "timestamp": datetime.now().isoformat(),
            "texto_entrada": texto_entrada,
            "respuesta_asistente": respuesta_ai
        }
        self.registro_interacciones["interacciones"].append(interaccion)
        self.guardar_interacciones(self.registro_interacciones)

        if texto_entrada.lower() == "salir":
            self.hablar("Saliendo del asistente.")
            self.destroy()

    def mostrar_configuracion_voz(self):
        """Muestra la ventana de configuración de voz."""
        VoiceConfigWindow(self, self.selected_voice_id, self.voice_rate, self._guardar_configuracion_voz_callback)

    def _guardar_configuracion_voz_callback(self, voice_config):
        """Callback para guardar la configuración de voz desde VoiceConfigWindow."""
        self.selected_voice_id = voice_config.get('voice_id')
        self.voice_rate = voice_config.get('voice_rate')

        if self.selected_voice_id:
            try:
                self.engine.setProperty('voice', self.selected_voice_id)
            except Exception as e:
                print(f"Error al establecer la voz: {e}")
        if self.voice_rate is not None:
            self.engine.setProperty('rate', self.voice_rate)

        config = self._load_config()
        config['voice_id'] = self.selected_voice_id
        config['voice_rate'] = self.voice_rate
        self._save_config(config)

        messagebox.showinfo("Configuración", "Configuración de voz guardada.")

    # Eliminamos la definición duplicada de _guardar_configuracion_voz