import streamlit as st
from src.core.database import SessionLocal
from src.models.entities import Task, Activity, StrategicItem, Policy
from sqlalchemy.orm import joinedload
from datetime import datetime, timedelta

def show_alerts_view():
    st.markdown("<div class='corporate-header'>", unsafe_allow_html=True)
    st.title("🚨 Centro de Alertas y Tareas Críticas")
    st.write("Monitoreo preventivo de plazos institucionales")
    st.markdown("</div>", unsafe_allow_html=True)
    
    db = SessionLocal()
    try:
        now = datetime.now()
        prox_limite = now + timedelta(days=7)
        
        # Consultar todas las tareas no cumplidas con sus relaciones
        tasks = db.query(Task).options(
            joinedload(Task.activity).joinedload(Activity.strategic_item).joinedload(StrategicItem.policy)
        ).filter(Task.status != "Cumplida").all()
        
        if not tasks:
            st.success("✅ ¡Excelente! No hay tareas pendientes con retraso o próximas a vencer.")
            return

        vencidas = [t for t in tasks if t.end_date and t.end_date < now]
        proximas = [t for t in tasks if t.end_date and now <= t.end_date <= prox_limite]
        criticas = [t for t in tasks if t.weight >= 50 and t.status == "Pendiente"] # Ejemplo de lógica crítica

        col1, col2 = st.columns(2)
        with col1:
            st.error(f"🔴 Tareas Vencidas: {len(vencidas)}")
        with col2:
            st.warning(f"🟡 Próximas a Vencer (7 días): {len(proximas)}")

        # --- SECCIÓN VENCIDAS ---
        if vencidas:
            st.subheader("❌ Tareas Fuera de Plazo")
            for t in vencidas:
                with st.container(border=True):
                    render_alert_card(t, "vencida")

        # --- SECCIÓN PRÓXIMAS ---
        if proximas:
            st.subheader("⚠️ Tareas por Vencer")
            for t in proximas:
                with st.container(border=True):
                    render_alert_card(t, "proxima")

        # --- SECCIÓN CRÍTICAS ---
        if criticas:
            st.subheader("🔥 Tareas de Alto Impacto (Pendientes)")
            for t in criticas:
                if t not in vencidas and t not in proximas: # Evitar duplicados
                    with st.container(border=True):
                        render_alert_card(t, "critica")

    finally:
        db.close()

def render_alert_card(t, tipo):
    c1, c2, c3 = st.columns([3, 1.5, 1])
    
    with c1:
        st.markdown(f"**{t.name}**")
        st.caption(f"📍 {t.activity.strategic_item.policy.name} > {t.activity.strategic_item.name}")
        st.markdown(f"👤 Responsable: `{t.responsible_name or 'No asignado'}`")
    
    with c2:
        if t.end_date:
            dias_diff = (t.end_date - datetime.now()).days
            if dias_diff < 0:
                st.markdown(f"<span style='color:#ef4444; font-weight:bold;'>Retraso: {abs(dias_diff)} días</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"<span style='color:#f59e0b; font-weight:bold;'>Faltan: {dias_diff} días</span>", unsafe_allow_html=True)
            st.caption(f"Fin: {t.end_date.strftime('%d/%m/%Y')}")
    
    with c3:
        st.metric("Peso", f"{t.weight}%")
        st.caption(f"Estado: {t.status}")
