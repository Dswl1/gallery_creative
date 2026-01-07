from flask import Flask, redirect,request,session,url_for,render_template,flash,abort,jsonify
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
import os , uuid
import pymysql


app = Flask(__name__)
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
            ("admin", password, "admin", "admin@system.com", "0000000000")
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

        flash("Registrasi berhasil, silakan login", "success")
        return redirect(url_for("login"))

    return render_template("register.html", message=message)





@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/detail/<int:id>')
def detail(id):
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
        abort(404)

    return render_template('detail.html', image=image)


@app.route('/dashboard')
def dashboard():
    if 'role' not in session:
        return redirect(url_for('login'))

    if session['role'] == 'admin':
        return redirect(url_for('dashboard_admin'))
    elif session['role'] == 'user':
        return redirect(url_for('dashboard_users'))
    else:
        return redirect(url_for('login'))


@app.route('/dashboard/admin')
def dashboard_admin():

    if 'role' not in session or 'username' not in session:
        return redirect(url_for('login'))

    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE username=%s",
        (session['username'],)
    )
    user = cursor.fetchone()

    return render_template('backend/profile.html', user=user)



@app.route('/dashboard/admin/profile')
def admin_profile():

    if 'role' not in session or 'username' not in session:
        return redirect(url_for('login'))

    if session['role'] != 'admin':
        return redirect(url_for('dashboard_users'))

    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE username=%s",
        (session['username'],)
    )
    user = cursor.fetchone()

    return render_template('backend/profile.html', user=user)



@app.route('/dashboard/admin/users')
def admin_users():

    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()

    return render_template('backend/users/users.html', users=users)


@app.route('/dashboard/users', endpoint='dashboard_users')
def dashboard_user():

    if 'role' not in session or 'username' not in session:
        return redirect(url_for('login'))

    if session['role'] != 'user':
        return redirect(url_for('dashboard_admin'))

    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE username=%s",
        (session['username'],)
    )
    user = cursor.fetchone()

    return render_template(
        "backend/profile.html",
        user=user,
        role=session['role']
    )





# CRUD USERS
@app.route('/dashboard/users/create_user', methods=['GET', 'POST'])
def create_users():
    if 'username' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))

    if request.method == 'POST':
        username = request.form.get('username')
        email    = request.form.get('email')
        phone    = request.form.get('phone')
        role     = request.form.get('role')
        password = request.form.get('password')
        confirm  = request.form.get('confirm_password')

        if not username or not email or not password or not confirm:
            flash('Field wajib belum diisi', 'error')
            return redirect(request.referrer)

        if password != confirm:
            flash('Password tidak sama', 'error')
            return redirect(request.referrer)

        hashed_password = generate_password_hash(password)

        photo = request.files.get('profile')
        filename = None

        if photo and photo.filename != '':
            photo.seek(0, os.SEEK_END)
            size = photo.tell()
            photo.seek(0)

            if size > 5 * 1024 * 1024:
                flash('Ukuran gambar maksimal 5MB', 'error')
                return redirect(request.referrer)

            ext = photo.filename.rsplit('.', 1)[1].lower()
            filename = f"{uuid.uuid4().hex}.{ext}"
            photo.save(os.path.join('static/assets', filename))

        db = get_db()
        cursor = db.cursor()

        cursor.execute("SELECT id FROM users WHERE username=%s", (username,))
        if cursor.fetchone():
            flash('Username sudah digunakan', 'error')
            return redirect(request.referrer)

        cursor.execute("""
            INSERT INTO users (username, email, phone, password, role, profile)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            username,
            email,
            phone,
            hashed_password,
            role,
            filename
        ))

        db.commit()
        flash('User berhasil ditambahkan', 'success')
        return redirect(url_for('admin_users'))

    return render_template('backend/users/create.html', role=session['role'])

@app.route('/dashboard/users/update_user', methods=['GET'])
def update_user_form():

    if 'username' not in session:
        return redirect(url_for('login'))

    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "SELECT username, email, phone FROM users WHERE username=%s",
        (session['username'],)
    )
    user = cursor.fetchone()

    return render_template(
        'backend/users/update.html',
        user=user,
        role=session['role']
    )


@app.route('/dashboard/users/update_user', methods=['POST'], endpoint='update_users')
def update_user():

    if 'username' not in session:
        return redirect(url_for('login'))

    db = get_db()
    cursor = db.cursor()

    username_baru = request.form.get('username')
    email = request.form.get('email')
    no_hp = request.form.get('phone')
    password = request.form.get('password')

    if password:
        password_hash = generate_password_hash(password)
        cursor.execute("""
            UPDATE users
            SET username=%s,
                email=%s,
                phone=%s,
                password=%s
            WHERE username=%s
        """, (
            username_baru,
            email,
            no_hp,
            password_hash,
            session['username']
        ))
    else:
        cursor.execute("""
            UPDATE users
            SET username=%s,
                email=%s,
                phone=%s
            WHERE username=%s
        """, (
            username_baru,
            email,
            no_hp,
            session['username']
        ))

    photo = request.files.get('profile')
    if photo and photo.filename != '':
        filename = f"{uuid.uuid4().hex}_{secure_filename(photo.filename)}"
        photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    
        cursor.execute("""
            UPDATE users SET profile=%s WHERE username=%s
        """, (filename, session['username']))


    db.commit()
    session['username'] = username_baru

    return redirect(url_for('dashboard'))


@app.route('/users')
def users_index():
    db = get_db()
    cursor = db.cursor(pymysql.cursors.DictCursor)

    cursor.execute("""
        SELECT id, username, email, created_at
        FROM users
        WHERE role = 'user'
    """)
    users = cursor.fetchall()

    return render_template('backend/users/users.html', users=users)


@app.route('/users/detail/<int:id>')
def users_detail(id):
    db = get_db()
    cursor = db.cursor(pymysql.cursors.DictCursor)

    cursor.execute("""
        SELECT * FROM users
        WHERE id=%s AND role='user'
    """, (id,))
    user = cursor.fetchone()

    if not user:
        return "User tidak ditemukan", 404

    return render_template('backend/users/detail.html', user=user)



@app.route('/users/update-form/<int:id>', methods=['GET', 'POST'])
def users_update_form(id):
    db = get_db()
    cursor = db.cursor()

    if request.method == 'POST':
        nama     = request.form['nama']
        username = request.form['username']
        email    = request.form['email']

        cursor.execute("""
            UPDATE users
            SET username=%s, email=%s
            WHERE id=%s
        """, (nama, username, email, id))
        db.commit()

        return redirect(url_for('users_index'))

    cursor.execute("SELECT * FROM users WHERE id=%s", (id,))
    user = cursor.fetchone()

    if not user:
        return "User tidak ditemukan", 404

    return render_template('backend/users/update.html', user=user)


@app.route('/users/delete/<int:id>')
def users_delete(id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        DELETE FROM users
        WHERE id=%s AND role='user'
    """, (id,))
    db.commit()

    return redirect(url_for('users_index'))  # ← PENTING

@app.route('/dashboard/account/delete', methods=['POST'])
def delete_own_account():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM users WHERE id=%s", (session['user_id'],))
    db.commit()

    session.clear()
    return redirect(url_for('index'))






# CRUD CONTENT

UPLOAD_FOLDER = app.config['UPLOAD_FOLDER'] = os.path.join('static', 'assets')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024 
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

    db = get_db()
    cursor = db.cursor(pymysql.cursors.DictCursor)

    cursor.execute("""
        SELECT * FROM content
        WHERE user_id = %s
        ORDER BY id DESC
    """, (session['user_id'],))

    images = cursor.fetchall()

    return render_template(
        'backend/content/content.html',
        images=images
    )

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

@app.route('/dashboard/content/delete/<int:id>')
def delete_content(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        DELETE FROM content
        WHERE id=%s AND user_id=%s
    """, (id, session['user_id']))
    db.commit()

    return redirect(url_for('dashboard_content'))




@app.route('/api/contents')
def api_contents():
    db = get_db()
    cursor = db.cursor(pymysql.cursors.DictCursor)

    search = request.args.get('search', '')
    sort = request.args.get('sort', 'latest')

    query = """
        SELECT content.*, users.username
        FROM content
        JOIN users ON content.user_id = users.id
        WHERE 1=1
    """
    params = []

    if search:
        query += " AND content.title LIKE %s"
        params.append(f"%{search}%")

    if sort == 'az':
        query += " ORDER BY content.title ASC"
    elif sort == 'za':
        query += " ORDER BY content.title DESC"
    else:
        query += " ORDER BY content.created_at DESC"

    cursor.execute(query, params)
    return jsonify(cursor.fetchall())



if __name__ == '__main__':
    seed_admin()
    app.run(debug=True)