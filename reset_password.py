"""Reset one account's password from Termux. Needs DATABASE_URL set.

Usage: python3 reset_password.py USERNAME
The new recovery code is printed once. Give it to the user, and don't store it anywhere else.
"""
import getpass
import sys

import app as a
from werkzeug.security import generate_password_hash

if len(sys.argv) != 2:
    sys.exit("Usage: python3 reset_password.py USERNAME")
username = sys.argv[1]
password = getpass.getpass("New password (8+ characters): ")
if len(password) < 8:
    sys.exit("Password too short.")

db = a.connect()
row = db.execute("SELECT username FROM users WHERE username = ?", (username,)).fetchone()
if row is None:
    db.close()
    sys.exit("No account with that username.")

code = a.new_recovery_code()
db.execute(
    "UPDATE users SET password_hash = ?, recovery_hash = ? WHERE username = ?",
    (generate_password_hash(password), generate_password_hash(a.normalize_code(code)), username),
)
db.commit()
db.close()
print("Password reset for", username)
print("New recovery code (give it to the user once):", code)
