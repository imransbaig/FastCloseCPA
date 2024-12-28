import os
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime
from models import Document, db

bp = Blueprint('client_portal', __name__)

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'csv', 'txt', 'jpg', 'jpeg', 'png'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/portal')
@login_required
def dashboard():
    documents = Document.query.filter_by(user_id=current_user.id).order_by(Document.upload_date.desc()).all()
    return render_template('client_portal/dashboard.html', documents=documents)

@bp.route('/portal/upload', methods=['GET', 'POST'])
@login_required
def upload_document():
    if request.method == 'POST':
        if 'document' not in request.files:
            flash('No file selected', 'error')
            return redirect(request.url)
        
        file = request.files['document']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            unique_filename = f"{timestamp}_{filename}"
            
            # Create upload directory if it doesn't exist
            upload_dir = os.path.join(current_app.root_path, 'uploads', str(current_user.id))
            os.makedirs(upload_dir, exist_ok=True)
            
            file_path = os.path.join(upload_dir, unique_filename)
            file.save(file_path)
            
            # Create document record
            document = Document(
                filename=unique_filename,
                original_filename=filename,
                file_path=file_path,
                file_type=file.content_type,
                file_size=os.path.getsize(file_path),
                user_id=current_user.id,
                description=request.form.get('description', '')
            )
            
            db.session.add(document)
            db.session.commit()
            
            flash('Document uploaded successfully!', 'success')
            return redirect(url_for('client_portal.dashboard'))
        else:
            flash(f'Invalid file type. Allowed types are: {", ".join(ALLOWED_EXTENSIONS)}', 'error')
            
    return render_template('client_portal/upload.html')

@bp.route('/portal/document/<int:document_id>')
@login_required
def view_document(document_id):
    document = Document.query.get_or_404(document_id)
    if document.user_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('client_portal.dashboard'))
    
    return send_file(document.file_path, as_attachment=True)
