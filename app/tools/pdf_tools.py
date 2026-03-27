from app.rag.rag import responder_con_rag

def ask_pdf(question):
    '''
    Herramienta que recibe una pregunta, busca en los documentos PDF indexados 
    usando RAG y devuelve una respuesta basada en ellos junto con las fuentes.
    '''
    print(f"herramienta llamada: ask_pdf con pregunta: '{question}'")
    try:
        resultado = responder_con_rag(question)
        return resultado
    except Exception as e:
        err = f"Error al consultar los PDFs: {e}"
        print(err)
        return err
