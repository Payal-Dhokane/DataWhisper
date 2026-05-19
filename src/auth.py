import streamlit as st
# pyrefly: ignore [missing-import]
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
    
    # 1. Clean Global Styling
    st.markdown("""
        <style>
        /* Base Background */
        .stApp {
            background-color: #0B0B14 !important;
            background-image: 
                radial-gradient(circle at 20% 30%, rgba(124, 58, 237, 0.04) 0%, transparent 50%),
                radial-gradient(circle at 80% 70%, rgba(192, 38, 211, 0.04) 0%, transparent 50%) !important;
        }

        /* Container Sizing */
        .block-container {
            padding-top: 6vh !important;
            max-width: 1100px !important;
        }

        /* 2. Left Column: Branding Section */
        .branding-container {
            padding-right: 2.5rem;
        }
        
        .branding-badge {
            background: rgba(124, 58, 237, 0.1);
            border: 1px solid rgba(124, 58, 237, 0.2);
            color: #C4B5FD;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
            display: inline-block;
            margin-bottom: 1.2rem;
            letter-spacing: 0.5px;
        }
        
        .branding-title {
            font-size: 3.5rem !important;
            font-weight: 800 !important;
            line-height: 1.1 !important;
            margin-bottom: 1.2rem !important;
            color: #FFFFFF;
            word-break: keep-all;
        }
        
        .branding-title-gradient {
            background: linear-gradient(135deg, #FFFFFF 10%, #A78BFA 70%);
            -webkit-background-clip: text;
            background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .branding-desc {
            font-size: 1.05rem;
            line-height: 1.6;
            color: #94A3B8;
            margin-bottom: 2.5rem;
            max-width: 90%;
        }
        
        .feature-item {
            display: flex;
            align-items: center;
            gap: 1rem;
            margin-bottom: 1rem;
        }
        
        .feature-icon {
            font-size: 1.2rem;
        }
        
        .feature-text {
            color: #CBD5E1;
            font-size: 1rem;
            font-weight: 500;
        }

        /* 3. Right Column: Auth Section */
        /* Proper vertical alignment with heading instead of arbitrary margins */
        div[data-testid="column"]:nth-child(2) {
            padding-top: 5.2rem !important; /* Aligns exactly with DataWhisper heading */
        }

        /* Auth Card Glassmorphism */
        div[data-testid="column"]:nth-child(2) > div[data-testid="stVerticalBlock"] {
            background: rgba(18, 18, 24, 0.6) !important;
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.06) !important;
            border-radius: 24px !important;
            padding: 2rem 2.4rem 2.4rem 2.4rem !important;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3) !important;
            max-width: 450px !important;
            margin: 0 auto !important;
        }

        /* Remove double styling from Streamlit Form */
        div[data-testid="column"]:nth-child(2) .stForm {
            border: none !important;
            padding: 0 !important;
            background: transparent !important;
        }

        /* 4. Auth Components */
        /* Segmented Toggle */
        div[data-testid="stRadio"] {
            margin-bottom: 1.5rem !important;
            display: flex;
            justify-content: center;
        }

        div[data-testid="stRadio"] > div {
            background: rgba(0, 0, 0, 0.3) !important;
            padding: 4px !important;
            border-radius: 12px !important;
            border: 1px solid rgba(255, 255, 255, 0.05) !important;
            display: inline-flex !important;
            width: 100% !important;
            gap: 4px !important;
        }
        
        div[data-testid="stRadio"] div[role="radiogroup"] label {
            background-color: transparent !important;
            padding: 10px 0 !important;
            border-radius: 8px !important;
            color: #64748B !important;
            font-weight: 600 !important;
            text-align: center !important;
            justify-content: center !important;
            flex: 1 !important;
            margin: 0 !important;
            cursor: pointer !important;
            transition: all 0.2s ease !important;
        }
        
        div[data-testid="stRadio"] div[role="radiogroup"] label:hover {
            color: #E2E8F0 !important;
        }
        
        div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) {
            background: rgba(255, 255, 255, 0.08) !important;
            color: #FFFFFF !important;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2) !important;
        }
        
        div[data-testid="stRadio"] div[data-baseweb="radio"] > div:first-child {
            display: none !important; /* Hide radio circle */
        }

        /* Inputs */
        div[data-baseweb="input"] {
            background-color: rgba(255, 255, 255, 0.03) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-radius: 12px !important;
            transition: all 0.2s ease !important;
        }
        
        div[data-baseweb="input"]:focus-within {
            border-color: rgba(167, 139, 250, 0.6) !important;
            background-color: rgba(255, 255, 255, 0.05) !important;
        }

        input {
            color: #F8FAFC !important;
            height: 44px !important;
            padding: 0 16px !important;
            font-size: 1rem !important;
            background: transparent !important;
        }
        
        div[data-testid="stWidgetLabel"] p {
            color: #94A3B8 !important;
            font-size: 0.85rem !important;
            font-weight: 500 !important;
            margin-bottom: 0.4rem !important;
        }

        /* Buttons */
        button[kind="secondaryFormSubmit"], button[kind="primaryFormSubmit"], button[kind="primary"] {
            background: linear-gradient(135deg, #7C3AED 0%, #C026D3 100%) !important;
            color: white !important;
            border-radius: 12px !important;
            border: none !important;
            padding: 0.8rem 2rem !important;
            font-weight: 600 !important;
            font-size: 1rem !important;
            width: 100% !important;
            margin-top: 0.5rem !important;
            min-height: 48px !important;
            transition: all 0.2s ease !important;
        }
        
        button[kind="secondaryFormSubmit"]:hover, button[kind="primaryFormSubmit"]:hover, button[kind="primary"]:hover {
            transform: translateY(-1px) !important;
            background: linear-gradient(135deg, #8B5CF6 0%, #D946EF 100%) !important;
            box-shadow: 0 6px 15px rgba(124, 58, 237, 0.3) !important;
        }

        /* Alerts */
        .stException, .stAlert {
            border-radius: 12px !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
        }
        
        /* 5. Mobile Responsiveness */
        @media (max-width: 768px) {
            .branding-container {
                padding-right: 0;
                text-align: center;
                margin-bottom: 2rem;
            }
            .branding-badge {
                margin: 0 auto 1.5rem auto;
            }
            .feature-list {
                display: flex;
                flex-direction: column;
                align-items: center;
            }
            div[data-testid="column"]:nth-child(2) {
                padding-top: 0 !important; /* Stack cleanly */
            }
            div[data-testid="column"]:nth-child(2) > div[data-testid="stVerticalBlock"] {
                padding: 2rem 1.5rem !important;
                max-width: 100% !important;
            }
        }
        </style>
    """, unsafe_allow_html=True)

    # UI Structure
    st.markdown('<div style="margin-top: 5vh;"></div>', unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        st.markdown(
            '<div class="branding-container">'
                '<div class="branding-badge">✨ Next-Generation Analytics</div>'
                '<h1 class="branding-title">Meet <br><span class="branding-title-gradient">DataWhisper</span></h1>'
                '<p class="branding-desc">'
                    'Transform your raw data into actionable intelligence in seconds. '
                    'The AI-powered exploratory data analysis platform built for modern teams.'
                '</p>'
                '<div class="feature-list">'
                    '<div class="feature-item">'
                        '<span class="feature-icon">⚡️</span>'
                        '<span class="feature-text">Lightning fast AI insights</span>'
                    '</div>'
                    '<div class="feature-item">'
                        '<span class="feature-icon">🔒</span>'
                        '<span class="feature-text">Enterprise-grade security</span>'
                    '</div>'
                    '<div class="feature-item">'
                        '<span class="feature-icon">📊</span>'
                        '<span class="feature-text">Automated visualizations</span>'
                    '</div>'
                '</div>'
            '</div>', 
            unsafe_allow_html=True
        )

    with col2:
        auth_choice = st.radio("Action", ["Login", "Register"], label_visibility="collapsed", horizontal=True)
        
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
            # Inject CSS to make Register Form a compact 2-column grid
            st.markdown("""
                <style>
                /* Grid Layout for Register Form */
                div[data-testid="column"]:nth-child(2) .stForm > div[data-testid="stVerticalBlock"] {
                    display: grid !important;
                    grid-template-columns: 1fr 1fr !important;
                    gap: 0 1rem !important;
                }
                
                /* Title (Hide arbitrary register title) */
                div[data-testid="column"]:nth-child(2) .stForm > div[data-testid="stVerticalBlock"] > div:nth-child(1) {
                    display: none !important;
                }
                
                /* Email - Full width */
                div[data-testid="column"]:nth-child(2) .stForm > div[data-testid="stVerticalBlock"] > div:nth-child(2) {
                    grid-column: 1 / -1 !important;
                }
                
                /* Name & Username - Side by Side */
                div[data-testid="column"]:nth-child(2) .stForm > div[data-testid="stVerticalBlock"] > div:nth-child(3) {
                    grid-column: 1 !important;
                }
                div[data-testid="column"]:nth-child(2) .stForm > div[data-testid="stVerticalBlock"] > div:nth-child(4) {
                    grid-column: 2 !important;
                }
                
                /* Password & Repeat Password - Side by Side */
                div[data-testid="column"]:nth-child(2) .stForm > div[data-testid="stVerticalBlock"] > div:nth-child(5) {
                    grid-column: 1 !important;
                }
                div[data-testid="column"]:nth-child(2) .stForm > div[data-testid="stVerticalBlock"] > div:nth-child(6) {
                    grid-column: 2 !important;
                }
                
                /* Submit Button & Alerts - Full width */
                div[data-testid="column"]:nth-child(2) .stForm > div[data-testid="stVerticalBlock"] > div:nth-child(n+7) {
                    grid-column: 1 / -1 !important;
                    margin-top: 0.5rem !important;
                }

                /* Mobile: Stack fields vertically */
                @media (max-width: 768px) {
                    div[data-testid="column"]:nth-child(2) .stForm > div[data-testid="stVerticalBlock"] {
                        grid-template-columns: 1fr !important;
                    }
                    div[data-testid="column"]:nth-child(2) .stForm > div[data-testid="stVerticalBlock"] > div {
                        grid-column: 1 / -1 !important;
                    }
                }
                </style>
            """, unsafe_allow_html=True)
            
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
