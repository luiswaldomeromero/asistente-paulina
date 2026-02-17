import streamlit as st
import google.generativeai as genai
import pandas as pd
from io import BytesIO

# --- 1. CONFIGURACIÓN DE LA INTERFAZ ---
st.set_page_config(page_title="OmniAgent Core Pro", page_icon="🎓", layout="wide")

# Estilo personalizado para que se vea como una herramienta profesional
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #4CAF50; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. BARRA LATERAL (CONFIGURACIÓN Y ARCHIVOS) ---
with st.sidebar:
    st.title("🚀 Panel de Control")
    st.markdown("### Configuración del Agente")
    api_key = st.text_input("Introduce tu Gemini API Key:", type="password")
    
    st.divider()
    st.markdown("### 📂 Carga de Datos")
    archivo_subido = st.file_uploader("Sube Excel o CSV de alumnos/profesionistas", type=['csv', 'xlsx'])
    
    if archivo_subido:
        st.success("Archivo listo para analizar")

    st.divider()
    st.info("Este agente tiene acceso a Google Search y puede crear planeaciones, guiones y analizar bases de datos.")

# --- 3. LÓGICA DEL MOTOR (GEMINI 1.5 FLASH) ---
if api_key:
    try:
        genai.configure(api_key=api_key)
        
        # Configuramos el modelo con herramientas de búsqueda web
        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            tools=[{"google_search_retrieval": {}}]
        )

        # Inicializar historial de chat con personalidad de "Nuevo Empleado"
        if "messages" not in st.session_state:
            st.session_state.messages = []
            bienvenida = "Hola Paulina, soy OmniAgent_Core, tu nuevo asistente. He activado mis módulos de búsqueda web y análisis de datos. ¿Qué materia o base de datos vamos a trabajar hoy?"
            st.session_state.messages.append({"role": "assistant", "content": bienvenida})

        # Mostrar el chat
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # --- 4. INTERACCIÓN Y EJECUCIÓN ---
        if prompt := st.chat_input("Escribe una instrucción (ej: 'Busca tendencias de IA en 2026')"):
            
            # Preparar contexto si hay un archivo cargado
            contexto_datos = ""
            if archivo_subido:
                try:
                    df = pd.read_excel(archivo_subido) if archivo_subido.name.endswith('xlsx') else pd.read_csv(archivo_subido)
                    contexto_datos = f"\n\nDATOS DEL ARCHIVO CARGADO:\n{df.to_string(index=False)}\n\n"
                except Exception as e:
                    st.error(f"Error al leer el archivo: {e}")

            # Guardar y mostrar mensaje del usuario
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Generar respuesta del Asistente
            with st.chat_message("assistant"):
                instruccion_sistema = (
                    "Eres OmniAgent_Core, un asistente académico de élite. "
                    "Tu tono es de un empleado brillante, proactivo y servicial. "
                    "Tienes permiso para usar Google Search si la información es reciente o externa. "
                    "Si hay datos de un archivo, úsalos para responder con precisión."
                )
                
                # Llamada al modelo
                response = model.generate_content(instruccion_sistema + contexto_datos + prompt)
                
                # Mostrar respuesta y guardar
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})

    except Exception as e:
        st.error(f"Ocurrió un error con la API: {e}")
else:
    st.warning("⚠️ Por favor, introduce tu API Key en la barra lateral para comenzar.")
    st.image("https://images.unsplash.com/photo-1434030216411-0b793f4b4173?ixlib=rb-4.0.3&auto=format&fit=crop&w=1470&q=80", caption="Listo para trabajar contigo.")
