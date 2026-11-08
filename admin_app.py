import streamlit as st
import base64
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from supabase import create_client
from datetime import datetime

# --- CONFIGURACIÓN DE CREDENCIALES DE SUPABASE ---
SUPABASE_URL = "https://drhoxkbmqwdgrnnuuhlq.supabase.co"
SUPABASE_KEY = "sb_publishable_n1yL2gCd5B6OjPZDf_6wGA_dG1iLcN7"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- CONFIGURACIÓN DE CORREO URGENTE (GMAIL) ---
CORREO_REMITENTE = "bojaispuro@gmail.com"
CONTRASENA_APLICACION = "jpma rfff vnkv tilv"
CORREO_DESTINO = "aispuro.bojorquez.chris@gmail.com"

def enviar_correo_urgente(asunto, cuerpo):
    """Envía un correo electrónico de alerta urgente vía SMTP de Gmail"""
    try:
        msg = MIMEMultipart()
        msg['From'] = CORREO_REMITENTE
        msg['To'] = CORREO_DESTINO
        msg['Subject'] = asunto
        
        msg.attach(MIMEText(cuerpo, 'plain'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(CORREO_REMITENTE, CONTRASENA_APLICACION)
        server.sendmail(CORREO_REMITENTE, CORREO_DESTINO, msg.as_string())
        server.quit()
    except Exception as e:
        print(f"Error al enviar correo: {e}")

# Funciones de utilidad para convertir fotos a Base64
def encode_image(uploaded_file):
    if uploaded_file is not None:
        return base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
    return ""

def decode_image(b64_string):
    if b64_string:
        try:
            return base64.b64decode(b64_string)
        except Exception:
            return None
    return None

# Configuración de la página web
st.set_page_config(page_title="Control de Misiones PC", page_icon="🎮", layout="centered")

st.title("🎮 Sistema de Misiones")
fecha_hoy = datetime.now().strftime('%Y-%m-%d')
st.write(f"**Fecha actual:** {fecha_hoy}")

# Consultar si existe el registro de hoy
res = supabase.table("pc_control").select("*").eq("fecha", fecha_hoy).execute()

if not res.data:
    supabase.table("pc_control").insert({
        "fecha": fecha_hoy, 
        "tiempo_restante_segundos": 0,
        "mision1_nombre": "🧹 Cuarto Limpio",
        "mision2_nombre": "📚 Tarea Hecha",
        "mision3_nombre": "🛋️ Sala Recogida"
    }).execute()
    res = supabase.table("pc_control").select("*").eq("fecha", fecha_hoy).execute()

data = res.data[0]

# --- CREACIÓN DE LAS 2 PESTAÑAS (UNA PÚBLICA Y UNA PRIVADA) ---
pestana_misiones, pestana_admin = st.tabs([
    "🎯 Entrega de Misiones", 
    "🔐 Control Parental y Historial"
])

# ==========================================
# PESTAÑA 1: ENTREGA DE MISIONES (PARA EL NIÑO)
# ==========================================
with pestana_misiones:
    st.subheader("📋 Misiones asignadas para hoy")
    st.write("Sube la foto de cada misión para poder marcarla como completada:")

    m1_nombre = data.get("mision1_nombre") or "🧹 Cuarto Limpio"
    m2_nombre = data.get("mision2_nombre") or "📚 Tarea Hecha"
    m3_nombre = data.get("mision3_nombre") or "🛋️ Sala Recogida"

    # --- MISIÓN 1 ---
    f1 = st.file_uploader(f"Foto para: {m1_nombre}", type=["jpg", "png", "jpeg"], key="u1")
    tiene_foto_1 = (f1 is not None)
    if f1:
        st.image(f1, caption="Vista previa", width=180)

    c1 = st.checkbox(f"Completado: {m1_nombre}", value=False, disabled=not tiene_foto_1)
    if not tiene_foto_1:
        st.caption("🔒 Sube una foto arriba para habilitar esta casilla.")

    st.markdown("---")

    # --- MISIÓN 2 ---
    f2 = st.file_uploader(f"Foto para: {m2_nombre}", type=["jpg", "png", "jpeg"], key="u2")
    tiene_foto_2 = (f2 is not None)
    if f2:
        st.image(f2, caption="Vista previa", width=180)

    c2 = st.checkbox(f"Completado: {m2_nombre}", value=False, disabled=not tiene_foto_2)
    if not tiene_foto_2:
        st.caption("🔒 Sube una foto arriba para habilitar esta casilla.")

    st.markdown("---")

    # --- MISIÓN 3 ---
    f3 = st.file_uploader(f"Foto para: {m3_nombre}", type=["jpg", "png", "jpeg"], key="u3")
    tiene_foto_3 = (f3 is not None)
    if f3:
        st.image(
