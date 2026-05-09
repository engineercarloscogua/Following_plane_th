import bcrypt
from sqlalchemy.orm import Session
from src.models.entities import User
import streamlit as st

class AuthService:
    """
    Service responsible for user authentication and session management.
    Handles login, logout, and role-based access control.
    """
    @staticmethod
    def hash_password(password: str) -> str:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

    @staticmethod
    def login(db: Session, username: str, password: str) -> bool:
        user = db.query(User).filter(User.username == username).first()
        if user and AuthService.verify_password(password, user.password_hash):
            st.session_state.user_id = user.id
            st.session_state.username = user.username
            st.session_state.role = user.role
            return True
        return False

    @staticmethod
    def logout():
        for key in ["user_id", "username", "role"]:
            if key in st.session_state:
                st.session_state[key] = None
        st.rerun()

    @staticmethod
    def is_authenticated() -> bool:
        return st.session_state.get("user_id") is not None

    @staticmethod
    def init_session():
        if "user_id" not in st.session_state:
            st.session_state.user_id = None
        if "username" not in st.session_state:
            st.session_state.username = None
        if "role" not in st.session_state:
            st.session_state.role = None
