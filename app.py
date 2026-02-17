import streamlit as st
from openai import OpenAI
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from pptx import Presentation
from io import BytesIO

# --- 1. CONFIGURACIÓN DE LA INTERFAZ ---
st.set_page_config(page_title="OmniAgent Core v4.1 (OpenAI Edition)", page_icon="🤖", layout="wide")

with st.sidebar:
    st.title("🚀 Sistema OmniAgent Pro")
    # Ahora pedimos la clave de OpenAI
    api_key = st.text_input("OpenAI API Key:", type="password")
    
    st.divider()
    st.markdown("### 📧 Módulo de Ejecución")
    email_user = st.text_input("Tu Gmail:")
    email_pass = st.text_input("Contraseña de Aplicación (16 letras):", type="password")
    
    st.divider()
    st.markdown("### 👤 Perfil del Agente")
    nivel = st.selectbox(
        "Nivel Educativo / Nicho", 
        ["Primaria", "Secundaria", "Preparatoria", "Universidad", "Legal", "RRHH"]
    )
    materias = st.text_area("Materias o contexto:", placeholder="Ej: Psicología, Historia...")
    
    st.divider()
    archivo = st.file_uploader("Cargar Material (Excel/CSV/PDF)", type=['csv', 'xlsx', 'pdf', 'txt'])

# --- 2. FUNCIONES DE HERRAMIENTAS ---

def enviar_email(destinatario, asunto, cuerpo):
    """Envía correos electrónicos automatizados"""
    try:
        msg = MIMEText(cuerpo)
        msg['Subject'] = asunto
        msg['From'] = email_user
        msg['To'] = destinatario
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(email_user, email_pass)
            server.send_message(msg)
        return True
    except Exception as e:
        st.error(f"Error de envío: {e}")
        return False

def crear_pptx(contenido):
    """Genera un archivo PowerPoint real"""
    prs = Presentation()
    lineas = contenido.split('\n')
    current_slide = None
    for linea in lineas:
        if "Diapositiva" in linea or "Slide" in linea:
            current_slide = prs.slides.add_slide(prs.slide_layouts[1])
            current_slide.shapes.title.text = linea
        elif linea.strip() and current_slide:
            try:
                p = current_slide.placeholders[1].text_frame.add_paragraph()
                p.text = linea
            except: pass
    buf = BytesIO()
    prs.save(buf)
    return buf.getvalue()

# --- 3. LÓGICA DEL AGENTE CON OPENAI ---
if api_key:
    try:
        # Inicializamos el cliente de OpenAI
        client = OpenAI(api_key=api_key)
        
        if "messages" not in st.session_state:
            st.session_state.messages = [
                {"role": "assistant", "content": f"OmniAgent v4.1 (OpenAI) activo para **{nivel}**. ¿En qué trabajamos hoy?"}
            ]

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("Escribe tu instrucción aquí..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                sistema = (
                    f"Eres OmniAgent_Core, un asistente de élite nivel {nivel}. "
                    f"Contexto: {materias}. "
                    "Si generas una presentación, usa siempre el formato 'Diapositiva X: Título'."
                )
                
                # Usamos GPT-4o-mini que es el equivalente al 'Nano' por velocidad y costo
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": sistema},
                        {"role": "user", "content": prompt}
                    ]
                )
                
                texto_respuesta = response.choices[0].message.content
                st.markdown(texto_respuesta)
                st.session_state.messages.append({"role": "assistant", "content": texto_respuesta})

                # --- ACCIONES ---
                col1, col2 = st.columns(2)
                
                if "@" in prompt and email_user and email_pass:
                    dest = [w for w in prompt.split() if "@" in w][0]
                    if col1.button(f"📧 Enviar a {dest}"):
                        if enviar_email(dest, f"Reporte OmniAgent - {nivel}", texto_respuesta):
                            st.success("✅ Enviado.")
                
                if "diapositiva" in texto_respuesta.lower() or "presentación" in prompt.lower():
                    pptx_data = crear_pptx(texto_respuesta)
                    col2.download_button("📥 Descargar PowerPoint", data=pptx_data, file_name="presentacion.pptx")

    except Exception as e:
        st.error(f"Error de OpenAI: {e}")
else:
    st.warning("⚠️ Introduce tu OpenAI API Key.")
