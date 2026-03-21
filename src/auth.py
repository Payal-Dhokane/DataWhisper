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
                'key': 'smart_eda_cookie_key_123',
                'name': 'smart_eda_cookie'
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
    st.markdown("<h1 style='text-align: center; color: #2563eb;'>Smart EDA Assistant</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748b;'>Please login to access your workspace. <i>(Demo Account: <b>demo</b> / <b>password</b>)</i></p>", unsafe_allow_html=True)
    
    authenticator, config_path = load_authenticator()
    
    # Try different API signatures depending on the streamlit_authenticator version installed
    try:
        # 0.3.1+ signature
        name, authentication_status, username = authenticator.login('main')
    except TypeError:
        try:
            # 0.2.x signature
            name, authentication_status, username = authenticator.login('Login', 'main')
        except Exception:
            st.error("Authentication module version mismatch. Please reinstall.")
            return False, None
            
    if authentication_status:
        return True, authenticator
    elif authentication_status == False:
        st.error('Username/password is incorrect')
        return False, None
    elif authentication_status == None:
        return False, None
    
    return False, None
