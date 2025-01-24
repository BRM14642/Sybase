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