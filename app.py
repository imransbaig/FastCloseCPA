import os
from flask import Flask, render_template, request, flash, redirect, url_for
import logging
from datetime import datetime
from extensions import db

# Setup detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
logger.info("Flask application instance created")

# setup a secret key, required by sessions
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or "fastcloseai2024"
logger.info("Secret key configured")

# Configure database - use PostgreSQL for Azure, fallback to SQLite for local
database_url = os.environ.get('DATABASE_URL', 'sqlite:///fastclose.db')
if database_url.startswith("postgres://"):  # Handle Azure PostgreSQL URL
    database_url = database_url.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
logger.info("Database configuration set")

# Initialize extensions
db.init_app(app)
logger.info("Database initialization complete")

# Import models after db initialization
try:
    from models import Consultation, BlogPost
    logger.info("Models imported successfully")
except Exception as e:
    logger.error(f"Error importing models: {e}")
    raise

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

        consultation = Consultation(
            name=name,
            email=email,
            message=message,
            service_type=service_type
        )

        try:
            db.session.add(consultation)
            db.session.commit()
            logger.info(f"New consultation created for {email}")
            flash('Thank you for your message! We will contact you soon.', 'success')
            return redirect(url_for('contact'))
        except Exception as e:
            logger.error(f"Error saving consultation: {e}")
            flash('An error occurred. Please try again.', 'error')
            db.session.rollback()

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