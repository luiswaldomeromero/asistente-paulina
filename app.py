import streamlit as st
from google import genai
import pandas as pd
from pptx import Presentation
from io import BytesIO

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="OmniAgent Core v3.7", page_icon="🎓", layout="wide")

with st.sidebar:
    st.title("🛡️ Sistema Gemini 3")
    api_key = st.text_input("API Key de Google:", type="password")
    st.divider()
    nivel = st.selectbox("Nivel Educativo", ["Primaria", "Secundaria", "Universidad"])
    st.info("Ahora puedes descargar tus presentaciones en PowerPoint.")

# --- 2. FUNCIÓN PARA CREAR POWERPOINT ---
def crear_pptx(texto_presentacion):
    prs = Presentation()
    lineas = texto_presentacion.split('\n')
    for linea in lineas:
        if linea.startswith('Diapositiva') or linea.startswith('Slide'):
            slide = prs.slides.add_slide(prs.slide_layouts[1])
            title = slide.shapes.title
            title.text = linea
        elif linea.strip():
            # Añadir contenido simple
            try:
                tf = slide.placeholders[1].text_frame
                tf.text += f"\n{linea}"
            except: pass
    
    binary_output = BytesIO()
    prs.save(binary_output)
    return binary_output.getvalue()

# --- 3. MOTOR DEL AGENTE ---
if api_key:
    try:
        client = genai.Client(api_key=api_key)
        
        if prompt := st.chat_input("Ej: Crea una presentación sobre la fotosíntesis"):
            st.chat_message("user").markdown(prompt)
            
            with st.chat_message("assistant"):
                # Instrucción para manejar la saturación
                sistema = f"Eres OmniAgent_Core nivel {nivel}. Si el tema es una presentación, estructúrala por 'Diapositiva X: Título y Contenido'."
                
                try:
                    response = client.models.generate_content(model="gemini-3-flash-preview", contents=sistema + prompt)
                    st.markdown(response.text)
                    
                    # Si detecta que es una presentación, ofrece la descarga
                    if "Diapositiva" in response.text or "Presentación" in prompt:
                        pptx_data = crear_pptx(response.text)
                        st.download_button(
                            label="📥 Descargar PowerPoint",
                            data=pptx_data,
                            file_name="presentacion_omniagent.pptx",
                            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
                        )
                except Exception as e:
                    st.error("⚠️ Los servidores de Google están saturados. Intenta de nuevo en 30 segundos.")

    except Exception as e:
        st.error(f"Error de API: {e}")
else:
    st.warning("Introduce tu API Key.")
