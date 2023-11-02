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