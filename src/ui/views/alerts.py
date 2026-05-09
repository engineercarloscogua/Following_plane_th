import streamlit as st
from src.core.database import SessionLocal
from src.models.entities import Task, Activity, StrategicItem, Policy, Responsible
from sqlalchemy.orm import joinedload
from datetime import datetime, timedelta

def show_alerts_view():
    """
    Critical monitoring module for overdue and upcoming tasks.
    Provides categorical audit views to ensure institutional timeline compliance.
    """
    st.markdown("<div class='corporate-header'>", unsafe_allow_html=True)
    st.title("🚨 Centro de Alertas y Tareas Críticas")
    st.write("Monitoreo preventivo y auditoría de plazos institucionales")
    st.markdown("</div>", unsafe_allow_html=True)
    
    db = SessionLocal()
    try:
        now = datetime.now()
        prox_limite = now + timedelta(days=7)
        
        # --- FILTRO POR RESPONSABLE ---
        responsibles = db.query(Responsible).all()
        res_names = ["Todos"] + [r.name for r in responsibles]
        sel_res = st.selectbox("👤 Filtrar por Responsable", res_names)

        # Consultar todas las tareas con sus relaciones
        query = db.query(Task).options(
            joinedload(Task.activity).joinedload(Activity.strategic_item).joinedload(StrategicItem.policy),
            joinedload(Task.responsibles)
        )
        
        all_tasks = query.all()
        
        # Filtrado por responsable (lógica M:N)
        if sel_res != "Todos":
            filtered_tasks = []
            for t in all_tasks:
                if any(r.name == sel_res for r in t.responsibles):
                    filtered_tasks.append(t)
            all_tasks = filtered_tasks

        if not all_tasks:
            st.info("No hay tareas registradas para el responsable seleccionado.")
            return

        # --- CATEGORIZACIÓN ---
        # 1. Terminadas con retraso
        retraso_cumplidas = [t for t in all_tasks if t.status == "Cumplida" and t.fulfillment_date and t.end_date and t.fulfillment_date > t.end_date]
        
        # 2. Vencidas (No cumplidas)
        vencidas = [t for t in all_tasks if t.status != "Cumplida" and t.end_date and t.end_date < now]
        
        # 3. Próximas a vencer (7 días)
        proximas = [t for t in all_tasks if t.status != "Cumplida" and t.end_date and now <= t.end_date <= prox_limite]

        # --- RESUMEN DE ALERTAS ---
        c1, c2, c3 = st.columns(3)
        c1.error(f"🔴 Vencidas: {len(vencidas)}")
        c2.warning(f"🟡 Próximas: {len(proximas)}")
        c3.info(f"🔵 Con Retraso (OK): {len(retraso_cumplidas)}")

        st.divider()

        # --- TABS DE VISUALIZACIÓN ---
        tab1, tab2, tab3 = st.tabs(["❌ Vencidas Críticas", "⚠️ Próximas a Vencer", "✅ Terminadas con Retraso"])

        with tab1:
            if vencidas:
                for t in vencidas:
                    render_alert_card(t, "vencida", now)
            else:
                st.success("No hay tareas vencidas.")

        with tab2:
            if proximas:
                for t in proximas:
                    render_alert_card(t, "proxima", now)
            else:
                st.success("No hay tareas próximas a vencer en los siguientes 7 días.")

        with tab3:
            if retraso_cumplidas:
                st.caption("Tareas marcadas como cumplidas pero cuya fecha de ejecución superó el plazo original.")
                for t in retraso_cumplidas:
                    render_alert_card(t, "retraso_ok", now)
            else:
                st.info("No se registran tareas terminadas fuera de plazo.")

    finally:
        db.close()

def render_alert_card(t, tipo, now):
    with st.container(border=True):
        c1, c2, c3 = st.columns([3, 1.5, 1])
        
        with c1:
            # Color del título basado en tipo
            title_color = "#ef4444" if tipo == "vencida" else ("#f59e0b" if tipo == "proxima" else "#3b82f6")
            st.markdown(f"<h4 style='margin:0; color:{title_color};'>{t.name}</h4>", unsafe_allow_html=True)
            st.caption(f"📍 {t.activity.strategic_item.policy.name} > {t.activity.strategic_item.name}")
            
            res_list = ", ".join([r.name for r in t.responsibles]) if t.responsibles else "Sin asignar"
            st.markdown(f"👤 **Responsables:** {res_list}")
        
        with c2:
            if t.end_date:
                if tipo == "vencida":
                    diff = (now - t.end_date).days
                    st.markdown(f"<span style='color:#ef4444; font-weight:bold;'>Retraso: {diff} días</span>", unsafe_allow_html=True)
                elif tipo == "proxima":
                    diff = (t.end_date - now).days
                    st.markdown(f"<span style='color:#f59e0b; font-weight:bold;'>Quedan: {diff} días</span>", unsafe_allow_html=True)
                elif tipo == "retraso_ok":
                    diff = (t.fulfillment_date - t.end_date).days
                    st.markdown(f"<span style='color:#3b82f6; font-weight:bold;'>Excedió: {diff} días</span>", unsafe_allow_html=True)
                
                st.caption(f"Plazo: {t.end_date.strftime('%d/%m/%Y')}")
                if t.fulfillment_date:
                    st.caption(f"Ejecutado: {t.fulfillment_date.strftime('%d/%m/%Y')}")
        
        with c3:
            st.metric("Peso", f"{t.weight}%")
            st.caption(f"Estado: {t.status}")
