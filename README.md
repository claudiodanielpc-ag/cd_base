# 📦 cd_base

Librería para conexión segura a base de datos mediante túnel SSH.

Este paquete permite conectarse a la base de datos de la empresa desde Python para:

🔎 Ejecutar consultas SQL

⚙️ Ejecutar Stored Procedures

## 🚀 Instalación

Para instalar la librería directamente desde GitHub:

```python
pip install git+https://github.com/claudiodanielpc-ag/cd_base.git
```
## 📥 Importación

Una vez instalada, la librería se importa de la siguiente manera:

```python
from cd_base import ConexionBD
```

## 🔐 Configuración de credenciales

La conexión requiere un archivo de configuración (por ejemplo: archivo.txt) con las siguientes variables:
```python
# =========================
# DATOS SSH
# =========================

SSH_HOST=xxxxxxx
SSH_PORT=xx
SSH_USER=usuario
SSH_KEY_PATH=ruta/a/credencial.pem
SSH_KEY_PASSPHRASE=tu_passphrase

# =========================
# TÚNEL SSH
# =========================

REMOTE_DB_HOST=xxxx
REMOTE_DB_PORT=xxxx
LOCAL_BIND_HOST=xxx
LOCAL_BIND_PORT=xxx

# =========================
# BASE DE DATOS
# =========================

DB_USER=usuario_bd
DB_PASS=contraseña_bd
```

## 🧠 Ejemplo de uso
🔌 Conectar a la base de datos

```python
import pandas as pd
from cd_base import ConexionBD

bd = ConexionBD("archivo.txt")
engine=bd.conectar("base_datos")
```

## 🔎 Ejecutar una consulta SQL


```python
query = """
SELECT 
    var_alumno,
    nombre,
    fecha_inscripcion
FROM tabla
LIMIT 10;
"""
result = pd.read_sql(query,engine)
result.head()
```

## ⚙️ Ejecutar un Stored Procedure
```python
sp_query = "CALL sp_bonito();"

tabla=pd.read_sql(sp_query,engine)
tabla.head()
"""
```

## 🔒 Cerrar conexión

```python
bd.cerrar()
```

