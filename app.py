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
    materias = st.text_area("¿Qué materias impartes?", placeholder="Ej: Psicología, Historia...")
    estilo = st.selectbox("Tono del Asistente", ["Muy Formal", "Colega/Amigable", "Creativo", "Ejecutivo"])
    
    st.divider()
    archivo = st.file_uploader("Subir base de datos (Excel/CSV)", type=['csv', 'xlsx'])

# --- 2. MOTOR GEMINI 3 FLASH ---
if api_key:
    try:
        genai.configure(api_key=api_key)
        
        # MODELO ACTUALIZADO: Gemini 3 Flash es el core de este agente
        model = genai.GenerativeModel(
            model_name='gemini-3-flash-latest', 
            tools=[{"google_search_retrieval": {}}]
        )

        if "messages" not in st.session_state:
            st.session_state.messages = []
            saludo = f"OmniAgent Core v3.0 (Motor Gemini 3) en línea. He cargado tu perfil de {estilo}. ¿Cómo te ayudo hoy, Paulina?"
            st.session_state.messages.append({"role": "assistant", "content": saludo})

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # --- 3. PROCESAMIENTO ---
        if prompt := st.chat_input("Escribe tu instrucción aquí..."):
            
            contexto_archivo = ""
            if archivo:
                try:
                    df = pd.read_excel(archivo) if archivo.name.endswith('xlsx') else pd.read_csv(archivo)
                    contexto_archivo = f"\n[DATOS DEL ARCHIVO]:\n{df.head(50).to_string(index=False)}\n"
                except:
                    st.error("Error al leer el archivo.")

            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                personalidad = (
                    f"Eres OmniAgent_Core, un asistente de élite basado en Gemini 3. "
                    f"Tu usuaria es Paulina e imparte: {materias}. Tu tono es {estilo}. "
                    "Tienes acceso a Google Search y análisis de datos avanzado."
                )
                
                response = model.generate_content(personalidad + contexto_archivo + prompt)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})

    except Exception as e:
        st.error(f"Error: {e}. Intenta usar el nombre de modelo 'gemini-1.5-flash' si tu región aún no activa Gemini 3.")
else:
    st.warning("Introduce la clave para activar la potencia de Gemini 3.")
