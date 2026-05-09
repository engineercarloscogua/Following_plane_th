import streamlit as st
from sqlalchemy.orm import joinedload
from src.core.database import SessionLocal
from src.models.entities import Task, Activity, Evidence, Responsible, User
from datetime import datetime
import html

def show_worker_view():
    """
    Personalized view for Workers.
    Shows only tasks assigned to the logged-in responsible.
    Allows evidence upload and descriptive observations.
    """
    st.markdown("<div class='corporate-header'>", unsafe_allow_html=True)
    st.title("👷 Mi Panel de Trabajo")
    st.write("Gestiona tus tareas asignadas, carga evidencias y reporta avances.")
    st.markdown("</div>", unsafe_allow_html=True)

    responsible_id = st.session_state.get("responsible_id")
    if not responsible_id:
        st.warning("⚠️ Tu cuenta no está vinculada a un perfil de Responsable. Contacta al Administrador.")
        return

    db = SessionLocal()
    try:
        # Get tasks assigned to this responsible
        # We need to filter tasks where this responsible is in t.responsibles
        tasks = db.query(Task).join(Task.responsibles).filter(Responsible.id == responsible_id).all()

        if not tasks:
            st.info("No tienes tareas asignadas actualmente. ¡Buen trabajo!")
            return

        # Group tasks by activity for better organization
        activities_map = {}
        for t in tasks:
            act = t.activity
            if act.id not in activities_map:
                activities_map[act.id] = {"obj": act, "tasks": []}
            activities_map[act.id]["tasks"].append(t)

        for act_id, data in activities_map.items():
            act = data["obj"]
            act_tasks = data["tasks"]
            
            with st.expander(f"🎯 Actividad: {act.name}", expanded=True):
                for t in act_tasks:
                    with st.container(border=True):
                        st.markdown(f"### {t.name}")
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.markdown(f"**Estado Actual:** `{t.status}`")
                            if t.start_date and t.end_date:
                                st.caption(f"📅 Plazo: {t.start_date.strftime('%d/%m/%y')} al {t.end_date.strftime('%d/%m/%y')}")
                        
                        with col2:
                            # Workers can set status to "En Proceso" or "Pendiente"
                            # For "Cumplida", they should probably set a status like "Para Revisión"
                            # But since the user didn't ask for new statuses, I'll allow them to update observations and evidence.
                            status_opts = ["Pendiente", "En Proceso"]
                            curr_idx = status_opts.index(t.status) if t.status in status_opts else 0
                            new_status = st.selectbox("Actualizar Estado", status_opts, index=curr_idx, key=f"st_work_{t.id}")

                        st.markdown("---")
                        obs = st.text_area("📝 Descripción/Observación de la ejecución", value=t.observations or "", key=f"obs_work_{t.id}", placeholder="Describe detalladamente qué hiciste en esta tarea...")
                        
                        ev_list = db.query(Evidence).filter(Evidence.task_id == t.id).all()
                        if ev_list:
                            st.caption("🔗 Evidencias Cargadas:")
                            for ev in ev_list:
                                url = ev.url if ev.url.startswith(("http://", "https://")) else f"https://{ev.url}"
                                st.markdown(f"- [Ver Evidencia]({url})")
                        
                        col_ev, col_save = st.columns([3, 1])
                        with col_ev:
                            new_ev = st.text_input("Añadir nuevo enlace de evidencia (Drive, SharePoint, etc.)", key=f"ev_work_{t.id}")
                        
                        with col_save:
                            st.markdown("<br>", unsafe_allow_html=True)
                            if st.button("💾 Reportar Avance", key=f"save_work_{t.id}", use_container_width=True):
                                t.status = new_status
                                t.observations = obs
                                if new_ev:
                                    db.add(Evidence(task_id=t.id, url=new_ev))
                                
                                # If it's a worker, we don't automatically set it to 100% progress
                                # unless the user explicitly wants that. 
                                # Usually "Cumplida" is for Supervisor.
                                if new_status == "En Proceso":
                                    t.progress = 50.0
                                elif new_status == "Pendiente":
                                    t.progress = 0.0
                                
                                db.commit()
                                st.success("✅ Avance reportado correctamente.")
                                st.rerun()
    finally:
        db.close()
