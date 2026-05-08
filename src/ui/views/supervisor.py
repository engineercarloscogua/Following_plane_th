import streamlit as st
from sqlalchemy.orm import joinedload
from src.core.database import SessionLocal
from src.models.entities import PlanMacro, Policy, StrategicItem, Activity, Task, Evidence
from src.services.calculations import CalculationService
from datetime import datetime

def show_supervisor_view():
    st.markdown("<div class='corporate-header'>", unsafe_allow_html=True)
    st.title("🧐 Supervisión y Seguimiento")
    st.write("Control operativo con validación de evidencias y observaciones")
    st.markdown("</div>", unsafe_allow_html=True)
    
    db = SessionLocal()
    try:
        macros = db.query(PlanMacro).order_by(PlanMacro.id).all()
        if not macros: return st.info("Sin planes configurados.")
        
        m_id = st.selectbox("Gestión Macro", options=[m.id for m in macros], format_func=lambda x: next(m.name for m in macros if m.id == x))
        macro = db.query(PlanMacro).filter(PlanMacro.id == m_id).first()
        
        pol_id = st.selectbox("Política", options=[p.id for p in macro.policies], format_func=lambda x: next(p.name for p in macro.policies if p.id == x))
        policy = db.query(Policy).filter(Policy.id == pol_id).first()
        
        si_id = st.selectbox("Plan / Programa", options=[si.id for si in policy.strategic_items], format_func=lambda x: f"{next(si.name for si in policy.strategic_items if si.id == x)} ({next(si.type for si in policy.strategic_items if si.id == x)})")
        item = db.query(StrategicItem).filter(StrategicItem.id == si_id).first()

        st.divider()
        st.subheader(f"Seguimiento: {item.name}")
        
        activities = db.query(Activity).options(joinedload(Activity.tasks)).filter(Activity.strategic_item_id == item.id).order_by(Activity.id).all()
        
        for i, act in enumerate(activities, 1):
            with st.expander(f"📌 {i}. {act.name} (Avance: {act.progress:.1f}%)", expanded=True):
                tasks = sorted(act.tasks, key=lambda x: x.id)
                for j, t in enumerate(tasks, 1):
                    st.markdown(f"#### {i}.{j} Tarea: {t.name}")
                    
                    ev_list = db.query(Evidence).filter(Evidence.task_id == t.id).all()
                    has_evidence = len(ev_list) > 0
                    
                    c1, c2, c3 = st.columns([2, 1.5, 1])
                    with c1: 
                        st.write(f"👤 Resp: `{t.responsible_name or 'Sin asignar'}`")
                        if t.target_date: st.caption(f"📅 Plazo: {t.target_date.strftime('%Y-%m-%d')}")
                    
                    with c2:
                        status_opts = ["Pendiente", "En Proceso", "Cumplida"]
                        curr_idx = status_opts.index(t.status) if t.status in status_opts else 0
                        new_status = st.selectbox("Estado", status_opts, index=curr_idx, key=f"st_sup_{t.id}")
                        
                        if new_status == "Cumplida" and not has_evidence:
                            st.error("⚠️ Falta evidencia")
                            if t.status != "Cumplida": new_status = t.status

                    with c3:
                        if t.status == "Cumplida" or new_status == "Cumplida":
                            f_date = st.date_input("Cumplimiento", value=t.fulfillment_date or datetime.now(), key=f"dt_sup_{t.id}")

                    obs = st.text_area("📝 Observaciones", value=t.observations or "", key=f"obs_sup_{t.id}")
                    
                    save_col1, save_col2 = st.columns([1, 4])
                    if save_col1.button("💾 Guardar", key=f"save_sup_{t.id}"):
                        if new_status == "Cumplida":
                            if not has_evidence: st.error("Sin evidencia.")
                            elif not obs or len(obs.strip()) < 5: st.error("Observaciones requeridas.")
                            else:
                                t.status = "Cumplida"
                                t.progress = 100.0
                                t.observations = obs
                                t.fulfillment_date = f_date
                                db.commit()
                                CalculationService.update_all_levels(db, t.id)
                                st.toast("✅ Tarea cumplida")
                                st.rerun()
                        else:
                            t.status = new_status
                            t.progress = 50.0 if new_status == "En Proceso" else 0.0
                            t.observations = obs
                            db.commit()
                            CalculationService.update_all_levels(db, t.id)
                            st.toast("✅ Cambios guardados")
                            st.rerun()

                    # Gestión de Evidencias con botón de apertura en nueva ventana
                    st.caption("🔗 Enlaces de Evidencia (Click para abrir en nueva pestaña)")
                    for ev in ev_list:
                        # Asegurar que la URL tenga protocolo
                        url = ev.url if ev.url.startswith(("http://", "https://")) else f"https://{ev.url}"
                        st.link_button(f"📎 Ver Soporte: {ev.url[:40]}...", url, use_container_width=True)
                    
                    with st.popover("➕ Agregar Enlace"):
                        link = st.text_input("URL de Evidencia", key=f"l_sup_{t.id}", help="Ej: https://onedrive.com/archivo")
                        if st.button("Vincular", key=f"b_sup_{t.id}"):
                            if link:
                                db.add(Evidence(task_id=t.id, url=link))
                                db.commit()
                                st.rerun()
                    st.divider()
    finally:
        db.close()
