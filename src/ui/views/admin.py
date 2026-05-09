import streamlit as st
from sqlalchemy.orm import joinedload
from src.core.database import SessionLocal
from src.models.entities import PlanMacro, Policy, StrategicItem, Activity, Task, Responsible
import pandas as pd
from datetime import datetime

def show_admin_view():
    """
    Main Administration interface for managing the 5-level institutional hierarchy.
    Allows CRUD operations on Plans, Policies, Programs, Activities, and Responsibles.
    """
    st.markdown("<div class='corporate-header'>", unsafe_allow_html=True)
    st.title("⚙️ Configuración de Estructura Institucional")
    st.write("Administración jerárquica y cronograma institucional")
    st.markdown("</div>", unsafe_allow_html=True)
    
    db = SessionLocal()
    try:
        t1, t2, t3, t4, t5 = st.tabs(["🏛️ Gestión Macro", "📂 Planes y Programas", "✅ Operación", "👥 Responsables", "🛠️ Continuidad"])
        
        with t1: manage_macro_level(db)
        with t2: manage_strategic_level(db)
        with t3: manage_operational_level(db)
        with t4: manage_responsibles_level(db)
        with t5: manage_tools_level(db)
            
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
            col_s1, col_s2 = st.columns(2)
            status_opts = ["Pendiente", "En Proceso", "Cumplida"]
            obj.status = col_s1.selectbox("Estado", status_opts, index=status_opts.index(obj.status) if obj.status in status_opts else 0)
            obj.progress = col_s2.number_input("Avance (%)", value=float(obj.progress), min_value=0.0, max_value=100.0)
            
            col1, col2 = st.columns(2)
            obj.start_date = col1.date_input("Fecha Inicio", value=obj.start_date or datetime.now())
            obj.end_date = col2.date_input("Fecha Fin", value=obj.end_date or datetime.now())
            
            # Gestión de Responsables Múltiples
            all_res = db.query(Responsible).all()
            res_map = {r.id: r for r in all_res}
            current_ids = [r.id for r in obj.responsibles]
            selected_ids = st.multiselect(
                "Responsables Asignados", 
                options=list(res_map.keys()), 
                default=current_ids,
                format_func=lambda x: f"{res_map[x].name} ({res_map[x].role})"
            )
            obj.responsibles = [res_map[rid] for rid in selected_ids]
            obj.responsible_name = ", ".join([res_map[rid].name for rid in selected_ids])
        
        if st.form_submit_button("Guardar"):
            try:
                db.add(obj) 
                db.commit()
                
                # RECALCULAR NIVELES si es una tarea
                if isinstance(obj, Task):
                    from src.services.calculations import CalculationService
                    CalculationService.update_all_levels(db, obj.id)
                
                st.toast("✅ Cambios guardados y dashboard actualizado")
                st.success("✅ Gestión actualizada exitosamente")
                st.rerun()
            except Exception as e:
                db.rollback()
                st.error(f"Error al guardar: {str(e)}")

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
            st.markdown("<div class='btn-activity'>", unsafe_allow_html=True)
            if st.form_submit_button("Crear"):
                db.add(PlanMacro(name=name, year=2026, objective=""))
                db.commit()
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
    
    macros = db.query(PlanMacro).options(joinedload(PlanMacro.policies)).order_by(PlanMacro.year.desc(), PlanMacro.id).all()
    for i, m in enumerate(macros, 1):
        with st.expander(f"📁 {i}. {m.name} ({m.year})", expanded=(i==1)):
            _render_item(db, m, "Macro", prefix="Gestión:")
            st.markdown("---")
            for j, pol in enumerate(m.policies, 1):
                with st.container(): _render_item(db, pol, "Política", prefix=f"{i}.{j}.")
            with st.popover("➕ Política"):
                with st.form(f"f_p_{m.id}"):
                    p_name = st.text_input("Nombre Política")
                    p_weight = st.number_input("Peso (%)", value=20.0)
                    st.markdown("<div class='btn-activity'>", unsafe_allow_html=True)
                    if st.form_submit_button("Añadir"):
                        db.add(Policy(name=p_name, weight=p_weight, plan_macro_id=m.id))
                        db.commit()
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)

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
    items = db.query(StrategicItem).options(
        joinedload(StrategicItem.activities).joinedload(Activity.tasks).joinedload(Task.responsibles)
    ).order_by(StrategicItem.id).all()
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
                with st.expander(f"{i}.{j} {t.name}"):
                    # Mostrar responsables de forma limpia (sin etiqueta de campo)
                    if t.responsibles:
                        res_html = " ".join([f"<span class='badge' style='background-color:#f1f5f9; color:#475569; border:1px solid #cbd5e1;'>{r.name}</span>" for r in t.responsibles])
                        st.markdown(res_html, unsafe_allow_html=True)
                    else:
                        st.caption("Sin responsables asignados")
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    col_t1, col_t2 = st.columns([5, 1])
                    if col_t1.button("✏️ Editar Tarea", key=f"e_{t.id}_T", use_container_width=True): edit_dialog(db, t, "Tarea")
                    if col_t2.button("🗑️", key=f"d_{t.id}_T", use_container_width=True): confirm_delete(db, t, "Tarea")
            
            with st.popover("➕ Añadir Tarea con Cronograma", use_container_width=True):
                with st.form(f"f_t_{act.id}"):
                    t_name = st.text_input("Descripción Tarea")
                    t_weight = st.number_input("Peso (%)", value=25.0)
                    col_d1, col_d2 = st.columns(2)
                    t_start = col_d1.date_input("Fecha Inicio", value=datetime.now())
                    t_end = col_d2.date_input("Fecha Fin", value=datetime.now())
                    
                    # Selección de Responsables
                    all_res = db.query(Responsible).all()
                    res_map = {r.id: r for r in all_res}
                    selected_res_ids = st.multiselect(
                        "Seleccionar Responsables", 
                        options=list(res_map.keys()),
                        format_func=lambda x: f"{res_map[x].name} ({res_map[x].role})"
                    )
                    
                    if st.form_submit_button("Vincular Tarea"):
                        new_task = Task(
                            name=t_name, 
                            weight=t_weight, 
                            activity_id=act.id, 
                            start_date=t_start, 
                            end_date=t_end, 
                            target_date=t_end,
                            responsible_name=", ".join([res_map[rid].name for rid in selected_res_ids])
                        )
                        new_task.responsibles = [res_map[rid] for rid in selected_res_ids]
                        db.add(new_task)
                        db.commit()
                        st.toast("✅ Tarea vinculada exitosamente")
                        st.rerun()

    st.markdown("<div class='btn-activity'>", unsafe_allow_html=True)
    with st.popover("➕ Nueva Actividad", use_container_width=True):
        with st.form("n_act"):
            name = st.text_input("Actividad")
            weight = st.number_input("Peso (%)", value=20.0)
            if st.form_submit_button("Crear"):
                db.add(Activity(name=name, weight=weight, strategic_item_id=item.id))
                db.commit()
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

def manage_responsibles_level(db):
    st.subheader("👥 Gestión de Responsables Institucionales")
    
    with st.expander("➕ Nuevo Responsable", expanded=False):
        with st.form("n_res"):
            col1, col2 = st.columns(2)
            name = col1.text_input("Nombre Completo")
            role = col2.text_input("Cargo/Rol")
            dept = st.text_input("Departamento/Área")
            if st.form_submit_button("Registrar Responsable"):
                if name and role:
                    db.add(Responsible(name=name, role=role, department=dept))
                    db.commit()
                    st.success(f"✅ {name} registrado.")
                    st.rerun()
                else:
                    st.error("Nombre y Cargo son obligatorios.")

    responsibles = db.query(Responsible).order_by(Responsible.name).all()
    if not responsibles:
        st.info("No hay responsables registrados.")
        return

    for res in responsibles:
        with st.container(border=True):
            c1, c2, c3 = st.columns([4, 0.5, 0.5])
            c1.markdown(f"**{res.name}** - {res.role} ({res.department})")
            if c2.button("✏️", key=f"e_res_{res.id}"):
                edit_responsible_dialog(db, res)
            if c3.button("🗑️", key=f"d_res_{res.id}"):
                confirm_delete(db, res, "Responsable")

@st.dialog("Editar Responsable")
def edit_responsible_dialog(db, res):
    with st.form("f_edit_res"):
        res.name = st.text_input("Nombre", value=res.name)
        res.role = st.text_input("Cargo", value=res.role)
        res.department = st.text_input("Departamento", value=res.department)
        if st.form_submit_button("Guardar Cambios"):
            db.commit()
            st.rerun()

def manage_tools_level(db):
    st.subheader("🛠️ Herramientas de Continuidad Estratégica")
    st.write("Duplica toda la estructura institucional para un nuevo año fiscal.")
    
    macros = db.query(PlanMacro).all()
    if not macros:
        st.info("No hay planes registrados para clonar.")
        return

    # Usar mapa de IDs para evitar DetachedInstanceError
    macro_map = {m.id: m for m in macros}
    
    with st.container(border=True):
        src_id = st.selectbox("Plan Origen (Fuente)", options=list(macro_map.keys()), format_func=lambda x: f"{macro_map[x].name} ({macro_map[x].year})")
        src_macro = db.query(PlanMacro).filter(PlanMacro.id == src_id).options(joinedload(PlanMacro.policies)).first()
        
        new_year = st.number_input("Año Destino", value=src_macro.year + 1)
        new_name = st.text_input("Nombre del Nuevo Plan", value=f"{src_macro.name} {new_year}")
        
        if st.button("🚀 Iniciar Clonación Estratégica", use_container_width=True):
            with st.spinner("Clonando estructura multinivel..."):
                tasks_to_bind = []
                try:
                    # 1. Macro (Ensure objective is not None)
                    new_macro = PlanMacro(
                        name=new_name, 
                        year=new_year, 
                        objective=src_macro.objective or ""
                    )
                    
                    # 2. Políticas
                    for p_src in src_macro.policies:
                        p_new = Policy(name=p_src.name, weight=p_src.weight)
                        new_macro.policies.append(p_new)
                        
                        # 3. Items
                        for si_src in p_src.strategic_items:
                            si_new = StrategicItem(name=si_src.name, type=si_src.type, weight=si_src.weight)
                            p_new.strategic_items.append(si_new)
                            
                            # 4. Actividades
                            for act_src in si_src.activities:
                                act_new = Activity(name=act_src.name, weight=act_src.weight)
                                si_new.activities.append(act_new)
                                
                                # 5. Tareas
                                for t_src in act_src.tasks:
                                    # Safe date shifting (handling Feb 29 if necessary)
                                    n_start, n_end = None, None
                                    try:
                                        if t_src.start_date: n_start = t_src.start_date.replace(year=new_year)
                                        if t_src.end_date: n_end = t_src.end_date.replace(year=new_year)
                                    except ValueError:
                                        # Fallback for leap year issues (Feb 29 -> Feb 28)
                                        if t_src.start_date: n_start = t_src.start_date.replace(year=new_year, day=28)
                                        if t_src.end_date: n_end = t_src.end_date.replace(year=new_year, day=28)
                                    
                                    t_new = Task(
                                        name=t_src.name, weight=t_src.weight,
                                        status="Pendiente", progress=0.0,
                                        start_date=n_start, end_date=n_end, target_date=n_end,
                                        responsible_name=t_src.responsible_name
                                    )
                                    act_new.tasks.append(t_new)
                                    # Store mapping to apply responsibles safely after flush
                                    tasks_to_bind.append((t_new, list({r for r in t_src.responsibles})))
                    
                    db.add(new_macro)
                    db.flush() # Forces IDs to be generated without committing
                    
                    # Safe many-to-many binding after IDs exist
                    for t_new, responsibles in tasks_to_bind:
                        t_new.responsibles = responsibles
                        
                    db.commit()
                    st.balloons()
                    st.success(f"✅ ¡Estructura '{new_name}' creada exitosamente para el año {new_year}!")
                    st.info("Nota: Todas las tareas han sido reiniciadas a estado 'Pendiente' con 0% de avance.")
                    st.rerun()
                except Exception as e:
                    db.rollback()
                    st.error(f"Error de Integridad: {str(e)}")
