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
    return render_template('backend/users.html')

@app.route('/dashboard/content')
def dashboard_content():
    return render_template('backend/content.html')

if __name__ == '__main__':
    app.run(debug=True)