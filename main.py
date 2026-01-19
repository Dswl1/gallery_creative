from flask import Flask, redirect,request,session,url_for,render_template,flash,abort,jsonify
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import os , uuid
import pymysql

app = Flask(__name__)
PROFILE_FOLDER = os.path.join('static', 'profile')
os.makedirs(PROFILE_FOLDER, exist_ok=True)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


def get_db():
    return pymysql.connect(
        host = "localhost",
        user = "root",
        password = "",
        database = "gallery_creative",
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route('/')
def index():
    db = get_db()
    cursor = db.cursor(pymysql.cursors.DictCursor)

    cursor.execute("""
        SELECT content.*, users.username
        FROM content
        JOIN users ON content.user_id = users.id
        ORDER BY content.created_at DESC
    """)
    contents = cursor.fetchall()

    return render_template('home.html', contents=contents)

def seed_admin():
    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "SELECT id FROM users WHERE role='admin' LIMIT 1"
    )
    admin = cursor.fetchone()

    if not admin:
        password = generate_password_hash("admin123")

        cursor.execute(
            """
            INSERT INTO users (username, password, role, email, phone)
            VALUES (%s, %s, %s, %s, %s)
            """,
            ("admin", password, "admin", "admin123@gmail.com", "08123445667")
        )
        db.commit()

@app.route("/login", methods=["GET", "POST"])
def login():
    message = ""

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        db = get_db()
        cursor = db.cursor(pymysql.cursors.DictCursor)

        cursor.execute(
            "SELECT * FROM users WHERE username=%s",
            (username,)
        )
        user = cursor.fetchone()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['email'] = user['email']
            session['phone'] = user['phone']
            session['role'] = user['role'].lower()

            return redirect(url_for("dashboard"))
        else:
            message = "Username atau Password Salah"

    return render_template("login.html", message=message)



@app.route('/register', methods=["GET", "POST"])
def register():
    message = ""

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirm  = request.form.get("confirm_password")
        email    = request.form.get("email")
        phone    = request.form.get("phone")

        if not password or not confirm:
            flash("Password dan konfirmasi wajib diisi", "error")
            return redirect(request.referrer)

        if password != confirm:
            flash("Password dan konfirmasi tidak cocok", "error")
            return redirect(request.referrer)

        hashed_password = generate_password_hash(password)

        db = get_db()
        cursor = db.cursor()

        cursor.execute(
            "SELECT id FROM users WHERE username=%s",
            (username,)
        )
        existing_user = cursor.fetchone()

        if existing_user:
            flash("Username sudah dipakai!", "error")
            return redirect(request.referrer)

        cursor.execute(
            """
            INSERT INTO users (username, password, role, email, phone)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (username, hashed_password, "user", email, phone)
        )
        db.commit()

        flash("Registrasi berhasil", "success")
        return redirect(url_for("dashboard"))

    return render_template("register.html", message=message)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/detail/<int:id>')
def detail(id):
    db = get_db()
    cursor = db.cursor(pymysql.cursors.DictCursor)

    # ambil konten + username pembuat
    cursor.execute("""
        SELECT content.*, users.username
        FROM content
        JOIN users ON content.user_id = users.id
        WHERE content.id = %s
    """, (id,))
    image = cursor.fetchone()

    if not image:
        abort(404)

    # ambil rating
    cursor.execute("""
        SELECT 
            AVG(rating) AS avg_rating,
            COUNT(*) AS total_rating
        FROM ratings
        WHERE content_id = %s
    """, (id,))
    rating = cursor.fetchone()

    # ambil komentar
    cursor.execute("""
        SELECT comments.*, users.username
        FROM comments
        JOIN users ON comments.user_id = users.id
        WHERE comments.content_id = %s
        ORDER BY comments.created_at DESC
    """, (id,))
    comments = cursor.fetchall()

    return render_template(
        'detail.html',
        image=image,
        rating=rating,
        comments=comments
    )


@app.route('/feedback', methods=['POST'])
def submit_feedback():
    if 'user_id' not in session:
        abort(403)

    rating = request.form.get('rating')
    type_   = request.form.get('type')
    msg    = request.form.get('message')

    if not rating or not type_ or not msg:
        flash('Semua field wajib diisi', 'error')
        return redirect(request.referrer)

    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        INSERT INTO feedbacks (user_id, rating, type, message)
        VALUES (%s,%s,%s,%s)
    """, (session['user_id'], rating, type_, msg))

    db.commit()
    flash('Terima kasih atas feedback kamu ❤️', 'success')
    return redirect(url_for('index'))



@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    db = get_db()
    cursor = db.cursor(pymysql.cursors.DictCursor)

    # ambil user
    cursor.execute("SELECT * FROM users WHERE id=%s", (session['user_id'],))
    user = cursor.fetchone()

    data = {}

    if user['role'] == 'admin':
        # ===== SYSTEM STATS =====
        cursor.execute("SELECT COUNT(*) total FROM content")
        data['total_content'] = cursor.fetchone()['total']
    
        cursor.execute("SELECT COUNT(*) total FROM users")
        data['total_users'] = cursor.fetchone()['total']
    
        cursor.execute("SELECT COUNT(*) total FROM feedbacks")
        data['total_feedback'] = cursor.fetchone()['total']

        cursor.execute("""
            SELECT ROUND(AVG(rating),1) avg
            FROM feedbacks
        """)
        data['avg_web_rating'] = cursor.fetchone()['avg'] or 0
    
        # ===== ADMIN PERSONAL STATS =====
        cursor.execute("""
            SELECT COUNT(*) total
            FROM content
            WHERE user_id=%s
        """, (user['id'],))
        data['my_content'] = cursor.fetchone()['total']
    
        cursor.execute("""
            SELECT ROUND(AVG(r.rating),1) avg
            FROM ratings r
            JOIN content c ON c.id = r.content_id
            WHERE c.user_id=%s
        """, (user['id'],))
        data['my_avg_rating'] = cursor.fetchone()['avg'] or 0
    
        cursor.execute("""
            SELECT title, created_at
            FROM content
            WHERE user_id=%s
            ORDER BY created_at DESC
            LIMIT 5
        """, (user['id'],))
        data['my_latest_content'] = cursor.fetchall()

    else:
        # ===== USER STATS =====
        cursor.execute("""
            SELECT COUNT(*) total
            FROM content
            WHERE user_id=%s
        """, (user['id'],))
        data['my_content'] = cursor.fetchone()['total']

        cursor.execute("""
            SELECT ROUND(AVG(r.rating),1) avg
            FROM ratings r
            JOIN content c ON c.id = r.content_id
            WHERE c.user_id=%s
        """, (user['id'],))
        data['avg_rating'] = cursor.fetchone()['avg'] or 0

        cursor.execute("""
            SELECT title, created_at
            FROM content
            WHERE user_id=%s
            ORDER BY created_at DESC
            LIMIT 5
        """, (user['id'],))
        data['latest_my_content'] = cursor.fetchall()

    return render_template(
        'backend/dashboard.html',
        user=user,
        data=data
    )

@app.route('/dashboard/admin/users')
def admin_users():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    db = get_db()
    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()

    return render_template('backend/users/users.html', users=users)

@app.route('/dashboard/feedback')
def admin_feedback():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))

    db = get_db()
    cursor = db.cursor(pymysql.cursors.DictCursor)

    # statistik ringkas
    cursor.execute("SELECT COUNT(*) total FROM feedbacks")
    total_feedback = cursor.fetchone()['total']

    cursor.execute("SELECT ROUND(AVG(rating),1) avg FROM feedbacks")
    avg_rating = cursor.fetchone()['avg'] or 0

    # list feedback
    cursor.execute("""
        SELECT 
            f.rating,
            f.type,
            f.message,
            f.created_at,
            u.username
        FROM feedbacks f
        LEFT JOIN users u ON u.id = f.user_id
        ORDER BY f.created_at DESC
    """)
    feedbacks = cursor.fetchall()

    return render_template(
        'backend/feedback.html',
        total_feedback=total_feedback,
        avg_rating=avg_rating,
        feedbacks=feedbacks
    )


# CRUD USERS
@app.route('/dashboard/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    db = get_db()
    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM users WHERE id=%s", (session['user_id'],))
    user = cursor.fetchone()

    return render_template('backend/profile.html', user=user)

@app.route('/dashboard/profile/edit', methods=['GET', 'POST'])
def profile_edit():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    db = get_db()
    cursor = db.cursor(pymysql.cursors.DictCursor)

    if request.method == 'GET':
        cursor.execute("SELECT * FROM users WHERE id=%s", (session['user_id'],))
        user = cursor.fetchone()
        return render_template('backend/users/update.html', user=user)

    username = request.form['username']
    email    = request.form['email']
    phone    = request.form['phone']
    password = request.form.get('password')
    file     = request.files.get('profile')

    # ambil profile lama
    cursor.execute("SELECT profile FROM users WHERE id=%s", (session['user_id'],))
    old = cursor.fetchone()
    profile_name = old['profile']

    # ==== HANDLE UPLOAD FOTO ====
    if file and file.filename != '':
        ext = file.filename.rsplit('.', 1)[1].lower()

        if ext not in ['jpg', 'jpeg', 'png']:
            flash("Format foto harus JPG / PNG", "error")
            return redirect(request.referrer)

        # hapus foto lama
        if profile_name:
            old_path = os.path.join(PROFILE_FOLDER, profile_name)
            if os.path.exists(old_path):
                os.remove(old_path)

        profile_name = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
        file.save(os.path.join(PROFILE_FOLDER, profile_name))

    # ==== UPDATE DB ====
    if password:
        password = generate_password_hash(password)
        cursor.execute("""
            UPDATE users
            SET username=%s, email=%s, phone=%s, password=%s, profile=%s
            WHERE id=%s
        """, (username, email, phone, password, profile_name, session['user_id']))
    else:
        cursor.execute("""
            UPDATE users
            SET username=%s, email=%s, phone=%s, profile=%s
            WHERE id=%s
        """, (username, email, phone, profile_name, session['user_id']))

    db.commit()
    flash("Profile berhasil diperbarui", "success")
    return redirect(url_for('profile'))

@app.route('/dashboard/profile/delete', methods=['POST'])
def profile_delete():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM users WHERE id=%s", (session['user_id'],))
    db.commit()

    session.clear()
    return redirect(url_for('index'))

# ADMIN
@app.route('/dashboard/admin/users/create', methods=['GET', 'POST'])
def admin_create_user():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    if request.method == 'POST':
        data = request.form
        password = generate_password_hash(data['password'])

        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO users (username, email, phone, password, role)
            VALUES (%s,%s,%s,%s,%s)
        """, (
            data['username'],
            data['email'],
            data['phone'],
            password,
            data['role']
        ))
        db.commit()

        flash('User ditambahkan', 'success')
        return redirect(url_for('admin_users'))

    return render_template('backend/users/create.html')

@app.route('/dashboard/admin/users/<int:id>/edit', methods=['GET', 'POST'])
def admin_edit_user(id):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    db = get_db()
    cursor = db.cursor(pymysql.cursors.DictCursor)

    if request.method == 'GET':
        cursor.execute("SELECT * FROM users WHERE id=%s", (id,))
        user = cursor.fetchone()
        return render_template('backend/users/update.html', user=user)

    data = request.form
    cursor.execute("""
        UPDATE users
        SET username=%s, email=%s, phone=%s, role=%s
        WHERE id=%s
    """, (
        data['username'],
        data['email'],
        data['phone'],
        data['role'],
        id
    ))
    db.commit()

    flash('User diperbarui', 'success')
    return redirect(url_for('admin_users'))

@app.route('/dashboard/admin/users/<int:id>/delete', methods=['POST'])
def admin_delete_user(id):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM users WHERE id=%s", (id,))
    db.commit()

    flash('User dihapus', 'success')
    return redirect(url_for('admin_users'))

# CRUD CONTENT
UPLOAD_FOLDER = app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2MB
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return (
        '.' in filename and
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    )

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
    
@app.route('/dashboard/content/create', methods=['GET', 'POST'])
def create_content():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        title       = request.form.get('judul')
        description = request.form.get('deskripsi')
        category    = request.form.get('kategori')
        file        = request.files.get('image')

        # VALIDASI
        if not title:
            flash("Judul wajib diisi", "error")
            return redirect(request.referrer)

        if not file or file.filename == '':
            flash("Gambar wajib diupload", "error")
            return redirect(request.referrer)

        if not allowed_file(file.filename):
            flash("Format gambar tidak didukung", "error")
            return redirect(request.referrer)

        # SIMPAN FILE
        filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        # SIMPAN DB
        db = get_db()
        cursor = db.cursor()

        cursor.execute("""
            INSERT INTO content (title, filename, description, category, user_id)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            title,
            filename,
            description,
            category,
            session['user_id']
        ))

        db.commit()

        flash("Konten berhasil dipublish", "success")
        return redirect(url_for('dashboard_content'))

    return render_template('backend/content/create.html')


@app.route('/dashboard/content', endpoint='dashboard_content')
def dashboard_content():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    mode = request.args.get('mode', 'mine')

    db = get_db()
    cursor = db.cursor(pymysql.cursors.DictCursor)

    if mode == 'all' and session.get('role') == 'admin':
        cursor.execute("""
            SELECT content.*, users.username
            FROM content
            JOIN users ON content.user_id = users.id
            ORDER BY content.created_at DESC
        """)
    else:
        cursor.execute("""
            SELECT *
            FROM content
            WHERE user_id = %s
            ORDER BY created_at DESC
        """, (session['user_id'],))

    images = cursor.fetchall()
    return render_template('backend/content/content.html', images=images)

@app.route('/dashboard/admin/content')
def dashboard_admin_content():
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    db = get_db()
    cursor = db.cursor(pymysql.cursors.DictCursor)

    cursor.execute("""
        SELECT content.*, users.username
        FROM content
        JOIN users ON content.user_id = users.id
        ORDER BY content.id DESC
    """)
    images = cursor.fetchall()

    return render_template(
        'backend/content/admin_content.html',
        images=images
    )

@app.route('/dashboard/content/detail/<int:id>')
def dashboard_content_detail(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    db = get_db()
    cursor = db.cursor(pymysql.cursors.DictCursor)

    cursor.execute("""
        SELECT content.*, users.username
        FROM content
        JOIN users ON content.user_id = users.id
        WHERE content.id = %s
    """, (id,))
    image = cursor.fetchone()

    if not image:
        return "Image tidak ditemukan", 404

    return render_template(
        'backend/content/detail.html',
        image=image
    )

@app.route('/dashboard/content/update/<int:id>', methods=['GET', 'POST'])
def update_content(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    db = get_db()
    cursor = db.cursor(pymysql.cursors.DictCursor)

    if request.method == 'POST':
        title       = request.form.get('judul')
        category    = request.form.get('kategori')
        description = request.form.get('deskripsi')
        file        = request.files.get('gambar_karya')

        cursor.execute(
            "SELECT * FROM content WHERE id=%s AND user_id=%s",
            (id, session['user_id'])
        )
        image = cursor.fetchone()

        if not image:
            return "Akses ditolak", 403

        filename = image['filename']

        if file and file.filename != '':
            if not allowed_file(file.filename):
                flash("Format gambar tidak didukung", "error")
                return redirect(request.referrer)

            old_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if filename and os.path.exists(old_path):
                os.remove(old_path)

            filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        cursor.execute("""
            UPDATE content
            SET title=%s,
                category=%s,
                description=%s,
                filename=%s
            WHERE id=%s AND user_id=%s
        """, (
            title,
            category,
            description,
            filename,
            id,
            session['user_id']
        ))

        db.commit()
        flash("Konten berhasil diupdate", "success")
        return redirect(url_for('dashboard_content'))

    # GET
    cursor.execute(
        "SELECT * FROM content WHERE id=%s AND user_id=%s",
        (id, session['user_id'])
    )
    image = cursor.fetchone()

    if not image:
        return "Akses ditolak", 403

    return render_template('backend/content/update.html', image=image)

@app.route('/dashboard/content/delete/<int:id>', methods=['POST'])
def delete_content(id):
    if 'user_id' not in session:
        abort(403)

    db = get_db()
    cursor = db.cursor()

    if session.get('role') == 'admin':
        cursor.execute("DELETE FROM content WHERE id=%s", (id,))
        redirect_to = url_for('dashboard_content', mode='all')
    else:
        cursor.execute(
            "DELETE FROM content WHERE id=%s AND user_id=%s",
            (id, session['user_id'])
        )
        redirect_to = url_for('dashboard_content')

    db.commit()

    flash("Konten berhasil dihapus", "success")
    return redirect(redirect_to)

# COMMENT AND RATING
@app.route('/content/<int:id>/rate', methods=['POST'])
def rate_content(id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 403

    rating = request.form.get('rating')
    if not rating:
        return jsonify({'error': 'Invalid rating'}), 400

    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        INSERT INTO ratings (content_id, user_id, rating)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE rating=%s
    """, (id, session['user_id'], rating, rating))
    db.commit()

    # ambil ulang avg
    cursor.execute("""
        SELECT AVG(rating) avg_rating, COUNT(*) total
        FROM ratings WHERE content_id=%s
    """, (id,))
    data = cursor.fetchone()

    return jsonify({
        'avg': round(float(data['avg_rating']), 1),
        'total': data['total']
    })

@app.route('/content/<int:id>/comment', methods=['POST'])
def comment_content(id):
    if 'user_id' not in session:
        abort(403)

    comment = request.form.get('comment')
    if not comment:
        flash("Komentar tidak boleh kosong", "error")
        return redirect(url_for('detail', id=id))

    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        INSERT INTO comments (content_id, user_id, comment)
        VALUES (%s, %s, %s)
    """, (id, session['user_id'], comment))

    db.commit()
    return redirect(url_for('detail', id=id))


@app.route('/api/contents')
def api_contents():
    db = get_db()
    cursor = db.cursor(pymysql.cursors.DictCursor)

    search = request.args.get('search', '')
    sort   = request.args.get('sort', 'latest')
    page   = int(request.args.get('page', 1))
    limit  = int(request.args.get('limit', 5))

    offset = (page - 1) * limit

    base_query = """
        FROM content
        JOIN users ON content.user_id = users.id
        LEFT JOIN ratings ON ratings.content_id = content.id
        WHERE 1=1
    """
    params = []

    if search:
        base_query += " AND (content.title LIKE %s OR users.username LIKE %s)"
        params.extend([f"%{search}%", f"%{search}%"])

    # TOTAL DATA
    cursor.execute(
        "SELECT COUNT(DISTINCT content.id) total " + base_query,
        params
    )
    total = cursor.fetchone()['total']

    # DATA
    query = """
        SELECT 
            content.*,
            users.username,
            COUNT(ratings.id) total_rating,
            AVG(ratings.rating) avg_rating
    """ + base_query + """
        GROUP BY content.id
    """

    if sort == 'popular':
        query += " ORDER BY avg_rating DESC, total_rating DESC "
    elif sort == 'az':
        query += " ORDER BY content.title ASC "
    elif sort == 'za':
        query += " ORDER BY content.title DESC "
    else:
        query += " ORDER BY content.created_at DESC "

    query += " LIMIT %s OFFSET %s"
    params.extend([limit, offset])

    cursor.execute(query, params)
    items = cursor.fetchall()

    return jsonify({
        "items": items,
        "total": total,
        "page": page,
        "limit": limit
    })


@app.errorhandler(413)
def file_too_large(e):
    flash("Ukuran file terlalu besar (maks 2MB)", "error")
    return redirect(request.referrer or url_for('profile'))


if __name__ == '__main__':
    seed_admin()
    app.run(debug=True)