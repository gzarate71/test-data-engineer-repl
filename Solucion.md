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
* El diagrama 1 muestra la arquitectura para realizar la carga inicial de las tablas originales que se encuentran en SQL Server.
    - Se debe ejecutar un job en el servicio de Dataproc Serverless, este job lanzará un ETL el cual está codificado en código PySpark y su nombre es [load_init.py](/dataproc/load_init.py)
* Invita una cerveza 🍺 o un café ☕ a alguien del equipo. 
* Da las gracias públicamente 🤓.
* Dona con cripto a esta dirección: `0xf253fc233333078436d111175e5a76a649890000`
* etc.

## Autor ✒️

* **Genaro Zárate** - *Documentación* - [gzarate71](https://github.com/gzarate71)

