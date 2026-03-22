# Smart EDA Assistant 🚀 - Deployment Guide

This guide covers how to deploy the Smart EDA Assistant to **Streamlit Community Cloud** (the fastest, easiest, and free method for Streamlit applications).

## Prerequisites
1. A GitHub account.
2. A Streamlit Community Cloud account (you can sign in with GitHub).

## Step 1: Push Code to GitHub
Ensure your code is uploaded to a GitHub repository. Your repository **MUST** contain the `requirements.txt` file so the cloud server knows what dependencies to install.

## Step 2: Connect to Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io) and log in.
2. Click **"New app"**.
3. Select your GitHub repository from the dropdown.
4. Set the **Branch** (usually `main` or `master`).
5. Set the **Main file path** to `app.py`.
6. **CRITICAL FOR SPEED**: Click **"Advanced settings"** and change the Python version to **3.11**. Streamlit defaults to the newest Python (e.g. 3.14), which forces packages to be built from source (taking 15+ minutes). Python 3.11 uses pre-built instant binaries.

## Step 3: Set Secrets (Optional)
If you wish to hardcode an OpenAI API Key for global use (not recommended for public apps), you can click "Advanced settings" before deploying and add your keys to the `Secrets` block:
```toml
OPENAI_API_KEY="sk-..."
```
*Note: We built the UI so users enter their own keys, which is safer.*

## Step 4: Deploy
Click **"Deploy!"**. Streamlit will automatically provision a server, install your `requirements.txt` using Python Pip, and launch your application.

## Authentication Note
We integrated `streamlit-authenticator` configured locally. The default demo credentials (`demo` / `password`) will work right out of the box in the cloud because the configuration gets pushed with the code and hashes securely via cookies. To manage users, edit the `config.yaml` using the built-in streamlit-authenticator utilities.
