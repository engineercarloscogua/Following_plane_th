import io
import os
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from src.models.entities import PlanMacro, Policy, StrategicItem, Activity, Task, Evidence

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY

class PdfExporterService:
    """
    Servicio encargado de generar reportes oficiales en formato PDF con diseño institucional.
    """
    
    @staticmethod
    def draw_background(canvas, doc):
        canvas.saveState()
        # Colores institucionales
        primary_color = colors.HexColor("#00594e")
        gray_text = colors.HexColor("#64748b")
        
        # Línea superior de cabecera (verde institucional)
        canvas.setStrokeColor(primary_color)
        canvas.setLineWidth(2)
        canvas.line(54, 750, 558, 750) # Ancho carta: 612 x 792 pt
        
        # Texto cabecera
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(gray_text)
        canvas.drawString(54, 755, "UNIVERSIDAD INTERCULTURAL DE CASANARE - UNITRÓPICO")
        canvas.drawRightString(558, 755, "GESTIÓN DE TALENTO HUMANO (PA_TH)")
        
        # Línea inferior de pie de página
        canvas.setStrokeColor(colors.HexColor("#cbd5e1"))
        canvas.setLineWidth(1)
        canvas.line(54, 50, 558, 50)
        
        # Texto pie de página
        canvas.drawString(54, 38, f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}  ·  Confidencial")
        canvas.drawRightString(558, 38, f"Página {doc.page}")
        canvas.restoreState()

    @staticmethod
    def generate_report(db: Session, start_date: datetime, end_date: datetime, filter_label: str) -> io.BytesIO:
        # Cargar datos estratégicos
        target_year = start_date.year
        macro = db.query(PlanMacro).filter(PlanMacro.year == target_year).options(
            joinedload(PlanMacro.policies)
            .joinedload(Policy.strategic_items)
            .joinedload(StrategicItem.activities)
            .joinedload(Activity.tasks)
        ).first()

        if not macro:
            macro = db.query(PlanMacro).order_by(PlanMacro.year.desc()).first()

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=54,
            leftMargin=54,
            topMargin=70,
            bottomMargin=70
        )

        styles = getSampleStyleSheet()
        
        # Estilos de texto personalizados
        style_title = ParagraphStyle(
            name='TitleStyle',
            fontName='Helvetica-Bold',
            fontSize=16,
            leading=20,
            textColor=colors.HexColor("#00594e"),
            alignment=TA_CENTER,
            spaceAfter=8
        )
        
        style_subtitle = ParagraphStyle(
            name='SubtitleStyle',
            fontName='Helvetica',
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#475569"),
            alignment=TA_CENTER,
            spaceAfter=15
        )
        
        style_h1 = ParagraphStyle(
            name='Heading1Style',
            fontName='Helvetica-Bold',
            fontSize=12,
            leading=16,
            textColor=colors.HexColor("#00594e"),
            spaceBefore=12,
            spaceAfter=6,
            keepWithNext=True
        )

        style_h2 = ParagraphStyle(
            name='Heading2Style',
            fontName='Helvetica-Bold',
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#0f766e"),
            spaceBefore=8,
            spaceAfter=4,
            keepWithNext=True
        )

        style_body = ParagraphStyle(
            name='BodyStyle',
            fontName='Helvetica',
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#334155"),
            spaceAfter=4
        )

        style_body_bold = ParagraphStyle(
            name='BodyBoldStyle',
            parent=style_body,
            fontName='Helvetica-Bold'
        )

        style_th = ParagraphStyle(
            name='TableHeaderStyle',
            fontName='Helvetica-Bold',
            fontSize=9,
            leading=11,
            textColor=colors.white,
            alignment=TA_CENTER
        )

        style_td = ParagraphStyle(
            name='TableCellStyle',
            fontName='Helvetica',
            fontSize=8,
            leading=10,
            textColor=colors.HexColor("#1e293b")
        )

        style_td_center = ParagraphStyle(
            name='TableCellCenterStyle',
            parent=style_td,
            alignment=TA_CENTER
        )

        story = []

        # --- LOGO INSTITUCIONAL Y ENCABEZADO ---
        logo_path = "assets/images/logo.png"
        header_data = []
        
        if os.path.exists(logo_path):
            try:
                # Cargar el logo y escalarlo
                logo_img = Image(logo_path, width=120, height=50)
                logo_img.hAlign = 'LEFT'
                header_data.append([logo_img])
            except Exception:
                header_data.append(["[Logo Institucional]"])
        else:
            header_data.append(["[Unitrópico]"])

        header_table = Table(header_data, colWidths=[504])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ]))
        story.append(header_table)

        # --- TÍTULO PRINCIPAL ---
        story.append(Paragraph("INFORME EJECUTIVO DE CUMPLIMIENTO ESTRATÉGICO", style_title))
        story.append(Paragraph(f"Periodo: {filter_label}  |  Plan Maestro: {macro.name if macro else 'No definido'}", style_subtitle))
        story.append(Spacer(1, 10))

        if not macro:
            story.append(Paragraph("No hay datos de planes macro registrados en el sistema.", style_body))
            doc.build(story, onFirstPage=PdfExporterService.draw_background, onLaterPages=PdfExporterService.draw_background)
            buffer.seek(0)
            return buffer

        # --- TABLA DE RESUMEN CONSOLIDADO ---
        story.append(Paragraph("1. Resumen Consolidado de Políticas", style_h1))
        
        table_data = [[
            Paragraph("Código / Nombre Política", style_th),
            Paragraph("Peso", style_th),
            Paragraph("Avance", style_th),
            Paragraph("Estado", style_th),
        ]]

        for idx, pol in enumerate(macro.policies, 1):
            # Semáforo
            prog = pol.progress
            if prog >= 80:
                semaforo = "<font color='#10b981'><b>● Sobresaliente</b></font>"
            elif prog >= 50:
                semaforo = "<font color='#f59e0b'><b>● En Proceso</b></font>"
            else:
                semaforo = "<font color='#ef4444'><b>● Crítico</b></font>"

            table_data.append([
                Paragraph(f"<b>Política {idx}:</b> {pol.name}", style_td),
                Paragraph(f"{pol.weight:.1f}%", style_td_center),
                Paragraph(f"{pol.progress:.1f}%", style_td_center),
                Paragraph(semaforo, style_td_center),
            ])

        summary_table = Table(table_data, colWidths=[264, 70, 70, 100])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#00594e")),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")]),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 15))

        # --- DETALLE DE EJECUCIÓN ---
        story.append(Paragraph("2. Detalle de Ejecución y Plan Operativo", style_h1))
        story.append(Paragraph("A continuación se presenta el desglose detallado de las actividades, metas y tareas programadas:", style_body))
        story.append(Spacer(1, 8))

        # Loop por políticas, estrategias y actividades
        for pol in macro.policies:
            story.append(Paragraph(f"<b>Política:</b> {pol.name} ({pol.progress:.1f}% de avance)", style_h2))
            
            for item in pol.strategic_items:
                story.append(Paragraph(f"<b>{item.type}:</b> {item.name} ({item.progress:.1f}% avance)", style_body_bold))
                
                for act in item.activities:
                    # Filtrar tareas por rango de fecha
                    filtered_tasks = []
                    for t in act.tasks:
                        t_start = t.start_date
                        t_end = t.end_date
                        
                        if t_start and t_end:
                            t_start_dt = datetime.combine(t_start, datetime.min.time())
                            t_end_dt = datetime.combine(t_end, datetime.max.time())
                            if t_start_dt <= end_date and t_end_dt >= start_date:
                                filtered_tasks.append(t)
                        elif t.fulfillment_date:
                            if start_date <= t.fulfillment_date <= end_date:
                                filtered_tasks.append(t)
                    
                    if not filtered_tasks:
                        continue

                    # Renderizar tabla para las tareas de la actividad
                    act_header = Paragraph(f"Actividad: <i>{act.name}</i> (Avance: {act.progress:.1f}%)", style_body_bold)
                    story.append(act_header)

                    task_table_data = [[
                        Paragraph("Tarea", style_th),
                        Paragraph("Responsables", style_th),
                        Paragraph("Estado (Avance)", style_th),
                        Paragraph("Plazo", style_th),
                    ]]

                    for t in filtered_tasks:
                        responsables = ", ".join([r.name for r in t.responsibles]) if t.responsibles else "Sin asignar"
                        rango_fechas = f"{t.start_date.strftime('%d/%m/%y') if t.start_date else '?'} al {t.end_date.strftime('%d/%m/%y') if t.end_date else '?'}"
                        
                        # Justificación de retraso
                        obs_text = t.observations or ""
                        if t.delay_justification:
                            obs_text += f"<br/><b>Justificación Retraso:</b> {t.delay_justification}"
                            
                        # Evidencias
                        evidences = db.query(Evidence).filter(Evidence.task_id == t.id).all()
                        if evidences:
                            obs_text += "<br/><b>Evidencias:</b> " + ", ".join([f"<a href='{e.url}'><u>{e.description or 'Ver'}</u></a>" for e in evidences])

                        task_cell = f"<b>{t.name}</b>"
                        if obs_text:
                            task_cell += f"<br/><font color='#64748b'>{obs_text}</font>"

                        task_table_data.append([
                            Paragraph(task_cell, style_td),
                            Paragraph(responsables, style_td),
                            Paragraph(f"{t.status} ({t.progress:.1f}%)", style_td_center),
                            Paragraph(rango_fechas, style_td_center),
                        ])

                    task_table = Table(task_table_data, colWidths=[204, 110, 90, 100])
                    task_table.setStyle(TableStyle([
                        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0f766e")),
                        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                        ('VALIGN', (0,0), (-1,-1), 'TOP'),
                        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
                        ('TOPPADDING', (0,0), (-1,-1), 5),
                        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
                        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")]),
                    ]))
                    story.append(task_table)
                    story.append(Spacer(1, 10))

            story.append(Spacer(1, 8))

        # --- SECCIÓN DE FIRMAS (AL FINAL) ---
        story.append(Spacer(1, 20))
        
        # Keep together to prevent orphans
        signature_data = [
            [
                Paragraph("<b>Elaboró / Reportó:</b><br/><br/><br/>___________________________________<br/><b>Coordinación de Talento Humano</b><br/>Unitrópico", style_td),
                Paragraph("<b>Revisó / Aprobó:</b><br/><br/><br/>___________________________________<br/><b>Rectoría / Dirección Administrativa</b><br/>Unitrópico", style_td)
            ]
        ]
        signature_table = Table(signature_data, colWidths=[252, 252])
        signature_table.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('TOPPADDING', (0,0), (-1,-1), 10),
            ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ]))
        
        story.append(KeepTogether([
            Paragraph("3. Firmas de Aprobación Institucional", style_h1),
            Spacer(1, 5),
            signature_table
        ]))

        # Generar el documento
        doc.build(
            story,
            onFirstPage=PdfExporterService.draw_background,
            onLaterPages=PdfExporterService.draw_background
        )
        
        buffer.seek(0)
        return buffer
