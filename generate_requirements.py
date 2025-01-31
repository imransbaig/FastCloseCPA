import subprocess
import sys

def generate_requirements():
    """Generate requirements.txt file from the installed packages"""
    packages = [
        "email-validator==2.2.0",
        "flask-login==0.6.3",
        "flask==3.1.0",
        "flask-sqlalchemy==3.1.1",
        "gunicorn==23.0.0",
        "psycopg2-binary==2.9.10",
        "pytest==8.0.0",
        "trafilatura==2.0.0",
        "werkzeug==3.1.3",
        "wfastcgi==3.0.0"
    ]

    try:
        # Generate requirements.txt directly
        with open('requirements.txt', 'w') as f:
            for package in packages:
                f.write(f"{package}\n")
        print("Requirements.txt generated successfully!")
        return True
    except Exception as e:
        print(f"Error occurred: {e}")
        return False

if __name__ == "__main__":
    sys.exit(0 if generate_requirements() else 1)