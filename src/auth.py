import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import os
from streamlit_oauth import OAuth2Component

def load_authenticator():
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.yaml')
    
    # Create default config on first run
    if not os.path.exists(config_path):
        # Generate robust hash dynamically
        hashed_password = stauth.Hasher(['password']).generate()[0]
        
        default_config = {
            'credentials': {
                'usernames': {
                    'demo': {
                        'email': 'demo@smarteda.com',
                        'name': 'Demo User',
                        'password': hashed_password
                    }
                }
            },
            'cookie': {
                'expiry_days': 30,
                'key': 'smart_eda_cookie_key_123_v2',
                'name': 'smart_eda_cookie_v2'
            },
            'preauthorized': {
                'emails': ['admin@smarteda.com']
            }
        }
        with open(config_path, 'w') as file:
            yaml.dump(default_config, file, default_flow_style=False)

    # Load configuration
    with open(config_path) as file:
        config = yaml.load(file, Loader=SafeLoader)

    # Initialize authenticator
    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
        config['preauthorized']
    )
    return authenticator, config_path

def authenticate_user():
    """Handles UI injection for authentication and blocks unauthenticated users."""
    
    # 1. Check Google OAuth status first if it exists in session
    if "google_auth" in st.session_state:
        return True, None # None for authenticator as it's not needed for logic, but app handles logout

    authenticator, config_path = load_authenticator()
    
    # Attempt login via streamlit-authenticator
    try:
        name, authentication_status, username = authenticator.login('Login', 'main')
    except Exception as e:
        st.error(f"Authentication setup error: {str(e)}")
        return False, None
            
    if authentication_status:
        # User is logged in successfully via traditional login
        return True, authenticator
        
    # User is NOT logged in. Show Login UI.
    st.markdown("<h1 style='text-align: center; color: #818cf8;'>DataWhisper</h1>", unsafe_allow_html=True)
    
    # Google OAuth 2.0 Integration
    st.markdown("---")
    st.subheader("Login with Google")
    
    CLIENT_ID = st.secrets.get("GOOGLE_CLIENT_ID")
    CLIENT_SECRET = st.secrets.get("GOOGLE_CLIENT_SECRET")
    REDIRECT_URI = st.secrets.get("REDIRECT_URI", "https://datawhisper.streamlit.app")

    if CLIENT_ID and CLIENT_SECRET:
        AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
        TOKEN_URL = "https://oauth2.googleapis.com/token"
        REVOKE_URL = "https://oauth2.googleapis.com/revoke"
        
        oauth2 = OAuth2Component(CLIENT_ID, CLIENT_SECRET, AUTHORIZE_URL, TOKEN_URL, TOKEN_URL, REVOKE_URL)
        
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
        st.warning("⚠️ Google OAuth credentials missing in Streamlit Secrets. Login via Google is disabled.")
        if st.button("How to add credentials?", use_container_width=True):
            st.info("Add GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET to your Streamlit Cloud Secrets.")

    st.markdown("---")
    st.markdown("<p style='text-align: center; color: #64748b;'>Or use your Demo Account: <b>demo</b> / <b>password</b></p>", unsafe_allow_html=True)
    
    if authentication_status == False:
        st.error('Username/password is incorrect')
    
    # STOP the app for unauthenticated users
    st.stop()
    return False, None
