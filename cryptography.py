# cryptography.py

import os
import random
import hashlib
import cv2
import numpy as np
from email.message import EmailMessage
import smtplib
from dotenv import load_dotenv

load_dotenv()  # for EMAIL_USER / EMAIL_PASS

def compute_image_hash_from_array(img):
    """
    Compute the SHA256 hash of a NumPy image array (encoded as PNG).
    """
    retval, buffer = cv2.imencode('.png', img)
    if not retval:
        return None
    return hashlib.sha256(buffer).hexdigest()

def save_shares_to_files(share1, share2, filename_prefix=""):
    """
    Write share1 and share2 images to disk under ./temp, return their paths + share2 bytes.
    """
    temp_dir = os.path.join(os.getcwd(), "temp")
    os.makedirs(temp_dir, exist_ok=True)

    if filename_prefix:
        name1 = f"{filename_prefix}-share1.png"
        name2 = f"{filename_prefix}-share2.png"
    else:
        rid = random.randint(10000, 99999)
        name1 = f"share1-{rid}.png"
        name2 = f"share2-{rid}.png"

    path1 = os.path.join(temp_dir, name1)
    path2 = os.path.join(temp_dir, name2)

    cv2.imwrite(path1, share1)
    cv2.imwrite(path2, share2)

    with open(path2, "rb") as f:
        share2_bytes = f.read()

    return path1, path2, share2_bytes

def generate_visual_shares(image_path, email="", cheque_number=""):
    """
    Create two XOR-shares of the original image and compute its SHA-256 hash.
    Returns (share1, share2, share1_path, share2_path, share2_bytes, original_hash).
    """
    original = cv2.imread(image_path, cv2.IMREAD_COLOR)
    if original is None:
        return None, None, None, None, None, None

    orig_hash = compute_image_hash_from_array(original)
    share1 = np.random.randint(0, 256, original.shape, dtype=np.uint8)
    share2 = cv2.bitwise_xor(original, share1)

    prefix = f"{email[:4]}-{cheque_number}" if email and cheque_number else ""
    p1, p2, p2b = save_shares_to_files(share1, share2, prefix)
    return share1, share2, p1, p2, p2b, orig_hash

def overlay_shares(share1_path, share2_path, original_hash):
    """
    XORs the two share files to reconstruct the original, then checks its hash.
    Returns (recovered_img_array, integrity_ok: bool).
    """
    s1 = cv2.imread(share1_path, cv2.IMREAD_COLOR)
    s2 = cv2.imread(share2_path, cv2.IMREAD_COLOR)
    if s1 is None or s2 is None:
        return None, False

    rec = cv2.bitwise_xor(s1, s2)
    ok  = (compute_image_hash_from_array(rec) == original_hash)
    return rec, ok

def send_email_with_attachment(recipient, subject, body, attachment_path=None):
    """
    Send an email (with optional attachment) via SMTP_SSL using EMAIL_USER/PASS.
    """
    EMAIL = os.getenv("EMAIL_USER")
    PASS  = os.getenv("EMAIL_PASS")
    if not EMAIL or not PASS:
        return False

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"]    = EMAIL
    msg["To"]      = recipient
    msg.set_content(body)

    if attachment_path:
        try:
            with open(attachment_path, "rb") as f:
                data = f.read()
            fn = os.path.basename(attachment_path)
            if fn.lower().endswith(".zip"):
                maintype, subtype = "application", "zip"
            elif fn.lower().endswith((".png",".jpg"," .jpeg")):
                maintype, subtype = "image", fn.split(".")[-1].lower()
            else:
                maintype, subtype = "application", "octet-stream"
            msg.add_attachment(data, maintype=maintype, subtype=subtype, filename=fn)
        except Exception as e:
            print(f"Attachment error: {e}")
            return False

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL, PASS)
            smtp.send_message(msg)
        return True
    except Exception as e:
        print(f"Email send error: {e}")
        return False