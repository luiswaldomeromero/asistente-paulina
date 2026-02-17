import streamlit as st
from openai import OpenAI
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from pptx import Presentation
from io import BytesIO
import re

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="OmniAgent Pro - OpenAI", page_icon="🚀", layout="wide")

with st.sidebar:
    st.title("🚀 OmniAgent Pro")
    api_key = st.text_input("OpenAI API Key:", type="password")
    
    st.divider()
    st.markdown("### 📧 Módulo de Ejecución")
    email_user = st.text_input("Tu Gmail:", value="luisfloresrios666@gmail.com")
    # Pega aquí tus 16 letras de nuevo
    email_pass = st.text_input("Contraseña de Aplicación:", type="password")
    
    st.divider()
    nivel = st.selectbox("Nivel Educativo", ["Primaria", "Secundaria", "Universidad", "Empresarial"])
    archivo = st.file_uploader("Cargar Material", type=['csv', 'xlsx', 'pdf', 'txt'])

# --- 2. MOTOR DE CORREO ---
def enviar_email(destinatario, asunto, cuerpo):
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
        st.error(f"Error técnico: {e}")
        return False

# --- 3. LÓGICA DEL AGENTE ---
if api_key:
    client = OpenAI(api_key=api_key)
    
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": f"OmniAgent v4.2 listo. Soy tu operario para nivel {nivel}. ¿A quién le enviamos un correo o qué presentación hacemos?"}]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ej: Redacta un examen y envíalo a ventas@ejemplo.com"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            # INSTRUCCIÓN REFORZADA: Le prohibimos decir que no puede
            sistema = (
                f"Eres un Agente Operativo nivel {nivel}. TIENES la capacidad de enviar correos y crear archivos. "
                "Tu respuesta será el CONTENIDO del correo o la presentación. "
                "Actúa como un asistente ejecutivo eficiente."
            )
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "system", "content": sistema}, {"role": "user", "content": prompt}]
            )
            
            respuesta = response.choices[0].message.content
            st.markdown(respuesta)
            st.session_state.messages.append({"role": "assistant", "content": respuesta})

            # BUSCADOR AUTOMÁTICO DE CORREOS EN EL TEXTO
            emails_encontrados = re.findall(r'[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+', prompt.lower())
            
            if emails_encontrados and email_pass:
                dest = emails_encontrados[0]
                if st.button(f"📧 Confirmar envío a {dest}"):
                    with st.spinner("Enviando..."):
                        if enviar_email(dest, f"Envío OmniAgent - {nivel}", respuesta):
                            st.success(f"✅ ¡Correo enviado a {dest}!")
            elif "@" in prompt and not email_pass:
                st.warning("Falta tu 'Contraseña de Aplicación' en la izquierda para enviar.")

else:
    st.warning("⚠️ Introduce tu OpenAI API Key para activar el sistema.")
