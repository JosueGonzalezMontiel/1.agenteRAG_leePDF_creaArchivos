# app/tools.py
# Este archivo contiene las "herramientas" que el agente puede usar. Son funciones normales de Python.
from app.tools.registry import register_tool
from app.config import SAFE_BASE_DIR
from app.logger import logger
import os

from app.config import SAFE_BASE_DIR
import os

def safe_path(path):
    abs_path = os.path.abspath(os.path.join(SAFE_BASE_DIR, path))
    
    if not abs_path.startswith(SAFE_BASE_DIR):
        raise ValueError("Acceso fuera del sandbox no permitido")
    
    return abs_path

@register_tool("list_files")
def list_files_in_dir(directory="."):
    '''
    Función que lee los archivos de un directorio y los devuelve como texto.
    El parámetro directory="." significa que si no le pasamos ninguno, por defecto mirará en
    la carpeta actual (el punto '.' significa "directorio actual").
    '''

    try:
        # os.listdir devuelve una lista con los nombres de todos los archivos y carpetas dentro de la ruta especificada.
        directory = safe_path(directory)

        files = os.listdir(directory)


        # Devolvemos un string formateado (f-string) que incluye la variable directory y la lista de archivos.
        return f"Archivos en {directory}: {files}"
        
    except Exception as e:  
        # Si hubo un error, convertimos el error (e) a texto con str() y lo devolvemos.
        return f"Error: {str(e)}"

@register_tool("read_file")
#herramienta para leer archivos
def read_file(file_path):
    logger.info("Tool ejecutada: read_file")
    try:
        file_path = safe_path(file_path)
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        # Agregado {e} para ver exactamente por qué falló
        err = f"Error al leer el archivo {file_path}: {e}"
        logger.error("Error en tool read_file", exc_info=True)
        return err

@register_tool("edit_file")
#herrameinta para editar archivos
def edit_file(file_path, prev_text, new_text):
    logger.info("Tool ejecutada: edit_file")
    try:
        file_path = safe_path(file_path)
        existed = os.path.exists(file_path)
        if existed and prev_text:
            content = read_file(file_path)
            if prev_text not in content:
                err_msg = f"Texto {prev_text} no encontrado en el archivo {file_path}"
                logger.error(err_msg)
                return err_msg
                
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
        logger.error("Error en tool edit_file", exc_info=True)
        return err
