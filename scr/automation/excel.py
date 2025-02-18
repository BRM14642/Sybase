import copy
from odf.opendocument import load
from odf.table import Table, TableRow, TableCell
from odf.text import P
from odf.style import Style, ParagraphProperties
from scr.utils.logging_config import logger
import xml.etree.ElementTree as ET  # Para convertir a XML en depuración

class ODSHandler:
    def __init__(self, file_path, sheet_name=None):
        self.file_path = file_path
        self.doc = load(file_path)
        self.sheet = None
        if sheet_name:
            for table in self.doc.spreadsheet.getElementsByType(Table):
                if table.getAttribute("name") == sheet_name:
                    self.sheet = table
                    break
        if not self.sheet:
            self.sheet = self.doc.spreadsheet.getElementsByType(Table)[0]

    def get_row(self, row_index):
        return self.sheet.getElementsByType(TableRow)[row_index]

    def get_cell(self, row_index, cell_index):
        row = self.get_row(row_index)
        return row.getElementsByType(TableCell)[cell_index]

    def read_cell(self, row_index, cell_index):
        """
        Lee el contenido de una celda específica.
        :param row_index: índice de la fila en la que se encuentra la celda
        :param cell_index: índice de la celda en la fila
        :return: valor de la celda
        """
        cell = self.get_cell(row_index, cell_index)
        text_content = ""
        for p in cell.getElementsByType(P):
            if p.firstChild:
                text_content += p.firstChild.data
        return text_content

    def write_cell(self, row_index, cell_index, value):
        """
        Escribe un valor en una celda específica.
        :param row_index: índice de la fila en la que se encuentra la celda
        :param cell_index: índice de la celda en la fila
        :param value: valor a escribir
        :return:
        """
        cell = self.get_cell(row_index, cell_index)
        for child in list(cell.childNodes):
            cell.removeChild(child)
        cell.addElement(P(text=value))

    def copy_row_with_format(self, target_row_index, format_row_index):
        """
        Copia una fila en el índice deseado con el formato de otra fila que indiquemos.
        :param target_row_index: posición de la fila a insertar
        :param format_row_index: posición de la fila que contiene el formato
        :return:
        """
        # Obtener la fila de formato
        format_row = self.get_row(format_row_index)

        # Crear una nueva fila con el mismo formato
        new_row = TableRow()

        # Copiar los atributos de la fila (por ejemplo, estilos y repeticiones de fila)
        for attr in ["stylename", "numberrowsrepeated"]:
            value = format_row.getAttribute(attr)
            if value:
                new_row.setAttribute(attr, value)

        current_column_index = 0
        for cell in format_row.getElementsByType(TableCell):
            new_cell = TableCell()

            # Copiar el contenido de la celda
            for p in cell.getElementsByType(P):
                if p.firstChild:
                    new_cell.addElement(P(text=p.firstChild.data))

            # Copiar todos los atributos importantes
            for attr in [
                "stylename", "numbercolumnsrepeated", "numberrowsspanned", "numbercolumnsspanned",
                "value", "formula", "protected"
            ]:
                value = cell.getAttribute(attr)

                # Asegurar que `numberrowsspanned` y `numbercolumnsspanned` no sean None
                if (attr in ["numberrowsspanned", "numbercolumnsspanned"]) and value is None:
                    value = "1"  # ODF usa strings para atributos, no enteros

                if value:
                    new_cell.setAttribute(attr, value)

            # Agregar celdas vacías si es necesario
            while current_column_index > len(new_row.childNodes):
                new_row.addElement(TableCell())

            # Agregar la celda a la nueva fila en la posición correcta
            if current_column_index < len(new_row.childNodes):
                new_row.insertBefore(new_cell, new_row.childNodes[current_column_index])
            else:
                new_row.addElement(new_cell)

            # Actualizar el índice de columna actual en función del atributo `numbercolumnsspanned`
            numbercolumnsspanned = cell.getAttribute("numbercolumnsspanned")
            if numbercolumnsspanned:
                current_column_index += int(numbercolumnsspanned)
            else:
                current_column_index += 1

        # Insertar la nueva fila en la posición deseada
        self.sheet.insertBefore(new_row, self.get_row(target_row_index))

        logger.debug(f"Se ha copiado la fila {format_row_index} en la posición {target_row_index} correctamente.")

    def save(self, output_path=None):
        if output_path is None:
            output_path = self.file_path
        self.doc.save(output_path)

    def print_all_values(self):
        for row in self.sheet.getElementsByType(TableRow):
            for cell in row.getElementsByType(TableCell):
                text_content = ""
                for p in cell.getElementsByType(P):
                    text_content += p.text
                print(text_content, end=' ')
            print()
