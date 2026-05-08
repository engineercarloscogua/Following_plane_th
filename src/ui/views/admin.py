import streamlit as st
from sqlalchemy.orm import joinedload
from src.core.database import SessionLocal
from src.models.entities import PlanMacro, Policy, StrategicItem, Activity, Task
import pandas as pd
from datetime import datetime

def show_admin_view():
    st.markdown("<div class='corporate-header'>", unsafe_allow_html=True)
    st.title("⚙️ Configuración de Estructura Institucional")
    st.write("Administración jerárquica y cronograma institucional")
    st.markdown("</div>", unsafe_allow_html=True)
    
    db = SessionLocal()
    try:
        t1, t2, t3 = st.tabs(["🏛️ Gestión Macro", "📂 Planes y Programas", "✅ Operación"])
        
        with t1: manage_macro_level(db)
        with t2: manage_strategic_level(db)
        with t3: manage_operational_level(db)
            
    finally:
        db.close()

@st.dialog("Eliminar")
def confirm_delete(db, obj, label):
    st.warning(f"¿Eliminar {label}: {obj.name}?")
    if st.button("Confirmar", type="primary"):
        db.delete(obj)
        db.commit()
        st.rerun()

@st.dialog("Editar")
def edit_dialog(db, obj, label):
    with st.form("f_edit"):
        obj.name = st.text_input("Nombre", value=obj.name)
        if hasattr(obj, 'weight'):
            obj.weight = st.number_input("Peso (%)", value=float(obj.weight))
        
        if isinstance(obj, Task):
            col1, col2 = st.columns(2)
            obj.start_date = col1.date_input("Fecha Inicio", value=obj.start_date or datetime.now())
            obj.end_date = col2.date_input("Fecha Fin", value=obj.end_date or datetime.now())
            obj.responsible_name = st.text_input("Responsable", value=obj.responsible_name or "")
        
        if st.form_submit_button("Guardar"):
            db.commit()
            st.rerun()

def _render_item(db, obj, label, prefix=""):
    c1, c2, c3 = st.columns([4, 0.5, 0.5])
    name_display = f"**{prefix} {obj.name}**"
    if hasattr(obj, 'type'): name_display += f" ({obj.type})"
    if hasattr(obj, 'weight'): name_display += f" - {obj.weight}%"
    
    # Mostrar fechas solo para tareas
    if isinstance(obj, Task) and obj.end_date:
        name_display += f" | 🗓️ {obj.start_date.strftime('%d/%m') if obj.start_date else '?'} al {obj.end_date.strftime('%d/%m/%y')}"
    
    c1.markdown(name_display)
    if c2.button("✏️", key=f"e_{obj.id}_{label}_{obj.__tablename__}_{prefix}"): edit_dialog(db, obj, label)
    if c3.button("🗑️", key=f"d_{obj.id}_{label}_{obj.__tablename__}_{prefix}"): confirm_delete(db, obj, label)

def manage_macro_level(db):
    st.subheader("1. Gestión Macro y Políticas")
    with st.expander("➕ Nuevo Plan Macro"):
        with st.form("n_m"):
            name = st.text_input("Nombre (Ej: Gestión TH)")
            if st.form_submit_button("Crear"):
                db.add(PlanMacro(name=name, year=2026, objective=""))
                db.commit()
                st.rerun()
    
    macros = db.query(PlanMacro).options(joinedload(PlanMacro.policies)).order_by(PlanMacro.id).all()
    for i, m in enumerate(macros, 1):
        with st.container(border=True):
            _render_item(db, m, "Macro", prefix=f"{i}.")
            for j, pol in enumerate(m.policies, 1):
                with st.container(): _render_item(db, pol, "Política", prefix=f"{i}.{j}.")
            with st.popover("➕ Política"):
                with st.form(f"f_p_{m.id}"):
                    p_name = st.text_input("Nombre Política")
                    p_weight = st.number_input("Peso (%)", value=20.0)
                    if st.form_submit_button("Añadir"):
                        db.add(Policy(name=p_name, weight=p_weight, plan_macro_id=m.id))
                        db.commit()
                        st.rerun()

def manage_strategic_level(db):
    st.subheader("2. Planes y Programas")
    policies = db.query(Policy).options(joinedload(Policy.plan_macro), joinedload(Policy.strategic_items)).order_by(Policy.id).all()
    if not policies: return st.info("Cree políticas primero.")
    
    pol_map = {p.id: p for p in policies}
    p_id = st.selectbox("Seleccione Política", options=list(pol_map.keys()), format_func=lambda x: pol_map[x].name)
    pol = pol_map[p_id]
    
    st.write(f"**Elementos de: {pol.name}**")
    items = sorted(pol.strategic_items, key=lambda x: x.id)
    for i, item in enumerate(items, 1):
        with st.container(border=True):
            _render_item(db, item, "Estratégico", prefix=f"{i}.")

    with st.popover("➕ Crear Plan o Programa", use_container_width=True):
        with st.form("n_si"):
            type = st.radio("Tipo", ["Plan", "Programa"])
            name = st.text_input(f"Nombre {type}")
            weight = st.number_input("Peso (%)", value=25.0)
            if st.form_submit_button("Guardar"):
                db.add(StrategicItem(name=name, type=type, weight=weight, policy_id=pol.id))
                db.commit()
                st.rerun()

def manage_operational_level(db):
    st.subheader("3. Operación (Cronograma de Tareas)")
    items = db.query(StrategicItem).options(joinedload(StrategicItem.activities).joinedload(Activity.tasks)).order_by(StrategicItem.id).all()
    if not items: return st.info("Cree Planes o Programas primero.")
    
    i_map = {i.id: i for i in items}
    i_id = st.selectbox("Seleccione Plan/Programa", options=list(i_map.keys()), format_func=lambda x: f"{i_map[x].name} ({i_map[x].type})")
    item = i_map[i_id]
    
    activities = sorted(item.activities, key=lambda x: x.id)
    for i, act in enumerate(activities, 1):
        with st.expander(f"🎯 {i}. Actividad: {act.name} ({act.progress:.1f}%)", expanded=True):
            _render_item(db, act, "Actividad", prefix=f"{i}.")
            
            tasks = sorted(act.tasks, key=lambda x: x.id)
            for j, t in enumerate(tasks, 1):
                _render_item(db, t, "Tarea", prefix=f"{i}.{j}.")
            
            with st.popover("➕ Añadir Tarea con Cronograma"):
                with st.form(f"f_t_{act.id}"):
                    t_name = st.text_input("Descripción Tarea")
                    t_weight = st.number_input("Peso (%)", value=25.0)
                    col_d1, col_d2 = st.columns(2)
                    t_start = col_d1.date_input("Fecha Inicio", value=datetime.now())
                    t_end = col_d2.date_input("Fecha Fin", value=datetime.now())
                    t_resp = st.text_input("Responsable")
                    if st.form_submit_button("Vincular Tarea"):
                        db.add(Task(name=t_name, weight=t_weight, activity_id=act.id, start_date=t_start, end_date=t_end, target_date=t_end, responsible_name=t_resp))
                        db.commit()
                        st.rerun()

    with st.popover("➕ Nueva Actividad", use_container_width=True):
        with st.form("n_act"):
            name = st.text_input("Actividad")
            weight = st.number_input("Peso (%)", value=20.0)
            if st.form_submit_button("Crear"):
                db.add(Activity(name=name, weight=weight, strategic_item_id=item.id))
                db.commit()
                st.rerun()
