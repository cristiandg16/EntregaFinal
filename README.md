
# Entrega_Final_DataEngineering
Repositorio de la última entrega del curso de Data Engineering dictado por CoderHouse

# Comisión
60340

# Alumno
Genga, Cristian Darío

# Consigna

## Objetivos generales
1. Crear un pipeline que extraiga datos de una API pública de forma
constante combinándolos con información extraída de una base de
datos (mínimamente estas 2 fuentes de datos, pero pueden utilizarse
hasta 4).
2. Colocar los datos extraídos en un Data Warehouse.
3. Automatizar el proceso que extraerá, transformará y cargará datos
cuantitativos (ejemplo estos son: valores de acciones de la bolsa,
temperatura de ciudades seleccionadas, valor de una moneda
comparado con el dólar, casos de covid).
4. Automatizar el proceso para lanzar alertas (2 máximo) por e-mail en
caso de que un valor sobrepase un límite configurado en el código.


# Descripción del Proyecto
Consultar la posición en tiempo real de cada colectivo de la ciudad de Buenos Aires y almacenarlo en una tabla de hechos en el DW de Redshift.

# Información de la API
► API Doc: https://api-transporte.buenosaires.gob.ar/console
► API Console: https://apitransporte.buenosaires.gob.ar/console/

# Proceso

El dag consta de las siguientes tareas que estan ordenadas segun ejecución:
1. *downloadFilesFeed*: Consulta a la API y como respuesta obtiene un zip con las tablas que arman el DW. Lo extraemos en la ruta /app/download_data/<file.txt> .
2. *checkFileAgency* : Consulta si el archivo agency.txt se encuentra alojado en el sistema. En caso que no envía un mensaje de error.
3. *loadDimAgency* : Se encarga de cargar la tabla Dim_Agency en el DW de Redshift.
4. *checkFileRoutes* : Consulta si el archivo routes.txt se encuentra alojado en el sistema. En caso que no envía un mensaje de error.
5. *loadDimRoutes* : Se encarga de cargar la tabla Dim_Routes en el DW de Redshift.
6. *loadFactPositions* : Consulta a la api, en caso de éxito retorna un archivo JSON con las posiciones de los colectivos de la ciudad. Luego es cargado en el DW de Redshift.
7. *sendMailFinished* : Si el proceso termina con éxito, se enviara un mail indicado lo mencionado.
8. *errorHandler* : Este step se encarga de escuchar cada paso del proceso. En caso de error, recopila el mensaje y envía un mail indicando lo sucedido.

# Airflow

Utilizamos la versión 2.3.3 . 
Username: admin
Password: admin

# Montar el contenedor
. Reconstruir la imagen de docker con el siguiente comando: docker build -t my_airflow_image .
. Ejecutar el contenedor con el siguiente comando: docker run -p 8080:8080 -d my_airflow_image