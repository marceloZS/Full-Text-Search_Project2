import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import psycopg2
import time

def buscar():
    texto_busqueda = entrada.get()

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
    
    cuadro1_texto = f"Resultado 1: {conteo_resultados} resultados, tiempo de ejecución: {execution_time} segundos"
    cuadro1.config(text=cuadro1_texto)
    
    for i, fila in enumerate(resultados):
        if i < 10:  # Mostrar solo los primeros 10 resultados
            resultados_text1.insert(tk.END, f"Resultado {i+1}: {fila}\n")

    cursor.close()
    conexion.close()

ventana = tk.Tk()
ventana.title("Super_proyecto_BD2")

# Cambiar el fondo de la ventana
ruta_fondo = "nuevo_fondo.png"
imagen_fondo = Image.open(ruta_fondo)

ventana.update()
ancho = ventana.winfo_screenwidth()
alto = ventana.winfo_screenheight()
imagen_fondo = imagen_fondo.resize((ancho, alto), Image.BICUBIC)

fondo = ImageTk.PhotoImage(imagen_fondo)
canvas = tk.Canvas(ventana, width=ancho, height=alto)
canvas.place(x=0, y=0, relwidth=1, relheight=1)
canvas.create_image(0, 0, image=fondo, anchor="nw")

ventana.state('zoomed')

entrada = ttk.Entry(ventana)
entrada.pack()

boton_buscar = ttk.Button(ventana, text="Buscar", command=buscar)
boton_buscar.pack()

contenedor = ttk.Frame(ventana)
contenedor.pack(pady=0)  # Ajustar el padding del contenedor

imagen_logo = tk.PhotoImage(file="logo.png")
imagen_logo = imagen_logo.subsample(2)  # Reducir el tamaño de la imagen a la mitad
label_logo = ttk.Label(contenedor, image=imagen_logo)
label_logo.grid(row=0, column=1, pady=0)  # Ajustar el padding de la imagen

cuadro1 = ttk.Label(contenedor, text="Resultado 1: ", style="Resultado.TLabel")
cuadro1.grid(row=0, column=0, padx=200, pady=0)  # Ajustar el padding del cuadro1

cuadro2 = ttk.Label(contenedor, text="Resultado 2: ", style="Resultado.TLabel")
cuadro2.grid(row=0, column=2, padx=200, pady=0)  # Ajustar el padding del cuadro2

style = ttk.Style()
style.configure("Resultado.TLabel", foreground="black", borderwidth=2, relief="solid", padding=(10, 10))

scrollbar1 = ttk.Scrollbar(contenedor)
scrollbar1.grid(row=1, column=1, sticky="NS")

resultados_text1 = tk.Text(contenedor, yscrollcommand=scrollbar1.set, height=10, bg='black', fg='cyan')
resultados_text1.grid(row=1, column=0)

scrollbar1.config(command=resultados_text1.yview)

scrollbar2 = ttk.Scrollbar(contenedor)
scrollbar2.grid(row=1, column=3, sticky="NS")

resultados_text2 = tk.Text(contenedor, yscrollcommand=scrollbar2.set, height=10, bg='black', fg='cyan')
resultados_text2.grid(row=1, column=2)

scrollbar2.config(command=resultados_text2.yview)

# Ajustar el tamaño de los cuadros y evitar que se redimensionen automáticamente
contenedor.grid_columnconfigure(0, weight=1)
contenedor.grid_columnconfigure(2, weight=1)
contenedor.grid_rowconfigure(0, weight=1)
contenedor.grid_rowconfigure(1, weight=1)

# Mostrar los elementos ocultos
cuadro1.grid()
cuadro2.grid()

ventana.mainloop()