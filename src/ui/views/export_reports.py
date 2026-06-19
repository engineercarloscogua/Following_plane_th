import streamlit as st
import calendar
from datetime import datetime, date
from src.core.database import SessionLocal
from src.services.word_exporter import WordExporterService
from src.services.excel_exporter import build_excel_report, OPENPYXL_OK
from src.services.pdf_exporter import PdfExporterService

def show_export_reports_view():
    """
    Renders the UI for filtering and exporting Word and Excel reports.
    """
    st.markdown("<div class='corporate-header'>", unsafe_allow_html=True)
    st.title("📄 Exportar Reportes")
    st.write("Descarga el informe ejecutivo en Word o Excel, filtrado por período.")
    st.markdown("</div>", unsafe_allow_html=True)

    with st.container(border=True):
        st.subheader("Filtros de Exportación")
        
        c1, c2 = st.columns(2)
        with c1:
            current_year = datetime.now().year
            years = list(range(2024, 2036))
            selected_year = st.selectbox("Año", years, index=years.index(current_year) if current_year in years else 0)
            
        with c2:
            filter_type = st.selectbox("Tipo de Filtro", ["Año Completo", "Semestre", "Trimestre", "Mes"])
            
        # Dynamic second filter
        start_dt = None
        end_dt = None
        filter_label = ""
        
        if filter_type == "Año Completo":
            start_dt = datetime(selected_year, 1, 1)
            end_dt = datetime(selected_year, 12, 31, 23, 59, 59)
            filter_label = f"Año {selected_year}"
            
        elif filter_type == "Semestre":
            sem = st.selectbox("Seleccione el Semestre", ["Semestre 1 (Ene-Jun)", "Semestre 2 (Jul-Dic)"])
            if "1" in sem:
                start_dt = datetime(selected_year, 1, 1)
                end_dt = datetime(selected_year, 6, 30, 23, 59, 59)
                filter_label = f"Primer Semestre {selected_year}"
            else:
                start_dt = datetime(selected_year, 7, 1)
                end_dt = datetime(selected_year, 12, 31, 23, 59, 59)
                filter_label = f"Segundo Semestre {selected_year}"
                
        elif filter_type == "Trimestre":
            trim = st.selectbox("Seleccione el Trimestre", ["Q1 (Ene-Mar)", "Q2 (Abr-Jun)", "Q3 (Jul-Sep)", "Q4 (Oct-Dic)"])
            if "Q1" in trim:
                start_dt = datetime(selected_year, 1, 1)
                end_dt = datetime(selected_year, 3, 31, 23, 59, 59)
            elif "Q2" in trim:
                start_dt = datetime(selected_year, 4, 1)
                end_dt = datetime(selected_year, 6, 30, 23, 59, 59)
            elif "Q3" in trim:
                start_dt = datetime(selected_year, 7, 1)
                end_dt = datetime(selected_year, 9, 30, 23, 59, 59)
            else:
                start_dt = datetime(selected_year, 10, 1)
                end_dt = datetime(selected_year, 12, 31, 23, 59, 59)
            filter_label = f"Trimestre {trim.split(' ')[0]} del {selected_year}"
            
        elif filter_type == "Mes":
            meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
            mes_str = st.selectbox("Seleccione el Mes", meses)
            mes_idx = meses.index(mes_str) + 1
            
            # Find the last day of the selected month
            last_day = calendar.monthrange(selected_year, mes_idx)[1]
            
            start_dt = datetime(selected_year, mes_idx, 1)
            end_dt = datetime(selected_year, mes_idx, last_day, 23, 59, 59)
            filter_label = f"Mes de {mes_str} del {selected_year}"

        st.info(f"📅 Rango seleccionado: {start_dt.strftime('%d/%m/%Y')} al {end_dt.strftime('%d/%m/%Y')}")

        st.markdown("<br>", unsafe_allow_html=True)
        
        tab_word, tab_excel, tab_pdf = st.tabs(["📝 Informe Word", "📊 Excel Ejecutivo", "📕 PDF Institucional"])
        
        with tab_word:
            st.subheader("📝 Generar Informe Word")
            st.caption("Exporta un reporte narrativo estructurado con todas las actividades, metas, responsables y observaciones del periodo filtrado.")
            if st.button("⚙️ Procesar Datos para Reporte Word", use_container_width=True, type="primary"):
                with st.spinner("Generando documento Word..."):
                    db = SessionLocal()
                    try:
                        bio = WordExporterService.generate_report(db, start_dt, end_dt, filter_label)
                        st.success("✅ Reporte Word generado.")
                        filename = f"reporte_TH_{filter_label.replace(' ', '_')}.docx"
                        st.download_button(
                            label="📥 Descargar Reporte en Word",
                            data=bio,
                            file_name=filename,
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            use_container_width=True
                        )
                    except Exception as e:
                        st.error(f"Error al generar reporte Word: {str(e)}")
                    finally:
                        db.close()

        with tab_excel:
            st.subheader("📊 Generar Excel Ejecutivo")
            st.caption("Genera un libro Excel corporativo con 4 hojas: Resumen por política, Detalle jerárquico completo, Avance por equipo y Trazabilidad de cambios.")
            if not OPENPYXL_OK:
                st.warning("⚠️ Instala `openpyxl` para habilitar la exportación Excel: `pip install openpyxl`")
            else:
                if st.button("📊 Generar Excel Ejecutivo", use_container_width=True, type="primary"):
                    with st.spinner("Generando Excel..."):
                        db = SessionLocal()
                        try:
                            buf = build_excel_report(db, year=selected_year)
                            if buf:
                                fname = f"Gestion_TH_{selected_year}_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
                                st.success("✅ Excel generado con éxito.")
                                st.download_button(
                                    label="📥 Descargar Excel",
                                    data=buf,
                                    file_name=fname,
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    use_container_width=True
                                )
                            else:
                                st.warning("No se encontraron datos para el año seleccionado.")
                        except Exception as e:
                            st.error(f"Error al generar Excel: {str(e)}")
                        finally:
                            db.close()

        with tab_pdf:
            st.subheader("📕 Generar PDF Institucional")
            st.caption("Exporta el reporte oficial con el membrete y logo de Unitrópico, tablas consolidadas con semáforos, firmas de autorización y diseño formal.")
            if st.button("📕 Generar PDF Oficial", use_container_width=True, type="primary"):
                with st.spinner("Generando PDF..."):
                    db = SessionLocal()
                    try:
                        pdf_data = PdfExporterService.generate_report(db, start_dt, end_dt, filter_label)
                        st.success("✅ Reporte PDF generado.")
                        filename = f"reporte_TH_{filter_label.replace(' ', '_')}.pdf"
                        st.download_button(
                            label="📥 Descargar PDF Oficial",
                            data=pdf_data,
                            file_name=filename,
                            mime="application/pdf",
                            use_container_width=True
                        )
                    except Exception as e:
                        st.error(f"Error al generar reporte PDF: {str(e)}")
                    finally:
                        db.close()
