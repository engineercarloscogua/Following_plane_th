import streamlit as st
from sqlalchemy.orm import joinedload
from src.core.database import SessionLocal
from src.models.entities import Task, Activity, Evidence, Responsible
from src.services.calculations import CalculationService
from datetime import datetime, timedelta
import html

def show_worker_view():
    """
    Vista personalizada para Workers.
    Muestra las tareas asignadas ordenadas por urgencia.
    Permite reportar avance con slider 0-100% y cargar evidencias.
    """
    st.markdown("<div class='corporate-header'>", unsafe_allow_html=True)
    st.title("👷 Mis Tareas")
    st.write("Gestiona tus tareas asignadas, carga evidencias y reporta tu avance real.")
    st.markdown("</div>", unsafe_allow_html=True)

    responsible_id = st.session_state.get("responsible_id")
    username = st.session_state.get("username", "")
    if not responsible_id:
        st.warning("⚠️ Tu cuenta no está vinculada a un perfil de Responsable. Contacta al Administrador.")
        return

    db = SessionLocal()
    try:
        tasks = db.query(Task).join(Task.responsibles).filter(
            Responsible.id == responsible_id
        ).options(
            joinedload(Task.activity),
            joinedload(Task.responsibles),
            joinedload(Task.evidences)
        ).all()

        if not tasks:
            st.success("🎉 No tienes tareas pendientes asignadas.")
            return

        now = datetime.now()

        # Clasificar por urgencia
        vencidas  = [t for t in tasks if t.status != "Cumplida" and t.end_date and t.end_date < now]
        proximas  = [t for t in tasks if t.status != "Cumplida" and t.end_date and now <= t.end_date <= now + timedelta(days=7)]
        restantes = [t for t in tasks if t.status not in ["Cumplida"] and t not in vencidas and t not in proximas]
        cumplidas = [t for t in tasks if t.status == "Cumplida"]

        # ── MÉTRICAS ──────────────────────────────────────────────────
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("📋 Total", len(tasks))
        c2.metric("🚫 Vencidas", len(vencidas), delta=f"-{len(vencidas)}" if vencidas else None, delta_color="inverse")
        c3.metric("⏳ Esta semana", len(proximas))
        c4.metric("✅ Cumplidas", len(cumplidas))
        st.divider()

        def render_task_card(t, urgency_label, border_color):
            """Renders a single task card with progress slider and evidence upload."""
            ev_list = db.query(Evidence).filter(Evidence.task_id == t.id).all()
            act = t.activity

            with st.container(border=True):
                if t.is_locked:
                    st.warning("🔒 Periodo cerrado para auditoría (Modo Solo Lectura)")

                # Cabecera de tarea
                col_h, col_prog = st.columns([3, 1])
                with col_h:
                    st.markdown(
                        f"<div style='border-left:4px solid {border_color}; padding-left:10px;'>"
                        f"<b style='font-size:1rem;'>{html.escape(t.name)}</b><br>"
                        f"<span style='font-size:0.8rem;color:#64748b;'>🎯 {html.escape(act.name)}</span>"
                        f"</div>",
                        unsafe_allow_html=True
                    )
                with col_prog:
                    st.markdown(
                        f"<div style='text-align:center;padding:8px;background:{border_color}15;border-radius:8px;'>"
                        f"<b style='font-size:1.4rem;color:{border_color};'>{t.progress:.0f}%</b><br>"
                        f"<span style='font-size:0.7rem;color:#64748b;'>{urgency_label}</span>"
                        f"</div>",
                        unsafe_allow_html=True
                    )

                # Fechas
                if t.start_date and t.end_date:
                    days_left = (t.end_date - now).days
                    days_str  = f"Vence en {days_left}d" if days_left >= 0 else f"Venció hace {-days_left}d"
                    st.caption(f"📅 {t.start_date.strftime('%d/%m/%y')} → {t.end_date.strftime('%d/%m/%y')}  ·  {days_str}")

                st.markdown("<br>", unsafe_allow_html=True)

                # ── CONTROLES DE AVANCE ────────────────────────────────────
                col_sl, col_ev = st.columns([2, 1])
                with col_sl:
                    new_progress = st.slider(
                        "Avance real (%)",
                        min_value=0, max_value=100,
                        value=int(t.progress),
                        key=f"prog_{t.id}",
                        help="Arrastra para indicar el % real de avance de esta tarea.",
                        disabled=t.is_locked
                    )
                    # Auto-sugerir estado
                    if new_progress == 0:
                        suggested_status = "Pendiente"
                    else:
                        suggested_status = "En Proceso"
                    new_status = suggested_status  # Worker no puede marcar "Cumplida" directamente

                with col_ev:
                    st.caption("🔗 Evidencias cargadas")
                    if ev_list:
                        for ev in ev_list:
                            url = ev.url if ev.url.startswith(("http://", "https://")) else f"https://{ev.url}"
                            ev_date = ev.uploaded_at.strftime('%d/%m/%y') if ev.uploaded_at else ""
                            who = ev.uploaded_by_name or "sistema"
                            st.markdown(f"- [Ver]({url}) · `{ev_date}` · 👤 `{who}`")
                    else:
                        st.caption("_Sin evidencias aún_")

                # Añadir evidencia
                with st.expander("➕ Añadir enlace de evidencia", expanded=False):
                    new_ev = st.text_input(
                        "Enlace (Drive, SharePoint, PDF en la nube…)",
                        placeholder="https://drive.google.com/...",
                        key=f"ev_{t.id}",
                        disabled=t.is_locked
                    )
                    ev_desc = st.text_input("Descripción breve", placeholder="Ej: Acta firmada", key=f"evd_{t.id}", disabled=t.is_locked)

                # Observaciones
                obs = st.text_area(
                    "📝 Observación de ejecución",
                    value=t.observations or "",
                    key=f"obs_{t.id}",
                    placeholder="Describe qué hiciste concretamente en esta tarea…",
                    height=80,
                    disabled=t.is_locked
                )

                # Guardar
                if st.button("💾 Reportar Avance", key=f"save_{t.id}", use_container_width=True, type="primary", disabled=t.is_locked):
                    t.status      = new_status
                    t.progress    = float(new_progress)
                    t.observations= obs
                    if new_ev and new_ev.strip():
                        db.add(Evidence(task_id=t.id, url=new_ev.strip(), description=ev_desc or None, uploaded_by_name=username))
                    db.add(t)
                    db.commit()
                    CalculationService.update_all_levels(db, t.id)
                    st.success(f"✅ Avance actualizado a {new_progress}%")
                    st.rerun()

        # ── VENCIDAS ─────────────────────────────────────────────────
        if vencidas:
            st.error(f"🚫 Tareas vencidas ({len(vencidas)}) — Requieren atención inmediata")
            for t in vencidas:
                render_task_card(t, "VENCIDA", "#ef4444")
            st.markdown("<br>", unsafe_allow_html=True)

        # ── PRÓXIMAS (esta semana) ────────────────────────────────────
        if proximas:
            st.warning(f"⏳ Vencen esta semana ({len(proximas)})")
            for t in proximas:
                render_task_card(t, "ESTA SEMANA", "#f59e0b")
            st.markdown("<br>", unsafe_allow_html=True)

        # ── RESTANTES ────────────────────────────────────────────────
        if restantes:
            with st.expander(f"📋 Otras tareas activas ({len(restantes)})", expanded=len(vencidas) + len(proximas) == 0):
                for t in restantes:
                    render_task_card(t, "ACTIVA", "#3b82f6")

        # ── HISTORIAL (cumplidas) ─────────────────────────────────────
        if cumplidas:
            with st.expander(f"✅ Historial — tareas cumplidas ({len(cumplidas)})", expanded=False):
                for t in cumplidas:
                    ev_list = db.query(Evidence).filter(Evidence.task_id == t.id).all()
                    with st.container(border=True):
                        st.markdown(
                            f"<b style='color:#10b981;'>✅ {html.escape(t.name)}</b>  "
                            f"<span style='font-size:0.8rem;color:#64748b;'>— {t.fulfillment_date.strftime('%d/%m/%Y') if t.fulfillment_date else 'Fecha no registrada'}</span>",
                            unsafe_allow_html=True
                        )
                        if ev_list:
                            for ev in ev_list:
                                url = ev.url if ev.url.startswith(("http://", "https://")) else f"https://{ev.url}"
                                st.markdown(f"  🔗 [Ver Evidencia]({url})")

    finally:
        db.close()
