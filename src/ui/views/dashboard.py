import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from sqlalchemy.orm import joinedload
from src.core.database import SessionLocal
from src.models.entities import PlanMacro, Policy, StrategicItem, Activity, Task
from src.services.calculations import CalculationService
import pandas as pd
from datetime import datetime

def show_executive_dashboard():
    db = SessionLocal()
    try:
        st.markdown("<div class='corporate-header'>", unsafe_allow_html=True)
        st.title("🏛️ Tablero de Control Estratégico TH")
        st.write("Seguimiento de Gestión Institucional Unitrópico")
        st.markdown("</div>", unsafe_allow_html=True)

        # 1. Filtros de Periodo
        col_f1, col_f2 = st.columns([1, 2])
        with col_f1:
            periodo = st.selectbox("Vista Temporal", ["Anual", "Semestral", "Trimestral", "Mensual"])
        
        # Cargar todos los datos con sus fechas
        macros = db.query(PlanMacro).options(
            joinedload(PlanMacro.policies).joinedload(Policy.strategic_items).joinedload(StrategicItem.activities).joinedload(Activity.tasks)
        ).all()
        
        if not macros: return st.info("No hay información registrada para mostrar indicadores.")

        m_map = {m.id: m for m in macros}
        m_id = st.selectbox("Gestión Macro para Análisis", options=list(m_map.keys()), format_func=lambda x: m_map[x].name)
        macro = m_map[m_id]

        # 2. Métricas de Cabecera (Resumen)
        st.subheader("📊 Indicadores de Desempeño")
        c1, c2, c3, c4 = st.columns(4)
        
        # Calcular métricas basadas en el periodo (Simulación de filtrado temporal)
        total_tasks = 0
        completed_tasks = 0
        for pol in macro.policies:
            for si in pol.strategic_items:
                for act in si.activities:
                    for t in act.tasks:
                        total_tasks += 1
                        if t.status == "Cumplida": completed_tasks += 1
        
        c1.metric("Avance Total", f"{macro.progress:.1f}%")
        c2.metric("Tareas Totales", total_tasks)
        c3.metric("Cumplidas", completed_tasks)
        c4.metric("Pendientes", total_tasks - completed_tasks)

        st.divider()

        # 3. Gráficos Principales
        col_g1, col_g2 = st.columns([1, 1.2])
        
        with col_g1:
            # Velocímetro (Gauge)
            status_text, color = CalculationService.get_semaforo(macro.progress)
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number", value = macro.progress,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Avance Consolidado Gestión TH", 'font': {'size': 18, 'color': '#00594e'}},
                gauge = {
                    'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "#00594e"},
                    'bar': {'color': color},
                    'bgcolor': "white",
                    'borderwidth': 2,
                    'bordercolor': "#e2e8f0",
                    'steps': [
                        {'range': [0, 60], 'color': '#fee2e2'},
                        {'range': [60, 80], 'color': '#fef3c7'},
                        {'range': [80, 100], 'color': '#d1fae5'}
                    ],
                }
            ))
            fig_gauge.update_layout(height=350, margin=dict(l=20, r=20, t=50, b=20))
            st.plotly_chart(fig_gauge, use_container_width=True)

        with col_g2:
            # Gráfico de Barras por Política
            pol_data = [{"Política": p.name, "Avance": p.progress} for p in macro.policies]
            if pol_data:
                df_pol = pd.DataFrame(pol_data)
                fig_bar = px.bar(df_pol, x="Política", y="Avance", 
                                 title="Avance por Política Institucional",
                                 color="Avance", color_continuous_scale='RdYlGn', range_color=[0, 100],
                                 text_auto='.1f')
                fig_bar.update_layout(height=350, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_bar, use_container_width=True)

        st.divider()

        # 4. Análisis Temporal (Progreso por Meses/Trimestres)
        st.subheader(f"📈 Trazabilidad Temporal ({periodo})")
        
        # Extraer datos temporales
        temp_data = []
        for pol in macro.policies:
            for si in pol.strategic_items:
                for act in si.activities:
                    for t in act.tasks:
                        if t.target_date:
                            date = t.target_date
                            month = date.strftime("%Y-%m")
                            quarter = f"{date.year}-Q{(date.month-1)//3 + 1}"
                            semester = f"{date.year}-S{(date.month-1)//6 + 1}"
                            temp_data.append({
                                "Fecha": date,
                                "Mes": month,
                                "Trimestre": quarter,
                                "Semestre": semester,
                                "Avance": t.progress,
                                "Peso": t.weight
                            })
        
        if temp_data:
            df_temp = pd.DataFrame(temp_data)
            group_col = "Mes" if periodo == "Mensual" else ("Trimestre" if periodo == "Trimestral" else "Semestre" if periodo == "Semestral" else "Fecha")
            
            if periodo == "Anual":
                df_grouped = df_temp.groupby(df_temp['Fecha'].dt.year)['Avance'].mean().reset_index()
                df_grouped.columns = ['Año', 'Avance Promedio']
                fig_line = px.line(df_grouped, x='Año', y='Avance Promedio', markers=True, title="Avance Promedio Anual")
            else:
                df_grouped = df_temp.groupby(group_col)['Avance'].mean().reset_index()
                fig_line = px.area(df_grouped, x=group_col, y='Avance', 
                                  title=f"Evolución del Avance {periodo}",
                                  line_shape='spline', markers=True)
            
            fig_line.update_traces(line_color='#00594e', fillcolor='rgba(0, 89, 78, 0.2)')
            st.plotly_chart(fig_line, use_container_width=True)

        # 5. Mapa de Calor (Treemap) de Programas
        st.subheader("🗺️ Mapa Estratégico de Programas y Planes")
        tree_items = []
        for pol in macro.policies:
            for si in pol.strategic_items:
                tree_items.append({
                    "Nombre": si.name,
                    "Política": pol.name,
                    "Avance": si.progress,
                    "Tipo": si.type
                })
        
        if tree_items:
            fig_tree = px.treemap(pd.DataFrame(tree_items), 
                                 path=["Política", "Nombre"], 
                                 values="Avance",
                                 color="Avance", 
                                 color_continuous_scale='RdYlGn', 
                                 range_color=[0, 100],
                                 hover_data=["Tipo"])
            fig_tree.update_layout(height=450)
            st.plotly_chart(fig_tree, use_container_width=True)

    finally:
        db.close()
