from flask import Flask, redirect,request,session,url_for,render_template

app = Flask(__name__)

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

@app.route('/')
def index():
    return render_template('home.html')

@app.route("/login", methods=["GET", "POST"])
def login():
    ADMIN_USERNAME = "ekall"
    ADMIN_PASSWORD = "admin123"

    USER_USERNAME = "user"
    USER_PASSWORD = "password"

    message = ""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['username'] = username
            session['role'] = "admin"
            return redirect(url_for('dashboard'))

        elif username == USER_USERNAME and password == USER_PASSWORD:
            session['username'] = username
            session['role'] = "user"
            return redirect(url_for('index'))

        else:
            message = "❌ Username atau password salah!"

    return render_template("login.html", message=message)

@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/detail')
def detail():
    return render_template('detail.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('backend/profile.html', role=session['role'])

@app.route('/dashboard/users')
def dashboard_users():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('backend/users/users.html', role=session['role'])
    

# CRUD USERS
@app.route('/dashboard/users/create_user')
def create_users():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('backend/users/create.html', role=session['role'])

@app.route('/dashboard/users/update_user')
def update_users():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('backend/users/update.html', role=session['role'])

@app.route('/dashboard/users/detail_user')
def detail_users():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('backend/users/detail.html', role=session['role'])

# CRUD CONTENT
@app.route('/dashboard/content')
def dashboard_content():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('backend/content/content.html', role=session['role'])

@app.route('/dashboard/content/all_content')
def dashboard_adm_content():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('backend/content/admin_content.html', role=session['role'])

@app.route('/dashboard/content/create_content')
def create_content():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('backend/content/create.html', role=session['role'])

@app.route('/dashboard/content/update_content')
def update_content():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('backend/content/update.html', role=session['role'])

@app.route('/dashboard/content/detail_content')
def detail_content():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('backend/content/detail.html', role=session['role'])


if __name__ == '__main__':
    app.run(debug=True)