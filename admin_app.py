import streamlit as st
from supabase import create_client
from datetime import datetime

# --- CONFIGURACIÓN DE CREDENCIALES DE SUPABASE ---
# Reemplaza esto con los datos de tu proyecto en Supabase (Project Settings -> API)
SUPABASE_URL = "https://drhoxkbmqwdgrnnuuhlq.supabase.co"
SUPABASE_KEY = "sb_publishable_n1yL2gCd5B6OjPZDf_6wGA_dG1iLcN7"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Configuración de la página web
st.set_page_config(page_title="Control Misiones Ezra", page_icon="🎮", layout="centered")

st.title("🎮 Panel de Misiones Diarias")
st.write(f"**Fecha actual:** {datetime.now().strftime('%Y-%m-%d')}")

# Obtener fecha de hoy
fecha_hoy = datetime.now().strftime('%Y-%m-%d')

# Consultar si ya existe un registro para hoy en Supabase
res = supabase.table("pc_control").select("*").eq("fecha", fecha_hoy).execute()

if not res.data:
    # Si no existe, lo creamos con 0 tiempo por defecto
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

st.markdown("---")
st.subheader("📋 Validación de Misiones del Día")

# Casillas de verificación interactivas
c1 = st.checkbox("🧹 Cuarto Limpio", value=data.get("cuarto_limpio", False))
f1 = st.file_uploader("Sube la foto del cuarto", type=["jpg", "png", "jpeg"], key="u1")

c2 = st.checkbox("📚 Tarea Hecha", value=data.get("tarea_hecha", False))
f2 = st.file_uploader("Sube la foto de la tarea", type=["jpg", "png", "jpeg"], key="u2")

c3 = st.checkbox("🛋️ Sala Recogida", value=data.get("sala_recogida", False))
f3 = st.file_uploader("Sube la foto de la sala", type=["jpg", "png", "jpeg"], key="u3")

st.markdown("---")
nota = st.text_area("📝 Nota de comportamiento del día:", value=data.get("nota_conducta", ""))

# Determinar horas según el día de la semana (Lunes a Jueves = 3 hrs, Vie a Dom = 5 hrs)
es_fin_de_semana = datetime.now().weekday() in [4, 5, 6] # 4=Viernes, 5=Sábado, 6=Domingo
horas_asignar = 5 if es_fin_de_semana else 3
segundos_totales = horas_asignar * 3600

st.info(f"💡 Al aprobar las misiones hoy, se asignarán automáticamente **{horas_asignar} Horas** de juego en la PC.")

col1, col2 = st.columns(2)

with col1:
    if st.button("🚀 Aprobar Misiones y Otorgar Tiempo", type="primary", use_container_width=True):
        if c1 and c2 and c3:
            # Actualizamos Supabase liberando el tiempo
            supabase.table("pc_control").update({
                "misiones_completadas": True,
                "cuarto_limpio": True,
                "tarea_hecha": True,
                "sala_recogida": True,
                "nota_conducta": nota,
                "tiempo_restante_segundos": segundos_totales,
                "bloqueado_manualmente": False
            }).eq("fecha", fecha_hoy).execute()
            
            st.success(f"¡Misiones aprobadas con éxito! Se liberaron {horas_asignar} horas en la PC de Ezra.")
            st.rerun()
        else:
            st.warning("⚠️ Debes marcar y verificar las 3 misiones como completadas para autorizar el tiempo.")

with col2:
    if st.button("🔒 Bloquear PC Inmediatamente", type="secondary", use_container_width=True):
        supabase.table("pc_control").update({
            "bloqueado_manualmente": True,
            "misiones_completadas": False
        }).eq("fecha", fecha_hoy).execute()
        
        st.error("🚨 ¡Se ha enviado la orden de bloqueo a la PC!")
        st.rerun()
