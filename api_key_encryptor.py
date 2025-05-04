import os
from cryptography.fernet import Fernet
from tkinter import messagebox

class ApiKeyEncryptor:
    KEY_FILE = 'encryption.key'

    def _get_encryption_key(self):
        """Obtiene la clave de encriptación."""
        if not os.path.exists(self.KEY_FILE):
            key = Fernet.generate_key()
            with open(self.KEY_FILE, 'wb') as key_file:
                key_file.write(key)
        try:
            with open(self.KEY_FILE, 'rb') as key_file:
                key = key_file.read()
            return key
        except Exception as e:
            messagebox.showerror("Error", f"Error al leer la clave de encriptación: {e}")
            return None

    def encrypt(self, data: str) -> bytes:
        """Encripta los datos proporcionados."""
        key = self._get_encryption_key()
        if key:
            f = Fernet(key)
            return f.encrypt(data.encode())
        return b''

    def decrypt(self, encrypted_data: bytes) -> str:
        """Desencripta los datos proporcionados."""
        key = self._get_encryption_key()
        if key:
            f = Fernet(key)
            try:
                return f.decrypt(encrypted_data).decode()
            except Exception as e:
                messagebox.showerror("Error", f"Error al desencriptar los datos: {e}")
                return ''
        return ''