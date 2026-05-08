from sqlalchemy.orm import Session
from src.models.entities import Task, Activity, StrategicItem, Policy, PlanMacro

class CalculationService:
    @staticmethod
    def update_all_levels(db: Session, task_id: int):
        """Recalcula toda la cadena desde una tarea hacia arriba (5 niveles)."""
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task: return

        # 1. Update Activity
        activity = task.activity
        CalculationService._update_node(db, activity, activity.tasks)

        # 2. Update Strategic Item (Plan o Programa)
        si = activity.strategic_item
        CalculationService._update_node(db, si, si.activities)

        # 3. Update Policy
        pol = si.policy
        CalculationService._update_node(db, pol, pol.strategic_items)

        # 4. Update Plan Macro (Gestión TH)
        macro = pol.plan_macro
        CalculationService._update_node(db, macro, macro.policies)

        db.commit()

    @staticmethod
    def _update_node(db: Session, node, children):
        if not children:
            node.progress = 0.0
            return
        
        total_weight = sum(c.weight for c in children)
        if total_weight > 0:
            node.progress = sum(c.progress * (c.weight / total_weight) for c in children)
        else:
            node.progress = sum(c.progress for c in children) / len(children)
        
        db.add(node)

    @staticmethod
    def get_semaforo(progress: float) -> tuple:
        if progress >= 80:
            return "Cumplimiento Sobresaliente", "#10b981"
        elif progress >= 60:
            return "Cumplimiento Aceptable", "#f59e0b"
        else:
            return "Cumplimiento Crítico", "#ef4444"
