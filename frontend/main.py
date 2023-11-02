import subprocess
import sys

def iniciar_sesion():
    proceso = subprocess.Popen(["python", "log.py"])
    proceso.wait()

    # Verificar si el inicio de sesión fue exitoso
    if proceso.returncode == 0:
        # Cerrar la ventana de log.py
        proceso.terminate()

        # Ejecutar UI.py
        subprocess.call(["python", "UI.py"])

if __name__ == "__main__":
    iniciar_sesion()