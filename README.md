# Full-Text-Search_Project2
Proyecto 2 del curso de Base de datos 2. Construcción del índice invertido textual.

# Integrantes
- Ana Maria Accilio
- Diego Pacheco
- Juan Pedro Vásquez
- Luis Enrique Cortijo
- Marcelo Zuloeta

# Introducción
El índice invertido es una estructura de datos utilizada en motores de búsqueda y sistemas de recuperación de información. Consiste en un diccionario que mapea términos a una lista de documentos en los que aparecen esos términos. Esta estructura permite una búsqueda eficiente de documentos que contengan ciertos términos clave. 
El presente proyecto tiene como objetivo desarrollar esta estructura de datos de manera eficiente, con motivo de realizar búsquedas rápidas en un conjunto de documentos.

# Dataset
La base de datos utilizada es la Fashion Product Images. Esta contiene alrededor de 44 mil productos etiquetados por ID, categoría, género, color, año, etc.

# Estructura del proyecto

[image]

# Frontend (GUI)

[imagen del front]



[otra imagen del front]

[capybara logo]

¿Cómo se utiliza la GUI?
La GUI tiene una pantalla principal con dos pestañas, donde se puede visualizar una casilla para introducir una consulta.

# Backend (SPIMI)
El archivo inverted_index.py contiene la implementación del índice invertido utilizando el algoritmo SPIMI (Single-Pass In-Memory Indexing). El algoritmo SPIMI divide el proceso de indexación en bloques más pequeños para manejar grandes volúmenes de datos de manera eficiente.

El código incluye las siguientes funciones principales:

1. spimi_invert(): Esta función realiza la indexación de los documentos presentes en una carpeta de entrada. Utiliza el algoritmo SPIMI para generar el índice invertido.

2. binary_search_term_blocks(): Esta función realiza una búsqueda binaria en los bloques del índice invertido para encontrar un término específico. Utiliza una implementación eficiente de búsqueda binaria para mejorar el rendimiento de la búsqueda.

3. cosine_similarity(): Esta función calcula la similitud de coseno entre una consulta y los documentos indexados. Utiliza el índice invertido y los pesos TF-IDF para calcular la similitud de coseno.

## ¿Cómo se construye el índice invertido en PostgreSQL?

A grandes rasgos, para la construcción del índice invertido en PostgreSQL se necesitan 3 tablas principales.
- Una tabla para almacenar los documentos
- Una tabla para almacenar los términos
- Una tabla de relación entre términos y documentos

A partir de esto, se requere extraer los términos de los documentos y almacenarlos en una tabla de términos. Por ejemplo, se tiene lo siguiente:
Code:
INSERT INTO terms (term)
SELECT DISTINCT unnest(string_to_array(lower(content), ' ')) AS term
FROM documents;

La función string_to_array se utiliza para dividir el contenido de los documentos en términos individuales, y la función unnest se utiliza para convertir el resultado en filas individuales.

Lo siguiente es armar la relación entre los documentos y términos. Esto se puede lograr utilizando consultas SQL que identifiquen los términos que aparecen en cada documento y los almacenen en la tabla de relación. Por ejemplo:
Code:
INSERT INTO document_term (document_id, term)
SELECT d.id, t.term
FROM documents d
JOIN terms t ON lower(d.content) LIKE '%' || t.term || '%';

Una vez que se han extraído los términos y se ha creado la tabla de relación, se pueden crear índices en las columnas relevantes para mejorar el rendimiento de las consultas de búsqueda. Por lo general, se crean índices en las columnas de términos y en las columnas de identificadores de documentos para acelerar las búsquedas.

Con el índice invertido ya construído se pueden realizar consultas de búsqueda utilizando cláusulas SQL como WHERE y JOIN. Estas consultas aprovechan los índices para buscar rápidamente los documentos que contienen los términos de búsqueda especificados. Por tal motivo, las búsquedas de texto se vuelven más eficientes, ya que se evita la necesidad de realizar exploraciones completas de los documentos.
