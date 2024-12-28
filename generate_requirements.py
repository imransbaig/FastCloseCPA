import subprocess
import sys

def generate_requirements():
    packages = [
        "email-validator==2.2.0",
        "flask-login==0.6.3",
        "flask==3.1.0",
        "flask-sqlalchemy==3.1.1",
        "gunicorn==23.0.0",
        "psycopg2-binary==2.9.10",
        "trafilatura==2.0.0",
        "werkzeug==3.1.3",
        "wfastcgi==3.0.0"
    ]
    
    try:
        # Install packages
        for package in packages:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        
        # Generate requirements.txt
        subprocess.check_call([sys.executable, "-m", "pip", "freeze", ">", "requirements.txt"], shell=True)
        print("Requirements.txt generated successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    generate_requirements()
