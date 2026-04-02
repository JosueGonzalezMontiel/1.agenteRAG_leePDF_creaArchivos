from app.rag.rag import responder_con_rag
from app.tools.registry import register_tool
from app.logger import logger

@register_tool("ask_pdf")   
def ask_pdf(question):
    '''
    Herramienta que recibe una pregunta, busca en los documentos PDF indexados 
    usando RAG y devuelve una respuesta basada en ellos junto con las fuentes.
    '''
    logger.info(f"Tool ejecutada: ask_pdf con pregunta: '{question}'")
    try:
        resultado = responder_con_rag(question)
        return resultado
    except Exception as e:
        err = f"Error al consultar los PDFs: {e}"
        logger.error("Error en tool ask_pdf", exc_info=True)
        return err
