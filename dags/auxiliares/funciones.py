from datetime import timedelta,datetime
from pathlib import Path
import zipfile
import io
import json
import datetime 
import requests
import psycopg2
import pandas as pd
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv
import smtplib
from email import message
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# Work path
dag_path = os.getcwd()

# Variables de entorno
load_dotenv()

# Descarga y descomprime los archivos desde la api
def download_files_feed_frequency():
    
    # Esta api devuelve un archivo .zip con varios files para armar el DW   
    api_url = "https://apitransporte.buenosaires.gob.ar/colectivos/feed-gtfs-frequency?client_id="+os.getenv('CLIENT_ID')+"&client_secret="+os.getenv('CLIENT_SECRET')
    
    response = requests.get(api_url)
    
    # Corroboramos la respuesta de la api
    if response.status_code == 200:
        
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            # Extraer todo el contenido del archivo ZIP en el directorio actual
            z.extractall("/app/download_data")
            print("Archivo ZIP descargado y extraído exitosamente.")
            
            for file_info in z.infolist():
                file_path = os.path.join("/app/download_data", file_info.filename)
                # Establecer permisos de lectura y escritura para el propietario y grupo, y solo lectura para otros
                os.chmod(file_path, 0o664)
            
    else:
        print(f"Error al descargar el archivo ZIP. Código de estado: {response.status_code}")
 
##################################################################
####                    AGENCY                                ####
##################################################################  
        
# Trunca y carga la Dimension Agency     
def load_dim_agency():
    # Buscamos el file de agency.txt para cargarlo en redshift
    connection = None
    file_path = os.path.join('/app/download_data', 'BUENOS_AIRES\\agency.txt')
    
    df_agency = pd.read_csv(file_path, delimiter=',')
    
    print(df_agency)
    
    df_agency['agency_id'] = df_agency['agency_id'].astype(str)
    
    
    try:
        conection = psycopg2.connect(
        dbname = os.getenv('NAME_DATABASE'),
        user = os.getenv('USER_DATABASE'),
        password = os.getenv('PASS_DATABASE'),
        host = os.getenv('HOST_DATABASE'),
        port= os.getenv('PORT_DATABASE'))

        cursor = conection.cursor()
        cursor.execute("TRUNCATE TABLE cristiangen16_coderhouse.dim_agency")
        
        for i in range(df_agency.shape[0]-1):
            tuple_insert = tuple(df_agency.iloc[i])
            cursor.execute("INSERT INTO cristiangen16_coderhouse.dim_agency(agency_id ,agency_name,agency_url,agency_timezone,agency_lang,agency_phone,agency_branding_url,agency_fare_url,agency_email) VALUES  (%s,%s,%s,%s,%s,%s,%s,%s,%s)",tuple_insert)
        
        conection.commit()
        print("Dimension Agency cargada en Amazon Redshift con éxito.")
        cursor.close()
        conection.close()
    
    except Exception as e:
        print("Error al cargar la Dimension Agency en Amazon Redshift:", e)
    
    finally:
        if cursor:
            cursor.close()
        if conection:
            conection.close()

##################################################################
####                    ROUTES                                ####
##################################################################        

# Trunca y carga la Dimension Routes
def load_dim_routes():
    connection = None
    file_path = os.path.join('/app/download_data', 'BUENOS_AIRES\\routes.txt')
    
    df_routes = pd.read_csv(file_path, delimiter=',')
    
    df_routes['route_id'] = df_routes['route_id'].astype(str)    
    df_routes['agency_id'] = df_routes['agency_id'].astype(str)
    df_routes['route_type'] = df_routes['route_type'].astype(str)
    
    try:
        conection = psycopg2.connect(
        dbname = os.getenv('NAME_DATABASE'),
        user = os.getenv('USER_DATABASE'),
        password = os.getenv('PASS_DATABASE'),
        host = os.getenv('HOST_DATABASE'),
        port= os.getenv('PORT_DATABASE'))

        cursor = conection.cursor()
        cursor.execute("TRUNCATE TABLE cristiangen16_coderhouse.dim_routes")
        
        for i in range(df_routes.shape[0]-1):
            tuple_insert = tuple(df_routes.iloc[i])
            cursor.execute("INSERT INTO cristiangen16_coderhouse.dim_routes(route_id,agency_id,route_short_name,route_long_name,route_desc,route_type,route_url,route_branding_url,route_color,route_text_color) VALUES  (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",tuple_insert)
        
        conection.commit()
        print("Dimension Routes cargada en Amazon Redshift con éxito.")
        cursor.close()
        conection.close()
    
    except Exception as e:
        print("Error al cargar la Dimension Routes en Amazon Redshift:", e)
    
    finally:
        if cursor:
            cursor.close()
        if conection:
            conection.close()
    

##################################################################
####                    fact                                  ####
##################################################################  
    
# Funcion encargada de conectar con la API
def consulta_api_params(url,params):
    try:
        response = requests.get(url,params = params)
        if response.status_code == 200:  #Corroboramos que la peticion sea exitosa
            print("Respuesta de la API:")
            # Convertimos la respuesta a JSON
            return response.json()
        else:
            print("Error al consultar la API. Código de estado:", response.status_code)
    except Exception as e:
        print("Error al conectarse a la API:", e)


# Funcion que nos permite pasarle los diferentes parametros a la consulta.
def get_params(route_id,agency_id,trip,client_id,client_secret):
    params = {}
    
    if(route_id != ""):
        params['route_id'] = route_id
    
    if(agency_id != ""):
        params['agency_id'] = agency_id
        
    if(trip != ""):
        params['Trip'] = trip
        
    if(client_id != ""):
        params['client_id'] = client_id
        
    if(client_secret != ""):
        params['client_secret'] = client_secret
        
    return params


# Funcion encargada de corregir valores que por defecto vienen con valores incompatibles
def correcion_valores(docjson):
    df = pd.DataFrame(docjson)
    df['datetime_consulta'] = pd.to_datetime(df['timestamp'],unit='s') - datetime.timedelta(hours=3)
    df['speed'] = df['speed'].round(3)
    df['timestamp'] = df['timestamp'].astype(str)
    df['direction'] = df['direction'].astype(str)
    df['agency_id'] = df['agency_id'].astype(str)
    
    new_order = ['id','datetime_consulta','route_id','latitude','longitude','speed','timestamp','direction','agency_name','agency_id','route_short_name','tip_id','trip_headsign']
    df = df[new_order]
 
    return df

# Función encargada de cargar los datos obtenidos en la tabla de Redshift
def cargar_df_redshift(df):
    try:
        conection = psycopg2.connect(
        dbname = os.getenv('NAME_DATABASE'),
        user = os.getenv('USER_DATABASE'),
        password = os.getenv('PASS_DATABASE'),
        host = os.getenv('HOST_DATABASE'),
        port= os.getenv('PORT_DATABASE'))
        
        
        datetime_insert = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") #Campo de fecha de insercion en la tabla
        cursor = conection.cursor()
        
        for i in range(df.shape[0]-1):
            tupla_final = tuple(df.iloc[i]) + (datetime_insert,)
            cursor.execute("INSERT INTO cristiangen16_coderhouse.Fact_Bus_Position(idTrack, dttmCatch,idRoute ,adLatitude,adLongitude,adSpeed,adTimestamp,adDirection,adAgencyName,idAgency,adRouteShortName,idTransport,adTripHeadsign,dttmInsert) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)" , tupla_final)
        
        conection.commit()
        print("Datos cargados en Amazon Redshift con éxito.")
        cursor.close()
        conection.close()
        
    except Exception as e:
        print("Error al cargar datos en Redshift:", e)
        
        
# Funcion Principal
def load_fact():
    url_p = 'https://apitransporte.buenosaires.gob.ar/colectivos/vehiclePositionsSimple'

    client_id = os.getenv('CLIENT_ID')
    client_secret = os.getenv('CLIENT_SECRET')

    params = get_params("","","",client_id,client_secret)

    datos_json = consulta_api_params(url_p, params)
    # Crear DataFrame a partir del JSON
    df = correcion_valores(datos_json)
    cargar_df_redshift(df)


########################################################
####                    MAILING                     ####
########################################################


def send_finished_email(param_subject, content):
    message = Mail(
        from_email=os.getenv('FROM_EMAIL'),
        to_emails=os.getenv('TO_EMAIL'),
        subject=param_subject,
        html_content='<strong>'+content+'</strong>')
    try:
        sg = SendGridAPIClient(os.getenv('API_CLIENT_SENDGRID'))
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e.message)
        
        
#########################################################

def send_error_email(**kwargs):
    """Enviar un correo electrónico cuando una tarea falla."""
    task_instance = kwargs['task_instance']
    task_id = task_instance.task_id
    dag_id = kwargs['dag'].dag_id
    execution_date = kwargs['execution_date']
    log_url = task_instance.log_url

    subject = f"Error en el DAG: {dag_id}"
    content = f"""
    La tarea {task_id} falló. \n
    DAG: {dag_id} \n
    Fecha de Ejecución: {execution_date} \n
    URL del Log: {log_url}
    """
    message = Mail(
        from_email=os.getenv('FROM_EMAIL'),
        to_emails=os.getenv('TO_EMAIL'),
        subject=subject,
        html_content='<strong>'+content+'</strong>')
    
    
    try:
        sg = SendGridAPIClient(os.getenv('API_CLIENT_SENDGRID'))
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e.message)
  
