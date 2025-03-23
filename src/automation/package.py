import os
from src.automation.excel import ODSHandler
from src.automation.xml_handler import XML_Handler
from src.utils.utils import remove_sql_extension, capitalize_initials, get_server_hey, get_server_br, clean_string, duplicate_file_in, delete_file, get_both_servers
from src.utils.constants import TEMPLATE_DIR
from src.utils.logging_config import logger
from src.automation.libreoffice import LibreOffice
from src.automation.docx import DocumentHandler
from src.automation.jira import Jira
from datetime import datetime
import textwrap


class Package:
    """
    Clase para manejar la creación y gestión de paquetes en Jira.
    """

    modified_objects_map = {
        'tablas': {
            'string_created': '',
            'string_modified': '',
            'modify_description': 'Se modifica la tabla',
            'add_description': 'Se crea la tabla',
            'index_design': 11
        },
        'indices': {
            'string_created': '',
            'string_modified': '',
            'modify_description': 'Se modifica el índice',
            'add_description': 'Se crea el índice',
            'index_design': 13
        },
        'sps': {
            'string_created': '',
            'string_modified': '',
            'modify_description': 'Se modifica el sp',
            'add_description': 'Se crea el sp',
            'index_design': 19,
            'involucrado': 'of:=Parámetros.B8'
        },
        'sib3': {
            'server_module': '',
            'client_module': '',
            'modify_description': 'Se modifica la clase',
            'add_description': 'Se crea la clase',
            'index_design': 35,
            'involucrado': 'of:=Parámetros.B8'
        },
        'classes': {  # **
            'modify_description': 'Se modifica la clase',
            'add_description': 'Se crea la clase',
            'index_design': 35,
            'involucrado': 'of:=Parámetros.B8'
        },
        'SIB21P_reports': {
            'string_created': '',
            'string_modified': '',
            'modify_description': 'Se modifica el reporte',
            'add_description': 'Se crea el reporte',
            'index_design': 37,
            'involucrado': 'of:=Parámetros.B8'
        }
    }

    def __init__(self, key_jira, local_package_path = os.getenv("DEFAULT_PATH_PACKAGES")):
        """
        Inicializa una instancia de la clase Package.

        :param key_jira: Clave de la tarea en Jira.
        :param local_package_path: Ruta local del paquete.
        """
        self.jira = Jira()
        issue = self.jira.jira_session.issue(key_jira)
        self.issue = issue
        self.title_issue = issue.fields.summary.strip()
        self.description_issue = issue.fields.description.strip()
        self.control_cambios = issue.fields.customfield_11101
        self.creador = capitalize_initials(str(self.jira.get_value_field(issue, 'creator')))
        self.lider_desarrollo = capitalize_initials(str(self.jira.get_value_field(issue, 'customfield_12709')))
        self.arq_negocio = capitalize_initials(str(self.jira.get_value_field(issue, 'customfield_12708'))) if self.jira.get_value_field(issue, 'customfield_12708') else 'Rafael Gutierrez'
        self.gerente_desarrollo = capitalize_initials(str(self.jira.get_value_field(issue, 'customfield_12707'))) if self.jira.get_value_field(issue, 'customfield_12707') else 'Evaristo Sánchez'
        self.local_package_path = f'{local_package_path}/{self.control_cambios}_DEV_V1'
        self.modified_objects = self.jira.clasify_changes(key_jira)

    def fill_helpdesk(self):
        output_dir = f'{self.local_package_path}/Documentos'

        helpdesk_template_file_path = f'{TEMPLATE_DIR}/Template_HelpDesk.ods'
        new_helpdesk_file_path = f'{output_dir}/{self.issue.key}_HelpDesk.ods'
        duplicate_file_in(helpdesk_template_file_path, new_helpdesk_file_path)

        self.fill_design_sheet(new_helpdesk_file_path, self.modified_objects)
        self.fill_installation_sheet(new_helpdesk_file_path, self.modified_objects, self.issue)
        self.fill_CAP_sheet(new_helpdesk_file_path)
        self.fill_params_sheet(new_helpdesk_file_path)

        estimacion_template_file_path = f'{TEMPLATE_DIR}/Template_Estimacion.ods'
        new_estimacion_file_path = f'{output_dir}/{self.control_cambios} - Estimacion.ods'
        duplicate_file_in(estimacion_template_file_path, new_estimacion_file_path)
        self.fill_estimation_file(new_estimacion_file_path, self.modified_objects)

    def fill_params_sheet(self, file_path):
        sheet_name = 'Parámetros'
        ods_handler = ODSHandler(file_path, sheet_name)

        ods_handler.write_cell(0, 1, self.issue.key)
        ods_handler.write_cell(1, 1, self.creador)
        ods_handler.write_cell(2, 1, self.lider_desarrollo)
        ods_handler.write_cell(3, 1, self.gerente_desarrollo)
        ods_handler.write_cell(4, 1, self.arq_negocio)
        ods_handler.write_cell(7, 1, self.creador)
        ods_handler.write_cell(21, 1, self.creador)
        ods_handler.write_cell(23, 1, self.description_issue)
        ods_handler.write_cell(24, 1, self.control_cambios)

        ods_handler.save()

    def fill_CAP_sheet(self, file_path):
        row_description_index = 11
        descripcion = textwrap.dedent(f"""
        Por medio de la presente acta se deja constancia que se consideran como aprobadas las Pruebas de Usuario realizadas en el Proyecto '{self.title_issue}'.
    
        En base a las pruebas realizadas el usuario tendrá el conocimiento de los puntos de función, alcance, delimitaciones y los resultados esperados de cada flujo que serán liberados al ambiente de Producción, de esta manera se valida el correcto funcionamiento de los requerimientos solicitados.
    
        Las Pruebas de Usuario del Proyecto cumplen con '{self.description_issue}'.
    
        Se deja constancia que las pruebas realizadas fueron en base a los casos de prueba:
        """)
        sheet_name = 'Carta Aceptación Pruebas'
        ods_handler = ODSHandler(file_path, sheet_name)

        ods_handler.write_cell(row_description_index, 1, descripcion)

        added_rows = 0
        while True:
            use_case = input("Ingrese un caso de uso: ")
            if not use_case:
                break
            added_rows += 1
            ods_handler.copy_row_with_format((row_description_index + added_rows), (row_description_index + added_rows))

            ods_handler.replace_text_in_row((row_description_index + added_rows), 'Caso_Uso', f'CU{added_rows}')
            ods_handler.replace_text_in_row((row_description_index + added_rows), 'Descripcion_Caso', use_case)

            another = input("¿Quiere ingresar otro caso de uso? (s/n): ").strip().lower()
            if another != 's':
                ods_handler.replace_text_in_row((row_description_index + (added_rows + 1)), 'Caso_Uso', '')
                ods_handler.replace_text_in_row((row_description_index + (added_rows + 1)), 'Descripcion_Caso', '')
                break

        ods_handler.save()

    def fill_installation_sheet(self, file_path, branches_info, issue):
        servidores = {
            'br': '',
            'hey': ''
        }

        for obj_type in ['tablas', 'indices', 'sps']:
            for object_diff in branches_info[obj_type]:
                project = object_diff.get('project')
                self.group_servers(project, servidores)

                element = remove_sql_extension(object_diff.get('path_file'))
                if object_diff.get('status') == 'ADD':
                    self.modified_objects_map.get(obj_type)['string_created'] += f"{element}, "
                elif object_diff.get('status') == 'MODIFY':
                    self.modified_objects_map.get(obj_type)['string_modified'] += f"{element}, "

        client_jars = ''
        if self.modified_objects['SIB21P_cliente']:
            for element in self.modified_objects['SIB21P_cliente']:
                repo = element['repository']
                jar = f'{repo}.jar'
                if jar not in client_jars:
                    client_jars = f"{client_jars}{jar}, "
            client_jars = clean_string(client_jars)

            servidores['br'] += "- Sibamex 21 cliente producción\n"
            servidores['hey'] += "- Sibamex 21 cliente producción\n"

        server_jars = ''
        if self.modified_objects['SIB21P_servidor']:
            xml_handler = XML_Handler()

            for element in self.modified_objects['SIB21P_servidor']:
                jar = xml_handler.get_jar_for_class(element['path_file'])
                if jar not in server_jars:
                    server_jars = f"{server_jars}{jar}, "
            server_jars = clean_string(server_jars)

            self.group_servers('SIB21P_servidor', servidores)

        if self.modified_objects['SIB3P_cliente']:
            client_module_sib3 = ''
            for element in self.modified_objects['SIB3P_cliente']:
                repo = element['repository']
                if repo not in client_module_sib3:
                    client_module_sib3 = f'{client_module_sib3}*{repo}\n'

            self.modified_objects_map['sib3']['client_module'] = client_module_sib3

            self.group_servers('SIB3P_cliente', servidores)


        if self.modified_objects['SIB3P_servidor']:
            self.modified_objects_map['sib3']['server_module'] = '\t*sibamex-serviciosweb-principal.war\n'

            self.group_servers('SIB3P_servidor', servidores)


        # si el texto ', ' se eliminara de la cadena
        for obj_type, obj_data in self.modified_objects_map.items():
            for key, value in obj_data.items():
                if isinstance(value, str):
                    self.modified_objects_map[obj_type][key] = clean_string(value)


        client_module_sib3 = f"Cliente Sibamex3:\n\t{clean_string(self.modified_objects_map['sib3']['client_module'])}" if self.modified_objects_map['sib3']['client_module'] != '' else ''
        server_module_sib3 = f"Servidor Sibamex3:\n\t{clean_string(self.modified_objects_map['sib3']['server_module'])}" if self.modified_objects_map['sib3']['server_module'] != '' else ''
        ejecutables = clean_string(f'{client_module_sib3}\n{server_module_sib3}')

        control_cambios = issue.fields.customfield_11101

        comp = ['Banregio', 'Hey']
        for marca in comp:
            if marca == 'Banregio':
                sheet = 'Hoja Instalación_Br'
                servers = servidores['br']
            else:
                sheet = 'Hoja Instalación_Hey'
                servers = servidores['hey']

            comments = f'- Para la instalación realizar los pasos en el orden indicado en el archivo {control_cambios}_PlanInstalacion_{marca}.txt \n- En caso de reversa realizar los pasos en el orden indicado en el archivo {control_cambios}_PlanReversa_{marca}.txt'

            ods_handler = ODSHandler(file_path, sheet)

            ods_handler.write_cell(5, 0, issue.fields.description.strip())
            ods_handler.write_cell(13, 1, servers)

            ods_handler.write_cell(31, 2, self.modified_objects_map['tablas']['string_created'])
            ods_handler.write_cell(32, 1, self.modified_objects_map['tablas']['string_modified'])
            ods_handler.write_cell(36, 2, self.modified_objects_map['indices']['string_created'])
            ods_handler.write_cell(37, 1, self.modified_objects_map['indices']['string_modified'])
            ods_handler.write_cell(40, 2, self.modified_objects_map['sps']['string_created'])
            ods_handler.write_cell(41, 1, self.modified_objects_map['sps']['string_modified'])

            ods_handler.write_cell(52, 1, ejecutables)

            ods_handler.write_cell(54, 1, server_jars)
            ods_handler.write_cell(55, 1, client_jars)

            ods_handler.write_cell(58, 0, comments)

            ods_handler.save()

    def group_servers(self, id_server, servidores):
        servers = get_both_servers(id_server)

        if servers['br']['description'] not in servidores['br']:
            servidores['br'] += clean_string(f"- {servers['br']['description']}(Hostname: {servers['br']['hostname']}, IP: {servers['br']['ip']}) \n")
            servidores['hey'] += clean_string(f"- {servers['hey']['description']}(Hostname: {servers['hey']['hostname']}, IP: {servers['hey']['ip']}) \n")

        return servidores

    # TODO - Agregar funcionalidad para detectar scripts de información
    def fill_design_sheet(self, file_path, branches_info):
        objets_type = ['tablas', 'indices', 'sps', 'classes', 'SIB21P_reports']

        added_rows = 0
        sheet_name = 'Diseño'
        ods_handler = ODSHandler(file_path, sheet_name)

        ods_handler.write_cell(6, 1, self.description_issue)

        for obj_type in objets_type:
            index_row = self.modified_objects_map.get(obj_type).get('index_design')

            for object_diff in branches_info[obj_type]:
                ods_handler.copy_row_with_format((index_row + added_rows), (index_row + added_rows))
                obj = remove_sql_extension(object_diff.get('path_file'))

                tipo_movimiento = ''
                descripcion_movimiento = ''

                if object_diff.get('status') == 'ADD':
                    tipo_movimiento = 'Agregado'
                    descripcion_movimiento = f"{self.modified_objects_map.get(obj_type).get('add_description')} {obj}"
                elif object_diff.get('status') == 'MODIFY':
                    tipo_movimiento = 'Modificado'
                    descripcion_movimiento = f"{self.modified_objects_map.get(obj_type).get('modify_description')} {obj}"

                if obj_type == 'classes':
                    obj = f"{object_diff.get('project')}/{object_diff.get('repository')}/{obj}"

                ods_handler.write_cell((index_row + added_rows), 0, obj)
                ods_handler.write_cell((index_row + added_rows), 2, tipo_movimiento)
                ods_handler.write_cell((index_row + added_rows), 3, descripcion_movimiento)

                if 'involucrado' in self.modified_objects_map.get(obj_type, {}):
                    involucrado_value = self.modified_objects_map.get(obj_type).get('involucrado')
                    ods_handler.write_cell((index_row + added_rows), 8, involucrado_value)

                added_rows += 1

        ods_handler.save()

    def fill_estimation_file(self, file_path, branches_info):
        counter = 0
        first_row = 15

        objets_type = ['sps']
        sheet_name = '3.Procedimientos'
        ods_handler = ODSHandler(file_path, sheet_name)

        ods_handler.write_cell(9, 1, self.description_issue)
        for obj_type in objets_type:
            for object_diff in branches_info[obj_type]:
                obj = remove_sql_extension(object_diff.get('path_file'))

                counter += 1
                ods_handler.write_cell((first_row + counter), 1, str(counter))
                ods_handler.write_cell((first_row + counter), 2, obj)
                ods_handler.write_cell((first_row + counter), 3, 'Media')

        ods_handler.save()

        sheet_name = '1.Parametros'
        ods_handler = ODSHandler(file_path, sheet_name)

        ods_handler.write_cell(0, 1, self.title_issue)
        ods_handler.write_cell(1, 1, self.creador)
        ods_handler.write_cell(2, 1, self.arq_negocio)
        ods_handler.write_cell(3, 1, self.lider_desarrollo)
        ods_handler.write_cell(4, 1, self.gerente_desarrollo)
        ods_handler.write_cell(5, 1, self.issue.key)

        ods_handler.save()

    def create_functional_especfication(self):
        template_path = f'{TEMPLATE_DIR}/Template_EF.docx'
        name_file = f'{self.control_cambios}_Especificacion Funcional.docx'
        new_file = f'{self.local_package_path}/Documentos/{name_file}'

        current_date = datetime.now()
        formatted_date = current_date.strftime('%d/%m/%Y')

        replacements = {
            'TituloRequerimiento': self.title_issue,
            'FechaRequerimiento': formatted_date,
            'DescripcionRequerimiento': self.description_issue,
            'ArquitectoNegocio': self.arq_negocio,
            'GerenteDesarrollo': self.gerente_desarrollo,
            'LiderDesarrollo': self.lider_desarrollo
        }

        docu = DocumentHandler()
        docu.fill_template(template_path, new_file, replacements)
        docu.convert_docx_to_pdf(new_file, f'{self.local_package_path}/Documentos')
        delete_file(new_file)

    def export_helpdesk_to_pdf(self):
        output_dir = f'{self.local_package_path}/Documentos'
        helpdesk_file_path = f'{output_dir}/{self.issue.key}_HelpDesk.ods'
        export_sheets = ['Hoja Instalación_Br', 'Hoja Instalación_Hey', 'Carta Aceptación Pruebas']

        libreoffice_process = LibreOffice.start_libreoffice_headless()

        ods = ODSHandler(helpdesk_file_path)
        for sheet in export_sheets:
            pdf_file_path = f'{output_dir}/{self.control_cambios}_{sheet}.pdf'
            ods.export_ods_sheet_to_pdf(helpdesk_file_path, sheet, pdf_file_path)

        LibreOffice.stop_libreoffice_headless(libreoffice_process)

    def create_installation_plan(self):
        objets_type = ['tablas', 'indices', 'sps', 'classes', 'reports']

        data = {
            'tablas': {
                'string_created': '',
                'string_modified': ''
            },
            'indices': {
                'string_created': '',
                'string_modified': ''
            },
            'sps': {
                'string_created': '',
                'string_modified': ''
            },
            'sib3': {
                'server_module': '',
                'client_module': ''
            },
            'reports': {
                'string_created': '',
                'string_modified': ''
            }
        }

        for obj_type in objets_type:
            for object_diff in self.modified_objects[obj_type]:
                project = object_diff.get('project')
                repo = object_diff.get('repository')
                obj = remove_sql_extension(object_diff.get('path_file'))
