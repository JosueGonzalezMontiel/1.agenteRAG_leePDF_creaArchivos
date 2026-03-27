# app/tools.py
# Este archivo contiene las "herramientas" que el agente puede usar. Son funciones normales de Python.
import os

def list_files_in_dir(directory="."):
    '''
    Función que lee los archivos de un directorio y los devuelve como texto.
    El parámetro directory="." significa que si no le pasamos ninguno, por defecto mirará en
    la carpeta actual (el punto '.' significa "directorio actual").
    '''

    try:
        # os.listdir devuelve una lista con los nombres de todos los archivos y carpetas dentro de la ruta especificada.
        files = os.listdir(directory)
        
        # Devolvemos un string formateado (f-string) que incluye la variable directory y la lista de archivos.
        return f"Archivos en {directory}: {files}"
        
    except Exception as e:
        # Si hubo un error, convertimos el error (e) a texto con str() y lo devolvemos.
        return f"Error: {str(e)}"

#herramienta para leer archivos
def read_file(file_path):
    print("herramienta llamada: read_file")
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        # Agregado {e} para ver exactamente por qué falló
        err = f"Error al leer el archivo {file_path}: {e}"
        print(err)
        return err

#herrameinta para editar archivos
def edit_file(file_path, prev_text, new_text):
    print("herramienta llamada: edit_file")
    try:
        existed = os.path.exists(file_path)
        if existed and prev_text:
            content = read_file(file_path)
            if prev_text not in content:
                return f"Texto {prev_text} no encontrado en el archivo {file_path}"
                
            content = content.replace(prev_text, new_text)
        else:
            #crear o sobreescribir archivo con el nuevo texto
            dir_name = os.path.dirname(file_path)
            if dir_name:
                os.makedirs(dir_name, exist_ok=True)
            content = new_text
        
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
        action = "editado" if existed and prev_text else "creado"
        return f"Archivo {file_path} {action} exitosamente."
    except Exception as e:
        # Agregado {e} para ver detalles del error
        err = f"Error al editar el archivo {file_path}: {e}"
        print(err)
        return err
