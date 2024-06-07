FROM python:3.9-slim

# Establecemos el directorio de trabajo del container
WORKDIR /app

# Instalamos herramientas de unzip
RUN apt-get update && apt-get install -y unzip curl && apt-get clean

# Copia los requisitos
COPY requirements.txt requirements.txt

# Upgradeamos el pip
RUN pip install --upgrade pip

# Instalamos Airflow con sus constraints
RUN pip install "apache-airflow==2.3.3" \
    --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.3.3/constraints-3.8.txt"

# Instalamos los requisitos necesarios    
RUN pip install -r requirements.txt 

COPY dags /app/dags

COPY logs /app/logs

COPY start_airflow.sh /app/

COPY .env /app/

USER root
RUN mkdir -p /app/download_data && chmod +x /app/download_data
RUN mkdir -p /app/processed_data && chmod +x /app/processed_data
RUN chmod +x /app/start_airflow.sh

ENV AIRFLOW_HOME=/app
ENV AIRFLOW__CORE__DAGS_FOLDER=/app/dags
ENV AIRFLOW__CORE__LOAD_EXAMPLES=False

EXPOSE 8080

# Define el comando por defecto para ejecutar el script de inicio
ENTRYPOINT ["/app/start_airflow.sh"]
