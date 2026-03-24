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
    st.markdown("<h1 style='text-align: center; color: #818cf8; margin-bottom: 0;'>DataWhisper</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #94a3b8; margin-bottom: 2rem;'>AI-Powered Exploratory Data Analysis</p>", unsafe_allow_html=True)

    # Login/Register UI in a clean container
    with st.container():
        auth_choice = st.selectbox("Action", ["Login", "Register"], label_visibility="collapsed")
        
        if auth_choice == "Login":
            try:
                name, authentication_status, username = authenticator.login('Login', 'main')
            except Exception as e:
                st.error(f"Authentication setup error: {str(e)}")
                return False, None
                
            if st.session_state.get('authentication_status'):
                st.rerun() # Rerun to hide the login UI immediately
            
            # Google OAuth Section (Only show on Login page)
            st.markdown("<div style='text-align: center; margin: 1.5rem 0;'>or</div>", unsafe_allow_html=True)
            
            CLIENT_ID = st.secrets.get("GOOGLE_CLIENT_ID")
            CLIENT_SECRET = st.secrets.get("GOOGLE_CLIENT_SECRET")
            # Try to detect redirect URI if not in secrets
            REDIRECT_URI = st.secrets.get("REDIRECT_URI")
            if not REDIRECT_URI:
                # Fallback for Streamlit Cloud
                REDIRECT_URI = "https://datawhisper.streamlit.app"
                st.info(f"ℹ️ Ensure your Redirect URI is set to `{REDIRECT_URI}` in Google Console.")

            if CLIENT_ID and CLIENT_SECRET:
                AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
                TOKEN_URL = "https://oauth2.googleapis.com/token"
                
                oauth2 = OAuth2Component(CLIENT_ID, CLIENT_SECRET, AUTHORIZE_URL, TOKEN_URL, TOKEN_URL, None)
                
                # Render button with a distinct key and clear name
                result = oauth2.authorize_button(
                    name="🚀 Sign in with Google",
                    scope="openid email profile",
                    redirect_uri=REDIRECT_URI,
                    use_container_width=True,
                    key="google_login_btn" # Added key for stability
                )
                
                if result:
                    st.session_state["google_auth"] = result
                    st.rerun()
            else:
                st.info("💡 Tip: Use local accounts if Google Login is not configured.")

            if st.session_state.get('authentication_status') == False:
                st.error('Username/password is incorrect')
                
        else: # Register
            try:
                if authenticator.register_user('Register User', preauthorization=False):
                    st.success('User registered successfully! You can now login.')
                    # Save the new user to config.yaml by syncing config with credentials
                    config['credentials'] = authenticator.credentials
                    with open(config_path, 'w') as file:
                        yaml.dump(config, file, default_flow_style=False)
            except Exception as e:
                st.error(f"Registration error: {str(e)}")

    # Stop execution for non-logged in users
    st.stop()
    return False, None
