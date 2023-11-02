import psycopg2

conexion = psycopg2.connect(
    host="localhost",
    database="BD2",
    user="postgres",
    password="cangrejoSJ20"
)

cursor = conexion.cursor()

cursor.execute("SELECT * FROM muertos")
resultados = cursor.fetchall()
for fila in resultados:
    print(fila)
cursor.close()
conexion.close()