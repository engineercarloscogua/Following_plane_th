#!/usr/bin/env python3
import os
import sys

# Adjust path to import src modules
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

from src.core.database import SessionLocal
from src.models.entities import User, Responsible
from src.services.auth import AuthService

def create_workers():
    db = SessionLocal()
    try:
        workers_to_create = [
            {
                "name": "Laura Vanesa Cely",
                "username": "laura.cely",
                "email": "laura.cely@unitropico.edu.co",
                "password": "laura123",
                "role_desc": "Profesional de Talento Humano"
            },
            {
                "name": "Claudia America Garcia",
                "username": "claudia.garcia",
                "email": "claudia.garcia@unitropico.edu.co",
                "password": "claudia123",
                "role_desc": "Profesional de Talento Humano"
            },
            {
                "name": "Leidy Yamile Garcia",
                "username": "leidy.garcia",
                "email": "leidy.garcia@unitropico.edu.co",
                "password": "leidy123",
                "role_desc": "Profesional de Talento Humano"
            },
            {
                "name": "Yusney Garcia",
                "username": "yusney.garcia",
                "email": "yusney.garcia@unitropico.edu.co",
                "password": "yusney123",
                "role_desc": "Profesional de Talento Humano"
            },
            {
                "name": "Yenny Cardenas",
                "username": "yenny.cardenas",
                "email": "yenny.cardenas@unitropico.edu.co",
                "password": "yenny123",
                "role_desc": "Profesional de Talento Humano"
            }
        ]

        print("Iniciando creación de nuevos trabajadores...")
        for w in workers_to_create:
            # Check if user already exists
            existing_user = db.query(User).filter(User.username == w["username"]).first()
            if existing_user:
                print(f"El usuario '{w['username']}' ya existe. Omitiendo.")
                continue

            # 1. Create Responsible
            resp = Responsible(
                name=w["name"],
                role=w["role_desc"],
                department="Talento Humano"
            )
            db.add(resp)
            db.flush() # Populate ID

            # 2. Create User
            password_hash = AuthService.hash_password(w["password"])
            user = User(
                username=w["username"],
                email=w["email"],
                password_hash=password_hash,
                role="Worker",
                status="active",
                responsible_id=resp.id
            )
            db.add(user)
            print(f"Creado trabajador: {w['name']} (Usuario: {w['username']}, Contraseña: {w['password']})")

        db.commit()
        print("\n=== TODOS LOS TRABAJADORES FUERON CREADOS Y GUARDADOS CORRECTAMENTE ===")

    except Exception as e:
        db.rollback()
        print(f"\n[ERROR] Falló la creación de trabajadores: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    create_workers()
