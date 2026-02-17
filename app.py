import streamlit as st
from google import genai
import pandas as pd

# --- 1. CONFIGURACIÓN DE LA INTERFAZ ---
st.set_page_config(page_title="OmniAgent Core v3.1", page_icon="🧠", layout="wide")

with st.sidebar:
    st.title("🛡️ Sistema Gemini 3")
    api_key = st.text_input("API Key de Google:", type="password")
    
    st.divider()
    st.markdown("### 👤 Configuración Profesional")
    
    # NUEVO: Selector de Nivel Educativo para personalización profunda
    nivel = st.selectbox(
        "Nivel Educativo", 
        ["Primaria", "Secundaria", "Preparatoria", "Universidad / Posgrado"]
    )
    
    materias = st.text_area("¿Qué materias o temas impartes?", placeholder="Ej: Matemáticas, Historia, Psicología...")
    estilo = st.selectbox("Tono del Asistente", ["Muy Formal", "Colega/Amigable", "Creativo", "Ejecutivo"])
    
    st.divider()
    archivo = st.file_uploader("Subir base de datos o lecturas (Excel/CSV/PDF)", type=['csv', 'xlsx'])

# --- 2. MOTOR GEMINI 3 FLASH ---
if api_key:
    try:
        client = genai.Client(api_key=api_key)
        
        if "messages" not in st.session_state:
            st.session_state.messages = []
            saludo = f"OmniAgent Core v3.1 activo. Configurado para nivel: **{nivel}**. ¿Cómo te ayudo hoy con tus clases?"
            st.session_state.messages.append({"role": "assistant", "content": saludo})

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # --- 3. PROCESAMIENTO CON INTELIGENCIA ADAPTATIVA ---
        if prompt := st.chat_input("Escribe tu instrucción aquí..."):
            
            contexto_datos = ""
            if archivo:
                try:
                    df = pd.read_excel(archivo) if archivo.name.endswith('xlsx') else pd.read_csv(archivo)
                    contexto_datos = f"\n[DATOS DEL ARCHIVO]:\n{df.head(20).to_string(index=False)}\n"
                except:
                    st.error("Error al procesar el archivo.")

            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                # Instrucción de sistema que inyecta el nivel educativo
                config_sistema = (
                    f"Eres OmniAgent_Core, un asistente experto en el nivel {nivel}. "
                    f"Tu usuario imparte {materias}. Tu tono es {estilo}. "
                    f"Si el nivel es Primaria, usa ejemplos sencillos y lúdicos. "
                    f"Si es Universidad, usa rigor académico y terminología avanzada. "
                    "Usa Google Search para datos del 2026."
                )
                
                response = client.models.generate_content(
                    model="gemini-3-flash-preview", 
                    contents=config_sistema + contexto_datos + prompt
                )
                
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})

    except Exception as e:
        st.error(f"Error: {e}. Revisa tu conexión y API Key.")
else:
    st.warning("⚠️ Configura tu API Key en la barra lateral para activar el motor Gemini 3.")
