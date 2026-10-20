from pwdlib import PasswordHash

# Create a password hashing context using the "recommended" preset.
# By default, pwdlib's recommended preset uses Argon2 (via the argon2-cffi
# backend), which is a modern, memory-hard hashing algorithm designed to
# resist GPU/ASIC brute-force attacks better than bcrypt.
password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """
    Hash a plain-text password using Argon2.

    Args:
        password: The plain-text password provided by the user.

    Returns:
        The Argon2 hash string (includes salt + parameters),
        safe to store in the database.
    """
    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Check a plain-text password against a stored Argon2 hash.

    Args:
        password: The plain-text password to check (e.g. from a login form).
        hashed_password: The Argon2 hash stored in the database.

    Returns:
        True if the password matches the hash, False otherwise.
    """
    return password_hash.verify(password, hashed_password)