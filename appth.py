import streamlit as st
from src.core.database import engine, Base, SessionLocal
from src.services.auth import AuthService
from src.models.entities import User
from src.ui.views.admin import show_admin_view
from src.ui.views.dashboard import show_executive_dashboard
from src.ui.views.supervisor import show_supervisor_view
from src.ui.views.alerts import show_alerts_view
import os
from PIL import Image

# Asegurar carpetas y archivos
Base.metadata.create_all(bind=engine)

# Configuración de página con Identidad Institucional
favicon_path = "assets/images/favicon.png"
page_icon = "🏛️"
if os.path.exists(favicon_path):
    page_icon = Image.open(favicon_path)

st.set_page_config(
    page_title="Plataforma TH | Unitrópico",
    page_icon=page_icon,
    layout="wide"
)

# Inicializar sesión
AuthService.init_session()

# Cargar CSS corporativo
def local_css(file_name):
    if os.path.exists(file_name):
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("assets/style.css")

def main():
    if not AuthService.is_authenticated():
        show_login()
    else:
        show_app()

def show_login():
    st.markdown("<div style='height: 80px;'></div>", unsafe_allow_html=True)
    col_l1, col_l2, col_l3 = st.columns([1, 1, 1])
    with col_l2:
        logo_path = "assets/images/logo.png"
        if os.path.exists(logo_path):
            st.image(logo_path, use_container_width=True)
    
    st.markdown("<p style='text-align: center; color: #64748b; font-weight: 500;'>Sistema de Gestión Estratégica Unitrópico</p>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        with st.container(border=True):
            st.markdown("<h3 style='color: #00594e;'>🔐 Acceso Seguro</h3>", unsafe_allow_html=True)
            username = st.text_input("Usuario")
            password = st.text_input("Contraseña", type="password")
            
            if st.button("Ingresar al Portal", use_container_width=True):
                db = SessionLocal()
                if AuthService.login(db, username, password):
                    st.toast("✅ Bienvenido")
                    st.rerun()
                else:
                    st.error("Credenciales inválidas")
                db.close()

def show_app():
    user_role = st.session_state.get('role')
    user_name = st.session_state.get('username')

    with st.sidebar:
        logo_path = "assets/images/logo.png"
        if os.path.exists(logo_path):
            st.image(logo_path, use_container_width=True)
            
        st.markdown(f"### 👤 {user_name}")
        st.caption(f"Rol: **{user_role}**")
        st.divider()
        
        menu_options = ["🏠 Dashboard"]
        if user_role == "Admin":
            menu_options += ["⚙️ Configuración Admin"]
        
        menu_options += ["🧐 Supervisión", "🚨 Tareas Críticas", "📊 Reportes"]
        
        choice = st.radio("Navegación Institucional", menu_options)
        st.divider()
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            AuthService.logout()

    if choice == "🏠 Dashboard":
        show_executive_dashboard()
    elif choice == "⚙️ Configuración Admin":
        if user_role == "Admin": show_admin_view()
    elif choice == "🧐 Supervisión":
        show_supervisor_view()
    elif choice == "🚨 Tareas Críticas":
        show_alerts_view()
    elif choice == "📊 Reportes":
        st.header("📊 Reportes Institucionales")
        st.info("Módulo de reportes en construcción.")

if __name__ == "__main__":
    main()
