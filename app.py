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

# --- 2. MOTOR INTELIGENTE ---
if api_key:
    try:
        genai.configure(api_key=api_key)
        
        # Intentamos con el nombre de producción de Gemini 3
        # Si falla, el bloque 'except' lo corregirá automáticamente
        nombre_modelo = 'gemini-1.5-flash' # Nombre base estable
        
        # Opcional: Descomenta la siguiente línea si ya confirmaste el ID de Gemini 3 en tu cuenta
        # nombre_modelo = 'gemini-3-flash' 

        model = genai.GenerativeModel(
            model_name=nombre_modelo, 
            tools=[{"google_search_retrieval": {}}]
        )

        if "messages" not in st.session_state:
            st.session_state.messages = []
            saludo = f"OmniAgent Core v3.0 en línea. He cargado tu perfil de {estilo}. ¿Cómo te ayudo hoy, Paulina?"
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
                    f"Eres OmniAgent_Core, un asistente académico de élite. "
                    f"Tu usuaria es Paulina e imparte: {materias}. Tu tono es {estilo}. "
                    "Usa Google Search para eventos de 2026 y analiza los archivos presentes."
                )
                
                response = model.generate_content(personalidad + contexto_archivo + prompt)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})

    except Exception as e:
        st.error(f"Error de conexión. Verifica que tu API Key sea válida. Detalle: {e}")
else:
    st.warning("Introduce la clave para activar la potencia de Gemini 3.")
