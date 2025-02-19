import os
import shutil
import subprocess

from scr.automation.excel import ODSHandler
from scr.automation.git import Git
from scr.automation.jira import Jira
from scr.automation.libreoffice import LibreOffice
from scr.automation.sybase import Sybase
from scr.utils.logging_config import logger
from scr.utils.utils import get_dev_status, remove_sql_extension, capitalize_initials, get_server_hey, get_server_br, clean_string
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
            project = branch['project_id']
            name_repository = branch['name_repository']
            logger.info(f"=== INICIA PROCESAMIENTO DE LA RAMA {project}/{name_repository} ===")

            clone_url = git.generate_clone_url(branch['url_repository'])
            path = git.find_or_clone_repo(os.getenv("LOCAL_REPOSITORY"), name_repository, clone_url)
            git.update_branch(path, branch['branch_name'])

            logger.info(f"=== FINALIZA PROCESAMIENTO DE LA RAMA {project}/{name_repository} ===\n")

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
            #'customfield_12708': {'name': 'rafael.gutierrez'},          # Product Owner
            'customfield_12709': {'name': 'sergio.trevino'},            # Líder desarrollo
            'customfield_11729': [{'id': '13132'}],                     # Areas involucradas: 13132 - SOP. APP, 13133 - SOP. TÉCNICO
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


    def fill_helpdesk(self, key_jira):
        self.jira.list_fields_from_task(key_jira)
        issue = self.jira.jira_session.issue(key_jira)
        num_cambio = self.jira.get_value_field(issue, 'customfield_11101').strip()

        branches_info = self.jira.get_branches_from_task(key_jira)

        template_dir = '/Users/ivan.riveros/Documents/MisAutomatizaciones/Sybase/files/templates'
        output_dir = f'/Users/ivan.riveros/Documents/MisAutomatizaciones/Sybase/files/outputs/{num_cambio}_DEV_V1'

        helpdesk_template_file_path = f'{template_dir}/Template_HelpDesk.ods'
        new_helpdesk_file_path = f'{output_dir}/{key_jira}_HelpDesk.ods'
        self.duplicate_file(helpdesk_template_file_path, new_helpdesk_file_path)


        modified_objects = []
        for branch in branches_info:
            dif = self.jira.get_diff_branch(branch['project_id'], branch['name_repository'], branch['branch_name'])
            modified_objects.append(dif)

        self.fill_design_sheet(new_helpdesk_file_path, issue, modified_objects)
        self.fill_installation_sheet(new_helpdesk_file_path, modified_objects, issue)
        self.fill_params_sheet(new_helpdesk_file_path, issue)

        estimacion_template_file_path = f'{template_dir}/Template_Estimacion.ods'
        new_estimacion_file_path = f'{output_dir}/{num_cambio} - Estimacion.ods'
        self.duplicate_file(estimacion_template_file_path, new_estimacion_file_path)

        self.fill_estimation_file(new_estimacion_file_path, issue, modified_objects)

        libreoffice_process = LibreOffice.start_libreoffice_headless()

        # Exportar a pdf según aplique
        sheet_to_export = 'Hoja Instalación_Br'
        pdf_file_path = f'{output_dir}/{num_cambio}_HojaInstalacionBanregio.pdf'
        self.ejecutar_exportacion(new_helpdesk_file_path, sheet_to_export, pdf_file_path)

        sheet_to_export = 'Hoja Instalación_Hey'
        pdf_file_path = f'{output_dir}/{num_cambio}_HojaInstalacionHey.pdf'
        self.ejecutar_exportacion(new_helpdesk_file_path, sheet_to_export, pdf_file_path)

        sheet_to_export = 'Carta Aceptación Pruebas'
        pdf_file_path = f'{output_dir}/{num_cambio}_Carta Aceptacion de Pruebas.pdf'
        self.ejecutar_exportacion(new_helpdesk_file_path, sheet_to_export, pdf_file_path)

        LibreOffice.stop_libreoffice_headless(libreoffice_process)


    def fill_params_sheet(self, file_path, issue):
        gerente_desarrollo = self.jira.get_value_field(issue, 'customfield_12707') if self.jira.get_value_field(issue, 'customfield_12707') else 'Evaristo Sánchez'
        arq = self.jira.get_value_field(issue, 'customfield_12708') if self.jira.get_value_field(issue, 'customfield_12708') else 'Rafael Gutierrez'

        creador = capitalize_initials(str(self.jira.get_value_field(issue, 'creator')))
        lider = capitalize_initials(str(self.jira.get_value_field(issue, 'customfield_12709')))
        usuario = capitalize_initials(str(arq))
        gerente = capitalize_initials(str(gerente_desarrollo))
        nombre = self.jira.get_value_field(issue, 'summary')
        num_cambio = self.jira.get_value_field(issue, 'customfield_11101')

        sheet_name = 'Parámetros'
        ods_handler = ODSHandler(file_path, sheet_name)

        ods_handler.write_cell(0, 1, issue.key)
        ods_handler.write_cell(1, 1, creador)
        ods_handler.write_cell(2, 1, lider)
        ods_handler.write_cell(3, 1, gerente)
        ods_handler.write_cell(4, 1, usuario)
        ods_handler.write_cell(7, 1, creador)
        ods_handler.write_cell(23, 1, nombre)
        ods_handler.write_cell(24, 1, num_cambio)

        ods_handler.save()

    def fill_installation_sheet(self, file_path, branches_info, issue):
        hey_servers = ''
        banregio_servers = ''

        created_tables = ''
        modified_tables = ''
        created_index = ''
        modified_index = ''
        created_sps = ''
        modified_sps = ''

        for branch in branches_info:
            for modified_object in branch:
                project = modified_object.get('project')
                repo = modified_object.get('repository')

                if project == 'BASDATOTR':
                    continue

                if project == 'SIB3P':
                    parts = repo.rsplit('-', 1)
                    type_sib3 = parts[-1] if len(parts) > 1 else ''
                    project = get_server_br(f"{project}-{type_sib3}")

                server_br = get_server_br(project)
                if server_br:
                    banregio_servers += f'{server_br}, ' if server_br not in banregio_servers else ''
                else:
                    logger.error(f"El proyecto {project} no tiene un servidor asociado en el diccionario de banregio")

                server_hey = get_server_hey(project)
                if server_hey:
                    hey_servers += f'{server_hey}, ' if server_hey not in hey_servers else ''
                else:
                    logger.error(f"El proyecto {project} no tiene un servidor asociado en el diccionario de hey")


                if project == 'SYB16':
                    if 'scriptsBase' in repo:
                        continue

                    element = remove_sql_extension(modified_object.get('path_file'))
                    if 'tablas' in repo:
                        if modified_object.get('status') == 'ADD':
                            created_tables += f"{element}, "
                            continue
                        elif modified_object.get('status') == 'MODIFY':
                            modified_tables += f"{element}, "
                            continue

                    if 'indice' in repo:
                        if modified_object.get('status') == 'ADD':
                            created_index += f"{element}, "
                            continue
                        elif modified_object.get('status') == 'MODIFY':
                            modified_index += f"{element}, "
                            continue

                    if 'sps' in repo:
                        if modified_object.get('status') == 'ADD':
                            created_sps += f"{element}, "
                        elif modified_object.get('status') == 'MODIFY':
                            modified_sps += f"{element}, "


        # si el texto ', ' se elimina
        hey_servers = clean_string(hey_servers)
        banregio_servers = clean_string(banregio_servers)

        created_tables = clean_string(created_tables)
        modified_tables = clean_string(modified_tables)
        created_index = clean_string(created_index)
        modified_index = clean_string(modified_index)
        created_sps = clean_string(created_sps)
        modified_sps = clean_string(modified_sps)


        control_cambios = issue.fields.customfield_11101

        comments = f'Para la instalación realizar los pasos en el orden indicado en el archivo {control_cambios}_PlanInstalacion.txt \nEn caso de reversa realizar los pasos en el orden indicado en el archivo {control_cambios}_PlanReversa.txt'


        ods_handler_br = ODSHandler(file_path, 'Hoja Instalación_Br')

        ods_handler_br.write_cell(13, 1, banregio_servers)

        ods_handler_br.write_cell(31, 2, created_tables)
        ods_handler_br.write_cell(32, 1, modified_tables)
        ods_handler_br.write_cell(36, 2, created_index)
        ods_handler_br.write_cell(37, 1, modified_index)
        ods_handler_br.write_cell(40, 2, created_sps)
        ods_handler_br.write_cell(41, 1, modified_sps)

        ods_handler_br.write_cell(58, 0, comments)

        ods_handler_br.save()


        ods_handler_hey = ODSHandler(file_path, 'Hoja Instalación_Hey')

        ods_handler_hey.write_cell(13, 1, hey_servers)

        ods_handler_hey.write_cell(31, 2, created_tables)
        ods_handler_hey.write_cell(32, 1, modified_tables)
        ods_handler_hey.write_cell(36, 2, created_index)
        ods_handler_hey.write_cell(37, 1, modified_index)
        ods_handler_hey.write_cell(40, 2, created_sps)
        ods_handler_hey.write_cell(41, 1, modified_sps)

        ods_handler_hey.write_cell(58, 0, comments)

        ods_handler_hey.save()


    # TODO - Agregar funcionalidad para detectar scripts de información
    def fill_design_sheet(self, file_path, issue, branches_info):
        added_rows = 0
        table_index_row = 11    # Índice de la fila donde se insertarán los datos de tablas modificadas
        indice_index_row = 13   # Índice de la fila donde se insertarán los datos de índices modificados
        sp_index_row = 19       # Índice de la fila donde se insertarán los datos de SPs modificados
        class_index_row = 35    # Índice de la fila donde se insertarán los datos de clases modificadas

        sheet_name = 'Diseño'
        ods_handler = ODSHandler(file_path, sheet_name)

        ods_handler.write_cell(6, 1, issue.fields.description.strip())

        # procesamos las tablas de la rama
        for table_branch in branches_info:
            if table_branch and table_branch[0].get('project') == 'SYB16' and 'tablas' in table_branch[0].get('repository'):
                for table_obj in table_branch:
                    ods_handler.copy_row_with_format((table_index_row + added_rows), (table_index_row + added_rows))

                    tabla = remove_sql_extension(table_obj.get('path_file'))

                    tipo_movimiento = ''
                    descripcion_movimiento = ''
                    if table_obj.get('status') == 'ADD':
                        tipo_movimiento = 'Agregado'
                        descripcion_movimiento = f'Se crea la tabla {tabla}'
                    else:
                        if table_obj.get('status') == 'MODIFY':
                            tipo_movimiento = 'Modificado'
                            descripcion_movimiento = f'Se modifica la tabla {tabla}'

                    ods_handler.write_cell((table_index_row + added_rows), 0, tabla)
                    ods_handler.write_cell((table_index_row + added_rows), 2, tipo_movimiento)
                    ods_handler.write_cell((table_index_row + added_rows), 3, descripcion_movimiento)
                    added_rows += 1

        # procesamos los indices de la rama
        for indice_branch in branches_info:
            if indice_branch and indice_branch[0].get('project') == 'SYB16' and 'indice' in indice_branch[0].get('repository'):
                for indice_obj in indice_branch:
                    ods_handler.copy_row_with_format((indice_index_row + added_rows), (indice_index_row + added_rows))

                    indice = remove_sql_extension(indice_obj.get('path_file'))

                    tipo_movimiento = ''
                    descripcion_movimiento = ''
                    if indice_obj.get('status') == 'ADD':
                        tipo_movimiento = 'Agregado'
                        descripcion_movimiento = f'Se crea el índice {indice}'
                    else:
                        if indice_obj.get('status') == 'MODIFY':
                            tipo_movimiento = 'Modificado'
                            descripcion_movimiento = f'Se modifica el índice {indice}'

                    ods_handler.write_cell((indice_index_row + added_rows), 0, indice)
                    ods_handler.write_cell((indice_index_row + added_rows), 2, tipo_movimiento)
                    ods_handler.write_cell((indice_index_row + added_rows), 3, descripcion_movimiento)
                    added_rows += 1

        # procesamos los SPS de la rama
        for sp_branch in branches_info:
            if sp_branch and sp_branch[0].get('project') == 'SYB16' and 'sps' in sp_branch[0].get('repository'):
                for sps_obj in sp_branch:
                    ods_handler.copy_row_with_format((sp_index_row + added_rows), (sp_index_row + added_rows))

                    sp = remove_sql_extension(sps_obj.get('path_file'))

                    tipo_movimiento = ''
                    descripcion_movimiento = ''
                    if sps_obj.get('status') == 'ADD':
                        tipo_movimiento = 'Agregado'
                        descripcion_movimiento = f'Se crea el sp {sp}'
                    else:
                        if sps_obj.get('status') == 'MODIFY':
                            tipo_movimiento = 'Modificado'
                            descripcion_movimiento = f'Se modifica el sp {sp}'

                    ods_handler.write_cell((sp_index_row + added_rows), 0, sp)
                    ods_handler.write_cell((sp_index_row + added_rows), 2, tipo_movimiento)
                    ods_handler.write_cell((sp_index_row + added_rows), 3, descripcion_movimiento)
                    added_rows += 1

        # procesamos las clases de la rama
        for class_branch in branches_info:
            if class_branch and class_branch[0].get('project') in ['SIB3P', 'SIB21P']:
                for class_obj in class_branch:
                    ods_handler.copy_row_with_format((class_index_row + added_rows), (class_index_row + added_rows))

                    clase = remove_sql_extension(class_obj.get('name_file'))

                    tipo_movimiento = ''
                    descripcion_movimiento = ''
                    if class_obj.get('status') == 'ADD':
                        tipo_movimiento = 'Agregado'
                        descripcion_movimiento = f'Se crea la clase {clase}'
                    else:
                        if class_obj.get('status') == 'MODIFY':
                            tipo_movimiento = 'Modificado'
                            descripcion_movimiento = f'Se modifica la clase {clase}'

                    elemento = f"{class_obj.get('project')}/{class_obj.get('repository')}/{class_obj.get('path_file')}"
                    ods_handler.write_cell((class_index_row + added_rows), 0, elemento)
                    ods_handler.write_cell((class_index_row + added_rows), 2, tipo_movimiento)
                    ods_handler.write_cell((class_index_row + added_rows), 3, descripcion_movimiento)
                    added_rows += 1

        ods_handler.save()

    def duplicate_file(self, original_file_path, new_file_path):
        new_file_dir = os.path.dirname(new_file_path)
        if not os.path.exists(new_file_dir):
            os.makedirs(new_file_dir)

        if os.path.exists(new_file_path):
            os.remove(new_file_path)

        shutil.copyfile(original_file_path, new_file_path)
        logger.info(f"File created: {new_file_path} from {original_file_path}")


    def fill_estimation_file(self, file_path, issue, branches_info):
        counter = 0
        first_row = 15

        sheet_name = '3.Procedimientos'
        ods_handler = ODSHandler(file_path, sheet_name)

        descripcion = issue.fields.description
        gerente_desarrollo = self.jira.get_value_field(issue, 'customfield_12707') if self.jira.get_value_field(issue, 'customfield_12707') else 'Evaristo Sánchez'
        arq = self.jira.get_value_field(issue, 'customfield_12708') if self.jira.get_value_field(issue, 'customfield_12708') else 'Rafael Gutierrez'

        creador = capitalize_initials(str(self.jira.get_value_field(issue, 'creator')))
        usuario = capitalize_initials(str(arq))


        ods_handler.write_cell(9, 1, descripcion)

        for branch in branches_info:
            if branch and branch[0].get('project') == 'SYB16' and 'sps' in branch[0].get('repository'):
                for sps_obj in branch:
                    counter += 1
                    ods_handler.write_cell((first_row + counter), 1, str(counter))
                    ods_handler.write_cell((first_row + counter), 2, remove_sql_extension(sps_obj.get('path_file')))
                    ods_handler.write_cell((first_row + counter), 3, 'Media')

        ods_handler.save()

        sheet_name = '1.Parametros'
        ods_handler = ODSHandler(file_path, sheet_name)

        ods_handler.write_cell(0, 1, issue.fields.summary)
        ods_handler.write_cell(1, 1, creador)
        ods_handler.write_cell(2, 1, usuario)
        ods_handler.write_cell(3, 1, capitalize_initials(str(self.jira.get_value_field(issue, 'customfield_12709'))))
        ods_handler.write_cell(4, 1, capitalize_initials(str(gerente_desarrollo)))
        ods_handler.write_cell(5, 1, issue.key)

        ods_handler.save()

    def ejecutar_exportacion(self, archivo_ods, nombre_hoja, archivo_pdf):
        command = [
            "/Applications/LibreOffice.app/Contents/Resources/python",
            "/Users/ivan.riveros/Documents/MisAutomatizaciones/Sybase/scr/automation/export_ods_to_pdf.py",
            archivo_ods,
            nombre_hoja,
            archivo_pdf
        ]
        subprocess.run(command)