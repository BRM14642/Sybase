import os

from scr.automation.git import Git
from scr.automation.jira import Jira
from scr.automation.sybase import Sybase
from scr.utils.logging_config import logger


class Automation:
    def __init__(self):
        self.sybase = Sybase()

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
        jira = Jira()
        git = Git()

        branches = jira.get_branches_from_task(task_key)

        for branch in branches:
            name_repository = branch['name_repository']
            logger.info(f"Procesando la rama de {name_repository}...")
            clone_url = git.generate_clone_url(branch['url_repository'])
            path = git.find_or_clone_repo(os.getenv("LOCAL_REPOSITORY"), name_repository, clone_url)
            git.update_branch(path, branch['name'])
            logger.info(f"=== Rama de {name_repository} procesada ===")

        logger.info(f"FINALIZA PROCESO DE ACTUALIZACIÓN DE RAMAS.")