# A.code AI Agent 🤖

Un agente de Inteligencia Artificial modular y profesional diseñado para la gestión de archivos y consulta de documentos técnicos mediante RAG (Retrieval-Augmented Generation).

Este proyecto combina un potente cerebro basado en LLM (Groq) con capacidades de ejecución de herramientas y memoria persistente, todo envuelto en una interfaz moderna y fluida.

## 🚀 Características Principales

- **Bucle de Razonamiento ReAct**: El agente puede pensar, actuar, observar el resultado y volver a pensar para resolver tareas complejas de forma autónoma.
- **RAG Avanzado (PDF/TXT)**: Indexación y búsqueda semántica en documentos locales usando FAISS y Embeddings de `sentence-transformers`.
- **Manipulación de Archivos**: Capacidad para listar, leer, crear y editar código o archivos de texto directamente.
- **Memoria Persistente**: Historial de conversación guardado localmente con sistema de resumen automático para gestionar el contexto.
- **Interfaz Glassmorphism**: UI moderna construida con Flet, con animaciones suaves y diseño premium.

## 🛠️ Tecnologías Utilizadas

- **Lenguaje**: Python 3.10+
- **LLM**: Groq API (Inferencia ultra rápida)
- **Frontend**: Flet (Flutter para Python)
- **Vector Store**: FAISS
- **Embeddings**: Sentence-Transformers (`all-MiniLM-L6-v2`)
- **Procesamiento de PDF**: PyPDF

## 📦 Instalación

1. **Clonar el repositorio**:
   ```bash
   git clone <tu-repositorio>
   cd "02.4_version con frontendmejorada"
   ```

2. **Crear y activar entorno virtual**:
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Linux/Mac:
   source .venv/bin/activate
   ```

3. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno**:
   Crea un archivo `.env` en la raíz con tu API Key de Groq:
   ```env
   GROQ_API_KEY=tu_api_key_aquí
   ```

## 🎮 Cómo Ejecutar

### Versión con Interfaz Gráfica (Recomendado)
Para iniciar la experiencia visual premium:
```bash
python app/gui.py
```

### Versión por Terminal
Para interactuar directamente desde la consola:
```bash
python -m app.main
```

## 📁 Estructura del Proyecto

- `app/`: Código fuente principal.
  - `rag/`: Lógica de recuperación de documentos y base de datos vectorial.
  - `tools/`: Herramientas que el agente puede ejecutar (archivos, pdf).
  - `agent.py`: Orquestador y despachador de herramientas.
  - `gui.py`: Interfaz de usuario Glassmorphism.
  - `memory.py`: Gestión del historial y resúmenes.
- `data/`: Almacenamiento local de memoria, índices y documentos fuente en `/docs`.

## 🛡️ Licencia
Este proyecto es de uso educativo para el aprendizaje de arquitectura de agentes de IA.
