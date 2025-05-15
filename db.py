# db.py

import os
from dotenv import load_dotenv
import mysql.connector

load_dotenv()

def get_db_connection():
    """
    Return a MySQL connection (via socket if CLOUD_SQL_CONNECTION_NAME set).
    """
    cfg = {
        "user":     os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "database": os.getenv("DB_NAME"),
    }
    socket = os.getenv("CLOUD_SQL_CONNECTION_NAME")
    if socket:
        cfg["unix_socket"] = f"/cloudsql/{socket}"
    else:
        cfg["host"] = os.getenv("DB_HOST", "127.0.0.1")
        cfg["port"] = int(os.getenv("DB_PORT", 3306))
    return mysql.connector.connect(**cfg)

def check_cheque_exists(cheque_number: str) -> bool:
    try:
        conn = get_db_connection()
        cur  = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM cheques WHERE cheque_number=%s", (cheque_number,))
        exists = cur.fetchone()[0] > 0
        conn.close()
        return exists
    except mysql.connector.Error as e:
        print(f"Error checking existence: {e}")
        return False

def save_cheque_data(cheque_number, share1_bytes, share2_bytes, original_hash, issue_message):
    """
    Insert the two shares, hash, and usage message into `cheques`.
    """
    try:
        conn = get_db_connection()
        cur  = conn.cursor()
        cur.execute("""
            INSERT INTO cheques
               (cheque_number, share1, share2, original_hash, issue_message)
            VALUES (%s,%s,%s,%s,%s)
        """, (cheque_number, share1_bytes, share2_bytes, original_hash, issue_message))
        conn.commit()
        conn.close()
        return True
    except mysql.connector.Error as e:
        print(f"Error saving cheque: {e}")
        return False

def get_cheque_share(cheque_number):
    """
    Return (share2_bytes, original_hash, issue_message) or None.
    """
    try:
        conn = get_db_connection()
        cur  = conn.cursor()
        cur.execute("SELECT share2, original_hash, issue_message FROM cheques WHERE cheque_number=%s",
                    (cheque_number,))
        row = cur.fetchone()
        conn.close()
        return row if row else None
    except mysql.connector.Error as e:
        print(f"Error retrieving share: {e}")
        return None

def get_share1_blob(cheque_number):
    """
    Return share1 bytes or None.
    """
    try:
        conn = get_db_connection()
        cur  = conn.cursor()
        cur.execute("SELECT share1 FROM cheques WHERE cheque_number=%s", (cheque_number,))
        row = cur.fetchone()
        conn.close()
        return row[0] if row else None
    except mysql.connector.Error as e:
        print(f"Error retrieving share1: {e}")
        return None

def verify_banker(username, password):
    """
    Return True if (username,password) matches bankers table.
    """
    try:
        conn = get_db_connection()
        cur  = conn.cursor()
        cur.execute("SELECT banker_password FROM bankers WHERE username=%s", (username,))
        row = cur.fetchone()
        conn.close()
        return bool(row and row[0] == password)
    except mysql.connector.Error as e:
        print(f"Error verifying banker: {e}")
        return False
