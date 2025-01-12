from string import Template

class ScriptHandler:
    def __init__(self, template_path):
        self.template_path = template_path

    def load_template(self):
        try:
            with open(self.template_path, "r") as file:
                return Template(file.read())
        except Exception as e:
            print(f"Error al cargar la plantilla: {e}")
            return None

    def generate_script(self, table_name, new_columns, existing_columns):
        # Nombre de la tabla nueva y backup
        new_table_name = f"{table_name}_tmp"
        backup_table_name = f"{table_name}_backup"

        # Generar los campos nuevos y existentes
        fields = ",\n    ".join(new_columns + existing_columns)
        existing_fields = ", ".join(existing_columns)

        # Cargar la plantilla
        template = self.load_template()
        if not template:
            return None

        # Rellenar la plantilla
        script = template.substitute(
            new_table_name=new_table_name,
            fields=fields,
            existing_fields=existing_fields,
            original_table_name=table_name,
            backup_table_name=backup_table_name
        )

        return script

    def save_script(self, script, output_path):
        try:
            with open(output_path, "w") as file:
                file.write(script)
            print(f"Script guardado en {output_path}")
        except Exception as e:
            print(f"Error al guardar el script: {e}")
