import uno
import sys

def exportar_hoja_con_formato(archivo_ods, nombre_hoja, archivo_pdf):
    # Conectar con LibreOffice en modo headless
    local_context = uno.getComponentContext()
    resolver = local_context.ServiceManager.createInstanceWithContext(
        "com.sun.star.bridge.UnoUrlResolver", local_context
    )
    context = resolver.resolve("uno:socket,host=localhost,port=2002;urp;StarOffice.ComponentContext")
    desktop = context.ServiceManager.createInstanceWithContext("com.sun.star.frame.Desktop", context)

    # Abrir el archivo ODS
    url = uno.systemPathToFileUrl(archivo_ods)
    props = (uno.createUnoStruct("com.sun.star.beans.PropertyValue"),)
    props[0].Name = "Hidden"
    props[0].Value = True
    doc = desktop.loadComponentFromURL(url, "_blank", 0, props)

    # Forzar el recálculo de todas las fórmulas
    doc.calculateAll()

    # Ocultar todas las hojas excepto la deseada
    hojas = doc.Sheets
    for i in range(hojas.getCount()):
        hoja = hojas.getByIndex(i)
        if hoja.Name != nombre_hoja:
            hoja.IsVisible = False

    # Configurar la escala para ajustar la hoja al ancho y alto de la página
    sheet = hojas.getByName(nombre_hoja)
    page_styles = doc.getStyleFamilies().getByName("PageStyles")
    page_style = page_styles.getByName(sheet.PageStyle)
    page_style.ScaleToPagesX = 1
    page_style.ScaleToPagesY = 1

    # Exportar a PDF
    export_props = []
    prop = uno.createUnoStruct("com.sun.star.beans.PropertyValue")
    prop.Name = "FilterName"
    prop.Value = "calc_pdf_Export"
    export_props.append(prop)

    output_url = uno.systemPathToFileUrl(archivo_pdf)
    doc.storeToURL(output_url, tuple(export_props))

    # Cerrar el documento
    doc.close(True)
    print(f"✅ Exportado correctamente: {archivo_pdf}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Uso: python export_ods_to_pdf.py <archivo_ods> <nombre_hoja> <archivo_pdf>")
        sys.exit(1)

    archivo_ods = sys.argv[1]
    nombre_hoja = sys.argv[2]
    archivo_pdf = sys.argv[3]

    try:
        exportar_hoja_con_formato(archivo_ods, nombre_hoja, archivo_pdf)
    except Exception as e:
        print(f"❌ Error al exportar: {e}")