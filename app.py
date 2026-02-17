import streamlit as st
import google.generativeai as genai
import pandas as pd

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="OmniAgent Core v3.0", page_icon="🧠", layout="wide")

with st.sidebar:
    st.title("🛡️ Sistema Gemini 3")
    api_key = st.text_input("API Key de Google:", type="password")
    st.divider()
    st.markdown("### 📝 Perfil de la Maestra")
    # Memoria de largo plazo manual (se guarda mientras la pestaña esté abierta)
    materias = st.text_area("¿Qué materias impartes?", placeholder="Ej: Psicología, Historia...")
    estilo = st.selectbox("Tono del Asistente", ["Muy Formal", "Colega/Amigable", "Creativo", "Ejecutivo"])
    
    st.divider()
    archivo = st.file_uploader("Subir base de datos (Excel/CSV)", type=['csv', 'xlsx'])

# --- 2. MOTOR GEMINI 3 FLASH ---
if api_key:
    try:
        genai.configure(api_key=api_key)
        # Actualizado al modelo de última generación
        model = genai.GenerativeModel(
            model_name='gemini-3-flash',
            tools=[{"google_search_retrieval": {}}]
        )

        if "messages" not in st.session_state:
            st.session_state.messages = []
            saludo = f"OmniAgent Core v3.0 en línea. Saludos, Paulina. He cargado tu perfil de {estilo}. ¿En qué avanzamos hoy?"
            st.session_state.messages.append({"role": "assistant", "content": saludo})

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # --- 3. PROCESAMIENTO ---
        if prompt := st.chat_input("Escribe tu instrucción aquí..."):
            
            contexto_archivo = ""
            if archivo:
                df = pd.read_excel(archivo) if archivo.name.endswith('xlsx') else pd.read_csv(archivo)
                contexto_archivo = f"\n[DATOS CARGADOS]:\n{df.head(30).to_string(index=False)}\n"

            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                # Instrucciones de personalidad basadas en el perfil del Sidebar
                personalidad = (
                    f"Eres OmniAgent_Core, un asistente de élite basado en Gemini 3. "
                    f"Paulina imparte: {materias}. Tu tono debe ser {estilo}. "
                    "Usa Google Search para datos del 2026 y analiza los archivos si están presentes."
                )
                
                response = model.generate_content(personalidad + contexto_archivo + prompt)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})

    except Exception as e:
        st.error(f"Error técnico: {e}. Asegúrate de que tu cuenta tenga acceso a Gemini 3.")
else:
    st.warning("Introduce la clave para activar la potencia de Gemini 3.")
