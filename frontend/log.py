from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QMessageBox
import csv
import sys

class LoginWindow(QMainWindow):
    def __init__(self):
        super(LoginWindow, self).__init__()

        self.setWindowTitle("Inicio de Sesión")
        self.setGeometry(100, 100, 300, 200)

        self.label_usuario = QLabel("Usuario:", self)
        self.label_usuario.setGeometry(50, 30, 60, 20)

        self.input_usuario = QLineEdit(self)
        self.input_usuario.setGeometry(120, 30, 150, 20)

        self.label_contraseña = QLabel("Contraseña:", self)
        self.label_contraseña.setGeometry(30, 70, 80, 20)

        self.input_contraseña = QLineEdit(self)
        self.input_contraseña.setGeometry(120, 70, 150, 20)
        self.input_contraseña.setEchoMode(QLineEdit.Password)

        self.boton_login = QPushButton("Iniciar Sesión", self)
        self.boton_login.setGeometry(100, 120, 100, 30)
        self.boton_login.clicked.connect(self.login)

        self.boton_crear_usuario = QPushButton("Crear Usuario", self)
        self.boton_crear_usuario.setGeometry(100, 160, 100, 30)
        self.boton_crear_usuario.clicked.connect(self.crear_usuario)

    def login(self):
        usuario = self.input_usuario.text()
        contraseña = self.input_contraseña.text()

        if not usuario or not contraseña:
            QMessageBox.warning(self, "Inicio de Sesión", "Por favor, ingrese usuario y contraseña.")
            return

        with open("usuarios.csv", "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["user"] == usuario and row["password"] == contraseña:
                    QMessageBox.information(self, "Inicio de Sesión", "Inicio de sesión exitoso.")
                    self.close()  # Cerrar la ventana de inicio de sesión
                    return

        QMessageBox.warning(self, "Inicio de Sesión", "Nombre de usuario o contraseña incorrectos.")

    def crear_usuario(self):
        usuario = self.input_usuario.text()
        contraseña = self.input_contraseña.text()

        if not usuario or not contraseña:
            QMessageBox.warning(self, "Crear Usuario", "Por favor, ingrese usuario y contraseña.")
            return

        with open("usuarios.csv", "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["user"] == usuario:
                    QMessageBox.warning(self, "Crear Usuario", "El usuario ya existe.")
                    return

        with open("usuarios.csv", "a") as file:
            writer = csv.writer(file)
            writer.writerow([usuario, contraseña])

        QMessageBox.information(self, "Crear Usuario", "Usuario creado exitosamente.")
        self.close()  # Cerrar la ventana de inicio de sesión

if __name__ == "__main__":
    app = QApplication([])
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())