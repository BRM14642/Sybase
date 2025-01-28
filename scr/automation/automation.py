import os

from scr.automation.git import Git
from scr.automation.jira import Jira
from scr.automation.sybase import Sybase
from scr.utils.logging_config import logger
from scr.utils.utils import get_dev_status
from datetime import datetime

class Automation:
    def __init__(self):
        self.sybase = Sybase()
        self.jira = Jira()

    def add_fields_table(self):
        table = input("Ingrese el nombre de la tabla: ")
        default_repo = f"{table[:2].lower()}-tablas"
        repo = input(f"Ingrese el nombre del repositorio donde se encuentra la tabla (o presione Enter para usar {default_repo}): ")
        # si no se ingresa un nombre de repositorio, se usa el predeterminado
        repo = repo or default_repo

        new_columns = []
        while True:
            column_name = input("Ingrese el nombre del campo (o presione Enter para finalizar): ")
            if not column_name:
                break
            data_type = input("Ingrese el tipo de dato del campo: ")
            new_columns.append({'name': column_name, 'type': data_type})

        sybase = Sybase()
        sybase.modify_table(table, repo, new_columns)

        # Procesar los nuevos campos ingresados
        for column in new_columns:
            print(f"Nuevo campo: {column['name']}, Tipo: {column['type']}")


    def update_branches_from_task(self, task_key):
        logger.info(f"INICIA LA ACTUALIZACIÓN DE LAS RAMAS DE LA TAREA {task_key}...")
        git = Git()

        branches = self.jira.get_branches_from_task(task_key)

        for branch in branches:
            name_repository = branch['name_repository']
            logger.info(f"Procesando la rama de {name_repository}...")
            clone_url = git.generate_clone_url(branch['url_repository'])
            path = git.find_or_clone_repo(os.getenv("LOCAL_REPOSITORY"), name_repository, clone_url)
            git.update_branch(path, branch['name'])
            logger.info(f"=== Rama de {name_repository} procesada ===")

        logger.info("FINALIZA PROCESO DE ACTUALIZACIÓN DE RAMAS.")


    def create_architecture_task(self, key_issue_develop, summary, description, status_change):
        """
        Crea una tarea de arquitectura de datos en Jira.
        :param key_issue_develop: Key de la tarea de tipo Installation Package donde tenemos el desarrollo
        :param summary: Título de la tarea a crear
        :param description: Descripción de la tarea a generar
        :param status_change: Estado del desarrollo
        :return: Objeto de la tarea generada
        """
        parent_key = self.jira.get_parent_key(key_issue_develop)

        issue_dict = {
            'project': self.jira.project_id,
            'summary': summary,
            'description': description,
            'issuetype': {'name': 'Data Architecture Sub-Task'},
            'parent': {'key': parent_key},
            'customfield_11517': '',
            'customfield_15400': {'id': get_dev_status(status_change)},
        }

        new_issue = self.jira.jira_session.create_issue(fields=issue_dict)
        print(f"Subtarea creada: {new_issue.key}")
        return new_issue

    # TODO: Realizar adecuaciones necesarias para crear tareas de corrección u optimización
    def create_traditional_package_task(self, parent_key, summary, description, numero_cambio):
        """
        Crea una tarea de tipo 'Package Installation' de monolito en Jira.
        :param parent_key: Key de la historia de jira sobre la que se creará la nueva tarea
        :param summary: Título de la tarea a crear
        :param description: Descripción de la tarea a generar
        :param numero_cambio: Control de cambios generado en ivanti
        :return: Objeto de la tarea generada
        """
        logger.info(f"Creando tarea de instalación de paquete sobre la historia {parent_key}...")

        issue_dict = {
            'project': self.jira.project_id,
            'parent': {'key': parent_key},
            'issuetype': {'name': 'Installation Package'},
            'summary': summary,
            'description': description,
            'customfield_16802': {'id': '27309'},                       # TIPO DE INSTALACIÓN: MONOLITO
            'customfield_12529': {'value': 'Normal'},                   # Tipo de Cambio
            'customfield_16701': '7751637678',                          # Teléfono del solicitante
            'customfield_12530': {'id': '15160'},                       # 15160 - Tipo de Servicio: Mantenimiento
            'customfield_11509': {'id': '12817'},                       # 12817 - Impacto: Medio
            'customfield_11101': numero_cambio,                         # ivanti
            'customfield_11801': {'id': '13548'},                       # Subdirección
            'customfield_11309': {'id': '12171'},                       # Célula responsable: 12171 - Productos crédito
            'customfield_12709': {'name': 'sergio.trevino'},            # Líder desarrollo
            'customfield_11729': [{'id': '13132'}, {'id': '13133'}],    # Areas involucradas: 13132 - SOP. APP, 13133 - SOP. TÉCNICO
            'customfield_11105': '6 PM antes del cierre de créditos',   # Ventana de implementación
            'customfield_11107': 'Seguir los pasos de instalación del archivo ZIP', # Plan de instalación
            'customfield_11730': [{'id': '13189'}],                     # Servicios Involucrados
            'customfield_13105': {'id': '15976'},                       # Área causante: 15976 - Productos crédito
            'customfield_11108': datetime.now().strftime('%Y-%m-%d'),   # Fecha propuesta de instalación
            'customfield_13001': {'id': '15605'},                       # VoBo Comité de Diseño: 15605 - No Requerido
            'customfield_16401': {'id': '26602'},                       # Plan de Reversa: Si
            'customfield_16304': 'NO APLICA',                           # Justificación de No Reversa
        }

        new_issue = self.jira.jira_session.create_issue(fields=issue_dict)
        logger.info(f"Tarea de instalación de paquete creada: {new_issue.key}")
        return new_issue