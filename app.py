# app.py

import os
from tempfile import NamedTemporaryFile
import streamlit as st
from dotenv import load_dotenv
import cv2
import duo_client
import streamlit.components.v1 as components

from db import (
    save_cheque_data, 
    get_cheque_share, 
    get_share1_blob,
    verify_banker, 
    check_cheque_exists
)
from cryptography import (
    generate_visual_shares, 
    overlay_shares,
    send_email_with_attachment
)

# Load env and Duo setup
load_dotenv()
BASE_URL = os.getenv('APP_BASE_URL', 'http://localhost:8501')
duo = duo_client.Auth(
    ikey=os.getenv('DUO_IKEY'),
    skey=os.getenv('DUO_SKEY'),
    host=os.getenv('DUO_HOST')
)

st.title("Bank Cheque Verification System")
role = st.sidebar.selectbox("Select Role", ["Customer", "Banker"])

if role == "Customer":
    st.header("Customer: Upload Signed Cheque")
    uploaded = st.file_uploader("Upload Signed Cheque", type=["png","jpg","jpeg"])
    num      = st.text_input("Enter Cheque Number")
    msg_txt  = st.text_input("Enter Cheque Usage Message")
    banker_e = st.text_input("Enter Banker Email")

    if st.button("Generate Shares"):
        if not uploaded or not num or not msg_txt or not banker_e:
            st.error("Fill in all fields.")
        else:
            # save upload
            with NamedTemporaryFile(delete=False, suffix='.png') as tf:
                tf.write(uploaded.getbuffer())
                img_path = tf.name

            p1 = p2 = None
            try:
                s1, s2, p1, p2, s2b, h = generate_visual_shares(img_path, banker_e, num)
                with open(p1, 'rb') as f:
                    s1b = f.read()

                # Save to DB and email Share1 directly
                if save_cheque_data(num, s1b, s2b, h, msg_txt):
                    link = f"{BASE_URL}/?download_share1={num}"
                    body = (
                        f"Dear Banker,\n\n"
                        f"Cheque #{num} ready. Click the link to download Share 1.\n\n"
                        f"{link}"
                    )
                    sent = send_email_with_attachment(banker_e, f"Cheque Share #{num}", body, p1)
                    if sent:
                        st.success("Share 1 emailed to banker successfully.")
                    else:
                        st.error("Email failed.")
                else:
                    st.error("Saving to DB failed (duplicate?).")
            finally:
                # Cleanup created files
                for p in (img_path, p1, p2):
                    if p:
                        try:
                            os.unlink(p)
                        except:
                            pass

elif role == "Banker":
    st.header("Banker Dashboard")
    st.session_state.setdefault('logged_in', False)
    st.session_state.setdefault('push_sent', False)
    st.session_state.setdefault('duo_tx', None)
    st.session_state.setdefault('username', '')

    # Handle download link first (before login check)
    try:
        params = st.query_params
        dl = params.get('download_share1', None)
    except:
        # Fallback for older Streamlit versions
        params = st.experimental_get_query_params()
        dl = params.get('download_share1', [None])[0]
        
    if dl:
        st.header(f"Download Share 1 for Cheque #{dl}")
        # Direct download without password protection
        blob = get_share1_blob(dl)
        if blob:
            st.image(blob, caption=f"Share 1—Cheque #{dl}", use_container_width=True)
            st.download_button("Download Share 1", data=blob,
                            file_name=f"share1-{dl}.png", mime="image/png")
        else:
            st.error("Share not found.")
        st.stop()

    # Duo Push login
    if not st.session_state.logged_in:
        user = st.text_input("Username")
        pwd  = st.text_input("Password", type='password')
        login_button = st.button("Login")
        
        # Show this message immediately after login button pressed
        if login_button:
            if verify_banker(user, pwd):
                # Show waiting message immediately when button is pressed
                st.info("⏳ Sending Duo authentication request...")
                st.warning("Please wait for the push notification on your device")
                
                # Create a visual indication immediately 
                st.markdown("""
                <div style="text-align:center; margin:20px;">
                    <div style="display:inline-block; border:2px solid #4CAF50; border-radius:50%; padding:15px; animation:pulse 1.5s infinite">
                        <span style="font-size:24px;">📱</span>
                    </div>
                </div>
                <style>
                    @keyframes pulse {
                        0% { transform: scale(1); }
                        50% { transform: scale(1.1); }
                        100% { transform: scale(1); }
                    }
                </style>
                """, unsafe_allow_html=True)
                
                # Now send the Duo request
                resp = duo.auth(username=user, factor="push", device="auto")
                if resp.get('result') == 'allow':
                    st.session_state.logged_in = True
                    st.success("Duo auto-approved—logged in!")
                    st.rerun()  # Use st.rerun() instead of experimental_rerun
                else:
                    st.session_state.duo_tx = resp.get('txid')
                    st.session_state.push_sent = True
                    st.session_state.username = user
            else:
                st.error("Invalid credentials.")

        if st.session_state.push_sent and not st.session_state.logged_in:
            st.info("⏳ Duo push notification sent to your device")
            st.warning("Please approve the authentication request on your Duo Mobile app")
            # Create a visual indication
            st.markdown("""
            <div style="text-align:center; margin:20px;">
                <div style="display:inline-block; border:2px solid #4CAF50; border-radius:50%; padding:15px; animation:pulse 1.5s infinite">
                    <span style="font-size:24px;">📱</span>
                </div>
            </div>
            <style>
                @keyframes pulse {
                    0% { transform: scale(1); }
                    50% { transform: scale(1.1); }
                    100% { transform: scale(1); }
                }
            </style>
            """, unsafe_allow_html=True)
            
            # Auto-refresh the page to check approval status
            components.html("<meta http-equiv='refresh' content='2'>", height=0)
            
            # Check if the Duo push has been approved
            if duo.auth_status(st.session_state.duo_tx).get('result') == 'allow':
                st.session_state.logged_in = True
                st.success("✅ Duo authentication approved!")
                st.rerun()  # Use st.rerun() instead of experimental_rerun
        
        # CRITICAL: Stop here if not logged in to prevent showing the verification UI
        if not st.session_state.logged_in:
            st.stop()

    # Verification UI - Only shown when logged in
    st.subheader("Cheque Verification")
    cheque = st.text_input("Enter Cheque Number")
    f1 = st.file_uploader("Upload Share 1", type=['png'])
    if st.button("Perform Integrity Check"):
        if not cheque or not f1:
            st.error("Please enter cheque number & upload share1.")
        else:
            with NamedTemporaryFile(delete=False, suffix='.png') as tf1:
                tf1.write(f1.getbuffer()); path1 = tf1.name
            row = get_cheque_share(cheque)
            if row:
                s2b, oh, usage = row
                with NamedTemporaryFile(delete=False, suffix='.png') as tf2:
                    tf2.write(s2b); path2 = tf2.name
                rec, ok = overlay_shares(path1, path2, oh)
                if rec is not None:
                    st.info(f"Usage Message: {usage}")
                    tmp = NamedTemporaryFile(delete=False, suffix='.png')
                    cv2.imwrite(tmp.name, rec)
                    st.image(tmp.name, use_container_width=True)
                    st.success("Integrity OK" if ok else "Integrity FAIL")
                    os.unlink(tmp.name)
                else:
                    st.error("Recovery failed.")
                os.unlink(path2)
            else:
                st.error("Cheque not found.")
            os.unlink(path1)