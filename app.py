import streamlit as st
from openai import OpenAI
import smtplib
from email.mime.text import MIMEText
from pptx import Presentation
from io import BytesIO
import re

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="OmniAgent Pro", page_icon="🚀", layout="wide")

with st.sidebar:
    st.title("🚀 OmniAgent Pro")
    api_key = st.text_input("OpenAI API Key:", type="password")
    
    st.divider()
    st.markdown("### 📧 Módulo de Ejecución")
    email_user = st.text_input("Tu Gmail:", value="luisfloresrios666@gmail.com")
    email_pass = st.text_input("Contraseña de Aplicación:", type="password")
    
    st.divider()
    nivel = st.selectbox("Nivel Educativo", ["Primaria", "Secundaria", "Universidad", "Empresarial"])

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
        st.session_state.messages = [{"role": "assistant", "content": f"OmniAgent v4.2 listo para nivel {nivel}. ¿A qué correo enviamos la información hoy?"}]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Escribe aquí..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            # INSTRUCCIÓN MAESTRA: Forzamos al modelo a actuar como operario
            sistema = (
                f"Eres un Agente Operativo nivel {nivel}. Tu función es redactar contenido para ser enviado por email. "
                "JAMÁS digas que no puedes enviar correos; tú redactas el texto y el sistema se encarga del envío. "
                "Sé ejecutivo y eficiente."
            )
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "system", "content": sistema}, {"role": "user", "content": prompt}]
            )
            
            respuesta = response.choices[0].message.content
            st.markdown(respuesta)
            st.session_state.messages.append({"role": "assistant", "content": respuesta})

            # DETECTOR DE CORREO EN LA CONVERSACIÓN
            emails = re.findall(r'[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+', (prompt + " " + respuesta).lower())
            
            if emails and email_pass:
                dest = emails[0]
                # Este botón es la clave: aparece fuera del texto de la IA
                if st.button(f"📧 CLIC AQUÍ PARA ENVIAR A: {dest}"):
                    if enviar_email(dest, f"Asunto: Información {nivel}", respuesta):
                        st.success(f"✅ ¡Correo enviado exitosamente a {dest}!")
            elif "@" in prompt and not email_pass:
                st.warning("⚠️ Configura tu 'Contraseña de Aplicación' en la izquierda para habilitar el botón de envío.")
else:
    st.warning("⚠️ Introduce tu OpenAI API Key.")
