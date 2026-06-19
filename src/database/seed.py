from datetime import datetime
from src.core.database import SessionLocal, engine, Base
from src.models.entities import User, PlanMacro, Policy, StrategicItem, Activity, Task, Responsible
from src.services.auth import AuthService
from src.services.calculations import CalculationService

def seed_data():
    print("Iniciando purga completa de la base de datos...")
    # 1. Purgar y recrear las tablas para un reinicio limpio
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        print("Creando responsables reales...")
        # 2. Responsables
        lilia = Responsible(
            name="Lilia Andrea Nocua Neme",
            role="Jefe Oficina de Talento Humano",
            department="Talento Humano"
        )
        rosaura = Responsible(
            name="Rosaura Andrea Ramirez",
            role="Profesional de Talento Humano",
            department="Talento Humano"
        )
        db.add_all([lilia, rosaura])
        db.commit()
        db.refresh(lilia)
        db.refresh(rosaura)
        
        print("Creando cuentas de acceso seguras...")
        # 3. Usuarios de acceso
        user_admin = User(
            username="admin",
            email="admin@unitropico.edu.co",
            password_hash=AuthService.hash_password("admin123"),
            role="Admin"
        )
        user_lilia = User(
            username="lilia.nocua",
            email="lilia.nocua@unitropico.edu.co",
            password_hash=AuthService.hash_password("lilia123"),
            role="Supervisor",
            responsible_id=lilia.id
        )
        user_rosaura = User(
            username="rosaura.ramirez",
            email="rosaura.ramirez@unitropico.edu.co",
            password_hash=AuthService.hash_password("rosaura123"),
            role="Worker",
            responsible_id=rosaura.id
        )
        db.add_all([user_admin, user_lilia, user_rosaura])
        db.commit()

        print("Creando estructura estratégica Plan Macro 2025...")
        # 4. Plan Macro 2025
        macro_2025 = PlanMacro(
            name="Plan de Acción de Talento Humano 2025",
            year=2025,
            objective=(
                "Dirigir, coordinar y controlar la gestión estratégica del talento humano de la Universidad "
                "Internacional del Trópico Americano durante la vigencia 2025, garantizando el desarrollo, "
                "formación, bienestar, evaluación y retiro de los servidores públicos."
            )
        )
        db.add(macro_2025)
        db.commit()
        db.refresh(macro_2025)

        # 5. Políticas
        p1 = Policy(name="Gestión Estratégica de Talento Humano", weight=25.0, plan_macro_id=macro_2025.id)
        p2 = Policy(name="Estímulos e Incentivos", weight=25.0, plan_macro_id=macro_2025.id)
        p3 = Policy(name="Integridad", weight=25.0, plan_macro_id=macro_2025.id)
        p4 = Policy(name="Plan de Desarrollo Institucional", weight=25.0, plan_macro_id=macro_2025.id)
        db.add_all([p1, p2, p3, p4])
        db.commit()
        db.refresh(p1)
        db.refresh(p2)
        db.refresh(p3)
        db.refresh(p4)

        # 6. Estrategias y tareas detalladas
        print("Registrando estrategias de Gestión Estratégica...")
        # ================= POLÍTICA 1: GESTIÓN ESTRATÉGICA (21 ítems) =================
        items_p1 = [
            ("Realizar el Plan Anual de Vacantes, Plan Previsión Laboral", [
                ("Adoptar el plan anual de vacantes (Res. Rectoral 2705 de 2024)", "Cumplida", 100.0, 50.0, datetime(2025,1,1), datetime(2025,1,31), rosaura),
                ("Adoptar el plan de previsión de talento humano (Res. Rectoral 2706 de 2024)", "Cumplida", 100.0, 50.0, datetime(2025,1,1), datetime(2025,1,31), rosaura)
            ]),
            ("Proveer las vacantes definitivas de forma temporal mediante la figura nombramiento provisionales eficientemente", [
                ("Gestionar provisión temporal de vacantes mediante nombramientos provisionales (199 cargos provistos)", "Cumplida", 100.0, 100.0, datetime(2025,1,1), datetime(2025,12,31), lilia)
            ]),
            ("Contar con la trazabilidad electrónica o física de la historia laboral de cada servidor", [
                ("Organizar, foliar y digitalizar historias laborales (409 historias gestionadas)", "Cumplida", 100.0, 100.0, datetime(2025,1,1), datetime(2025,12,31), rosaura)
            ]),
            ("Dar cumplimiento al Decreto 2011 de 2017 de porcentaje vinculación de personas con discapacidad en la planta de empleos de la universidad", [
                ("Diseñar acciones afirmativas para promover la inclusión laboral en futuros procesos de selección", "Pendiente", 0.0, 100.0, datetime(2025,10,1), datetime(2025,12,31), lilia)
            ]),
            ("Dar cumplimiento a los artículos 4 y 6 de la ley 2214 de 2022 y el decreto 2365 de 2019 relacionados con el porcentaje de vinculación de jóvenes entre los 18 y 28 años", [
                ("Mantener vinculados al menos 16 jóvenes (10% de la planta) y reportar encuesta DAFP (18 vinculados logrados)", "Cumplida", 100.0, 100.0, datetime(2025,1,1), datetime(2025,12,31), rosaura)
            ]),
            ("Dar cumplimiento de la Ley 581 de 2000 relacionada con la participación efectiva de la mujer en los cargos de nivel directivo", [
                ("Garantizar la participación de la mujer en al menos el 30% de los cargos directivos (63.6% logrado)", "Cumplida", 100.0, 100.0, datetime(2025,1,1), datetime(2025,12,31), lilia)
            ]),
            ("Elaborar y ejecutar el Plan de Formación y Capacitación anual alineado a las necesidades", [
                ("Ejecutar y certificar capacitaciones (16 eventos y 536 certificaciones emitidas)", "Cumplida", 100.0, 100.0, datetime(2025,2,1), datetime(2025,11,30), rosaura)
            ]),
            ("Realizar inducción que permita asegurar la integración efectiva de nuevos miembros a la organización y reinducción", [
                ("Realizar inducción virtual a nuevos servidores en Classroom (37 de 37 certificados)", "Cumplida", 100.0, 50.0, datetime(2025,1,1), datetime(2025,12,31), rosaura),
                ("Realizar curso asincrónico de reinducción para personal administrativo (106 de 107 certificados)", "Cumplida", 100.0, 50.0, datetime(2025,7,1), datetime(2025,7,18), rosaura)
            ]),
            ("Desarrollar un programa de bilingüismo para potenciar las habilidades en lengua extranjera para planta administrativa", [
                ("Ejecutar curso corto de inglés nivel A1 (23 inscritos, 17 certificados)", "Cumplida", 100.0, 100.0, datetime(2025,9,8), datetime(2025,9,12), rosaura)
            ]),
            ("Implementar estándares mínimos del Sistema de Gestión de Seguridad y Salud en el Trabajo SG – SST", [
                ("Alcanzar el 100% de cumplimiento verificado en estándares mínimos de SST (Res. 0312 de 2019)", "Cumplida", 100.0, 100.0, datetime(2025,1,1), datetime(2025,12,31), lilia)
            ]),
            ("Desarrollar programas de Promoción y Prevención de la salud", [
                ("Ejecutar Plan de Capacitaciones SST y simulacro nacional de evacuación (316 evacuados)", "Cumplida", 100.0, 50.0, datetime(2025,1,1), datetime(2025,11,30), lilia),
                ("Realizar exámenes médicos ocupacionales de ingreso y periódicos para funcionarios", "Cumplida", 100.0, 50.0, datetime(2025,1,1), datetime(2025,12,31), rosaura)
            ]),
            ("Identificar, evaluar, prevenir, intervenir y monitorear la exposición a factores de riesgo psicosocial", [
                ("Aplicar Batería de Riesgo Psicosocial y actualizar el PVE Psicosocial (195 servidores)", "Cumplida", 100.0, 100.0, datetime(2025,4,1), datetime(2025,6,30), lilia)
            ]),
            ("Coadyudar en la elaboración y ejecución del plan de bienestar social laboral y fortalecimiento del clima", [
                ("Desarrollar actividades del plan de bienestar (19 actividades y 2066 participaciones logradas)", "Cumplida", 100.0, 100.0, datetime(2025,1,1), datetime(2025,12,31), rosaura)
            ]),
            ("Coordinar el proceso de Evaluación de Rendimiento Laboral (Provisionales)", [
                ("Coordinar y consolidar evaluaciones semestrales 1 y 2 para personal administrativo provisional", "Cumplida", 100.0, 100.0, datetime(2025,3,1), datetime(2026,1,31), lilia)
            ]),
            ("Coordinar el proceso de Evaluación Acuerdos de Gestión (LNR y periodo fijo)", [
                ("Coordinar evaluación parcial de única calificación bajo Res. Rectoral 1378 de 2025", "Cumplida", 100.0, 100.0, datetime(2025,9,1), datetime(2026,1,31), lilia)
            ]),
            ("Coordinar el proceso de Evaluación de Desempeño Profesoral", [
                ("Consolidar y notificar resultados de evaluación profesoral de periodos 2025A y 2025B (568 profesores)", "Cumplida", 100.0, 100.0, datetime(2025,5,1), datetime(2025,12,31), lilia)
            ]),
            ("Suministrar información para la preparación del proceso de rendición de cuentas y buen gobierno", [
                ("Suministrar reportes para SNIES, Jóvenes en el Estado y declaraciones de bienes SIGEP II", "Cumplida", 100.0, 100.0, datetime(2025,1,1), datetime(2025,12,31), lilia)
            ]),
            ("Tramitar la nómina y llevar los registros estadísticos correspondientes", [
                ("Procesar nóminas y transmitir comprobantes a la DIAN (4392 comprobantes totales en la vigencia)", "Cumplida", 100.0, 100.0, datetime(2025,1,1), datetime(2025,12,31), rosaura)
            ]),
            ("Desarrollar el proceso de dotación de vestido y calzado de labor en la entidad", [
                ("Adquirir y entregar dotación a funcionarios beneficiarios (44 beneficiarios, DotaPetrol)", "Cumplida", 100.0, 100.0, datetime(2025,5,1), datetime(2025,12,31), rosaura)
            ]),
            ("Tramitar situaciones administrativas de licencias e incapacidades", [
                ("Gestionar cobro de 101 incapacidades (83 recuperadas) y 12 licencias de maternidad/paternidad", "Cumplida", 100.0, 100.0, datetime(2025,1,1), datetime(2025,12,31), rosaura)
            ]),
            ("Desarrollar el Plan de Desvinculación Laboral Asistida", [
                ("Realizar 5 actividades de preparación para jubilación y el respectivo reconocimiento a jubilados", "Cumplida", 100.0, 100.0, datetime(2025,1,1), datetime(2025,12,31), lilia)
            ])
        ]

        w_si = 100.0 / len(items_p1)
        for name, tasks in items_p1:
            si = StrategicItem(name=name, type="Estrategia", weight=w_si, policy_id=p1.id)
            db.add(si)
            db.commit()
            db.refresh(si)
            
            act = Activity(name=f"Ejecución de {name[:120]}", weight=100.0, strategic_item_id=si.id)
            db.add(act)
            db.commit()
            db.refresh(act)
            
            for t_desc, status, progress, weight, start, end, resp in tasks:
                t = Task(
                    name=t_desc,
                    status=status,
                    progress=progress,
                    weight=weight,
                    start_date=start,
                    end_date=end,
                    target_date=end,
                    responsible_name=resp.name
                )
                t.responsibles.append(resp)
                act.tasks.append(t)
            db.commit()

        print("Registrando estrategias de Estímulos e Incentivos...")
        # ================= POLÍTICA 2: ESTÍMULOS E INCENTIVOS (8 ítems) =================
        items_p2 = [
            ("Reglamentar el otorgamiento de estímulos e incentivos pecuniarios y no pecuniarios", [
                ("Redactar el borrador del reglamento integral de estímulos e incentivos de Talento Humano", "En Proceso", 50.0, 100.0, datetime(2025,8,1), datetime(2025,12,31), lilia)
            ]),
            ("Realizar estrategia de comunicación para dar a conocer la reglamentación de los estímulos", [
                ("Diseñar piezas informativas y socializar el nuevo reglamento de estímulos tras su expedición", "Pendiente", 0.0, 100.0, datetime(2025,11,1), datetime(2025,12,31), rosaura)
            ]),
            ("Conceder descanso remunerado por cumpleaños en el mínimo del 20% de los funcionarios", [
                ("Otorgar día compensado por cumpleaños a los funcionarios (75 permisos autorizados)", "Cumplida", 100.0, 100.0, datetime(2025,1,1), datetime(2025,12,31), rosaura)
            ]),
            ("Brindar condiciones preferenciales de acceso y pago de cursos de capacitación", [
                ("Gestionar convenios y condiciones de pago preferenciales para la formación de funcionarios", "En Proceso", 70.0, 100.0, datetime(2025,3,1), datetime(2025,12,31), rosaura)
            ]),
            ("Otorgar estímulo a los mejores empleados por nivel jerárquico y mejores profesores", [
                ("Organizar comisión de estímulos y seleccionar mejores empleados de carrera y provisionales", "Pendiente", 0.0, 100.0, datetime(2025,10,1), datetime(2025,12,31), lilia)
            ]),
            ("Ofrecer estímulos e incentivos por participación en la ejecución de proyectos de academia, investigación", [
                ("Conceder incentivos a la excelencia en labor profesoral e innovación educativa (4 reconocimientos)", "Cumplida", 100.0, 100.0, datetime(2025,1,1), datetime(2025,12,31), lilia)
            ]),
            ("Conceder permiso para desarrollar actividades de estudios que se contrapongan a la jornada", [
                ("Tramitar y avalar permisos compensados de estudio para servidores públicos en 2025", "Cumplida", 100.0, 100.0, datetime(2025,1,1), datetime(2025,12,31), lilia)
            ]),
            ("Otorgar distinción por tiempo de servicio o condecoración para quinquenales", [
                ("Revisar y actualizar lineamientos para quinquenios y realizar reconocimientos correspondientes", "En Proceso", 40.0, 100.0, datetime(2025,7,1), datetime(2025,12,31), lilia)
            ])
        ]

        w_si = 100.0 / len(items_p2)
        for name, tasks in items_p2:
            si = StrategicItem(name=name, type="Estrategia", weight=w_si, policy_id=p2.id)
            db.add(si)
            db.commit()
            db.refresh(si)
            
            act = Activity(name=f"Ejecución de {name[:120]}", weight=100.0, strategic_item_id=si.id)
            db.add(act)
            db.commit()
            db.refresh(act)
            
            for t_desc, status, progress, weight, start, end, resp in tasks:
                t = Task(
                    name=t_desc,
                    status=status,
                    progress=progress,
                    weight=weight,
                    start_date=start,
                    end_date=end,
                    target_date=end,
                    responsible_name=resp.name
                )
                t.responsibles.append(resp)
                act.tasks.append(t)
            db.commit()

        print("Registrando estrategias de Integridad...")
        # ================= POLÍTICA 3: INTEGRIDAD (12 ítems) =================
        items_p3 = [
            ("Realizar diagnóstico de apropiación de los valores de la Política de Integridad", [
                ("Aplicar la encuesta de percepción de valores a los servidores de la universidad", "Cumplida", 100.0, 100.0, datetime(2025,9,1), datetime(2025,11,30), lilia)
            ]),
            ("Incluir formación en valores establecidos en la Política de Integridad en la inducción de los empleados", [
                ("Desarrollar y evaluar el módulo de integridad dentro del aula virtual de inducción/reinducción", "Cumplida", 100.0, 100.0, datetime(2025,1,1), datetime(2025,12,31), rosaura)
            ]),
            ("Realizar seguimiento a la gestión adecuada de conflictos de interés y declaración de bienes", [
                ("Verificar registros de bienes y rentas y conflicto de intereses en SIGEP II (114 admin, 9 prof)", "Cumplida", 100.0, 100.0, datetime(2025,1,1), datetime(2025,12,31), rosaura)
            ]),
            ("Revisar periódicamente Antecedentes Disciplinarios y fiscales para identificar posibles conflictos", [
                ("Revisar antecedentes sistemáticamente a servidores y contratistas (Directiva Conjunta 002 de 2025)", "Cumplida", 100.0, 100.0, datetime(2025,1,1), datetime(2025,12,31), lilia)
            ]),
            ("Coadyudar en la divulgación de la estrategia de apropiación de la cultura de transparencia", [
                ("Promover transparencia activa publicando información misional en canales accesibles", "Cumplida", 100.0, 100.0, datetime(2025,1,1), datetime(2025,12,31), lilia)
            ]),
            ("Realizar una estrategia trimestral de boletín virtual que permita visibilizar los buenos hechos", [
                ("Diseñar y difundir 4 boletines trimestrales virtuales sobre la Política de Integridad", "Cumplida", 100.0, 100.0, datetime(2025,1,1), datetime(2025,12,31), rosaura)
            ]),
            ("Realizar estrategia de comunicación mediante piezas publicitarias para difundir valores cotidianos", [
                ("Estructurar piezas gráficas pedagógicas de valores para personal administrativo y docente", "Cumplida", 100.0, 100.0, datetime(2025,1,1), datetime(2025,12,31), rosaura)
            ]),
            ("Implementar actividad pedagógica de prevención y promoción del valor de la honestidad y respeto", [
                ("Instalar la 'Tiendita de la honestidad' por 6 días y evaluar porcentaje de recaudo (91.52% logrado)", "Cumplida", 100.0, 100.0, datetime(2025,10,1), datetime(2025,10,31), lilia)
            ]),
            ("Implementar actividad pedagógica de prevención y promoción del valor de compromiso", [
                ("Desarrollar el concurso artístico familiar 'Los valores Unitropistas se viven en casa'", "Cumplida", 100.0, 100.0, datetime(2025,8,1), datetime(2025,9,30), rosaura)
            ]),
            ("Implementar actividad pedagógica de prevención y promoción del valor de solidaridad", [
                ("Efectuar la campaña 'Su aporte hace la diferencia' y entregar kits de aseo en La Guafilla", "Cumplida", 100.0, 100.0, datetime(2025,9,1), datetime(2025,9,30), rosaura)
            ]),
            ("Implementar actividad pedagógica de prevención y promoción del valor de la justicia y diligencia", [
                ("Realizar el taller práctico 'Semáforo de la Integridad' y rompecabezas sobre dilemas éticos", "Cumplida", 100.0, 100.0, datetime(2025,4,1), datetime(2025,5,31), lilia)
            ]),
            ("Implementar actividad pedagógica de prevención y promoción del valor de liderazgo", [
                ("Desarrollar dinámicas cooperativas de ensamble para fortalecer liderazgo y coordinación de roles", "Cumplida", 100.0, 100.0, datetime(2025,11,1), datetime(2025,11,30), lilia)
            ])
        ]

        w_si = 100.0 / len(items_p3)
        for name, tasks in items_p3:
            si = StrategicItem(name=name, type="Estrategia", weight=w_si, policy_id=p3.id)
            db.add(si)
            db.commit()
            db.refresh(si)
            
            act = Activity(name=f"Ejecución de {name[:120]}", weight=100.0, strategic_item_id=si.id)
            db.add(act)
            db.commit()
            db.refresh(act)
            
            for t_desc, status, progress, weight, start, end, resp in tasks:
                t = Task(
                    name=t_desc,
                    status=status,
                    progress=progress,
                    weight=weight,
                    start_date=start,
                    end_date=end,
                    target_date=end,
                    responsible_name=resp.name
                )
                t.responsibles.append(resp)
                act.tasks.append(t)
            db.commit()

        print("Registrando metas de Plan de Desarrollo Institucional...")
        # ================= POLÍTICA 4: PLAN DE DESARROLLO INSTITUCIONAL (2 ítems) =================
        items_p4 = [
            ("Meta 1: E3M10 - Implementar una herramienta digital que integre la gestión de TH y bienestar", [
                ("Avanzar un 20% en la meta digital mediante análisis previo y selección preliminar de Novasoft", "Cumplida", 100.0, 100.0, datetime(2025,1,1), datetime(2025,12,31), lilia)
            ]),
            ("Meta 2: E4M3 - Fortalecer y modernizar la estructura orgánica institucional", [
                ("Ajustar planta de personal y manual de funciones fundamentado en el Acuerdo CS N° 075 de 2024", "Cumplida", 100.0, 100.0, datetime(2025,1,1), datetime(2025,12,31), lilia)
            ])
        ]

        w_si = 100.0 / len(items_p4)
        for name, tasks in items_p4:
            si = StrategicItem(name=name, type="Meta PDI", weight=w_si, policy_id=p4.id)
            db.add(si)
            db.commit()
            db.refresh(si)
            
            act = Activity(name=f"Ejecución de {name[:120]}", weight=100.0, strategic_item_id=si.id)
            db.add(act)
            db.commit()
            db.refresh(act)
            
            for t_desc, status, progress, weight, start, end, resp in tasks:
                t = Task(
                    name=t_desc,
                    status=status,
                    progress=progress,
                    weight=weight,
                    start_date=start,
                    end_date=end,
                    target_date=end,
                    responsible_name=resp.name
                )
                t.responsibles.append(resp)
                act.tasks.append(t)
            db.commit()

        print("Recalculando avances y estados en todos los niveles...")
        # 7. Recalcular todo el árbol jerárquico
        CalculationService.recalculate_all(db)
        
        print("Base de datos preparada con éxito para 2025.")
        
    except Exception as e:
        print(f"Error al sembrar base de datos: {e}")
        db.rollback()
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
