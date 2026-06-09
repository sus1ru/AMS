import hashlib
import os

def hash_password(password):
    salt = os.urandom(16)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        salt,
        100000,
    )

    return f"{salt.hex()}:{password_hash.hex()}"


def verify_password(password, stored_password):
    salt_hex, hash_hex = stored_password.split(":")

    salt = bytes.fromhex(salt_hex)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        salt,
        100000,
    )

    return password_hash.hex() == hash_hex