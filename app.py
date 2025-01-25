import os
from flask import Flask, render_template, request, flash, redirect, url_for
import logging
from datetime import datetime
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from extensions import db
from werkzeug.security import generate_password_hash

# Setup detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
logger.info("Flask application instance created")

# setup a secret key, required by sessions
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or "a secret key"

# Configure SendGrid
SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
logger.info(f"SendGrid API Key configured: {'Yes' if SENDGRID_API_KEY else 'No'}")

# Configure database - use PostgreSQL for Azure, fallback to SQLite for local
database_url = os.environ.get('DATABASE_URL', 'sqlite:///fastclose.db')
if database_url.startswith("postgres://"):  # Handle Azure PostgreSQL URL
    database_url = database_url.replace("postgres://", "postgresql://", 1)
    # Add SSL mode and connection retry parameters
    if '?' in database_url:
        database_url += '&sslmode=require&connect_timeout=10'
    else:
        database_url += '?sslmode=require&connect_timeout=10'
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
    'pool_timeout': 900
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
logger.info("Database configuration set")

# Initialize extensions
db.init_app(app)
logger.info("Database initialization complete")

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
logger.info("Flask-Login initialized")

# Import models after db initialization
try:
    from models import User, Consultation, BlogPost, Document
    logger.info("Models imported successfully")
except Exception as e:
    logger.error(f"Error importing models: {e}")
    raise

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Import and register blueprints
try:
    from blueprints.client_portal import bp as client_portal_bp
    app.register_blueprint(client_portal_bp)
    logger.info("Client portal blueprint registered")
except Exception as e:
    logger.error(f"Error registering client portal blueprint: {e}")

# Add a test route to verify the server is working
@app.route('/health')
def health_check():
    return {'status': 'ok', 'message': 'Flask server is running'}

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()
        if user and user.check_password(request.form['password']):
            login_user(user)
            flash('Logged in successfully.', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        flash('Invalid email or password.', 'error')
    return render_template('auth/login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if User.query.filter_by(email=request.form['email']).first():
            flash('Email already registered.', 'error')
            return redirect(url_for('register'))

        user = User(
            username=request.form['username'],
            email=request.form['email']
        )
        user.set_password(request.form['password'])

        try:
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash('Registration successful!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            logger.error(f"Registration error: {e}")
            db.session.rollback()
            flash('An error occurred during registration.', 'error')

    return render_template('auth/register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

@app.route('/')
def index():
    logger.debug("Accessing index route")
    return render_template('index.html')

@app.route('/blog')
def blog():
    logger.debug("Accessing blog route")
    posts = BlogPost.query.filter_by(published=True).order_by(BlogPost.created_at.desc()).all()
    return render_template('blog.html', posts=posts)

@app.route('/blog/<slug>')
def blog_post(slug):
    logger.debug(f"Accessing blog post with slug: {slug}")
    post = BlogPost.query.filter_by(slug=slug, published=True).first_or_404()
    return render_template('blog_post.html', post=post)

@app.route('/industries')
def industries():
    logger.debug("Accessing industries route")
    return render_template('industries.html')

@app.route('/services')
def services():
    logger.debug("Accessing services route")
    return render_template('services.html')

@app.route('/about')
def about():
    logger.debug("Accessing about route")
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    logger.debug(f"Accessing contact route with method: {request.method}")
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        service_type = request.form.get('service_type')

        logger.info(f"Processing contact form submission from {email}")

        consultation = Consultation(
            name=name,
            email=email,
            message=message,
            service_type=service_type
        )

        try:
            # Save to database
            db.session.add(consultation)
            db.session.commit()
            logger.info(f"New consultation created for {email}")

            # Send email using SendGrid
            try:
                message_body = f"""
                New contact form submission:

                Name: {name}
                Email: {email}
                Service Type: {service_type}
                Message:
                {message}
                """

                message = Mail(
                    from_email='imran.s.baig.cpa@gmail.com',  # Changed to verified sender
                    to_emails='imran.s.baig.cpa@gmail.com',
                    subject=f'New Contact Form Submission - {service_type}',
                    plain_text_content=message_body
                )

                sg = SendGridAPIClient(SENDGRID_API_KEY)
                response = sg.send(message)
                logger.info(f"SendGrid Response Status Code: {response.status_code}")
                logger.info(f"Email notification sent for consultation from {email}")

                flash('Thank you for your message! We will contact you soon.', 'success')
                return redirect(url_for('contact'))

            except Exception as email_error:
                logger.error(f"Error sending email via SendGrid: {email_error}")
                # Don't rollback database transaction if email fails
                flash('Your message was saved but there was an issue sending the notification email.', 'warning')
                return redirect(url_for('contact'))

        except Exception as e:
            logger.error(f"Error processing contact form: {e}")
            db.session.rollback()
            flash('An error occurred while processing your message. Please try again later.', 'error')
            return render_template('contact.html')

    return render_template('contact.html')

if __name__ == '__main__':
    with app.app_context():
        try:
            db.create_all()
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating database tables: {e}")
            raise

    logger.info("Starting Flask development server")
    app.run(host='0.0.0.0', port=5000, debug=True)