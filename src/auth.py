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
    st.markdown("<div style='text-align: center;'><h2 class='sidebar-brand'>DataWhisper</h2></div>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.1rem; margin-bottom: 2rem; opacity: 0.8;'>AI-Powered Exploratory Data Analysis</p>", unsafe_allow_html=True)

    # Injecting specific CSS for login page elements
    st.markdown("""
        <style>
        .sidebar-brand {
            background: linear-gradient(135deg, #FFFFFF 30%, #A78BFA 100%);
            -webkit-background-clip: text;
            background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800 !important;
            letter-spacing: 1.5px;
            font-size: 3rem !important;
            margin-bottom: 0 !important;
            display: inline-block;
            text-transform: none;
        }
        
        /* Glass Login Container */
        div[data-testid="stVerticalBlock"] > div:has(div.stSelectbox), .stForm {
            background: rgba(30, 30, 46, 0.45) !important;
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 20px !important;
            padding: 2rem !important;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.4) !important;
            width: 100% !important;
        }
        
        /* Input fields in login */
        input {
            background: rgba(255, 255, 255, 0.05) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            color: white !important;
            border-radius: 12px !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # Use columns to center and constrain the width
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # 1. Google OAuth Section 
        CLIENT_ID = st.secrets.get("GOOGLE_CLIENT_ID")
        CLIENT_SECRET = st.secrets.get("GOOGLE_CLIENT_SECRET")
        REDIRECT_URI = st.secrets.get("REDIRECT_URI", "https://datawhisper.streamlit.app")

        if CLIENT_ID and CLIENT_SECRET:
            try:
                AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
                TOKEN_URL = "https://oauth2.googleapis.com/token"
                oauth2 = OAuth2Component(CLIENT_ID, CLIENT_SECRET, AUTHORIZE_URL, TOKEN_URL, TOKEN_URL, None)
                
                result = oauth2.authorize_button(
                    name="🚀 Sign in with Google",
                    scope="openid email profile",
                    redirect_uri=REDIRECT_URI,
                    use_container_width=True,
                    key="google_login_v3"
                )
                
                if result:
                    st.session_state["google_auth"] = result
                    st.rerun()
            except Exception as e:
                st.error(f"Google Login error: {e}")
            
            st.markdown("<div style='margin: 1.5rem 0;'></div>", unsafe_allow_html=True)
        else:
            st.warning("⚠️ **Google Login Setup Required**: Please add `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` to your Streamlit Secrets to enable this feature.")

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
