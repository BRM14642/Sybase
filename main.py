import os

from scr.automation.automation import Automation
from scr.automation.bitbucket import Bitbucket
from scr.automation.git import Git
from scr.automation.jira import Jira
from scr.utils.utils import get_dev_status, remove_sql_extension, capitalize_initials, get_server_hey, get_server_br, SERVERS_BR, clean_string






def main():
    auto = Automation()
    jira = Jira()

    # Ejemplo funcional para crear una tarea de instalación tradicional
    # auto.create_traditional_package_task(
    #     'TCPC-17592',
    #     'Mantenimiento en proceso de aplicación de sobregiros en fecha de vencimiento',
    #     'Se realiza el ajuste en el proceso de aplicación de sobregiros para que se apliquen correctamente también en la fecha de vencimiento de la fecha de vencimiento de la línea de crédito',
    #     '51553'
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
    auto.fill_helpdesk('TCPC-17593')
    #auto.update_branches_from_task("TCPC-17421")



    #print(SERVERS_BR["SYB16"])
    #print(get_server_hey("SYB16"))


    #browse_url = 'https://bitbucket.banregio.com:8443/projects/SYB16/repos/cr-sps/browse'
    #clone_url = git.generate_clone_url(browse_url)
    #print(clone_url)

    #base_directory = '/Users/ivan.riveros/Documents/AmbientesDesa/Sibamex21/Sibamex_21/src'
    #itbucket.iterate_and_pull(base_directory)

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