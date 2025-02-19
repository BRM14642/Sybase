import re
import shutil
from scr.automation.bitbucket import Bitbucket
from scr.scripts.script_handler import ScriptHandler
from scr.utils.utils import get_default_value_to_string


class Sybase:
    def get_columns_script_table(self, file_path):
        with open(file_path, 'r') as file:
            sql_content = file.read()

        column_pattern = re.compile(
            r'\s*((NumTransac|Transaccio|Usuario|FechaSis|SucOrigen|SucDestino|[A-Za-z]{3}_[A-Za-z]{1,6}))\s+(\w+(\(\d+\))?(\s+identity)?)\s+(not null|null|identity)?',
            re.IGNORECASE)
        columns = column_pattern.findall(sql_content)

        column_data = []
        for column in columns:
            column_name = column[0]
            data_type = column[2]
            if any('identity' in part.lower() for part in column):
                data_type += ' identity'
            column_data.append({'name': column_name, 'type': data_type})

        return column_data

    def replace_word_in_sql(self, file_path, old_word, new_word):
        with open(file_path, 'r') as file:
            sql_content = file.read()

        updated_sql_content = re.sub(rf'\b{old_word}\b', new_word, sql_content)

        with open(file_path, 'w') as file:
            file.write(updated_sql_content)

    def add_string_specific_line(self, file_path, line_number, str_to_add):
        try:
            with open(file_path, 'r') as file:
                lines = file.readlines()
        except IOError as e:
            print(f"Error reading file {file_path}: {e}")
            return

        if line_number < 1 or line_number > len(lines):
            print(f"Line number {line_number} is out of range.")
            return

        # Obtener el contenido de la línea específica
        original_content = lines[line_number - 1].rstrip()
        print(f"Original content: '{original_content}'")
        print(f"modified content: '{original_content + str_to_add}'")

        # Modificar la línea específica
        lines[line_number - 1] = original_content + str_to_add

        try:
            with open(file_path, 'w') as file:
                file.writelines(lines)
            print(f"Line {line_number} modified successfully.")
        except IOError as e:
            print(f"Error writing to file {file_path}: {e}")

    # TODO Validar cuando se agrega mas de una columna a la tabla que no tiene
    #  NumTransac puede que algunos renglones queden sin coma al final
    def add_columns_to_table(self, file_path, new_columns):
        try:
            with open(file_path, 'r') as file:
                sql_content = file.readlines()
        except IOError as e:
            print(f"Error reading file {file_path}: {e}")
            return

        column_pattern = re.compile(
            r'\s*((NumTransac|Transaccio|Usuario|FechaSis|SucOrigen|SucDestino|[A-Za-z]{3}_[A-Za-z]{1,6}))\s+(\w+(\(\d+\))?(\s+identity)?)\s+(not null|null|identity)?',
            re.IGNORECASE)

        # Find the position to insert new columns
        insert_position = None
        line_field = ''
        transac_field_found = False
        for i, line in enumerate(sql_content):
            print(line)
            if line == '\n' or line.strip() == '':
                print("vacío")
                continue
            if re.match(r'^\s*NumTransac\s', line):
                transac_field_found = True
                insert_position = i - 1
                break
            if column_pattern.match(line):
                print("Columna")
                line_field = line
                insert_position = i + 1

        columns = column_pattern.findall(line_field)

        print(f"insert_position:{insert_position} columns:{columns} new_columns:{new_columns}")

        #line_field = line_field.replace(columns[0][0], new_columns[0]['name'])
        print(f"nueva line {line_field}")

        if insert_position is None:
            print("No se encontró el campo NumTransac en el archivo.")
            return

        new_column_format = ''
        # Prepare new columns with the same format
        formatted_new_columns = []
        for column in new_columns:
            new_column_format = line_field.replace(columns[0][0], new_columns[0]['name'])
            new_column_format = new_column_format.replace(columns[0][2], column['type'])

            formatted_new_columns.append(new_column_format)
            print(f"Formatted new column: {new_column_format}")



        # Insert new columns into the original content
        updated_sql_content = (
                sql_content[:insert_position] +
                [f"{col}" for col in formatted_new_columns] +
                sql_content[insert_position:]
        )

        # Write the updated content back to the file
        try:
            with open(file_path, 'w') as file:
                file.writelines(updated_sql_content)
            print(f"New columns added to {file_path}")
        except IOError as e:
            print(f"Error writing to file {file_path}: {e}")

        if not transac_field_found:
            self.add_string_specific_line(file_path, insert_position, ',\n')

    def modify_table(self, table, repository, new_columns):

        source_script_path = f"scripts/outputs/{table}.sql"
        new_script = f"scripts/outputs/{table}_1_TMP.sql"


        bitbucket = Bitbucket()
        bitbucket.download_file_to(
            source_script_path,
            f"{repository}",
            f"{table}.sql",
            "develop"
        )

        self.copy_file_with_new_name(source_script_path, new_script)

        self.add_columns_to_table(source_script_path, new_columns)

        self.replace_word_in_sql(source_script_path, f"{table}", f"{table}_TMP")

        original_columns = self.get_columns_script_table(source_script_path)
        integrated_columns = self.integrate_columns(original_columns, new_columns)



        # ***************************************************************************
        template = ScriptHandler('scripts/templates/tables/respaldo.sql')
        temp = template.load_template()

        if not temp:
            return None

        string_original_colums = self.create_string_columns(original_columns)

        script = temp.substitute(
            table_name = f"{table}",
            table_tmp = f"{table}_TMP",
            original_columns = string_original_colums,
        )

        output_path = f"scripts/outputs/{table}_2_RES.sql"
        template.save_script(script, output_path)

        # ***************************************************************************
        template = ScriptHandler('scripts/templates/tables/validacion.sql')
        temp = template.load_template()

        if not temp:
            return None

        script = temp.substitute(
            table_name=f"{table}",
            table_tmp=f"{table}_TMP"
        )

        output_path = f"scripts/outputs/{table}_3_REV.sql"
        template.save_script(script, output_path)

        # ***************************************************************************
        template = ScriptHandler('scripts/templates/tables/validacion.sql')
        temp = template.load_template()

        if not temp:
            return None

        script = temp.substitute(
            table_name=f"{table}",
            table_tmp=f"{table}_TMP"
        )

        output_path = f"scripts/outputs/{table}_3_REV.sql"
        template.save_script(script, output_path)

        # ***************************************************************************
        template = ScriptHandler('scripts/templates/tables/drop.sql')
        temp = template.load_template()

        if not temp:
            return None

        script = temp.substitute(
            table_name=f"{table}"
        )

        output_path = f"scripts/outputs/{table}_4_DRO.sql"
        template.save_script(script, output_path)


        # ***************************************************************************
        template = ScriptHandler('scripts/templates/tables/regreso.sql')
        temp = template.load_template()

        if not temp:
            return None

        string_integrated_colums = self.create_string_columns(integrated_columns)
        string_new_values = string_integrated_colums
        # Crear una cadena donde los nombres de new_columns existan en string_integrated_colums reemplazarlas con el valor por defecto que se obtendran de SYBASE_DEFAULT_VALUES
        for column in new_columns:
            print(column)
            default_value = get_default_value_to_string(column['type'])
            print(default_value)
            string_new_values = string_new_values.replace(column['name'], default_value)

        script = temp.substitute(
            table_name = f"{table}",
            table_tmp = f"{table}_TMP",
            colums = string_integrated_colums,
            values = string_new_values
        )

        output_path = f"scripts/outputs/{table}_6_REG.sql"
        template.save_script(script, output_path)

        # ***************************************************************************
        template = ScriptHandler('scripts/templates/tables/validacion.sql')
        temp = template.load_template()

        if not temp:
            return None

        script = temp.substitute(
            table_name=f"{table}",
            table_tmp=f"{table}_TMP"
        )

        output_path = f"scripts/outputs/{table}_7_REV.sql"
        template.save_script(script, output_path)

        # ***************************************************************************
        template = ScriptHandler('scripts/templates/tables/drop.sql')
        temp = template.load_template()

        if not temp:
            return None

        script = temp.substitute(
            table_name=f"{table}_TMP"
        )

        output_path = f"scripts/outputs/{table}_8_DRO.sql"
        template.save_script(script, output_path)

        # ***************************************************************************
        template = ScriptHandler('scripts/templates/tables/grants.sql')
        temp = template.load_template()

        if not temp:
            return None

        script = temp.substitute(
            table_name=f"{table}"
        )

        output_path = f"scripts/outputs/{table}_9_PER.sql"
        template.save_script(script, output_path)

    def integrate_columns(self, original_columns, new_columns):
        integrated_columns = []
        isNumTransac = False
        for column in original_columns:
            if column['name'] == 'NumTransac':
                isNumTransac = True
                for new_column in new_columns:
                    integrated_columns.append(new_column)
            integrated_columns.append(column)

        if not isNumTransac:
            for column in new_columns:
                integrated_columns.append(column)

        return integrated_columns

    def create_string_columns(self, columns):
        columns_str = ""
        counter = 0
        for column in columns:
            if counter % 5 == 0 and counter > 0:
                columns_str += "\n\t\t"
            counter += 1
            columns_str += f"\t{column['name']},"

        columns_str = columns_str[:-1]

        return columns_str

    def copy_file_with_new_name(self, source_path, destination_path):
        try:
            shutil.copy(source_path, destination_path)
            print(f"File copied from {source_path} to {destination_path}")
        except IOError as e:
            print(f"Error copying file: {e}")

