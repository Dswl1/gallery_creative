from flask import Flask, redirect,request,session,url_for,render_template

app = Flask(__name__)

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

@app.route('/')
def index():
    return render_template('home.html')

@app.route("/login", methods=["GET", "POST"])
def login():
    USERNAME = "ekall"
    PASSWORD = "blobanjeng"
    
    message = ""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == USERNAME and password == PASSWORD:
            session['username'] = username
            # message = "✅ Anda berhasil login!"
            return redirect(url_for('index'))
        else:
            message = "❌ Username atau password salah!"

    return render_template("login.html", message=message)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/detail')
def detail():
    return render_template('detail.html')

@app.route('/dashboard')
def dashboard():
    return render_template('backend/profile.html')

@app.route('/dashboard/users')
def dashboard_users():
    return render_template('backend/users/users.html')

# CRUD USERS
@app.route('/dashboard/users/create_user')
def create_users():
    return render_template('backend/users/create.html')
@app.route('/dashboard/users/update_user')
def update_users():
    return render_template('backend/users/update.html')
@app.route('/dashboard/users/detail_user')
def detail_users():
    return render_template('backend/users/detail.html')

# CRUD CONTENT
@app.route('/dashboard/content')
def dashboard_content():
    return render_template('backend/content/content.html')
@app.route('/dashboard/content/create_content')
def create_content():
    return render_template('backend/content/create.html')
@app.route('/dashboard/content/update_content')
def update_content():
    return render_template('backend/content/update.html')
@app.route('/dashboard/content/detail_content')
def detail_content():
    return render_template('backend/content/detail.html')

if __name__ == '__main__':
    app.run(debug=True)