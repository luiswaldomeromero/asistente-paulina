import streamlit as st
from google import genai
import pandas as pd

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="OmniAgent Core v3.0", page_icon="🧠", layout="wide")

with st.sidebar:
    st.title("🛡️ Sistema Gemini 3")
    api_key = st.text_input("API Key de Google:", type="password")
    st.divider()
    st.markdown("### 📝 Perfil de la Maestra")
    materias = st.text_area("¿Qué materias impartes?", placeholder="Ej: Psicología, Historia...")
    estilo = st.selectbox("Tono del Asistente", ["Muy Formal", "Colega/Amigable", "Creativo", "Ejecutivo"])
    archivo = st.file_uploader("Subir base de datos (Excel/CSV)", type=['csv', 'xlsx'])

# --- 2. MOTOR GEMINI 3 FLASH ---
if api_key:
    try:
        # Nueva forma de inicializar el cliente según tu documentación
        client = genai.Client(api_key=api_key)
        
        if "messages" not in st.session_state:
            st.session_state.messages = []
            saludo = f"OmniAgent Core v3.0 (Gemini 3) activo. Perfil: {estilo}. ¿En qué avanzamos, Paulina?"
            st.session_state.messages.append({"role": "assistant", "content": saludo})

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # --- 3. INTERACCIÓN ---
        if prompt := st.chat_input("Escribe tu instrucción..."):
            
            contexto_datos = ""
            if archivo:
                df = pd.read_excel(archivo) if archivo.name.endswith('xlsx') else pd.read_csv(archivo)
                contexto_datos = f"\n[DATOS CARGADOS]:\n{df.head(20).to_string(index=False)}\n"

            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                # Instrucción de sistema
                config_sistema = f"Eres OmniAgent_Core, asistente de Paulina ({materias}). Tono: {estilo}. Usa búsqueda web si es necesario."
                
                # Llamada al modelo Gemini 3 Flash
                response = client.models.generate_content(
                    model="gemini-3-flash-preview", 
                    contents=config_sistema + contexto_datos + prompt
                )
                
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})

    except Exception as e:
        st.error(f"Error: {e}. Asegúrate de haber actualizado el archivo requirements.txt primero.")
else:
    st.warning("Introduce tu clave para activar Gemini 3.")
