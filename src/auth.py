import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import os

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
    authenticator, config_path = load_authenticator()
    
    try:
        # Try both signatures safely
        try:
            name, authentication_status, username = authenticator.login('main')
        except TypeError:
            name, authentication_status, username = authenticator.login('Login', 'main')
    except Exception as e:
        st.error(f"Authentication setup error: {str(e)}")
        return False, None
            
    if authentication_status:
        # User is logged in successfully. We do NOT print the Please Login text.
        return True, authenticator
        
    # User is NOT logged in. Print the instructions.
    st.markdown("<h1 style='text-align: center; color: #2563eb;'>Smart EDA Assistant</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748b;'>Please login to access your workspace. <i>(Demo Account: <b>demo</b> / <b>password</b>)</i></p>", unsafe_allow_html=True)
    
    if authentication_status == False:
        st.error('Username/password is incorrect')
        return False, None
    elif authentication_status == None:
        return False, None
    
    return False, None
