import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import os
from streamlit_oauth import OAuth2Component

def load_authenticator():
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.yaml')
    
    default_config = {
        'credentials': {
            'usernames': {
                'demo': {
                    'email': 'demo@smarteda.com',
                    'name': 'Demo User',
                    'password': stauth.Hasher(['password']).generate()[0]
                }
            }
        },
        'cookie': {
            'expiry_days': 30,
            'key': 'smart_eda_cookie_key_123_v3',
            'name': 'smart_eda_cookie_v3'
        },
        'preauthorized': {
            'emails': ['admin@smarteda.com']
        }
    }

    # Create default config on first run or if file is missing
    if not os.path.exists(config_path):
        with open(config_path, 'w') as file:
            yaml.dump(default_config, file, default_flow_style=False)

    # Load configuration
    config = None
    if os.path.exists(config_path):
        with open(config_path) as file:
            try:
                config = yaml.load(file, Loader=SafeLoader)
            except Exception:
                config = None

    # Fallback if file is empty or invalid
    if not config or 'credentials' not in config:
        config = default_config
        with open(config_path, 'w') as file:
            yaml.dump(default_config, file, default_flow_style=False)

    # Initialize authenticator
    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
        config['preauthorized']
    )
    return authenticator, config, config_path

def authenticate_user():
    """Handles UI injection for authentication and blocks unauthenticated users."""
    
    # 1. Check Google OAuth status first if it exists in session
    if "google_auth" in st.session_state:
        return True, None

    authenticator, config, config_path = load_authenticator()
    
    # 2. Check traditional authentication status
    if st.session_state.get('authentication_status'):
        return True, authenticator

    # --- BELOW ONLY SHOWS IF NOT AUTHENTICATED ---
    
    # Main App branding
    st.markdown("<div style='text-align: center;'><h2 class='login-brand'>DataWhisper</h2></div>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.1rem; margin-bottom: 2.5rem; opacity: 0.7; letter-spacing: 0.5px;'>AI-Powered Exploratory Data Analysis</p>", unsafe_allow_html=True)

    # Injecting specific CSS for login page elements
    st.markdown("""
        <style>
        .login-brand {
            background: linear-gradient(135deg, #FFFFFF 30%, #A78BFA 100%);
            -webkit-background-clip: text;
            background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800 !important;
            letter-spacing: 2px;
            font-size: 3.5rem !important;
            margin-bottom: 0 !important;
            display: inline-block;
            text-transform: none;
        }
        
        /* Glass Login Container */
        div[data-testid="stVerticalBlock"] > div:has(div.stSelectbox), .stForm {
            background: rgba(30, 30, 46, 0.45) !important;
            backdrop-filter: blur(15px);
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 24px !important;
            padding: 2.5rem !important;
            box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.5) !important;
            width: 100% !important;
        }
        
        /* Input fields fix */
        input {
            background: rgba(255, 255, 255, 0.03) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            color: white !important;
            border-radius: 12px !important;
            height: 45px !important;
        }
        
        /* Fix Selectbox width / cutoff */
        div[data-testid="stSelectbox"] div[data-baseweb="select"] {
            border-radius: 12px !important;
            background: rgba(255, 255, 255, 0.03) !important;
        }
        
        /* Submit Button Styling */
        button[kind="secondaryFormSubmit"], button[kind="primaryFormSubmit"] {
            background: linear-gradient(135deg, #7C3AED 0%, #C026D3 100%) !important;
            color: white !important;
            border-radius: 12px !important;
            border: none !important;
            box-shadow: 0 4px 15px rgba(124, 58, 237, 0.4) !important;
            padding: 0.8rem 2rem !important;
            font-weight: 700 !important;
            width: 100% !important;
            margin-top: 1.5rem !important;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        </style>
    """, unsafe_allow_html=True)

    # Use columns to center and constrain the width
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # 2. Login/Register UI
        auth_choice = st.selectbox("Action", ["Login", "Register"], label_visibility="collapsed")
        
        if auth_choice == "Login":
            try:
                name, authentication_status, username = authenticator.login('Login', 'main')
            except Exception as e:
                st.error(f"Authentication setup error: {str(e)}")
                return False, None
                
            if st.session_state.get('authentication_status'):
                st.rerun()

            if st.session_state.get('authentication_status') == False:
                st.error('Username/password is incorrect')
                
        else: # Register
            try:
                if authenticator.register_user('Register User', preauthorization=False):
                    st.success('User registered successfully! You can now login.')
                    config['credentials'] = authenticator.credentials
                    with open(config_path, 'w') as file:
                        yaml.dump(config, file, default_flow_style=False)
            except Exception as e:
                st.error(f"Registration error: {str(e)}")

    # Stop execution for non-logged in users
    st.stop()
    return False, None
