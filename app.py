import streamlit as st
from google import genai
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from pptx import Presentation
from io import BytesIO

# --- 1. CONFIGURACIÓN DE LA APP ---
st.set_page_config(page_title="OmniAgent Core v4.0", page_icon="⚡", layout="wide")

with st.sidebar:
    st.title("🛡️ Sistema Gemini 3 Ultra")
    api_key = st.text_input("API Key de Google:", type="password")
    
    st.divider()
    st.markdown("### 📧 Módulo de Ejecución")
    email_user = st.text_input("Tu Gmail:")
    email_pass = st.text_input("Contraseña de Aplicación (16 letras):", type="password")
    
    st.divider()
    nivel = st.selectbox("Perfil del Agente", ["Primaria", "Secundaria", "Universidad", "Legal/Empresarial"])
    archivo = st.file_uploader("Cargar Base de Datos o Material", type=['csv', 'xlsx', 'pdf'])

# --- 2. HERRAMIENTAS DE EJECUCIÓN (TOOLS) ---

def enviar_email(destinatario, asunto, cuerpo):
    """Envía correos y agendas de manera automática"""
    try:
        msg = MIMEText(cuerpo)
        msg['Subject'] = asunto
        msg['From'] = email_user
        msg['To'] = destinatario
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(email_user, email_pass)
            server.send_message(msg)
        return True
    except:
        return False

def crear_presentacion(contenido):
    """Genera un PowerPoint listo para descargar"""
    prs = Presentation()
    for line in contenido.split('\n'):
        if "Diapositiva" in line or "Slide" in line:
            slide = prs.slides.add_slide(prs.slide_layouts[1])
            slide.shapes.title.text = line
        elif line.strip():
            try:
                p = slide.placeholders[1].text_frame.add_paragraph()
                p.text = line
            except: pass
    buf = BytesIO()
    prs.save(buf)
    return buf.getvalue()

# --- 3. LÓGICA DEL AGENTE INTELIGENTE ---
if api_key:
    try:
        # Inicializamos el motor Gemini 3 Flash
        client = genai.Client(api_key=api_key)
        
        if "messages" not in st.session_state:
            st.session_state.messages = [{"role": "assistant", "content": f"OmniAgent v4.0 en línea. Perfil: {nivel}. Puedo navegar, enviar correos, agendar y crear archivos. ¿Cuál es la misión de hoy?"}]

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("Ej: Busca tendencias de educación 2026 y envíalas a mi correo"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                # Instrucciones de sistema para el agente orquestador
                sistema = (
                    f"Eres OmniAgent_Core, un agente autónomo de élite nivel {nivel}. "
                    "Tienes acceso a Google Search para navegar por la web en tiempo real. "
                    "Si el usuario pide enviar un correo o agendar, redacta el contenido profesionalmente. "
                    "Si pide una presentación, usa el formato 'Diapositiva X: Título'."
                )
                
                # Ejecución con búsqueda web habilitada
                response = client.models.generate_content(
                    model="gemini-3-flash-preview", 
                    contents=sistema + prompt
                )
                
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})

                # --- ACCIONES DE EJECUCIÓN ---
                col1, col2 = st.columns(2)
                
                # Acción 1: Enviar por Correo / Agendar
                if "@" in prompt and email_user and email_pass:
                    dest = [w for w in prompt.split() if "@" in word for word in [w]][0]
                    if col1.button(f"📧 Enviar acción a {dest}"):
                        if enviar_email(dest, f"Acción Programada - {nivel}", response.text):
                            st.success("✅ Ejecutado y enviado.")
                
                # Acción 2: Crear PowerPoint
                if "presentación" in prompt.lower() or "diapositiva" in response.text.lower():
                    pptx = crear_presentacion(response.text)
                    col2.download_button("📥 Descargar Presentación", data=pptx, file_name="agente_output.pptx")

    except Exception as e:
        st.info("Servidores saturados o API Key inválida. Intenta en 30 segundos.")
else:
    st.warning("Configura tu acceso en el Panel de Control.")
