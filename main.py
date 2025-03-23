import os

from src.automation.automation import Automation
from src.automation.bitbucket import Bitbucket
from src.automation.docx import DocumentHandler
from src.automation.git import Git
from src.automation.jira import Jira
from src.automation.package import Package
from src.utils.utils import get_dev_status, remove_sql_extension, capitalize_initials, get_server_hey, get_server_br, SERVERS_BR, clean_string






def main():
    bitbucket = Bitbucket()
    auto = Automation()
    jira = Jira()

    auto.create_package('TCPC-18067')
    #objetos = jira.list_changes('TCPC-17452')
    # imprimir el contenido de cada objeto en 'objetos'
    #print(objetos)

    # auto.create_package('TCPC-17892')

    # issue = jira.jira_session.issue('TCPC-17892')
    #
    # branches_info = jira.get_branches_from_task('TCPC-17892')
    #
    # modified_objects = []
    # for branch in branches_info:
    #     dif = jira.get_diff_branch(branch['project_id'], branch['name_repository'], branch['branch_name'])
    #     modified_objects.append(dif)
    #
    # auto.scriptsbase_files(issue, modified_objects)

    # Ejemplo funcional para crear una tarea de instalación tradicional
    # auto.create_traditional_package_task(
    #     'TCPC-17998',
    #     'Ajuste de código para renovación de seguros de auto',
    #     'Se ajustan las validaciones de edad del cliente para permitir que, en las renovaciones del seguro de auto, se pueda dar de alta con o sin seguro de vida, considerando también el mes entre la fecha de nacimiento del cliente y la fecha de renovación del seguro y ya no solo el año.',
    #     '52845'
    # )

    # my_jql = 'assignee = currentUser() AND sprint in openSprints() AND issuetype = Story'
    # my_jql = 'assignee = currentUser() AND issuetype = Story AND updated >= "2025/01/01" AND updated <= "2025/12/31"'
    # my_jql = 'assignee = currentUser() AND issuetype = Story'
    # results = jira.execute_jql(my_jql)
    # count = 0
    # for issue in results:
    #     count += 1
    #     print(f'{count} - {issue} - {issue.fields.summary} - {issue.fields.updated} - {issue.fields.status}')
    #     # Check if the issue has sub-tasks
    #     if hasattr(issue.fields, 'subtasks'):
    #         for subtask in issue.fields.subtasks:
    #             subtask_issue = jira.jira_session.issue(subtask.key)
    #             if subtask_issue.fields.issuetype.name == "Installation Package":
    #                 print(f"\tSub-task {subtask.key}: '{subtask_issue.fields.summary}'")
    #                 print(f"\t\t> Fecha de instalación= {subtask_issue.fields.customfield_11800}")
    #     print("\n")



    #jira.print_issue_fields_metadata('TCPC-17080')
    #auto.fill_helpdesk('TCPC-17736')


    #
    # auto.move_and_upload_scripts(issue)

    # auto.update_branches_from_task("TCPC-17892")



    #print(SERVERS_BR["SYB16"])
    #print(get_server_hey("SYB16"))


    #browse_url = 'https://bitbucket.banregio.com:8443/projects/SYB16/repos/cr-sps/browse'
    #clone_url = git.generate_clone_url(browse_url)
    #print(clone_url)

    # base_directory = '/Users/ivan.riveros/Documents/AmbientesDesa/Sibamex21/Sibamex_21/src'
    # bitbucket.iterate_and_pull(base_directory)

    #dirs_to_exclude = ['principal', 'dir2']
    #bitbucket.iterate_and_reset(base_directory, dirs_to_exclude)


    #jira.test_connection()
    #issue_key = 'TCPC-17223'
    #jira.print_issue_fields_metadata(issue_key)

    # jira.list_fields_from_task("TCPC-17223")




    # Ejemplo de uso
    #issue_key = 'TCPC-17223'
    #field_name = 'customfield_12530'
    #description = 'Mantenimiento'
    #field_id = jira.get_field_id_from_description(issue_key, field_name, description)
    #print(f"El ID para la descripción '{description}' es: {field_id}")

    #jira.list_issue_types()
    #jira.print_all_fields_metadata()
    # #jira.create_architecture_task("TCPC-17007", "MODIFICACION DE TABLA FISICA", "PRUEBA DEL CAMPO DESACRIPCION", "Desarrollo")
    # branches_info = jira.get_branches_from_task("TCPC-17250")
    # jira.get_diff_branch('SIB3P', 'sibamex-credito-api', 'feature/TCPC-17250-50015')
    # jira.get_diff_branch('SYB16', 'scriptsbase', 'feature/TCPC-17250-50015')
    # jira.get_diff_branch('SIB21P', 'cr', 'feature/TCPC-17250-50015')

if __name__ == "__main__":
    main()