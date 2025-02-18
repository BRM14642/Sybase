import re
import os

# Diccionario de tipos de datos de Sybase ASE con valores por defecto
SYBASE_DEFAULT_VALUES = {
    "int": 0,
    "bigint": 0,
    "smallint": 0,
    "tinyint": 0,
    "decimal": 0.0,
    "numeric": 0.0,
    "float": 0.0,
    "real": 0.0,
    "char": "",
    "varchar": "",
    "text": "",
    "nchar": "",
    "nvarchar": "",
    "datetime": "1900-01-01 00:00:00",
    "smalldatetime": "1900-01-01 00:00:00",
    "date": "1900-01-01",
    "time": "00:00:00",
    "bit": 0,
    "binary": b"",
    "varbinary": b"",
    "image": b"",
}

# Diccionario de estatus posibles en tareas de
DEV_STATUS_VALUES = {
    "Análisis": '23303',
    "Desarrollo": '23304',
    "Diseño": '23305',
    "QA": '23306',
    "Instalación": '23307',
}

# Diccionarios de servidores
SERVERS_HEY = {
    "SYB16": 'Sybase Hey Producción (HBO1PDSYBPRO)',
    "SIB21P": 'SIBAMEX 21 Producción Hey',
    "SIB3P-api": 'Servidor SIBAMEX3 Producción Hey',
    "SIB3P-extjs": 'Cliente SIBAMEX3 Producción Hey',
}
SERVERS_BR = {
    "SYB16": 'Sybase Banregio Producción (BRMPSYBPRO)',
    "SIB21P": 'SIBAMEX 21 Producción Banregio',
    "SIB3P-api": 'Servidor SIBAMEX3 Producción Banregio',
    "SIB3P-extjs": 'Cliente SIBAMEX3 Producción Banregio',
}

# Expresión regular para nombre de archivos de sps
SQL_SP_REGEX = re.compile(r'^[A-Z0-9]{11}\.sql$', re.IGNORECASE)

def get_default_value(data_type):
    """
    Devuelve el valor por defecto para un tipo de dato Sybase ASE.

    :param data_type: El tipo de dato (str).
    :return: Valor por defecto correspondiente al tipo de dato o None si no está definido.
    """
    return SYBASE_DEFAULT_VALUES.get(data_type.lower(), None)

def get_default_value_to_string(data_type):
    # si es algun dato numerico o bit no se retorna con '' de lo contrario se debe devolver '' o el valor envuelto por '
    if data_type.lower() in ['int', 'bigint', 'smallint', 'tinyint', 'decimal', 'numeric', 'float', 'real', 'bit']:
        return str(SYBASE_DEFAULT_VALUES.get(data_type.lower(), None))

    return f"'{SYBASE_DEFAULT_VALUES.get(data_type.lower(), None)}'"

def get_dev_status(dev_status):
    return DEV_STATUS_VALUES.get(dev_status, None)

def is_sp_file(filename):
    return bool(SQL_SP_REGEX.match(filename))

def remove_sql_extension(filename):
    """
    Removes the .sql extension from a filename if it exists.
    :param filename: The name of the file
    :return: The filename without the .sql extension
    """
    if filename.lower().endswith('.sql'):
        return os.path.splitext(filename)[0]
    return filename

def capitalize_initials(text):
    return text.title()

def get_server_hey(project):
    return SERVERS_HEY.get(project, None)

def get_server_br(project):
    return SERVERS_BR.get(project, None)

# limpiar coma y espacios al final de una cadena
def clean_string(text):
    return text.strip().rstrip(',').strip()