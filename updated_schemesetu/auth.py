import os
import re
import smtplib
import msvcrt
from email.message import EmailMessage

from database import (
    authenticate_user,
    create_user,
    email_exists,
)


# ---------------------------------------------------
# LOAD .ENV FILE
# ---------------------------------------------------

def load_env_file(path=".env"):
    if not os.path.exists(path):
        return

    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)

            os.environ.setdefault(
                key.strip(),
                value.strip().strip('"').strip("'"),
            )


load_env_file()


# ---------------------------------------------------
# PASSWORD INPUT WITH *
# ---------------------------------------------------

def input_password(prompt="Password: "):
    print(prompt, end="", flush=True)

    password = ""

    while True:
        char = msvcrt.getwch()

        # Enter key
        if char == "\r":
            print()
            break

        # Backspace
        elif char == "\b":
            if password:
                password = password[:-1]
                print("\b \b", end="", flush=True)

        # Ignore special keys
        elif char in ("\x00", "\xe0"):
            msvcrt.getwch()

        # Ctrl + C
        elif char == "\x03":
            raise KeyboardInterrupt

        else:
            password += char
            print("*", end="", flush=True)

    return password


# ---------------------------------------------------
# EMAIL VALIDATION
# ---------------------------------------------------

def valid_email(email):
    pattern = (
        r"^[A-Za-z0-9._%+-]+"
        r"@[A-Za-z0-9.-]+"
        r"\.[A-Za-z]{2,}$"
    )

    return re.fullmatch(
        pattern,
        email.strip()
    ) is not None


# ---------------------------------------------------
# PASSWORD VALIDATION
# ---------------------------------------------------

def validate_password(password):
    errors = []

    if len(password) < 8:
        errors.append("At least 8 characters")

    if not any(char.isupper() for char in password):
        errors.append("At least one uppercase letter")

    if not any(char.islower() for char in password):
        errors.append("At least one lowercase letter")

    if not any(char.isdigit() for char in password):
        errors.append("At least one number")

    if not any(not char.isalnum() for char in password):
        errors.append("At least one special character")

    return errors


# ---------------------------------------------------
# SEND REGISTRATION CONFIRMATION EMAIL
# ---------------------------------------------------

def send_registration_email(receiver_email, name):
    sender_email = (
        os.getenv(
            "SCHEMESETU_EMAIL",
            ""
        )
        .strip()
    )

    app_password = (
        os.getenv(
            "SCHEMESETU_APP_PASSWORD",
            ""
        )
        .replace(" ", "")
    )

    # Email notification is optional.
    # Registration should still succeed without it.
    if not sender_email or not app_password:
        print(
            "\nNote: Email notification is not configured."
        )
        return False

    message = EmailMessage()

    message["Subject"] = (
        "Welcome to SchemeSetu"
    )

    message["From"] = sender_email
    message["To"] = receiver_email

    message.set_content(
        f"""
Hello {name},

Your SchemeSetu account has been created successfully.

You can now login using your registered email address
and password.

SchemeSetu helps you discover government schemes
based on your profile and eligibility information.

Thank you for using SchemeSetu.

Regards,
SchemeSetu Team
"""
    )

    try:
        with smtplib.SMTP_SSL(
            "smtp.gmail.com",
            465,
            timeout=20
        ) as smtp:

            smtp.login(
                sender_email,
                app_password
            )

            smtp.send_message(
                message
            )

        print(
            "Confirmation email sent successfully."
        )

        return True

    except Exception as error:
        print(
            "\nAccount was created successfully,"
        )
        print(
            "but the confirmation email could not be sent."
        )
        print(
            "Email error:",
            error
        )

        return False


# ---------------------------------------------------
# REGISTER USER
# ---------------------------------------------------

def register_user():

    print("\n" + "=" * 52)
    print("                    REGISTER")
    print("=" * 52)

    # -----------------------------------------------
    # NAME
    # -----------------------------------------------

    name = input(
        "Full name: "
    ).strip()

    if len(name) < 2:
        print(
            "Please enter a valid name."
        )
        return None

    # -----------------------------------------------
    # EMAIL
    # -----------------------------------------------

    email = (
        input(
            "Email: "
        )
        .strip()
        .lower()
    )

    if not valid_email(email):
        print(
            "Invalid email format."
        )
        return None

    if email_exists(email):
        print(
            "An account with this email already exists."
        )
        return None

    # -----------------------------------------------
    # PASSWORD
    # -----------------------------------------------

    print(
        "\nPassword requirements:"
    )
    print(
        "- Minimum 8 characters"
    )
    print(
        "- One uppercase letter"
    )
    print(
        "- One lowercase letter"
    )
    print(
        "- One number"
    )
    print(
        "- One special character\n"
    )

    password = input_password(
        "Password: "
    )

    errors = validate_password(
        password
    )

    if errors:
        print(
            "\nPassword is not strong enough."
        )

        print(
            "Missing requirements:"
        )

        for error in errors:
            print(
                "-",
                error
            )

        return None

    confirm_password = input_password(
        "Confirm password: "
    )

    if password != confirm_password:
        print(
            "\nPasswords do not match."
        )
        return None

    # -----------------------------------------------
    # CREATE USER
    # -----------------------------------------------

    try:
        user_id = create_user(
            name,
            email,
            password
        )

    except Exception as error:
        print(
            "\nCould not create account."
        )
        print(
            "Reason:",
            error
        )
        return None

    # -----------------------------------------------
    # SUCCESS
    # -----------------------------------------------

    print("\n" + "=" * 52)
    print("ACCOUNT CREATED SUCCESSFULLY!")
    print("=" * 52)

    print(
        f"Welcome to SchemeSetu, {name}!"
    )

    # -----------------------------------------------
    # SEND CONFIRMATION EMAIL
    # -----------------------------------------------

    send_registration_email(
        email,
        name
    )

    print(
        "\nYou can now login."
    )

    return user_id


# ---------------------------------------------------
# LOGIN USER
# ---------------------------------------------------

def login_user():

    print("\n" + "=" * 52)
    print("                      LOGIN")
    print("=" * 52)

    # -----------------------------------------------
    # EMAIL
    # -----------------------------------------------

    email = (
        input(
            "Email: "
        )
        .strip()
        .lower()
    )

    if not valid_email(email):
        print(
            "Invalid email format."
        )
        return None

    # -----------------------------------------------
    # PASSWORD
    # -----------------------------------------------

    password = input_password(
        "Password: "
    )

    # -----------------------------------------------
    # DATABASE AUTHENTICATION
    # -----------------------------------------------

    user = authenticate_user(
        email,
        password
    )

    if user is None:
        print(
            "\nInvalid email or password."
        )
        return None

    # -----------------------------------------------
    # SUCCESS
    # -----------------------------------------------

    print(
        "\nLogin successful!"
    )

    print(
        f"Welcome, {user['name']}!"
    )

    return user