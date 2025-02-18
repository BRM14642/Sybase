import os
import requests
from jira import JIRA
from dotenv import load_dotenv

from scr.utils.logging_config import logger
from scr.utils.utils import get_dev_status
load_dotenv()

class Jira:

    def __init__(self):
        self.auth = (os.getenv("JIRA_USER"), os.getenv("JIRA_PASSWORD"))
        self.server = os.getenv("JIRA_DOMAIN")
        self.server_bitbucket = os.getenv("BITBUCKET_DOMAIN")
        self.jira_session = JIRA(server=self.server, basic_auth=self.auth)
        self.project_id = self.get_project_id(os.getenv("JIRA_PROJECT_KEY"))

    def test_connection(self):
        try:
            user = self.jira_session.myself()
            print(f"Conexion exitosa. Usuario: {user['emailAddress']}")
            return True
        except Exception as e:
            print(f"Error al conectar: {e}")
            return False

    def get_current_sprint(self, board_id):
        sprints = self.jira_session.sprints(board_id, state='active')
        if sprints:
            return sprints[0].name
        else:
            return "No hay sprints activos :V"

    def get_sprint_stories(self, sprint_id):
        jql_query = f'sprint = {sprint_id} AND issuetype = Story'
        return self.jira_session.search_issues(jql_query)

    def list_issue_types(self):
        issue_types = self.jira_session.issue_types()
        for issue_type in issue_types:
            print(f"ID: {issue_type.id}, Name: {issue_type.name}")

    def get_issue_type_id(self, issue_type_name):
        issue_types = self.jira_session.issue_types()
        for issue_type in issue_types:
            if issue_type.name == issue_type_name:
                return issue_type.id
        return None

    def get_value_field(self, issue, field_name):
        return getattr(issue.fields, field_name, None)

    def list_fields_from_task(self, issue_key):
        """
        Imprime la lista de los campos disponibles en una tarea de jira
        :param  issue_key: Key de la tarea
        """
        issue = self.jira_session.issue(issue_key)
        for field_name, field_value in issue.fields.__dict__.items():
            print(f"{field_name}: {field_value}")
        fields = issue.fields
        print("Campos disponibles:")
        print(dir(fields))

    def list_projects(self):
        projects = self.jira_session.projects()
        for project in projects:
            print(f"ID: {project.id} -> Key: {project.key} -> Name: {project.name}")

    def print_all_fields_metadata(self):
        all_fields = self.jira_session.fields()
        for field in all_fields:
            print(f"ID: {field['id']}, Name: {field['name']}, Schema: {field.get('schema', {})}")

    def get_project_id(self, project_key):
        project = self.jira_session.project(project_key)
        return project.id

    def create_architecture_task(self, key_issue_develop, summary, description, status_change):
        """
        Crea una tarea de arquitectura de datos en Jira.
        :param key_issue_develop: Key de la tarea de tipo Installation Package donde tenemos el desarrollo
        :param summary: Título de la tarea a crear
        :param description: Descripción de la tarea a generar
        :param status_change: Estado del desarrollo
        :return: Objeto de la tarea generada
        """
        parent_key = self.get_parent_key(key_issue_develop)

        issue_dict = {
            'project': self.project_id,
            'summary': summary,
            'description': description,
            'issuetype': {'name': 'Data Architecture Sub-Task'},
            'parent': {'key': parent_key},
            'customfield_11517': '',
            'customfield_15400': {'id': get_dev_status(status_change)},
        }

        new_issue = self.jira_session.create_issue(fields=issue_dict)
        print(f"Subtarea creada: {new_issue.key}")
        return new_issue

    def get_parent_key(self, subtask_key):
        subtask = self.jira_session.issue(subtask_key)
        return subtask.fields.parent.key

    def get_intern_id(self, issue_key):
        issue = self.jira_session.issue(issue_key)
        return issue.id  # Este es el ID interno necesario para la API de desarrollo

    # Obtener los datos de desarrollo de una tarea
    def get_develop_info(self, task_key):
        logger.info(f"Obteniendo información de desarrollo de la tarea {task_key}...")
        issue_id = self.get_intern_id(task_key)
        url = f"{self.server}/rest/dev-status/1.0/issue/detail?issueId={issue_id}&applicationType=stash&dataType=pullrequest"
        params = {
            "issueId": issue_id,  # Usar el ID de la tarea
            "applicationType": "bitbucket",  # Especifica Bitbucket como origen
            "dataType": "branch",  # Solicitar información de ramas
        }
        response = requests.get(url, params=params, auth=self.auth)
        if response.status_code == 200:
            return response.json()
        else:
            logger.warning(f"Error al obtener ramas: {response.status_code} - {response.text}")
        return None

    # Obtener las branches ligadas a la tarea
    def get_branches_from_task(self, task_key):
        data = self.get_develop_info(task_key)
        branches_info = []
        if data.get("detail"):
            detail = data["detail"][0]
            branches = detail.get("branches", [])
            for branch in branches:
                project_id = self.extract_project_name(branch['repository']['url'])
                branch_info = {
                    "branch_name": branch['name'],
                    "project_id": project_id,
                    "name_repository": branch['repository']['name'],
                    "url_repository": branch['repository']['url']
                }
                branches_info.append(branch_info)
        else:
            logger.warning("No se encontraron datos relacionados.")
        return branches_info

    # Obtener las pullrequest ligadas a la tarea
    def get_pullrequest_from_task(self, task_key):
        data = self.get_develop_info(task_key)
        if data.get("detail"):
            detail = data["detail"][0]
            pull_requests = detail.get("pullRequests", [])
            print("Pull Requests relacionados:")
            for pr in pull_requests:
                print(f"Pull Request: {pr['name']}")
                print(f"Source Branch: {pr['source']['repository']}")
                print("-" * 40)
        else:
            print("No se encontraron datos relacionados.")

    def get_diff_branch(self, workspace, name_repository, source_branch, destination_branch="develop"):
        logger.debug(f"Obteniendo diferencias de {workspace}/{name_repository} entre las ramas {source_branch} y {destination_branch}...")
        url = f"{self.server_bitbucket}/rest/api/1.0/projects/{workspace}/repos/{name_repository}/compare/changes?from={source_branch}&to={destination_branch}"

        response = requests.get(url, auth=self.auth)

        if response.status_code == 200:
            diffstat = response.json()

            changes = []
            for diff in diffstat.get("values", []):
                change_info = {
                    "project": workspace,
                    "repository": name_repository,
                    "name_file": diff['path']['name'],
                    "path_file": diff['path']['toString'],
                    "extension": diff['path']['extension'],
                    "status": diff['properties']['gitChangeType']
                }
                changes.append(change_info)
            return changes
        else:
            logger.error(f"Error al obtener las diferencias: {response.status_code} - {response.text}")
            return []

    def get_field_id_from_description(self, issue_key, field_name, description):
        url = f"https://devops.banregio.com:8443/rest/api/2/issue/{issue_key}/editmeta"
        response = requests.get(url,
                                auth=('username', 'password'))  # Reemplaza 'username' y 'password' con tus credenciales
        response.raise_for_status()
        metadata = response.json()

        fields = metadata.get('fields', {})
        field = fields.get(field_name, {})
        allowed_values = field.get('allowedValues', [])

        for value in allowed_values:
            if value.get('name') == description:
                return value.get('id')

        return None

    def get_field_id_from_description2(self, field_name, description):
        url = "https://devops.banregio.com:8443/rest/api/2/field"
        response = requests.get(url,
                                auth=('username', 'password'))  # Reemplaza 'username' y 'password' con tus credenciales
        response.raise_for_status()
        fields = response.json()

        for field in fields:
            if field['name'] == field_name:
                allowed_values = field.get('allowedValues', [])
                for value in allowed_values:
                    if value.get('name') == description:
                        return value.get('id')

    # Function to get and print issue fields metadata
    def print_issue_fields_metadata(self, issue_key):
        issue = self.jira_session.issue(issue_key)
        for field_name, field_value in issue.raw['fields'].items():
            descri = self.get_custom_field_description(field_name)
            print(f"{descri} --> {field_name}: {field_value}")

    def extract_project_name(self, url):
        """
        Extracts the project name from a Bitbucket URL.
        :param url: The URL containing the project name
        :return: The project name
        """
        parts = url.split('/')
        if 'projects' in parts:
            project_index = parts.index('projects') + 1
            if project_index < len(parts):
                return parts[project_index]
        return 'Unknown Project'


    def execute_jql(self, jql_query):
        """
        Execute a JQL query in Jira.
        :param jql_query: The JQL query to execute
        :return: The result of the query
        """
        return self.jira_session.search_issues(jql_query)

    def get_custom_field_description(self, custom_field_id):
        all_fields = self.jira_session.fields()
        for field in all_fields:
            if field['id'] == custom_field_id:
                return field['name']
        print(f"Custom field {custom_field_id} not found")
        return 'Custom field not found'