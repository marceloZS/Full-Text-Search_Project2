from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QGridLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QScrollBar, QFrame
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtCore import Qt, QPropertyAnimation

import psycopg2
import time
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        # Configurar la ventana
        self.setWindowTitle("Super_proyecto_BD2")
        self.setGeometry(0, 0, self.width(), self.height())

        # Configurar el fondo
        self.fondo = QtGui.QPixmap('fondo_.png')
        self.fondo = self.fondo.scaled(self.width(), self.height(), QtCore.Qt.KeepAspectRatio)
        self.palette = QtGui.QPalette()
        self.palette.setBrush(QtGui.QPalette.Background, QtGui.QBrush(self.fondo))
        self.setPalette(self.palette)

       # Cargar la imagen del logo
        logo = QtGui.QPixmap('logo.png')
        logo = logo.scaled(logo.width() + 1, logo.height() + 1, QtCore.Qt.KeepAspectRatio)

        # Configurar el layout
        self.layout = QGridLayout()
        self.widget = QtWidgets.QWidget(self)
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)

        # Configurar los elementos
        self.entrada = QLineEdit(self)
        self.entrada.setStyleSheet("QLineEdit { color: #ffff00; font-size: 16px; font-weight: bold; text-shadow: 2px 2px 4px #000000; }")
        self.entrada.setPlaceholderText("Inserte el texto a buscar")
        self.boton_buscar = QPushButton("Buscar", self)
        self.boton_buscar.setStyleSheet("QPushButton { color: #ffff00; font-size: 16px; font-weight: bold; text-shadow: 2px 2px 4px #000000; }")
        self.boton_buscar.clicked.connect(self.buscar)
        self.entrada_numero = QLineEdit(self)
        self.entrada_numero.setStyleSheet("QLineEdit { color: #ffff00; font-size: 16px; font-weight: bold; text-shadow: 2px 2px 4px #000000; }")
        self.entrada_numero.setPlaceholderText("Ingrese la cantidad de resultados esperados")

        self.cuadro1 = QLabel("Postgres: ", self)
        self.cuadro1.setStyleSheet("QLabel { color: #ffff00; font-size: 20px; font-weight: bold; text-shadow: 2px 2px 4px #00ffff; background-color: #000000; }")

        self.cuadro2 = QLabel("Resultado 2: ", self)
        self.cuadro2.setStyleSheet("QLabel { color: #ffff00; font-size: 20px; font-weight: bold; text-shadow: 2px 2px 4px #ffff00; background-color: #000000; }")

        self.resultados_text1 = QTextEdit(self)
        self.resultados_text1.setStyleSheet("QTextEdit { color: #ffff00; font-size: 16px; font-weight: bold; text-shadow: 2px 2px 4px #00ffff; background-color: #000000; }")
        self.resultados_text2 = QTextEdit(self)
        self.resultados_text2.setStyleSheet("QTextEdit { color: #ffff00; font-size: 16px; font-weight: bold; text-shadow: 2px 2px 4px #ffff00; background-color: #000000; }")

        self.scrollbar1 = QScrollBar(self)
        self.scrollbar1.setStyleSheet("QScrollBar { background-color: #000000; } QScrollBar::handle { background-color: #ff00ff; }")
        self.scrollbar2 = QScrollBar(self)
        self.scrollbar2.setStyleSheet("QScrollBar { background-color: #000000; } QScrollBar::handle { background-color: #00ff00; }")

        self.resultados_text1.setVerticalScrollBar(self.scrollbar1)
        self.resultados_text2.setVerticalScrollBar(self.scrollbar2)

        # Crear los QFrames para los cuadros
        frame_cuadro1 = QFrame(self)
        frame_cuadro1.setObjectName("frame_cuadro")
        frame_cuadro2 = QFrame(self)
        frame_cuadro2.setObjectName("frame_cuadro")

        # Configurar los estilos CSS para los QFrames
        frame_cuadro1.setStyleSheet("#frame_cuadro { background-color: #000000; border: 1px solid black; }")
        frame_cuadro2.setStyleSheet("#frame_cuadro { background-color: #000000; border: 1px solid black; }")

        # Configurar los layouts para los QFrames
        layout_cuadro1 = QVBoxLayout(frame_cuadro1)
        layout_cuadro2 = QVBoxLayout(frame_cuadro2)

        # Añadir los QLabel a los layouts de los QFrames
        layout_cuadro1.addWidget(self.cuadro1)
        layout_cuadro2.addWidget(self.cuadro2)

        # Añadir los QFrames al layout principal
        self.layout.addWidget(frame_cuadro1, 1, 0)
        self.layout.addWidget(frame_cuadro2, 1, 2)

        # Añadir los elementos al layout
        self.layout.addWidget(self.entrada, 0, 0)
        self.layout.addWidget(self.entrada_numero, 0, 1)  # Cambiado de posición
        self.layout.addWidget(self.boton_buscar, 0, 2)  # Cambiado de posición
        self.layout.addWidget(self.resultados_text1, 2, 0)
        self.layout.addWidget(self.resultados_text2, 2, 2)
        self.layout.addWidget(self.scrollbar1, 2, 1)
        self.layout.addWidget(self.scrollbar2, 2, 3)

        # Configurar la imagen del logo
        self.label_logo = QLabel(self)
        self.label_logo.setPixmap(logo)
        self.label_logo.setAlignment(QtCore.Qt.AlignCenter)

        # Añadir el QLabel al layout en la posición deseada
        self.layout.addWidget(self.label_logo, 1, 1)

        # Animación de desvanecimiento para el logo
        self.fade_animation = QPropertyAnimation(self.label_logo, b"opacity")
        self.fade_animation.setDuration(2000)
        self.fade_animation.setStartValue(1.0)
        self.fade_animation.setEndValue(0.0)
        self.fade_animation.setEasingCurve(QtCore.QEasingCurve.InOutQuad)
        self.fade_animation.setLoopCount(-1)
        self.fade_animation.start()

    def buscar(self):
        texto_busqueda = self.entrada.text()

        conexion = psycopg2.connect(
            host="localhost",
            database="BD2",
            user="postgres",
            password="cangrejoSJ20"
        )
        cursor = conexion.cursor()

        consulta = f"SELECT * FROM proyecto WHERE datos ILIKE '%{texto_busqueda}%'"

        start_time = time.time()
        cursor.execute(consulta)
        resultados = cursor.fetchall()
        execution_time = time.time() - start_time

        conteo_resultados = len(resultados)

        cuadro1_texto = f"Postgres: {conteo_resultados} resultados" +"\n" + f"tiempo de ejecución: {execution_time} msec"
        self.cuadro1.setText(cuadro1_texto)

        self.resultados_text1.clear()

        if self.entrada_numero.text() != "":
            k = int(self.entrada_numero.text())
        else:
            k = 10

        for i, fila in enumerate(resultados):
            if i < k:
                self.resultados_text1.append(f"Resultado {i+1}: {fila}\n")

        cursor.close()
        conexion.close()

app = QApplication([])
window = MainWindow()
window.show()
sys.exit(app.exec_())