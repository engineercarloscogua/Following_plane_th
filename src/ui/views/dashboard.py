import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from sqlalchemy.orm import joinedload
from src.core.database import SessionLocal
from src.models.entities import PlanMacro, Policy, StrategicItem, Activity, Task, Responsible
from src.services.calculations import CalculationService
import pandas as pd
from datetime import datetime, timedelta
import html

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

COLORS = {
    "primary":   "#00594e",
    "secondary": "#b5a160",
    "neutral":   "#64748b",
    "success":   "#10b981",
    "warning":   "#f59e0b",
    "danger":    "#ef4444",
}

def _alert_banner(db):
    """Shows collapsible alert banners at the top of the dashboard."""
    now = datetime.now()
    vencidas = db.query(Task).options(
        joinedload(Task.responsibles),
        joinedload(Task.activity).joinedload(Activity.strategic_item).joinedload(StrategicItem.policy)
    ).filter(Task.status != "Cumplida", Task.end_date < now).all()

    proximas = db.query(Task).options(
        joinedload(Task.responsibles),
        joinedload(Task.activity).joinedload(Activity.strategic_item).joinedload(StrategicItem.policy)
    ).filter(
        Task.status != "Cumplida",
        Task.end_date >= now,
        Task.end_date <= now + timedelta(days=7)
    ).all()

    if not vencidas and not proximas:
        return  # Nothing urgent — don't show banners

    if vencidas:
        with st.expander(f"🔴 **{len(vencidas)} tarea(s) VENCIDA(S)** — Sin cumplir dentro del plazo", expanded=True):
            for t in vencidas:
                dias = (now - t.end_date).days
                res  = ", ".join(r.name for r in t.responsibles) if t.responsibles else "Sin asignar"
                pol  = t.activity.strategic_item.policy.name if t.activity and t.activity.strategic_item else "—"
                st.markdown(
                    f"- **{html.escape(t.name)}** · `{res}` · "
                    f"<span style='color:#ef4444;'>Venció hace {dias} día(s)</span> · _{html.escape(pol)}_",
                    unsafe_allow_html=True
                )

    if proximas:
        with st.expander(f"🟡 **{len(proximas)} tarea(s)** vencen esta semana", expanded=False):
            for t in proximas:
                dias = (t.end_date - now).days
                res  = ", ".join(r.name for r in t.responsibles) if t.responsibles else "Sin asignar"
                pol  = t.activity.strategic_item.policy.name if t.activity and t.activity.strategic_item else "—"
                st.markdown(
                    f"- **{html.escape(t.name)}** · `{res}` · "
                    f"<span style='color:#f59e0b;'>Vence en {dias} día(s)</span> · _{html.escape(pol)}_",
                    unsafe_allow_html=True
                )

    st.markdown("<br>", unsafe_allow_html=True)


def _team_table(db, macro):
    """Shows a summary table of all responsibles and their task progress."""
    responsibles = db.query(Responsible).all()
    rows = []
    now  = datetime.now()

    for r in responsibles:
        tasks_year = [
            t for t in r.tasks
            if t.activity and t.activity.strategic_item
            and t.activity.strategic_item.policy
            and t.activity.strategic_item.policy.plan_macro_id == macro.id
        ]
        if not tasks_year:
            continue

        total     = len(tasks_year)
        cumplidas = sum(1 for t in tasks_year if t.status == "Cumplida")
        vencidas  = sum(1 for t in tasks_year if t.status != "Cumplida" and t.end_date and t.end_date < now)
        avg_prog  = sum(t.progress for t in tasks_year) / total

        semaforo = "🟢" if avg_prog >= 80 else ("🟡" if avg_prog >= 50 else "🔴")
        rows.append({
            "Funcionaria":  r.name,
            "Cargo":        r.role,
            "Total":        total,
            "✅ Cumplidas": cumplidas,
            "🚫 Vencidas":  vencidas,
            "Avance %":     round(avg_prog, 1),
            " ":            semaforo,
        })

    if not rows:
        st.info("No hay responsables con tareas asignadas en este plan.")
        return

    df = pd.DataFrame(rows).sort_values("Avance %", ascending=False)
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Avance %": st.column_config.ProgressColumn(
                "Avance %", format="%.1f%%", min_value=0, max_value=100
            )
        }
    )

# ─────────────────────────────────────────────────────────────────────────────
# Main view
# ─────────────────────────────────────────────────────────────────────────────

def show_executive_dashboard():
    """
    Tablero de control estratégico con alertas integradas, métricas clave,
    gráficos de cumplimiento y tabla de equipo.
    """
    st.markdown("<div class='corporate-header'>", unsafe_allow_html=True)
    st.title("🏛️ Tablero de Control Estratégico TH")
    st.write("Seguimiento integral: alertas, políticas, programas y equipo.")
    st.markdown("</div>", unsafe_allow_html=True)

    db = SessionLocal()
    try:
        macros = db.query(PlanMacro).options(
            joinedload(PlanMacro.policies).joinedload(Policy.strategic_items)
            .joinedload(StrategicItem.activities).joinedload(Activity.tasks)
        ).all()

        if not macros:
            return st.info("No hay datos registrados para análisis.")

        # ── AÑO ────────────────────────────────────────────────────────
        all_years = sorted(set(m.year for m in macros))
        col_year, _ = st.columns([1, 3])
        sel_year = col_year.selectbox("📅 Año de gestión", all_years,
                                      index=all_years.index(datetime.now().year)
                                      if datetime.now().year in all_years else len(all_years) - 1)
        macro = next((m for m in macros if m.year == sel_year), macros[-1])

        # ── ALERTAS AL TOPE ────────────────────────────────────────────
        _alert_banner(db)

        # ── MÉTRICAS PRINCIPALES ───────────────────────────────────────
        tasks_all = [
            t for pol in macro.policies
            for si in pol.strategic_items
            for act in si.activities
            for t in act.tasks
        ]
        now          = datetime.now()
        en_proceso   = sum(1 for t in tasks_all if t.status == "En Proceso")
        n_resp       = db.query(Responsible).count()

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("📊 Avance Consolidado",  f"{macro.progress:.1f}%")
        k2.metric("📂 Políticas",           len(macro.policies))
        k3.metric("⚙️ En Proceso",          en_proceso)
        k4.metric("👥 Funcionarias",        n_resp)

        st.divider()

        # ── GRÁFICOS: VELOCÍMETRO + BARRAS POR POLÍTICA ────────────────
        col_left, col_right = st.columns([1, 1.2])

        with col_left:
            _, color = CalculationService.get_semaforo(macro.progress)
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number", value=macro.progress,
                number={"suffix": "%", "valueformat": ".1f"},
                title={"text": "Avance Consolidado TH", "font": {"size": 17, "color": COLORS["primary"]}},
                gauge={
                    "axis": {"range": [None, 100]},
                    "bar":  {"color": color},
                    "steps": [
                        {"range": [0,  60], "color": "#fee2e2"},
                        {"range": [60, 80], "color": "#fef3c7"},
                        {"range": [80, 100], "color": "#d1fae5"},
                    ],
                }
            ))
            fig_gauge.update_layout(height=320, margin=dict(l=20, r=20, t=50, b=10), template="plotly_white")
            st.plotly_chart(fig_gauge, use_container_width=True)

        with col_right:
            pol_data = [{"Nombre": p.name, "Avance": p.progress} for p in macro.policies]
            df_pol   = pd.DataFrame(pol_data).sort_values("Avance", ascending=True)
            fig_pol  = px.bar(
                df_pol, x="Avance", y="Nombre", orientation="h",
                title="Cumplimiento por Política",
                color="Avance",
                color_continuous_scale=[[0, "#ef4444"], [0.5, "#f59e0b"], [1, "#10b981"]],
                template="plotly_white"
            )
            fig_pol.update_traces(texttemplate="%{x:.1f}%", textposition="outside")
            fig_pol.update_layout(
                showlegend=False,
                xaxis=dict(range=[0, 110]),
                yaxis=dict(title=""),
                height=320,
                margin=dict(l=10, r=30, t=50, b=10)
            )
            st.plotly_chart(fig_pol, use_container_width=True)

        st.divider()

        # ── TREEMAP DESGLOSE ESTRATÉGICO ───────────────────────────────
        tasks_data = []
        for pol in macro.policies:
            for si in pol.strategic_items:
                for act in si.activities:
                    for t in act.tasks:
                        # Truncar nombre de estrategia para legibilidad e incrementar tamaño de letra
                        short_estr = si.name[:50] + "..." if len(si.name) > 50 else si.name
                        tasks_data.append({
                            "Política":      pol.name,
                            "Estrategia":    short_estr,
                            "Avance":        t.progress,
                        })

        df_f = pd.DataFrame(tasks_data)
        if not df_f.empty:
            st.subheader("🧩 Desglose Estratégico")
            df_f["Peso"] = 1
            fig_tree = px.treemap(
                df_f,
                path=[px.Constant("Plan TH"), "Política", "Estrategia"],
                values="Peso",
                color="Avance",
                color_continuous_scale=[[0, "#fee2e2"], [0.5, "#fef3c7"], [1, "#d1fae5"]],
                title="Mapa de calor — volumen y avance por área"
            )
            fig_tree.update_traces(
                texttemplate="<b>%{label}</b><br>%{color:.1f}%",
                hovertemplate="<b>%{label}</b><br>Avance: %{color:.1f}%<extra></extra>",
                marker=dict(line=dict(color="#fff", width=2)),
                textfont=dict(size=14)  # Forzar tamaño de fuente visible
            )
            fig_tree.update_layout(margin=dict(t=40, l=0, r=0, b=0), height=450)
            st.plotly_chart(fig_tree, use_container_width=True)
        else:
            st.info("Sin hitos estratégicos configurados.")

        st.divider()

        # ── TABLA DE EQUIPO ────────────────────────────────────────────
        st.subheader("👥 Avance por Funcionaria")
        _team_table(db, macro)

        st.divider()

        # ── PROYECCIÓN DE CUMPLIMIENTO (2.6) ──────────────────────────
        st.subheader("📈 Proyección de Cumplimiento")
        st.caption("Estimación de cuándo se alcanzará el 100% al ritmo actual de avance.")

        from datetime import timedelta
        tasks_active = [
            t for pol in macro.policies
            for si in pol.strategic_items
            for act in si.activities
            for t in act.tasks
            if t.status != "Cumplida"
        ]

        # Calcular velocidad promedio: progreso acumulado / días transcurridos
        now_dt = datetime.now()
        velocidades = []
        for t in tasks_active:
            if t.start_date and t.progress > 0:
                dias_trans = max((now_dt - t.start_date).days, 1)
                vel = t.progress / dias_trans  # % por día
                velocidades.append(vel)

        current_prog = macro.progress
        if velocidades and current_prog < 100:
            vel_promedio = sum(velocidades) / len(velocidades)
            restante     = 100 - current_prog
            dias_proy    = int(restante / vel_promedio) if vel_promedio > 0 else None
            fecha_proy   = now_dt + timedelta(days=dias_proy) if dias_proy else None

            pc1, pc2, pc3 = st.columns(3)
            pc1.metric("🚀 Velocidad actual", f"{vel_promedio:.2f}% / día")
            pc2.metric("🎯 Restante para 100%", f"{restante:.1f}%")
            if fecha_proy:
                pc3.metric(
                    "📅 Fecha estimada de cierre",
                    fecha_proy.strftime("%d/%m/%Y"),
                    delta=f"en {dias_proy} días",
                    delta_color="normal" if dias_proy > 0 else "inverse"
                )

            # Mini gráfico de proyección lineal
            fechas_hist = [now_dt - timedelta(days=30), now_dt]
            prog_hist   = [max(current_prog - vel_promedio * 30, 0), current_prog]
            if fecha_proy and dias_proy < 730:  # Solo proyectar si < 2 años
                fechas_proj = [now_dt, fecha_proy]
                prog_proj   = [current_prog, 100]

                fig_proj = go.Figure()
                fig_proj.add_trace(go.Scatter(
                    x=fechas_hist, y=prog_hist, mode="lines+markers",
                    name="Avance real", line=dict(color="#00594e", width=3)
                ))
                fig_proj.add_trace(go.Scatter(
                    x=fechas_proj, y=prog_proj, mode="lines",
                    name="Proyección", line=dict(color="#b5a160", width=2, dash="dash")
                ))
                fig_proj.add_hline(y=100, line_dash="dot", line_color="#10b981",
                                   annotation_text="100% ✅")
                fig_proj.update_layout(
                    height=260, template="plotly_white",
                    yaxis=dict(range=[0, 110], title="% Avance"),
                    margin=dict(l=10, r=10, t=20, b=20),
                    legend=dict(orientation="h", y=-0.3)
                )
                st.plotly_chart(fig_proj, use_container_width=True)
        elif current_prog >= 100:
            st.success("🎉 ¡Plan al 100%! Todos los objetivos están cumplidos.")
        else:
            st.info("No hay suficientes datos para proyectar. Actualiza el avance de las tareas para generar la proyección.")

    finally:
        db.close()
