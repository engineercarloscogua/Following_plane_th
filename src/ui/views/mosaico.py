import streamlit as st
import plotly.express as px
import pandas as pd
from src.core.database import SessionLocal
from src.models.entities import PlanMacro, Policy, StrategicItem, Activity, Task
from sqlalchemy.orm import joinedload
from datetime import datetime
import html

def show_mosaico_view():
    """
    Estructura TH — Vista jerárquica colapsable de toda la estructura institucional.
    Tab 1: árbol Macro → Política → Estrategia → Actividad → Tarea.
    Tab 2: Cronograma Gantt — línea de tiempo de actividades y tareas (2.1).
    Tab 3: Tablero Kanban de tareas por estado.
    """
    st.markdown("<div class='corporate-header'>", unsafe_allow_html=True)
    st.title("🧩 Estructura TH")
    st.write("Explorador jerárquico integral por vigencia fiscal")
    st.markdown("</div>", unsafe_allow_html=True)

    db = SessionLocal()
    try:
        macros_all = db.query(PlanMacro).all()
        if not macros_all:
            st.info("No hay información registrada.")
            return

        all_years = sorted(list(set([m.year for m in macros_all])))
        sel_year = st.selectbox("📅 Vigencia Fiscal", all_years, index=len(all_years) - 1)

        macros = db.query(PlanMacro).filter(PlanMacro.year == sel_year).options(
            joinedload(PlanMacro.policies)
            .joinedload(Policy.strategic_items)
            .joinedload(StrategicItem.activities)
            .joinedload(Activity.tasks)
        ).all()

        tab_tree, tab_gantt, tab_kanban = st.tabs(["🧩 Vista Jerárquica", "📅 Cronograma Gantt", "📋 Kanban"])

        # ═══════════════════════════════════════════════════════════════════
        # TAB 1 — VISTA JERÁRQUICA
        # ═══════════════════════════════════════════════════════════════════
        with tab_tree:
            for macro in macros:
                with st.expander(f"🏛️ **{macro.name}** — Avance: {macro.progress:.1f}%", expanded=True):
                    for pol in macro.policies:
                        with st.expander(f"📂 **{html.escape(pol.name)}** — {pol.progress:.1f}%", expanded=False):
                            st.progress(pol.progress / 100)
                            st.markdown("<br>", unsafe_allow_html=True)
                            for si in pol.strategic_items:
                                with st.expander(f"📝 {html.escape(si.type)}: {html.escape(si.name)} — {si.progress:.1f}%"):
                                    for act in si.activities:
                                        pct = act.progress / 100
                                        sem = "🟢" if pct >= 0.8 else ("🟡" if pct >= 0.5 else "🔴")
                                        st.markdown(f"**⚡ {sem} {html.escape(act.name)}** — `{act.progress:.1f}%`")
                                        st.progress(pct)
                                        cols = st.columns(3)
                                        for idx, t in enumerate(act.tasks):
                                            sc = "#10b981" if t.status == "Cumplida" else ("#f59e0b" if t.status == "En Proceso" else "#94a3b8")
                                            with cols[idx % 3]:
                                                st.markdown(
                                                    f"<div style='background:white;padding:10px;border-radius:8px;"
                                                    f"border-left:4px solid {sc};margin-bottom:8px;"
                                                    f"box-shadow:0 1px 3px rgba(0,0,0,0.08);'>"
                                                    f"<p style='margin:0;font-size:0.88rem;'><b>{html.escape(t.name)}</b></p>"
                                                    f"<p style='margin:0;font-size:0.78rem;color:#64748b;'>{t.status} · {t.progress:.0f}%</p>"
                                                    f"</div>",
                                                    unsafe_allow_html=True
                                                )
                                        st.markdown("<br>", unsafe_allow_html=True)

        # ═══════════════════════════════════════════════════════════════════
        # TAB 2 — CRONOGRAMA GANTT (2.1)
        # ═══════════════════════════════════════════════════════════════════
        with tab_gantt:
            st.subheader("📅 Cronograma de Actividades y Tareas")
            st.caption("Línea de tiempo basada en fechas de inicio y fin configuradas.")

            # Recopilar datos para el Gantt
            gantt_rows = []
            for macro in macros:
                for pol in macro.policies:
                    for si in pol.strategic_items:
                        for act in si.activities:
                            for t in act.tasks:
                                if t.start_date and t.end_date:
                                    pct = t.progress
                                    color_status = (
                                        "Cumplida" if t.status == "Cumplida"
                                        else ("En Proceso" if t.status == "En Proceso"
                                              else "Pendiente")
                                    )
                                    gantt_rows.append({
                                        "Tarea":     t.name[:55] + ("…" if len(t.name) > 55 else ""),
                                        "Política":  pol.name,
                                        "Estrategia": si.name[:40] + ("…" if len(si.name) > 40 else ""),
                                        "Inicio":    t.start_date,
                                        "Fin":       t.end_date,
                                        "Avance %":  pct,
                                        "Estado":    color_status,
                                    })

            if not gantt_rows:
                st.warning("⚠️ No hay tareas con fechas de inicio y fin configuradas. Configúralas en **Seguimiento → Gestión de Tareas → ✏️ Editar**.")
            else:
                df_gantt = pd.DataFrame(gantt_rows)

                # Filtros del Gantt
                g1, g2 = st.columns([1, 1])
                pol_g = g1.selectbox("Política", ["Todas"] + sorted(df_gantt["Política"].unique().tolist()), key="gantt_pol")
                est_g = g2.selectbox("Estado", ["Todos", "Pendiente", "En Proceso", "Cumplida"], key="gantt_est")

                df_g = df_gantt.copy()
                if pol_g != "Todas": df_g = df_g[df_g["Política"] == pol_g]
                if est_g != "Todos": df_g = df_g[df_g["Estado"]   == est_g]

                if df_g.empty:
                    st.info("Ninguna tarea coincide con los filtros.")
                else:
                    color_map = {"Cumplida": "#10b981", "En Proceso": "#f59e0b", "Pendiente": "#94a3b8"}
                    fig_gantt = px.timeline(
                        df_g,
                        x_start="Inicio",
                        x_end="Fin",
                        y="Tarea",
                        color="Estado",
                        color_discrete_map=color_map,
                        hover_data={"Política": True, "Estrategia": True, "Avance %": True, "Estado": True},
                        title=f"Cronograma de Tareas — {sel_year}",
                        template="plotly_white",
                    )
                    fig_gantt.update_yaxes(autorange="reversed")
                    fig_gantt.update_layout(
                        height=max(400, len(df_g) * 28 + 120),
                        margin=dict(l=10, r=10, t=50, b=30),
                        legend_title="Estado",
                    )
                    # Línea de hoy
                    fig_gantt.add_vline(
                        x=datetime.now().timestamp() * 1000,
                        line_dash="dash",
                        line_color="#ef4444",
                        annotation_text="Hoy",
                        annotation_position="top right"
                    )
                    st.plotly_chart(fig_gantt, use_container_width=True)
                    st.caption(f"Mostrando **{len(df_g)}** tareas con cronograma.")

        # ═══════════════════════════════════════════════════════════════════
        # TAB 3 — KANBAN
        # ═══════════════════════════════════════════════════════════════════
        with tab_kanban:
            st.subheader("📋 Tablero Kanban de Tareas")
            st.write("Estado de todas las tareas operativas organizadas por avance.")

            tasks_pendientes, tasks_proceso, tasks_cumplidas = [], [], []

            for m in macros:
                for pol in m.policies:
                    for si in pol.strategic_items:
                        for act in si.activities:
                            for t in act.tasks:
                                t._policy_name   = pol.name
                                t._activity_name = act.name
                                if t.status == "Cumplida":        tasks_cumplidas.append(t)
                                elif t.status == "En Proceso":    tasks_proceso.append(t)
                                else:                             tasks_pendientes.append(t)

            def render_kanban_card(column, t, border_color):
                res_badges = "".join([
                    f"<span style='font-size:0.7rem;margin-right:4px;padding:2px 6px;"
                    f"background:#f1f5f9;color:#475569;border:1px solid #cbd5e1;border-radius:6px;'>"
                    f"👤 {html.escape(r.name)}</span>"
                    for r in t.responsibles
                ])
                pol_short = html.escape(t._policy_name[:45]) + ("…" if len(t._policy_name) > 45 else "")
                act_short = html.escape(t._activity_name[:65]) + ("…" if len(t._activity_name) > 65 else "")
                fin_str   = t.end_date.strftime('%d/%m/%y') if t.end_date else "S/F"
                column.markdown(
                    f"<div style='background:white;padding:12px;border-radius:10px;"
                    f"border-left:5px solid {border_color};margin-bottom:12px;"
                    f"box-shadow:0 2px 6px rgba(0,0,0,0.07);'>"
                    f"<div style='font-size:0.72rem;font-weight:700;color:#00594e;margin-bottom:4px;'>📁 {pol_short}</div>"
                    f"<div style='font-size:0.9rem;font-weight:700;color:#1e293b;margin-bottom:6px;'>{html.escape(t.name)}</div>"
                    f"<div style='font-size:0.77rem;color:#64748b;margin-bottom:8px;'>🎯 {act_short}</div>"
                    f"<div style='display:flex;justify-content:space-between;font-size:0.78rem;margin-bottom:6px;'>"
                    f"<span><b>{t.progress:.0f}%</b></span><span style='color:#ef4444;'>🗓️ {fin_str}</span></div>"
                    f"<div style='background:#e2e8f0;border-radius:4px;height:5px;margin-bottom:10px;'>"
                    f"<div style='background:{border_color};width:{t.progress}%;height:100%;border-radius:4px;'></div></div>"
                    f"<div>{res_badges if res_badges else '<span style=\"font-size:0.75rem;color:#94a3b8;font-style:italic;\">Sin asignar</span>'}</div>"
                    f"</div>",
                    unsafe_allow_html=True
                )

            c_pend, c_proc, c_cump = st.columns(3)
            with c_pend:
                st.markdown(f"#### 📋 Pendientes ({len(tasks_pendientes)})")
                st.markdown("<hr style='margin:4px 0 12px;border-top:3px solid #94a3b8;'>", unsafe_allow_html=True)
                for t in tasks_pendientes: render_kanban_card(c_pend, t, "#94a3b8")
                if not tasks_pendientes: st.caption("Sin tareas pendientes")

            with c_proc:
                st.markdown(f"#### ⏳ En Proceso ({len(tasks_proceso)})")
                st.markdown("<hr style='margin:4px 0 12px;border-top:3px solid #f59e0b;'>", unsafe_allow_html=True)
                for t in tasks_proceso: render_kanban_card(c_proc, t, "#f59e0b")
                if not tasks_proceso: st.caption("Sin tareas en proceso")

            with c_cump:
                st.markdown(f"#### ✅ Cumplidas ({len(tasks_cumplidas)})")
                st.markdown("<hr style='margin:4px 0 12px;border-top:3px solid #10b981;'>", unsafe_allow_html=True)
                for t in tasks_cumplidas: render_kanban_card(c_cump, t, "#10b981")
                if not tasks_cumplidas: st.caption("Sin tareas cumplidas")

    finally:
        db.close()
