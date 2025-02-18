# Sybase


## Inicializar proyecto
En terminal ejecutar el siguiente comando:
```bash
pip install -r requirements.txt
```

### Variables de Entorno

Para configurar las variables de entorno necesarias para la conexión a la base de datos y otros servicios, sigue estos pasos:

1. Copia el archivo `.env.example` y renómbralo a `.env`:
```sh
cp .env.example .env
```
2. Abre el archivo `.env` y modifica las variables de entorno según sea necesario.
3. Guarda el archivo .env. Ahora tu aplicación debería poder cargar estas variables de entorno correctamente.

Ver la metadata de los campos que contiente una tarea de jira y sus valores o valores permitidos: https://devops.banregio.com:8443/rest/api/2/issue/{Key_Jira}/editmeta
https://confluence.atlassian.com/jirakb/how-to-retrieve-available-options-for-a-multi-select-customfield-via-jira-rest-api-815566715.html


Instalar para exportar a pdf usando open office: brew install unoconv