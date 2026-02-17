import streamlit as st
import google.generativeai as genai
import pandas as pd

st.set_page_config(page_title="OmniAgent Core Pro", page_icon="🚀")

with st.sidebar:
    st.title("⚙️ Panel de Control")
    api_key = st.text_input("Introduce la API Key:", type="password")
    st.divider()
    # NUEVA FUNCIÓN: Cargador de archivos
    archivo_subido = st.file_uploader("Subir lista de alumnos o profesionistas (Excel/CSV)", type=['csv', 'xlsx'])

if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "¡Hola! Soy tu asistente Pro. Ahora puedo leer tus archivos de Excel. ¿Qué quieres que analicemos hoy?"}]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ej: Analiza este Excel y dime quiénes están reprobados"):
        # Si hay un archivo, le pasamos los datos al agente
        contexto_archivo = ""
        if archivo_subido:
            df = pd.read_excel(archivo_subido) if archivo_subido.name.endswith('xlsx') else pd.read_csv(archivo_subido)
            contexto_archivo = f"\n\nAquí tienes los datos del archivo que subí:\n{df.to_string(index=False)}"
            st.info("📊 Archivo cargado correctamente")

        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            sistema = "Eres OmniAgent_Core, un experto en gestión académica. Si el usuario sube datos, analízalos con precisión, crea tablas resumen y responde proactivamente."
            # El agente recibe el texto del usuario + los datos del Excel
            response = model.generate_content(sistema + contexto_archivo + prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
else:
    st.warning("Configura la API Key para activar las funciones Pro.")
