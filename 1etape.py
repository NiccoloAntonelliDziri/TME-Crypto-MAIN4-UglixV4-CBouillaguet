import base64
import os
import subprocess

def decrypt(cipherText, passphrase):
    # If the cipherText is a string, convert it to bytes
    if isinstance(cipherText, str):
        cipherText = cipherText.encode('utf-8')    

    # Decode the base64-encoded ciphertext
    cipherText = base64.b64decode(cipherText)
    
    # Write the decoded cipherText to a file
    with open("encrypted_message.bin", "wb") as enc_file:
        enc_file.write(cipherText)
    
    # Decrypt the cipherText using OpenSSL with passphrase-based decryption
    subprocess.run([
        "openssl", "enc", "-d", "-aes-128-cbc", "-pbkdf2", 
        "-in", "encrypted_message.bin", 
        "-out", "decrypted_message.txt", 
        "-pass", f"pass:{passphrase}"
    ], check=True)
    
    # Read the decrypted message
    with open("decrypted_message.txt", "rb") as dec_file:
        decrypted_message = dec_file.read()
    
    # Clean up the files
    os.remove("encrypted_message.bin")
    os.remove("decrypted_message.txt")
    
    return decrypted_message

# Get input from the user for enc_message and passphrase
enc_message = input("Enter the encrypted message (Base64 encoded): ")
passphrase = input("Enter the passphrase: ")
message = decrypt(enc_message, passphrase)

print("Decrypted message:")
print(message.decode("utf-8"))
