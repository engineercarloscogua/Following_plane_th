from src.core.database import SessionLocal, engine
from src.models.entities import PlanMacro, Policy, StrategicItem, Activity, Task, Responsible, Base
from datetime import datetime, timedelta
import random

def seed():
    db = SessionLocal()
    try:
        # 1. Asegurar Responsables
        responsibles = db.query(Responsible).all()
        if not responsibles:
            r1 = Responsible(name="Dr. Ricardo Serna", role="Director TH", department="Administración")
            r2 = Responsible(name="Ing. Claudia Mendoza", role="Coordinadora", department="Sistemas")
            db.add_all([r1, r2])
            db.commit()
            responsibles = [r1, r2]

        # 2. Plan Macro 2026
        macro = db.query(PlanMacro).filter(PlanMacro.year == 2026).first()
        if not macro:
            macro = PlanMacro(name="Plan Estratégico de Talento Humano 2026", year=2026, description="Gestión integral 2026")
            db.add(macro)
            db.commit()
            db.refresh(macro)

        # 3. Políticas
        p_names = ["Bienestar y Clima Organizacional", "Gestión del Conocimiento y Desempeño"]
        policies = []
        for name in p_names:
            pol = db.query(Policy).filter(Policy.name == name, Policy.plan_macro_id == macro.id).first()
            if not pol:
                pol = Policy(name=name, weight=50.0, plan_macro_id=macro.id)
                db.add(pol)
            policies.append(pol)
        db.commit()

        # 4. Programas/Planes (Strategic Items)
        months = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11] # Feb a Nov
        task_idx = 0
        
        for pol in policies:
            for i in range(1, 3): # 2 programas por política
                prog_name = f"Programa {i} de {pol.name[:10]}"
                prog = StrategicItem(name=prog_name, weight=50.0, policy_id=pol.id, type="Programa")
                db.add(prog)
                db.commit()
                db.refresh(prog)
                
                for j in range(1, 3): # 2 actividades por programa
                    act_name = f"Actividad {j} de {prog_name[:10]}"
                    act = Activity(name=act_name, weight=50.0, strategic_item_id=prog.id)
                    db.add(act)
                    db.commit()
                    db.refresh(act)
                    
                    for k in range(1, 3): # 2 tareas por actividad
                        month = months[task_idx % len(months)]
                        start = datetime(2026, month, 1)
                        end = start + timedelta(days=20)
                        
                        task = Task(
                            name=f"Tarea {task_idx + 1} - Ejecución {start.strftime('%B')}",
                            weight=50.0,
                            activity_id=act.id,
                            status="Pendiente",
                            progress=0.0,
                            start_date=start,
                            end_date=end
                        )
                        task.responsibles.append(random.choice(responsibles))
                        db.add(task)
                        task_idx += 1
        
        db.commit()
        print("SUCCESS: Base de datos poblada con exito para 2026.")

    except Exception as e:
        print(f"ERROR: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed()
