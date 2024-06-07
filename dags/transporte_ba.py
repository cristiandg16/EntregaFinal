from datetime import timedelta,datetime
from pathlib import Path
import json
import datetime
import requests
import psycopg2
from auxiliares.funciones import * 
from dotenv import load_dotenv
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.sensors.filesystem import FileSensor
from airflow.operators.dummy import DummyOperator
from airflow.utils.trigger_rule import TriggerRule
import pandas as pd
import os


# Cargar variables de entorno desde el archivo .env
load_dotenv()
dag_path = os.getcwd()



# argumentos por defecto para el DAG
default_args = {
    'owner': 'Cristian Genga',
    'start_date': datetime.datetime(2024,6,1) ,
    'email_on_retry': False,
    'email_on_failure': True,
    'retries':1,
    'retry_delay': timedelta(minutes=1)
}


transport_dag = DAG(
    dag_id='Consulta_Colectivos_CABA',
    default_args=default_args,
    description='Consulta a la API de transporte de la ciudad de Buenos Aires e inserta en Redshift',
    schedule_interval="@daily",
    catchup=False
)

downloadFilesFeed = PythonOperator(
    task_id='descargar_files',
    python_callable=download_files_feed_frequency,
    dag = transport_dag
)

checkFileAgency = FileSensor(
        task_id='check_file_agency',
        filepath=os.path.join('app', 'download_data', 'BUENOS_AIRES\\agency.txt'),
        poke_interval=60,
        timeout=600,
        dag = transport_dag
)

checkFileRoutes = FileSensor(
        task_id='check_file_routes',
        filepath=os.path.join('app', 'download_data', 'BUENOS_AIRES\\routes.txt'),
        poke_interval=60,
        timeout=600,
        dag = transport_dag
)

loadDimAgency = PythonOperator(
    task_id='load_dim_agency',
    python_callable=load_dim_agency,
    dag = transport_dag
)

loadDimRoutes = PythonOperator(
    task_id='load_dim_routes',
    python_callable=load_dim_routes,
    dag = transport_dag
)

loadFactPositions = PythonOperator(
    task_id='load_fact',
    python_callable=load_fact,
    dag = transport_dag
)

sendMailFinished = PythonOperator(
    task_id='mailing',
    python_callable=send_finished_email,
    op_kwargs={'param_subject':'Proceso Terminado', 'content':'Ha Finalizado el proceso con exito.'},
    dag = transport_dag
)

errorHandler = PythonOperator(
    task_id='error_handler',
    python_callable=send_error_email,
    provide_context=True,
    trigger_rule=TriggerRule.ONE_FAILED,
    dag=transport_dag
)


downloadFilesFeed >> checkFileAgency >> loadDimAgency >> checkFileRoutes >> loadDimRoutes >> loadFactPositions >> sendMailFinished

# Configuración del error handler para todas las tareas
tasks = [downloadFilesFeed, checkFileAgency, loadDimAgency, checkFileRoutes, loadDimRoutes, loadFactPositions, sendMailFinished]
for task in tasks:
    task >> errorHandler

