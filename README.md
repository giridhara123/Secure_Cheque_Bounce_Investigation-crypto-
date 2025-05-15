# Secure Cheque Bounce Investigation System

A multi-layered secure cheque verification system using Visual Cryptography, SHA-256 hashing, and Two-Factor Authentication to prevent cheque tampering and fraud.

## 📑 Index Terms

Bank Cheque Verification, Visual Cryptography, Two-Factor Authentication, XOR-based Secret Sharing, SHA-256, Financial Security, Tamper Detection.

## 📝 Overview

This system addresses security challenges in traditional cheque processing by implementing a multi-layered verification process. It leverages visual cryptography to split cheque images into two complementary shares, ensures tamper detection using SHA-256 hashing, and secures banker access via Duo two-factor authentication.

## 🚀 Features

- XOR-based Visual Cryptography: Splits cheque images into two shares.
- SHA-256 Integrity Checking: Detects tampering through cryptographic hashing.
- Duo Two-Factor Authentication: Secures banker login via push notifications.
- Role-based Access Control: Distinct interfaces for customers and bankers.
- Secure Email Transmission: Sends Share 1 securely via email.
- Encrypted Database Storage: Stores Share 2 and metadata securely.
- User-friendly Web Interface: Built using Streamlit for easy navigation.

## 🏛️ System Architecture

1. Customer Interface: Upload cheque images and provide verification details.
2. Visual Cryptography Engine: Generate XOR-based shares and compute SHA-256 hash.
3. Authentication Module: Duo push-based multi-factor authentication for bankers.
4. Verification Interface: Reconstruct cheque and validate integrity.

## 🔄 Workflows

### 🧑‍💼 Customer Workflow

1. Upload signed cheque image.
2. Enter cheque number and usage message.
3. Provide banker’s email.
4. Submit for share generation.
5. System emails Share 1 to banker and stores Share 2 securely.

### 🏦 Banker Workflow

1. Login with username/password.
2. Approve Duo push notification on mobile device.
3. Enter cheque number to verify.
4. Upload Share 1 (received via email).
5. System retrieves Share 2, reconstructs cheque, and verifies integrity.
6. View verification result.

## 🛠️ Technology Stack

- Backend: Python
- Web Framework: Streamlit
- Image Processing: OpenCV (cv2)
- Database: MySQL
- Authentication: Duo Security SDK
- Email: SMTP via smtplib
- Cryptography: NumPy & hashlib

## ⚙️ Installation & Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables (.env)

```
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_NAME=your_db_name
DB_HOST=localhost
DB_PORT=3306
EMAIL_USER=your_email@example.com
EMAIL_PASS=your_email_password
DUO_IKEY=your_duo_integration_key
DUO_SKEY=your_duo_secret_key
DUO_HOST=your_duo_api_hostname
APP_BASE_URL=http://localhost:8501
```

### 3. Create MySQL Database Schema

```sql
CREATE TABLE cheques (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cheque_number VARCHAR(50) UNIQUE,
    share1 LONGBLOB,
    share2 LONGBLOB,
    original_hash VARCHAR(64),
    issue_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE bankers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE,
    banker_password VARCHAR(255),
    email VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 4. Run the Application

```bash
streamlit run app.py
```

## 🛡️ Security Considerations

- Credentials secured via environment variables.
- Temporary files removed after processing.
- Input validation against SQL Injection.
- Secure email transmission for Share 1.
- Two-factor authentication to prevent unauthorized access.

## ⚡ Performance Benchmarks

| Process             | Average Time |
|--------------------|--------------|
| Share Generation    | ~0.6 sec     |
| Verification        | ~0.9 sec     |
| Email Delivery      | ~4.4 sec     |
| Authentication     | ~6.2 sec     |

## 🧩 Implementation Details

### 1. Visual Cryptography (XOR-Based)

- Share Generation:
  - S1: Random matrix of same dimensions as cheque image C.
  - S2 = C ⊕ S1

- Reconstruction:
  - C = S1 ⊕ S2

### 2. SHA-256 Integrity Verification

1. Compute SHA-256 hash of the original cheque image.
2. Store hash in the database with Share 2.
3. On verification, reconstruct cheque using S1 and S2.
4. Compute and compare SHA-256 hash with stored hash to detect tampering.

### 3. Two-Factor Authentication

- Step 1: Username/Password verification.
- Step 2: Duo Push Notification to banker’s registered device.

## 📬 Contact

For any questions or issues, please contact [Giridhara venkat vootla](vootlagiridharavenkat@gmail.com).
