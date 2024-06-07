#!/bin/bash


# Inicializar la base de datos de Airflow (necesario la primera vez)

airflow db init

# Crear un usuario administrador si no existe
airflow users create \
    --username admin \
    --password admin \
    --firstname Nombre \
    --lastname Apellido \
    --role Admin \
    --email admin@example.com

# Iniciar el scheduler y el webserver de Airflow
airflow scheduler &
exec airflow webserver