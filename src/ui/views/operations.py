import streamlit as st
import html
from sqlalchemy.orm import joinedload
from src.core.database import SessionLocal
from src.models.entities import Plan, Program, Activity, Task, User
from src.services.calculations import CalculationService

def show_operations_view():
    st.markdown("<div class='corporate-header'>", unsafe_allow_html=True)
    st.title("✅ Seguimiento y Operación")
    st.write("Gestión de avances y actividades estratégicas")
    st.markdown("</div>", unsafe_allow_html=True)
    
    db = SessionLocal()
    try:
        plans = db.query(Plan).options(joinedload(Plan.programs)).all()
        if not plans:
            st.warning("No hay planes configurados.")
            return

        plan_map = {p.id: p for p in plans}
        selected_plan_id = st.selectbox(
            "Seleccione Plan de Trabajo", 
            options=list(plan_map.keys()), 
            format_func=lambda x: f"{plan_map[x].name} ({plan_map[x].year})"
        )
        plan = plan_map[selected_plan_id]
        
        programs = plan.programs
        if not programs:
            st.info("No hay programas asociados a este plan.")
            return

        program_map = {pr.id: pr for pr in programs}
        selected_prog_id = st.selectbox(
            "Seleccione Programa", 
            options=list(program_map.keys()), 
            format_func=lambda x: program_map[x].name
        )
        program = program_map[selected_prog_id]
        
        st.divider()
        st.subheader(f"Actividades Estratégicas: {program.name}")
        
        activities = db.query(Activity).options(joinedload(Activity.tasks)).filter(Activity.program_id == program.id).all()
        
        if not activities:
            st.info("No hay actividades registradas.")
        
        for act in activities:
            with st.expander(f"📌 {act.name} - Avance: {act.progress:.1f}%", expanded=True):
                col_a1, col_a2 = st.columns([3, 1])
                with col_a1:
                    st.write(f"**Peso:** {act.weight}%")
                with col_a2:
                    _, color = CalculationService.get_semaforo(act.progress)
                    st.markdown(f"<div style='padding:5px; border-radius:5px; background-color:{color}; color:white; text-align:center;'>{html.escape(act.status)}</div>", unsafe_allow_html=True)
                
                st.markdown("---")
                
                for t in act.tasks:
                    c_t1, c_t2, c_t3 = st.columns([3, 1, 1])
                    with c_t1:
                        new_prog = st.slider(
                            f"Tarea: {t.name}", 
                            0.0, 100.0, 
                            float(t.progress), 
                            key=f"task_slider_{t.id}"
                        )
                        if new_prog != t.progress:
                            t.progress = new_prog
                            db.commit()
                            CalculationService.update_activity_progress(db, act.id)
                            st.rerun()
                    with c_t2:
                        st.write(f"Peso: {t.weight}%")
                    with c_t3:
                        if st.button("📁 Evidencia", key=f"btn_ev_{t.id}"):
                            st.toast(f"Módulo de evidencias para: {t.name}")

                with st.popover("➕ Añadir Tarea"):
                    with st.form(key=f"form_task_{act.id}"):
                        t_name = st.text_input("Descripción de la Tarea")
                        t_weight = st.number_input("Peso (%)", min_value=1.0, max_value=100.0, value=10.0)
                        if st.form_submit_button("Guardar"):
                            admin = db.query(User).filter(User.username == "admin").first()
                            new_task = Task(name=t_name, weight=t_weight, activity_id=act.id, responsible_id=admin.id)
                            db.add(new_task)
                            db.commit()
                            CalculationService.update_activity_progress(db, act.id)
                            st.success("Tarea añadida")
                            st.rerun()

        st.divider()
        with st.expander("🚀 Registrar Nueva Actividad"):
            with st.form("new_activity_op_form"):
                a_name = st.text_input("Nombre de la Actividad")
                a_weight = st.number_input("Peso Estratégico (%)", min_value=1.0, max_value=100.0, value=20.0)
                if st.form_submit_button("Crear Actividad"):
                    admin = db.query(User).filter(User.username == "admin").first()
                    new_act = Activity(name=a_name, weight=a_weight, program_id=program.id, responsible_id=admin.id)
                    db.add(new_act)
                    db.commit()
                    st.success("Actividad creada")
                    st.rerun()
                    
    finally:
        db.close()
