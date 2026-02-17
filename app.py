import streamlit as st
import google.generativeai as genai

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Asistente de Paulina", page_icon="🎓")

# --- BARRA LATERAL: CONFIGURACIÓN ---
with st.sidebar:
    st.title("⚙️ Configuración")
    api_key = st.text_input("Introduce la API Key de Gemini:", type="password")
    
    st.divider()
    st.markdown("""
    **Instrucciones para la Maestra:**
    Como soy tu nuevo asistente, cuéntame sobre tus materias, 
    el tono que prefieres para tus clases y cómo quieres que 
    organice tus bases de datos.
    """)

# --- INICIALIZACIÓN DE GEMINI ---
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

    # --- MEMORIA DE LA CONVERSACIÓN ---
    if "messages" not in st.session_state:
        st.session_state.messages = []
        # Mensaje inicial de "Bienvenida como empleado"
        bienvenida = "Hola Paulina, soy tu nuevo asistente académico. Estoy listo para integrarme a tu equipo. Cuéntame, ¿en qué materias te voy a ayudar y cómo te gusta que trabaje?"
        st.session_state.messages.append({"role": "assistant", "content": bienvenida})

    # Mostrar historial
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # --- LÓGICA DE INTERACCIÓN ---
    if prompt := st.chat_input("Escribe aquí..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            # Contexto de "Nuevo Empleado"
            sistema = "Eres el asistente personal de Paulina, una maestra universitaria. Tu tono es profesional, servicial y proactivo, como un empleado brillante en su primer día. Tu meta es aprender sus procesos para automatizar sus planeaciones, presentaciones y bases de datos."
            
            response = model.generate_content([sistema] + [m["content"] for m in st.session_state.messages])
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
else:
    st.warning("Por favor, introduce tu API Key en la barra lateral para comenzar.")
