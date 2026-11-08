import streamlit as st
from supabase import create_client
from datetime import datetime

# --- CONFIGURACIÓN DE CREDENCIALES DE SUPABASE ---
SUPABASE_URL = "https://drhoxkbmqwdgrnnuuhlq.supabase.co"
SUPABASE_KEY = "sb_publishable_n1yL2gCd5B6OjPZDf_6wGA_dG1iLcN7"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Configuración de la página web
st.set_page_config(page_title="Control Misiones Ezra", page_icon="🎮", layout="centered")

st.title("🎮 Sistema de Misiones - Ezra")
st.write(f"**Fecha actual:** {datetime.now().strftime('%Y-%m-%d')}")

# Obtener fecha de hoy
fecha_hoy = datetime.now().strftime('%Y-%m-%d')

# Consultar si ya existe un registro para hoy en Supabase
res = supabase.table("pc_control").select("*").eq("fecha", fecha_hoy).execute()

if not res.data:
    supabase.table("pc_control").insert({"fecha": fecha_hoy, "tiempo_restante_segundos": 0}).execute()
    data = {
        "misiones_completadas": False, 
        "tiempo_restante_segundos": 0, 
        "cuarto_limpio": False, 
        "tarea_hecha": False, 
        "sala_recogida": False, 
        "nota_conducta": ""
    }
else:
    data = res.data[0]

# --- CREACIÓN DE LAS DOS PESTAÑAS ---
pestana_misiones, pestana_admin = st.tabs(["🎯 Misiones (Ezra / Familiar)", "🔐 Control Parental (Papá)"])

# ==========================================
# PESTAÑA 1: MISIONES (LIBRE PARA SUBIR FOTOS)
# ==========================================
with pestana_misiones:
    st.subheader("📋 Entrega de Misiones Diarias")
    st.write("Sube las evidencias de tus responsabilidades para que papá pueda revisarlas.")

    c1 = st.checkbox("🧹 Cuarto Limpio", value=data.get("cuarto_limpio", False))
    f1 = st.file_uploader("Foto del cuarto", type=["jpg", "png", "jpeg"], key="u1")

    c2 = st.checkbox("📚 Tarea Hecha", value=data.get("tarea_hecha", False))
    f2 = st.file_uploader("Foto de la tarea", type=["jpg", "png", "jpeg"], key="u2")

    c3 = st.checkbox("🛋️ Sala Recogida", value=data.get("sala_recogida", False))
    f3 = st.file_uploader("Foto de la sala", type=["jpg", "png", "jpeg"], key="u3")

    nota_enviada = st.text_area("📝 Nota sobre cómo te portaste hoy:", value=data.get("nota_conducta", ""))

    if st.button("📤 Enviar Evidencias a Papá", type="primary", use_container_width=True):
        # Guardamos el progreso de las casillas y la nota en Supabase para que papá lo vea
        supabase.table("pc_control").update({
            "cuarto_limpio": c1,
            "tarea_hecha": c2,
            "sala_recogida": c3,
            "nota_conducta": nota_enviada
        }).eq("fecha", fecha_hoy).execute()
        
        st.success("¡Evidencias enviadas con éxito! Papá las revisará en su panel para autorizar el tiempo.")

# ==========================================
# PESTAÑA 2: CONTROL PARENTAL (EXCLUSIVO PAPÁ)
# ==========================================
with pestana_admin:
    st.subheader("🔐 Panel de Administración y Autorización")
    st.write("Área exclusiva para el papá. Introduce tu contraseña para desbloquear el control de tiempo.")

    password_ingresada = st.text_input("Contraseña de Papá:", type="password", key="pass_admin")
    es_admin = (password_ingresada == "0310") # <--- CAMBIA "1234" POR TU CONTRASEÑA SECRETA

    if not es_admin:
        st.warning("⚠️ Introduce tu contraseña de papá arriba para poder validar o bloquear la PC.")
    else:
        st.success("✅ Acceso de Administrador Autorizado.")
        
        st.markdown("---")
        st.write("### 👁️ Revisión del Estado Actual")
        st.write(f"- **Cuarto Limpio marcado:** {'Sí 🟢' if data.get('cuarto_limpio') else 'No 🔴'}")
        st.write(f"- **Tarea Hecha marcada:** {'Sí 🟢' if data.get('tarea_hecha') else 'No 🔴'}")
        st.write(f"- **Sala Recogida marcada:** {'Sí 🟢' if data.get('sala_recogida') else 'No 🔴'}")
        st.info(f"**Nota del niño:** {data.get('nota_conducta', 'Sin nota registrada')}")

        # Determinar horas según el día (Lun-Jue = 3 hrs, Vie-Dom = 5 hrs)
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
                st.success(f"¡Tiempo otorgado! Se liberaron {horas_asignar} horas en la PC.")
                st.rerun()

        with col2:
            if st.button("🔒 Bloquear PC Inmediatamente", type="secondary", use_container_width=True):
                supabase.table("pc_control").update({
                    "bloqueado_manualmente": True,
                    "misiones_completadas": False
                }).eq("fecha", fecha_hoy).execute()
                st.error("🚨 ¡PC Bloqueada por orden de papá!")
                st.rerun()
