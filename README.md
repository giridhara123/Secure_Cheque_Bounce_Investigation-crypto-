# Secure_Cheque_Bounce_Investigation-crypto-
index Terms—Bank Cheque Verification, Visual Cryptography, Two-Factor Authentication, XOR-based Secret Sharing, SHA- 256, Financial Security, Tamper Detection.

1.Overview
This system addresses security challenges in traditional cheque processing by implementing a multi-
layered approach to cheque verification. It uses visual cryptography to split cheque images into two
complementary shares, stores them securely, and provides a tamper-evident verification process.
2 Features
• XOR-based Visual Cryptography: Splits cheque images into two complementary shares
• SHA-256 Integrity Checking: Ensures tamper detection through cryptographic hashing
• Duo Two-Factor Authentication: Secures banker access with push notifications
• Role-based Access Control: Separate interfaces for customers and bankers
• Secure Email Transmission: Safely delivers Share 1 to bankers
• Encrypted Database Storage: Securely stores Share 2 and verification data
• User-friendly Web Interface: Built with Streamlit for easy navigation
3 System Architecture
The application follows a client-server architecture with four primary components:
1. Customer Interface: Upload cheque images and provide reference information
2. Visual Cryptography Engine: Generate shares and compute hash for integrity verification
3. Authentication Module: Implement multi-factor authentication for banker access
4. Verification Interface: Combine shares and verify cheque integrity
4 How It Works
4.1 Customer Workflow
1. Upload a signed cheque image
2. Enter cheque number and usage message
3. Provide banker’s email
4. Submit for share generation
5. System emails Share 1 to banker and stores Share 2 in database
1
4.2 Banker Workflow
1. Login with username/password
2. Approve Duo push notification on mobile device
3. Enter cheque number to verify
4. Upload Share 1 (received via email)
5. System retrieves Share 2 from database
6. System overlays shares and verifies hash integrity
7. View reconstructed cheque and verification status
5 Technology Stack
• Backend: Python
• Web Framework: Streamlit
• Image Processing: OpenCV (cv2)
• Database: MySQL
• Authentication: Duo Security SDK
• Email: SMTP via Python’s smtplib
• Cryptography: Custom implementation with NumPy and hashlib
6 Installation
1. Install dependencies
1 pip install -r r e q u i r e m e n t s . txt
2. Set up environment variables in a .env file
1 DB_USER = y o u r _ d b _ u s e r
2 D B _ P A S S W O R D = y o u r _ d b _ p a s s w o r d
3 DB_NAME = y o u r _ d b _ n a m e
4 DB_HOST = l o ca lh os t
5 DB_PORT =3306
10 11 6 E M A I L _ U S E R = y o u r _ e m a i l @ e x a m p l e . com
7 E M A I L _ P A S S = y o u r _ e m a i l _ p a s s w o r d
8 DUO_IKEY = y o u r _ d u o _ i n t e g r a t i o n _ k e y
9 DUO_SKEY = y o u r _ d u o _ s e c r e t _ k e y
DUO_HOST = y o u r _ d u o _ a p i _ h o s t n a m e
A P P _ B A S E _ U R L = http :// lo c al ho s t :8501
8 c r e a t e d _ a t TI ME S TA MP 3. Create the MySQL database schema
1 CREATE TABLE cheques (
3 c h e q u e _ n u m b e r 4 share1 LONGBLOB ,
5 share2 LONGBLOB ,
6 o r i g i n a l _ h a s h 7 i s s u e _ m e s s a g e VARCHAR (50) VARCHAR (64) ,
TEXT ,
9 ) ;
10
11 12 13 14 15 16 17 2 id INT A U T O _ I N C R E M E N T PRIMARY KEY ,
UNIQUE ,
DEFAULT C U R R E N T _ T I M E S T A M P
CREATE TABLE bankers (
id INT A U T O _ I N C R E M E N T PRIMARY KEY ,
username VARCHAR (50) UNIQUE ,
b a n k e r _ p a s s w o r d VARCHAR (255) ,
email VARCHAR (100) ,
c r e a t e d _ a t TI ME S TA MP DEFAULT C U R R E N T _ T I M E S T A M P
) ;
2
4. Run the application
1 s tr ea m li t run app . py
7 Security Considerations
• All sensitive credentials are stored in environment variables
• Temporary files are securely handled and immediately removed after use
• Input validation prevents common attacks like SQL injection
• Share 1 is delivered securely via email rather than as direct attachments
• Two-factor authentication prevents unauthorized access even if credentials are compromised
8 Performance
• Share Generation: ∼0.6 seconds per cheque
• Verification Process: ∼0.9 seconds per verification
• Email Delivery: ∼4.4 seconds on average
• Authentication: ∼6.2 seconds including Duo push response
9 Implementation Details
9.1 Visual Cryptography Process
The system uses XOR-based visual cryptography with the following steps:
1. Share Generation: For a cheque image C, we generate two shares (S1 and S2):
• S1 is a random pixel matrix with the same dimensions as C
• S2 = C ⊕ S1 (where ⊕ represents the bitwise XOR operation)
2. Image Reconstruction: To recover the original cheque image, the system performs:
• C= S1 ⊕ S2
9.2 SHA-256 Integrity Check
SHA-256 is used to verify the integrity of the reconstructed cheque:
1. Compute SHA-256 hash of the original cheque image
2. Store the hash in the database along with Share 2
3. Reconstruct the cheque by XORing Share 1 and Share 2
4. Compute SHA-256 hash of the reconstructed cheque
5. Compare the reconstructed hash with the stored hash:
• If hashes match, integrity is verified
• If hashes differ, tampering is detected
3
9.3 Two-Factor Authentication
Banker authentication employs a multi-layered approach:
1. Username/Password Authentication: Basic credential verification against the secure MySQL
database
2. Duo Push Authentication: Upon successful credential verification, the system initiates a Duo
push notification to the banker’s registered device, requiring explicit approval before granting access
to the verification interface
