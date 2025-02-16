from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .models import Note, User
from . import db
import os
from werkzeug.utils import secure_filename
import json

views = Blueprint('views', __name__)

UPLOAD_FOLDER = 'website/static/uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Existing home route
@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        note = request.form.get('note')
        tags = request.form.get('tags')
        attached_file = request.files.get('attachment')

        if not note or len(note) < 1:
            flash('Note is too short!', category='error')
        else:
            file_path = None
            if attached_file and allowed_file(attached_file.filename):
                if not os.path.exists(UPLOAD_FOLDER):
                    os.makedirs(UPLOAD_FOLDER)

                filename = secure_filename(attached_file.filename)
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                attached_file.save(file_path)
            elif attached_file:
                flash('File type not allowed.', category='error')
                return redirect(url_for('views.home'))

            new_note = Note(data=note, tags=tags, file_path=file_path, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            flash('Note added!', category='success')

    return render_template("home.html", user=current_user)

# Existing delete note route
@views.route('/delete-note', methods=['POST'])
@login_required
def delete_note():
    try:
        note_data = json.loads(request.data)
        note_id = note_data.get('noteId')
        note = Note.query.get(note_id)

        if note and note.user_id == current_user.id:
            if note.file_path and os.path.exists(note.file_path):
                os.remove(note.file_path)

            db.session.delete(note)
            db.session.commit()
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": "Note not found or unauthorized"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# New /update-profile route
@views.route('/update-profile', methods=['POST'])
@login_required
def update_profile():
    email = request.form.get('email')
    first_name = request.form.get('firstName')

    if len(email) < 4:
        flash('Email must be greater than 3 characters.', category='error')
    elif len(first_name) < 2:
        flash('First name must be greater than 1 character.', category='error')
    else:
        current_user.email = email
        current_user.first_name = first_name
        db.session.commit()
        flash('Profile updated successfully!', category='success')

    return redirect(url_for('views.profile'))

# New /profile route
@views.route('/profile', methods=['GET'])
@login_required
def profile():
    return render_template("profile.html", user=current_user)

# Existing search functionality
@views.route('/search', methods=['GET'])
@login_required
def search():
    query = request.args.get('query', '').strip()
    notes = Note.query.filter(Note.user_id == current_user.id, Note.data.contains(query)).all()
    return render_template("search_results.html", user=current_user, notes=notes, query=query)

# Existing pagination functionality
@views.route('/paginate', methods=['GET'])
@login_required
def paginate():
    page = request.args.get('page', 1, type=int)
    per_page = 5
    notes = Note.query.filter_by(user_id=current_user.id).paginate(page=page, per_page=per_page)
    return render_template("paginate.html", user=current_user, notes=notes)

# Existing edit note functionality
@views.route('/edit-note/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_note(id):
    note = Note.query.get_or_404(id)
    if request.method == 'POST':
        new_data = request.form.get('note')
        new_tags = request.form.get('tags')

        if not new_data or len(new_data) < 1:
            flash('Note content cannot be empty!', category='error')
        else:
            note.data = new_data
            note.tags = new_tags
            db.session.commit()
            flash('Note updated successfully!', category='success')
            return redirect(url_for('views.home'))

    return render_template("edit_note.html", note=note, user=current_user)
