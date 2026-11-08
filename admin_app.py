import streamlit as st
from supabase import create_client
from datetime import datetime

# --- CONFIGURACIÓN DE CREDENCIALES DE SUPABASE ---
SUPABASE_URL = "https://drhoxkbmqwdgrnnuuhlq.supabase.co"
SUPABASE_KEY = "sb_publishable_n1yL2gCd5B6OjPZDf_6wGA_dG1iLcN7"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Configuración de la página web
st.set_page_config(page_title="Control de Misiones PC", page_icon="🎮", layout="centered")

st.title("🎮 Sistema de Misiones")
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

# --- CREACIÓN DE LAS DOS PESTAÑAS NEUTRALES ---
pestana_misiones, pestana_admin = st.tabs(["🎯 Entrega de Misiones", "🔐 Control Parental"])

# ==========================================
# PESTAÑA 1: ENTREGA DE MISIONES
# ==========================================
with pestana_misiones:
    st.subheader("📋 Entrega de Misiones Diarias")
    st.write("Sube las evidencias para solicitar la autorización de tiempo de juego.")

    c1 = st.checkbox("🧹 Cuarto Limpio", value=data.get("cuarto_limpio", False))
    f1 = st.file_uploader("Sube la foto del cuarto", type=["jpg", "png", "jpeg"], key="u1")
    if f1:
        st.image(f1, caption="Vista previa: Cuarto", width=180)

    c2 = st.checkbox("📚 Tarea Hecha", value=data.get("tarea_hecha", False))
    f2 = st.file_uploader("Sube la foto de la tarea", type=["jpg", "png", "jpeg"], key="u2")
    if f2:
        st.image(f2, caption="Vista previa: Tarea", width=180)

    c3 = st.checkbox("🛋️ Sala Recogida", value=data.get("sala_recogida", False))
    f3 = st.file_uploader("Sube la foto de la sala", type=["jpg", "png", "jpeg"], key="u3")
    if f3:
        st.image(f3, caption="Vista previa: Sala", width=180)

    nota_enviada = st.text_area("📝 Nota de comportamiento del día:", value=data.get("nota_conducta", ""))

    if st.button("📤 Enviar Evidencias", type="primary", use_container_width=True):
        # Guardar imágenes en session_state para previsualizar en el panel de control
        if f1: st.session_state["img_cuarto"] = f1.getvalue()
        if f2: st.session_state["img_tarea"] = f2.getvalue()
        if f3: st.session_state["img_sala"] = f3.getvalue()

        supabase.table("pc_control").update({
            "cuarto_limpio": c1,
            "tarea_hecha": c2,
            "sala_recogida": c3,
            "nota_conducta": nota_enviada
        }).eq("fecha", fecha_hoy).execute()
        
        st.success("¡Evidencias enviadas correctamente! Quedan pendientes de validación.")

# ==========================================
# PESTAÑA 2: CONTROL PARENTAL
# ==========================================
with pestana_admin:
    st.subheader("🔐 Panel de Administración y Autorización")
    st.write("Área exclusiva de administración. Introduce tu contraseña para validar las misiones.")

    password_ingresada = st.text_input("Contraseña de Administración:", type="password", key="pass_admin")
    es_admin = (password_ingresada == "1234") # <--- CAMBIA "1234" POR TU CLAVE PRIVADA

    if not es_admin:
        st.warning("⚠️ Introduce la contraseña de administración arriba para habilitar la autorización o el bloqueo.")
    else:
        st.success("✅ Acceso de Administrador Autorizado.")
        
        st.markdown("---")
        st.write("### 👁️ Revisión del Estado y Evidencias")
        st.write(f"- **Cuarto Limpio:** {'Sí 🟢' if data.get('cuarto_limpio') else 'No 🔴'}")
        st.write(f"- **Tarea Hecha:** {'Sí 🟢' if data.get('tarea_hecha') else 'No 🔴'}")
        st.write(f"- **Sala Recogida:** {'Sí 🟢' if data.get('sala_recogida') else 'No 🔴'}")
        st.info(f"**Nota recibida:** {data.get('nota_conducta', 'Sin nota registrada')}")

        st.write("#### 📸 Vistas previas de las fotos recibidas:")
        col_img1, col_img2, col_img3 = st.columns(3)
        
        with col_img1:
            if "img_cuarto" in st.session_state:
                st.image(st.session_state["img_cuarto"], caption="Cuarto", use_container_width=True)
            elif f1:
                st.image(f1, caption="Cuarto", use_container_width=True)
            else:
                st.caption("Sin foto de cuarto")

        with col_img2:
            if "img_tarea" in st.session_state:
                st.image(st.session_state["img_tarea"], caption="Tarea", use_container_width=True)
            elif f2:
                st.image(f2, caption="Tarea", use_container_width=True)
            else:
                st.caption("Sin foto de tarea")

        with col_img3:
            if "img_sala" in st.session_state:
                st.image(st.session_state["img_sala"], caption="Sala", use_container_width=True)
            elif f3:
                st.image(f3, caption="Sala", use_container_width=True)
            else:
                st.caption("Sin foto de sala")

        # Asignación de horas (3h Lunes a Jueves / 5h Viernes a Domingo)
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
                st.success(f"¡Tiempo autorizado! Se liberaron {horas_asignar} horas de uso.")
                st.rerun()

        with col2:
            if st.button("🔒 Bloquear PC Inmediatamente", type="secondary", use_container_width=True):
                supabase.table("pc_control").update({
                    "bloqueado_manualmente": True,
                    "misiones_completadas": False
                }).eq("fecha", fecha_hoy).execute()
                st.error("🚨 ¡Orden de bloqueo enviada a la PC!")
                st.rerun()
