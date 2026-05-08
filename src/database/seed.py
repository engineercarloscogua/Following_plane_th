from src.core.database import SessionLocal, engine, Base
from src.models.entities import User, PlanMacro
from src.services.auth import AuthService

def seed_data():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    # 1. Admin
    admin = db.query(User).filter(User.username == "admin").first()
    if not admin:
        admin = User(
            username="admin", 
            email="admin@unitropico.edu.co", 
            password_hash=AuthService.hash_password("admin123"),
            role="Admin"
        )
        db.add(admin)
    
    # 2. Supervisor
    supervisor = db.query(User).filter(User.username == "supervisor").first()
    if not supervisor:
        supervisor = User(
            username="supervisor", 
            email="supervisor@unitropico.edu.co", 
            password_hash=AuthService.hash_password("sup123"),
            role="Supervisor"
        )
        db.add(supervisor)
    
    db.commit()
    print("Base de datos preparada.")
    db.close()

if __name__ == "__main__":
    seed_data()
