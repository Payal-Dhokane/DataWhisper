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
    
    # Login/Register Selection
    auth_choice = st.selectbox("Login or Register", ["Login", "Register"], label_visibility="collapsed")
    
    if auth_choice == "Login":
        try:
            name, authentication_status, username = authenticator.login('Login', 'main')
        except Exception as e:
            st.error(f"Authentication setup error: {str(e)}")
            return False, None
            
        if authentication_status:
            return True, authenticator
        
        # Google OAuth Section (Only show on Login page)
        st.markdown("---")
        st.subheader("Login with Google")
        
        CLIENT_ID = st.secrets.get("GOOGLE_CLIENT_ID")
        CLIENT_SECRET = st.secrets.get("GOOGLE_CLIENT_SECRET")
        REDIRECT_URI = st.secrets.get("REDIRECT_URI", "https://datawhisper.streamlit.app")

        if CLIENT_ID and CLIENT_SECRET:
            AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
            TOKEN_URL = "https://oauth2.googleapis.com/token"
            
            # Using a more robust way to render the button
            oauth2 = OAuth2Component(CLIENT_ID, CLIENT_SECRET, AUTHORIZE_URL, TOKEN_URL, TOKEN_URL, None)
            
            result = oauth2.authorize_button(
                name="🚀 Sign in with Google",
                scope="openid email profile",
                redirect_uri=REDIRECT_URI,
                use_container_width=True
            )
            
            if result:
                st.session_state["google_auth"] = result
                st.rerun()
        else:
            st.warning("⚠️ Google OAuth credentials missing. Using local accounts.")

        if authentication_status == False:
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
