# Solución propuesta para replicación de datos de SQL Server a BigQuery

En este documento se presenta la solución propuesta para la replicación de datos de SQL Server a BigQuery

## Arquitectura

Este es el diagrama de arquitectura que nos permite entender como podemos realizar replicación de tablas desde SQL Server hacia BigQuery en GCP.

![Arquitectura Carga Inicial](/images/Arquitectura_Inicial.jpg)
_Diagrama 1. Arquitectura de la carga inicial de datos_      


![Arquitectura Carga Inicial](/images/Arquitectura_Replicacion.jpg)
_Diagrama 2. Arquitectura de la replicación de datos_       


### Supuestos 📋
En esta solución propuesta se asume que existe comunicación entre la nube de GCP y los servidores de SQL Server, por lo cual los scripts y códigos mostrados en este repositorio no contemplan alguna configuración de redes.

### Pre-requisitos 📋

1. Habilitar el CDC en SQL Server tanto en la Base de Datos como en las tablas:
```
-- enable CDC on the database
EXEC sys.sp_cdc_enable_db;
-- enable CDC on the CatLineasAereas table
EXEC sys.sp_cdc_enable_table
  @source_schema = N'dbo',
  @source_name   = N'CatLineasAereas',
  @role_name     = NULL;
-- enable CDC on the Pasajeros table
EXEC sys.sp_cdc_enable_table
  @source_schema = N'dbo',
  @source_name   = N'Pasajeros',
  @role_name     = NULL;
-- enable CDC on the Vuelos table
EXEC sys.sp_cdc_enable_table
  @source_schema = N'dbo',
  @source_name   = N'Vuelos',
  @role_name     = NULL;
```
   
2. Crear los datasets y las tablas necesarias en BigQuery
Creación de datasets
```
-- create dataset central
CREATE SCHEMA central
OPTIONS(
  location="us"
  );
-- create dataset sucursal1
CREATE SCHEMA sucursal1
OPTIONS(
  location="us"
  );
-- create dataset sucursal2
CREATE SCHEMA sucursal2
OPTIONS(
  location="us"
  );
```

Creación de tablas
```
-- create table CatLineasAereas
CREATE TABLE central.CatLineasAereas
(
  code STRING,
  linea_aerea STRING
);
-- create table sucursal1.Pasajeros 
CREATE TABLE sucursal1.Pasajeros
(
  id_pasajero INT64,
  pasajero STRING,
  edad INT64
);
-- create table sucursal1.Vuelos
CREATE TABLE sucursal1.Vuelos
(
  cve_la STRING,
  viaje DATE,
  clase STRING,
  precio NUMERIC,
  Ruta STRING,
  cve_cliente INT64
);
-- create table sucursal2.Pasajeros 
CREATE TABLE sucursal2.Pasajeros
(
  id_pasajero INT64,
  pasajero STRING,
  edad INT64
);
-- create table sucursal2.Vuelos
CREATE TABLE sucursal2.Vuelos
(
  cve_la STRING,
  viaje DATE,
  clase STRING,
  precio NUMERIC,
  Ruta STRING,
  cve_cliente INT64
);
```

## Solución 🔧
1. El diagrama 1 muestra la arquitectura para realizar la carga inicial de las tablas originales que se encuentran en SQL Server.
    - Se lanza un job en el servicio de Dataproc Serverless por cada una de las tablas en SQL Server. 
    - Este job lanzará un ETL el cual está codificado en PySpark y su nombre es [load_init.py](/dataproc/load_init.py). 
    - El código se conecta con SQL Server por medio de un conector JDBC, extrae la información de una tabla, se almacena en un dataframe para posteriormente guardarla en BigQuery, utilizando otro conector.
2. Se habilita el CDC en cada una de las tablas de SQL Server que se van a replicar hacia BigQuery, como se indica en el [paso 1](/###pre-reuisitos) de la sección de Pre-requisitos.
3. El diagrama 2 muestra la arquitectura para realizar la replicación de cada una de las tablas que se encuentran en SQL Server hacia BigQuery.
    - Se calendariza cada 5 minutos la ejecución de los jobs en el servicio de Dataproc Serverless por cada una de las tablas en SQL Server que estamos replicando con CDC.
    - Estos jobs calendarizados lanzan un ETL el cual está codificado en PySpark y su nombre es [replicate_cdc.py](/dataproc/replicate_cdc.py).
    - El código se conecta con SQL Server por medio de un conector JDBC, extrae la información de las tablas que tienen el prefijo "cdc.dbo_", se almacena en un dataframe, con el cual se identificarán los cambios que existieron en la tabla, para posteriormente reflejar los cambios en BigQuery, utilizando otro conector.
    - La calendarización de estos jobs se realiza por medio del servicio de Cloud Composer (Airflow), para llevar a cabo la orquestación se crea un DAG llamado "run_dataproc_job", el cual está codificado en Apache Airflow, que se encuentra en este archivo [dag_dataproc_job,py](/composer/dag_dataproc_job_py).

## Autor ✒️

* **Genaro Zárate** - *Documentación* - [gzarate71](https://github.com/gzarate71)

