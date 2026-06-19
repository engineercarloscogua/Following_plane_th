import streamlit as st
from sqlalchemy.orm import joinedload
from src.core.database import SessionLocal
from src.models.entities import (
    PlanMacro, Policy, StrategicItem, Activity, Task, Evidence, Responsible, ChangeLog
)
from src.services.calculations import CalculationService
from datetime import datetime
import pandas as pd
import html

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _semaforo(prog):
    if prog >= 80: return "🟢"
    if prog >= 50: return "🟡"
    return "🔴"

def _status_color(status):
    return {"Cumplida": "#10b981", "En Proceso": "#f59e0b", "Pendiente": "#94a3b8"}.get(status, "#94a3b8")

# ─────────────────────────────────────────────────────────────────────────────
# Dialogs
# ─────────────────────────────────────────────────────────────────────────────

@st.dialog("✏️ Editar Tarea", width="large")
def edit_task_dialog(db, task_id):
    """Modal de edición de tarea — sin recargar la página principal."""
    t = db.query(Task).options(
        joinedload(Task.responsibles),
        joinedload(Task.evidences)
    ).filter(Task.id == task_id).first()
    if not t:
        st.error("Tarea no encontrada.")
        return

    st.markdown(f"**{html.escape(t.name)}**")
    st.caption(f"Actividad: {html.escape(t.activity.name)}")
    st.divider()

    if t.is_locked:
        st.warning("🔒 Periodo cerrado para auditoría (Modo Solo Lectura)")

    now = datetime.now()
    is_overdue = t.end_date and t.end_date < now and t.status != "Cumplida"
    if is_overdue:
        st.warning("⚠️ Esta tarea está vencida. Se requiere justificación del retraso.")

    col_s, col_p = st.columns(2)
    with col_s:
        status_opts = ["Pendiente", "En Proceso", "Cumplida"]
        curr_idx = status_opts.index(t.status) if t.status in status_opts else 0
        new_status = st.selectbox("Estado", status_opts, index=curr_idx, disabled=t.is_locked)
    with col_p:
        new_progress = st.slider("Avance (%)", 0, 100, int(t.progress), disabled=t.is_locked)

    col_d1, col_d2 = st.columns(2)
    with col_d1:
        new_start = st.date_input("Fecha inicio", value=t.start_date or datetime.now(), disabled=t.is_locked)
    with col_d2:
        new_end = st.date_input("Fecha fin", value=t.end_date or datetime.now(), disabled=t.is_locked)

    obs = st.text_area("📝 Observaciones", value=t.observations or "",
                        placeholder="Describe el avance, novedades o acuerdos…", height=90, disabled=t.is_locked)

    # Justificación obligatoria si está vencida
    justif = None
    if is_overdue:
        justif = st.text_area("⚠️ Justificación del retraso (obligatorio)",
                               placeholder="Ej: Dependía de aprobación externa, se retomará el 25/06…",
                               height=70, disabled=t.is_locked)

    # Mostrar evidencias existentes con metadatos
    ev_list = db.query(Evidence).filter(Evidence.task_id == t.id).all()
    if ev_list:
        st.markdown("**🔗 Evidencias cargadas:**")
        for ev in ev_list:
            url      = ev.url if ev.url.startswith(("http://", "https://")) else f"https://{ev.url}"
            date_str = ev.uploaded_at.strftime('%d/%m/%y') if ev.uploaded_at else "—"
            who      = ev.uploaded_by_name or "sistema"
            desc     = ev.description or ""
            st.markdown(
                f"  - [🔗 {html.escape(desc) if desc else 'Ver evidencia'}]({url})  "
                f"\u00b7  📅 `{date_str}`  ·  👤 `{who}`",
                unsafe_allow_html=False
            )

    with st.expander("➕ Agregar nueva evidencia", expanded=False):
        new_ev_url  = st.text_input("Enlace de evidencia", placeholder="https://…", key=f"ev_url_{t.id}", disabled=t.is_locked)
        new_ev_desc = st.text_input("Descripción", placeholder="Ej: Acta de reunión", key=f"ev_desc_{t.id}", disabled=t.is_locked)

    st.divider()
    can_save = True
    if new_status == "Cumplida" and not ev_list and not (new_ev_url and new_ev_url.strip()):
        st.error("Para marcar como Cumplida se requiere al menos una evidencia.")
        can_save = False
    if is_overdue and (not justif or len(justif.strip()) < 10):
        st.error("Ingresa una justificación de al menos 10 caracteres.")
        can_save = False

    if st.button("💾 Guardar cambios", disabled=t.is_locked or not can_save, use_container_width=True, type="primary"):
        username = st.session_state.get("username", "sistema")

        # — Registrar cambios en ChangeLog (2.2)
        changes = []
        if t.status != new_status:
            changes.append(("status", t.status, new_status))
        new_prog = 100.0 if new_status == "Cumplida" else float(new_progress)
        if abs(t.progress - new_prog) > 0.5:
            changes.append(("progress", f"{t.progress:.1f}%", f"{new_prog:.1f}%"))

        for field, old_v, new_v in changes:
            db.add(ChangeLog(
                entity_type="Task",
                entity_id=t.id,
                entity_name=t.name,
                field_changed=field,
                old_value=str(old_v),
                new_value=str(new_v),
                changed_by=username,
            ))

        # — Guardar tarea
        t.status               = new_status
        t.progress             = new_prog
        t.observations         = obs
        t.start_date           = datetime.combine(new_start, datetime.min.time())
        t.end_date             = datetime.combine(new_end,   datetime.min.time())
        if new_status == "Cumplida":
            t.fulfillment_date = datetime.now()
        if justif and justif.strip():
            t.delay_justification = justif.strip()  # campo dedicado (2.3)
        if new_ev_url and new_ev_url.strip():
            db.add(Evidence(
                task_id=t.id,
                url=new_ev_url.strip(),
                description=new_ev_desc or None,
                uploaded_by_name=username  # metadato (2.4)
            ))
        db.add(t)
        db.commit()
        CalculationService.update_all_levels(db, t.id)
        st.success("✅ Tarea actualizada correctamente.")
        st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# Main view
# ─────────────────────────────────────────────────────────────────────────────

def show_supervisor_view():
    """
    Vista de Supervisión refactorizada.
    Pestaña "Mi Equipo": tabla de avance por funcionaria.
    Pestaña "Gestión de Tareas": filtros horizontales + tabla + modal de edición.
    """
    st.markdown("<div class='corporate-header'>", unsafe_allow_html=True)
    st.title("🧐 Seguimiento y Gestión")
    st.write("Supervisa el avance de tu equipo y actualiza el estado de las tareas.")
    st.markdown("</div>", unsafe_allow_html=True)

    db = SessionLocal()
    try:
        user_role = st.session_state.get("role")
        res_id    = st.session_state.get("responsible_id")
        now       = datetime.now()

        # Cargar datos completos
        macros = db.query(PlanMacro).options(
            joinedload(PlanMacro.policies)
            .joinedload(Policy.strategic_items)
            .joinedload(StrategicItem.activities)
            .joinedload(Activity.tasks).joinedload(Task.responsibles)
        ).order_by(PlanMacro.year.desc()).all()

        if not macros:
            return st.info("Sin planes configurados.")

        all_years = sorted(set(m.year for m in macros))
        col_y, _ = st.columns([1, 3])
        sel_year = col_y.selectbox("📅 Año", all_years, index=len(all_years)-1)
        macro = next((m for m in macros if m.year == sel_year), macros[0])

        # ── TABS ──────────────────────────────────────────────────────
        tab_equipo, tab_tareas, tab_historial = st.tabs(["👥 Mi Equipo", "✅ Gestión de Tareas", "📋 Historial"])

        # ═══════════════════════════════════════════════════════════════
        # TAB 1 — MI EQUIPO
        # ═══════════════════════════════════════════════════════════════
        with tab_equipo:
            st.subheader("Avance por Funcionaria")

            responsibles = db.query(Responsible).options(joinedload(Responsible.tasks)).all()
            rows = []
            for r in responsibles:
                tasks_y = [
                    t for t in r.tasks
                    if t.activity and t.activity.strategic_item
                    and t.activity.strategic_item.policy
                    and t.activity.strategic_item.policy.plan_macro_id == macro.id
                ]
                if not tasks_y:
                    continue
                total     = len(tasks_y)
                cumplidas = sum(1 for t in tasks_y if t.status == "Cumplida")
                en_proc   = sum(1 for t in tasks_y if t.status == "En Proceso")
                vencidas  = sum(1 for t in tasks_y if t.status != "Cumplida" and t.end_date and t.end_date < now)
                avg_prog  = sum(t.progress for t in tasks_y) / total
                rows.append({
                    " ":            _semaforo(avg_prog),
                    "Funcionaria":  r.name,
                    "Cargo":        r.role,
                    "Total":        total,
                    "✅ Cumplidas": cumplidas,
                    "⚙️ En Proceso": en_proc,
                    "🚫 Vencidas":  vencidas,
                    "Avance %":     round(avg_prog, 1),
                })

            if rows:
                df_team = pd.DataFrame(rows).sort_values("Avance %", ascending=False)
                st.dataframe(
                    df_team, use_container_width=True, hide_index=True,
                    column_config={
                        "Avance %": st.column_config.ProgressColumn(
                            "Avance %", format="%.1f%%", min_value=0, max_value=100
                        )
                    }
                )

                import plotly.express as px
                fig_team = px.bar(
                    df_team.sort_values("Avance %"),
                    x="Avance %", y="Funcionaria", orientation="h",
                    color="Avance %",
                    color_continuous_scale=[[0, "#ef4444"], [0.5, "#f59e0b"], [1, "#10b981"]],
                    title="Rendimiento del Equipo", template="plotly_white"
                )
                fig_team.update_traces(texttemplate="%{x:.1f}%", textposition="outside")
                fig_team.update_layout(showlegend=False, xaxis=dict(range=[0, 115]),
                                        yaxis=dict(title=""), height=320)
                st.plotly_chart(fig_team, use_container_width=True)
            else:
                st.info("No hay funcionarias con tareas asignadas en este plan.")

        # ═══════════════════════════════════════════════════════════════
        # TAB 2 — GESTIÓN DE TAREAS (filtros + tabla + modal)
        # ═══════════════════════════════════════════════════════════════
        with tab_tareas:
            # Recopilar todas las tareas del macro
            all_tasks = []
            for pol in macro.policies:
                for si in pol.strategic_items:
                    for act in si.activities:
                        for t in act.tasks:
                            # Filtrar por rol
                            if user_role == "Supervisor" and res_id:
                                is_sup    = any(s.id == res_id for s in act.supervisors) if hasattr(act, 'supervisors') else False
                                is_worker = any(r.id == res_id for r in t.responsibles)
                                if not is_sup and not is_worker:
                                    continue
                            all_tasks.append({
                                "_task_id":    t.id,
                                "_pol_name":   pol.name,
                                "Política":    pol.name,
                                "Estrategia":  si.name,
                                "Actividad":   act.name,
                                "Tarea":       t.name,
                                "Responsable": ", ".join(r.name for r in t.responsibles) or "Sin asignar",
                                "Avance":      t.progress,
                                "Estado":      t.status,
                                "Fin":         t.end_date.strftime("%d/%m/%y") if t.end_date else "—",
                                "_vencida":    bool(t.end_date and t.end_date < now and t.status != "Cumplida"),
                            })

            if not all_tasks:
                st.info("No hay tareas disponibles para este plan o rol.")
            else:
                df_tasks = pd.DataFrame(all_tasks)

                # ── FILTROS HORIZONTALES EN CASCADA ───────────────────
                # El filtro Estrategia se actualiza según la Política elegida
                f1, f2, f3, f4 = st.columns(4)

                pol_opts = ["Todas"] + sorted(df_tasks["Política"].unique().tolist())
                sel_pol  = f1.selectbox("Política", pol_opts, key="fil_pol")

                # Cascada: limitar estrategias a las de la política seleccionada
                if sel_pol != "Todas":
                    est_disponibles = sorted(
                        df_tasks[df_tasks["_pol_name"] == sel_pol]["Estrategia"].unique().tolist()
                    )
                else:
                    est_disponibles = sorted(df_tasks["Estrategia"].unique().tolist())
                sel_estrategia = f2.selectbox("Estrategia", ["Todas"] + est_disponibles, key="fil_estrategia")

                resp_opts = ["Todas"] + sorted(df_tasks["Responsable"].unique().tolist())
                sel_resp  = f3.selectbox("Funcionaria", resp_opts, key="fil_resp")

                estado_opts = ["Todos", "Pendiente", "En Proceso", "Cumplida", "🚫 Vencidas"]
                sel_est     = f4.selectbox("Estado", estado_opts, key="fil_est")

                # Aplicar filtros en orden correcto
                df_vis = df_tasks.copy()
                if sel_pol        != "Todas":       df_vis = df_vis[df_vis["Política"]   == sel_pol]
                if sel_estrategia != "Todas":       df_vis = df_vis[df_vis["Estrategia"] == sel_estrategia]
                if sel_resp       != "Todas":       df_vis = df_vis[df_vis["Responsable"].str.contains(sel_resp, na=False)]
                if sel_est        == "🚫 Vencidas": df_vis = df_vis[df_vis["_vencida"]   == True]
                elif sel_est      != "Todos":       df_vis = df_vis[df_vis["Estado"]     == sel_est]

                st.caption(f"Mostrando **{len(df_vis)}** de {len(df_tasks)} tareas")
                st.markdown("<br>", unsafe_allow_html=True)

                # ── TARJETAS DE TAREA ─────────────────────────────────
                if df_vis.empty:
                    st.info("Ninguna tarea coincide con los filtros seleccionados.")
                else:
                    for _, row in df_vis.iterrows():
                        border = "#ef4444" if row["_vencida"] else _status_color(row["Estado"])
                        with st.container():
                            c1, c2, c3 = st.columns([4, 1.5, 0.8])
                            with c1:
                                st.markdown(
                                    f"<div style='border-left:4px solid {border};padding-left:10px;margin-bottom:4px;'>"
                                    f"<b>{html.escape(str(row['Tarea']))}</b><br>"
                                    f"<span style='font-size:0.78rem;color:#64748b;'>"
                                    f"📁 {html.escape(str(row['Política']))} › {html.escape(str(row['Estrategia']))}</span>"
                                    f"</div>",
                                    unsafe_allow_html=True
                                )
                                st.caption(f"👤 {row['Responsable']}  ·  🗓️ Fin: {row['Fin']}")
                            with c2:
                                pct = row["Avance"] / 100
                                st.progress(pct)
                                badge_color = "#10b981" if row["Estado"] == "Cumplida" else ("#f59e0b" if row["Estado"] == "En Proceso" else "#94a3b8")
                                st.markdown(
                                    f"<span style='background:{badge_color}22;color:{badge_color};"
                                    f"padding:2px 8px;border-radius:8px;font-size:0.75rem;font-weight:600;'>"
                                    f"{row['Estado']} · {row['Avance']:.0f}%</span>",
                                    unsafe_allow_html=True
                                )
                            with c3:
                                if st.button("✏️ Editar", key=f"edit_sup_{row['_task_id']}", use_container_width=True):
                                    task_obj = db.query(Task).filter(Task.id == row["_task_id"]).first()
                                    if task_obj:
                                        edit_task_dialog(db, task_obj.id)
                            st.markdown("<hr style='margin:6px 0;border:none;border-top:1px solid #f1f5f9;'>",
                                        unsafe_allow_html=True)

        # ═══════════════════════════════════════════════════════════════
        # TAB 3 — HISTORIAL DE CAMBIOS (2.2)
        # ═══════════════════════════════════════════════════════════════
        with tab_historial:
            st.subheader("📋 Historial de Cambios")
            st.caption("Registro completo de modificaciones en el estado y avance de las tareas.")

            logs = db.query(ChangeLog).order_by(ChangeLog.changed_at.desc()).limit(200).all()

            if not logs:
                st.info("Aún no hay cambios registrados. Los cambios se registran automáticamente al editar tareas.")
            else:
                # Filtro rápido
                col_u, col_f = st.columns([1, 1])
                users_in_log = sorted(set(l.changed_by for l in logs))
                sel_user = col_u.selectbox("Filtrar por usuario", ["Todos"] + users_in_log, key="hist_user")
                sel_field = col_f.selectbox("Filtrar por campo", ["Todos", "status", "progress"], key="hist_field")

                rows_log = []
                for l in logs:
                    if sel_user != "Todos" and l.changed_by != sel_user: continue
                    if sel_field != "Todos" and l.field_changed != sel_field: continue
                    rows_log.append({
                        "Fecha":      l.changed_at.strftime("%d/%m/%y %H:%M"),
                        "Usuario":    l.changed_by,
                        "Tarea":      l.entity_name[:60] + ("…" if len(l.entity_name) > 60 else ""),
                        "Campo":      l.field_changed,
                        "Antes":      l.old_value or "—",
                        "Después":    l.new_value or "—",
                    })

                if rows_log:
                    st.dataframe(pd.DataFrame(rows_log), use_container_width=True, hide_index=True)
                else:
                    st.info("No hay cambios con los filtros seleccionados.")

            st.divider()
            st.subheader("⚠️ Justificaciones de Retrasos")
            st.caption("Tareas que tuvieron un retraso documentado.")

            overdue_tasks = db.query(Task).filter(Task.delay_justification != None).all()
            if not overdue_tasks:
                st.success("✅ No hay retrasos justificados registrados.")
            else:
                for t in overdue_tasks:
                    with st.container(border=True):
                        st.markdown(f"**{html.escape(t.name)}**")
                        st.caption(f"Actividad: {html.escape(t.activity.name)}")
                        st.warning(f"⚠️ {t.delay_justification}")

    finally:
        db.close()
