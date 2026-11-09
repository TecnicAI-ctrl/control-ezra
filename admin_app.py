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

st.set_page_config(page_title="Control de Misiones PC", page_icon="🎮", layout="centered")

st.title("🎮 Sistema de Misiones")
fecha_hoy = datetime.now().strftime('%Y-%m-%d')
st.write(f"**Fecha actual:** {fecha_hoy}")

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

    f1 = st.file_uploader(f"Foto para: {m1_nombre}", type=["jpg", "png", "jpeg"], key="u1")
    tiene_foto_1 = (f1 is not None)
    if f1:
        st.image(f1, caption="Vista previa", width=180)

    c1 = st.checkbox(f"Completado: {m1_nombre}", value=False, disabled=not tiene_foto_1)
    if not tiene_foto_1:
        st.caption("🔒 Sube una foto arriba para habilitar esta casilla.")

    st.markdown("---")

    f2 = st.file_uploader(f"Foto para: {m2_nombre}", type=["jpg", "png", "jpeg"], key="u2")
    tiene_foto_2 = (f2 is not None)
    if f2:
        st.image(f2, caption="Vista previa", width=180)

    c2 = st.checkbox(f"Completado: {m2_nombre}", value=False, disabled=not tiene_foto_2)
    if not tiene_foto_2:
        st.caption("🔒 Sube una foto arriba para habilitar esta casilla.")

    st.markdown("---")

    f3 = st.file_uploader(f"Foto para: {m3_nombre}", type=["jpg", "png", "jpeg"], key="u3")
    tiene_foto_3 = (f3 is not None)
    if f3:
        st.image(f3, caption="Vista previa", width=180)

    c3 = st.checkbox(f"Completado: {m3_nombre}", value=False, disabled=not tiene_foto_3)
    if not tiene_foto_3:
        st.caption("🔒 Sube una foto arriba para habilitar esta casilla.")

    st.markdown("---")

    nota_enviada = st.text_area("📝 Escribe una nota u observaciones del día (Obligatorio):", value="", placeholder="Ej. Me porté bien, terminé mis deberes...")

    if st.button("📤 Enviar Evidencias", type="primary", use_container_width=True):
        if not nota_enviada.strip():
            st.error("⚠️ El campo de notas no puede estar vacío. Debes escribir un comentario o resumen para poder enviar.")
        elif not (f1 and f2 and f3):
            st.error("⚠️ Debes subir las fotografías de todas las misiones para poder enviarlas.")
        else:
            update_dict = {
                "cuarto_limpio": c1,
                "tarea_hecha": c2,
                "sala_recogida": c3,
                "nota_conducta": nota_enviada,
                "img1_data": encode_image(f1),
                "img2_data": encode_image(f2),
                "img3_data": encode_image(f3)
            }

            supabase.table("pc_control").update(update_dict).eq("fecha", fecha_hoy).execute()
            
            link_sistema = "https://control-ezra-r45z6xjjqbekjhk4pwfrw7.streamlit.app/"
            asunto_correo = f"🚨 [URGENTE] Misiones Parentales Completadas - {fecha_hoy}"
            cuerpo_correo = f"""¡Hola, Papá! Se han enviado nuevas evidencias de misiones para revisión.

Fecha: {fecha_hoy}

Estado de las misiones:
- {m1_nombre}: {'✅ Completada' if c1 else '❌ Pendiente'}
- {m2_nombre}: {'✅ Completada' if c2 else '❌ Pendiente'}
- {m3_nombre}: {'✅ Completada' if c3 else '❌ Pendiente'}

Nota del día:
"{nota_enviada}"

Entra inmediatamente al sistema para revisar las fotografías y autorizar el tiempo de juego:
{link_sistema}
"""
            enviar_correo_urgente(asunto_correo, cuerpo_correo)

            st.success("¡Evidencias enviadas con éxito y notificación urgente enviada a tu correo!")
            st.rerun()

# ==========================================
# PESTAÑA 2: CONTROL PARENTAL E HISTORIAL (PRIVADO)
# ==========================================
with pestana_admin:
    st.subheader("🔐 Panel de Administración y Seguridad")
    password_ingresada = st.text_input("Contraseña de Administración:", type="password", key="pass_admin")
    es_admin = (password_ingresada == "0310")

    if not es_admin:
        st.warning("⚠️ Introduce tu contraseña de administrador para desbloquear los controles, misiones y el historial privado.")
    else:
        st.success("✅ Acceso de Administrador Autorizado")
        
        st.markdown("---")
        st.write("### ⚙️ Personalizar Misiones para Hoy")
        st.caption("Cambia el nombre de las tareas de hoy si deseas asignarle actividades diferentes:")
        
        n_m1 = st.text_input("Misión 1:", value=m1_nombre)
        n_m2 = st.text_input("Misión 2:", value=m2_nombre)
        n_m3 = st.text_input("Misión 3:", value=m3_nombre)

        if st.button("💾 Guardar Nuevas Misiones del Día"):
            supabase.table("pc_control").update({
                "mision1_nombre": n_m1,
                "mision2_nombre": n_m2,
                "mision3_nombre": n_m3
            }).eq("fecha", fecha_hoy).execute()
            st.success("¡Misiones del día actualizadas correctamente!")
            st.rerun()

        st.markdown("---")
        st.write("### 👁️ Evidencias Recibidas de Hoy")
        
        st.write(f"- **{m1_nombre}:** {'Sí 🟢' if data.get('cuarto_limpio') else 'No 🔴'}")
        st.write(f"- **{m2_nombre}:** {'Sí 🟢' if data.get('tarea_hecha') else 'No 🔴'}")
        st.write(f"- **{m3_nombre}:** {'Sí 🟢' if data.get('sala_recogida') else 'No 🔴'}")
        st.info(f"**Nota recibida:** {data.get('nota_conducta', 'Sin nota')}")

        st.write("#### 📸 Fotografías Guardadas de Hoy:")
        col_img1, col_img2, col_img3 = st.columns(3)
        
        img1_b64 = decode_image(data.get("img1_data"))
        img2_b64 = decode_image(data.get("img2_data"))
        img3_b64 = decode_image(data.get("img3_data"))

        with col_img1:
            if img1_b64:
                st.image(img1_b64, caption=m1_nombre, use_container_width=True)
            else:
                st.caption("Sin foto")
        with col_img2:
            if img2_b64:
                st.image(img2_b64, caption=m2_nombre, use_container_width=True)
            else:
                st.caption("Sin foto")
        with col_img3:
            if img3_b64:
                st.image(img3_b64, caption=m3_nombre, use_container_width=True)
            else:
                st.caption("Sin foto")

        es_fin_de_semana = datetime.now().weekday() in [4, 5, 6]
        horas_asignar = 5 if es_fin_de_semana else 3
        segundos_totales = horas_asignar * 3600

        st.markdown("---")
        col1, col2 = st.columns(2)

        with col1:
            if st.button("🚀 Aprobar y Otorgar Tiempo", type="primary", use_container_width=True):
                supabase.table("pc_control").update({
                    "misiones_completadas": True,
                    "tiempo_restante_segundos": segundos_totales,
                    "bloqueado_manualmente": False
                }).eq("fecha", fecha_hoy).execute()
                st.success(f"¡Tiempo otorgado! Se liberaron {horas_asignar} horas.")
                st.rerun()

        with col2:
            if st.button("🔒 Bloquear PC Inmediatamente", type="secondary", use_container_width=True):
                supabase.table("pc_control").update({
                    "bloqueado_manualmente": True,
                    "misiones_completadas": False
                }).eq("fecha", fecha_hoy).execute()
                st.error("🚨 ¡PC Bloqueada!")
                st.rerun()

        st.markdown("---")
        st.subheader("📜 Historial Privado de Registros Pasados")
        st.write("Consulta el registro histórico acumulado (Área protegida):")

        all_records = supabase.table("pc_control").select("*").order("fecha", desc=True).execute()
        
        if all_records.data:
            fechas_disponibles = [r["fecha"] for r in all_records.data]
            fecha_seleccionada = st.selectbox("Selecciona una fecha a consultar:", fechas_disponibles, key="sel_historial")
            
            hist_data = next((r for r in all_records.data if r["fecha"] == fecha_seleccionada), None)
            
            if hist_data:
                st.markdown(f"#### 📅 Registro del {hist_data['fecha']}")
                st.write(f"- **Misión 1 ({hist_data.get('mision1_nombre', 'Misión 1')}):** {'Cumplida 🟢' if hist_data.get('cuarto_limpio') else 'No realizada 🔴'}")
                st.write(f"- **Misión 2 ({hist_data.get('mision2_nombre', 'Misión 2')}):** {'Cumplida 🟢' if hist_data.get('tarea_hecha') else 'No realizada 🔴'}")
                st.write(f"- **Misión 3 ({hist_data.get('mision3_nombre', 'Misión 3')}):** {'Cumplida 🟢' if hist_data.get('sala_recogida') else 'No realizada 🔴'}")
                st.write(f"- **Tiempo Otorgado:** {'Sí 🎮' if hist_data.get('misiones_completadas') else 'No / Bloqueado 🔒'}")
                st.info(f"**Nota del día:** {hist_data.get('nota_conducta', 'Sin registro')}")

                st.write("#### 📸 Evidencias fotográficas del día:")
                h_col1, h_col2, h_col3 = st.columns(3)
                
                h_img1 = decode_image(hist_data.get("img1_data"))
                h_img2 = decode_image(hist_data.get("img2_data"))
                h_img3 = decode_image(hist_data.get("img3_data"))

                with h_col1:
                    if h_img1:
                        st.image(h_img1, caption="Misión 1", use_container_width=True)
                    else:
                        st.caption("Sin foto")
                with h_col2:
                    if h_img2:
                        st.image(h_img2, caption="Misión 2", use_container_width=True)
                    else:
                        st.caption("Sin foto")
                with h_col3:
                    if h_img3:
                        st.image(h_img3, caption="Misión 3", use_container_width=True)
                    else:
                        st.caption("Sin foto")
