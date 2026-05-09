import streamlit as st
from src.core.database import SessionLocal
from src.models.entities import PlanMacro, Policy, StrategicItem, Activity, Task
from sqlalchemy.orm import joinedload
import html

def show_mosaico_view():
    """
    Interactive Hierarchical Explorer (Mosaic).
    Provides a collapsible 360° view of the entire organizational structure for a given year.
    """
    st.markdown("<div class='corporate-header'>", unsafe_allow_html=True)
    st.title("🧩 Mosaico TH")
    st.write("Explorador jerárquico integral por vigencia fiscal")
    st.markdown("</div>", unsafe_allow_html=True)
    
    db = SessionLocal()
    try:
        # 1. Filtro de Año para navegar entre clonaciones
        macros_all = db.query(PlanMacro).all()
        if not macros_all:
            st.info("No hay información registrada.")
            return
            
        all_years = sorted(list(set([m.year for m in macros_all])))
        sel_year = st.selectbox("📅 Seleccione Vigencia Fiscal", all_years, index=len(all_years)-1)

        # Carga profunda filtrada por año
        macros = db.query(PlanMacro).filter(PlanMacro.year == sel_year).options(
            joinedload(PlanMacro.policies)
            .joinedload(Policy.strategic_items)
            .joinedload(StrategicItem.activities)
            .joinedload(Activity.tasks)
        ).all()
        
        for macro in macros:
            # NIVEL 5: PLAN MACRO
            with st.expander(f"🏛️ **PLAN MACRO: {macro.name}** | Avance: {macro.progress:.1f}%", expanded=True):
                for pol in macro.policies:
                    # NIVEL 4: POLÍTICA
                    with st.container(border=True):
                        st.markdown(f"#### 📂 Política: {html.escape(pol.name)}")
                        st.progress(pol.progress / 100)
                        st.caption(f"Avance Consolidado: {pol.progress:.1f}%")
                        
                        for si in pol.strategic_items:
                            # NIVEL 3: PROGRAMA / PLAN
                            with st.expander(f"📝 {html.escape(si.type)}: {html.escape(si.name)} ({si.progress:.1f}%)"):
                                for act in si.activities:
                                    # NIVEL 2: ACTIVIDAD
                                    with st.container():
                                        st.markdown(f"**⚡ Actividad:** {html.escape(act.name)} | `{act.progress:.1f}%`")
                                        
                                        # NIVEL 1: TAREAS (Mosaico)
                                        cols = st.columns(3)
                                        for idx, t in enumerate(act.tasks):
                                            with cols[idx % 3]:
                                                status_color = "#10b981" if t.status == "Cumplida" else ("#f59e0b" if t.status == "En Proceso" else "#94a3b8")
                                                st.markdown(f"""
                                                    <div style='background: white; padding: 10px; border-radius: 8px; border-left: 4px solid {status_color}; margin-bottom: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);'>
                                                        <p style='margin:0; font-size: 0.9rem;'><b>{html.escape(t.name)}</b></p>
                                                        <p style='margin:0; font-size: 0.8rem; color: #64748b;'>{t.status} | {t.progress:.0f}%</p>
                                                    </div>
                                                """, unsafe_allow_html=True)
                                        st.markdown("<br>", unsafe_allow_html=True)

    finally:
        db.close()
