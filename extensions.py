from flask_sqlalchemy import SQLAlchemy
import logging

logger = logging.getLogger(__name__)

try:
    db = SQLAlchemy()
    logger.info("SQLAlchemy instance created successfully")
except Exception as e:
    logger.error(f"Error creating SQLAlchemy instance: {e}")
    raise