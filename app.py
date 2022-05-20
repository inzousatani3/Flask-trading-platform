#venv\Scripts\activate
#$env:FLASK_APP = "app"
#flask run
import os
from flask import Flask, render_template, url_for, redirect, request, session, jsonify
import sqlite3
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.utils import secure_filename
import uuid

app = Flask(__name__)
#CREATE TABLE items (id INTEGER PRIMARY KEY NOT NULL,image_name TEXT NOT NULL, name TEXT NOT NULL, price INTEGER NOT NULL);
#CREATE TABLE users (id INTEGER PRIMARY KEY NOT NULL,username TEXT NOT NULL,password TEXT NOT NULL);
#db = sqlite3.connect("data.db",check_same_thread=False)

UPLOAD_FOLDER = './static/upload'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'sec_key'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

from functools import wraps

def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("username_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function



print("alive")

@app.route("/", methods = ["GET", "POST"])
@login_required
def index():
    if request.method == "POST":
        print("posting")
        if not request.form.get("name") or not request.form.get("price"):
            return redirect("/")

        item_name = request.form.get("name")
        item_price = request.form.get("price")
        if not item_price.isnumeric() or int(item_price) <= 0:
            return redirect("/")
        print("the input is valid")
        print(str(item_name)+ " / "+str(item_price))

        if 'file1' not in request.files:
            return redirect("/")
        
        file = request.files["file1"]
        print("file name:" + file.filename)
        print(secure_filename(file.filename))
        
        if not allowed_file(file.filename):
            return redirect("/")

        print("the file is valid")

        uid = str(uuid.uuid4())
        print(uid)
        #connect to the database
        db = sqlite3.connect("data.db",check_same_thread=False)
        #db.execute("INSERT INTO items (image_name, name, price) VALUES (?,?,?)",(secure_filename(file.filename), item_name, item_price))

        db.execute("INSERT INTO items (image_name, name, price) VALUES (?,?,?)",(uid + ".jpg", item_name, item_price))
        #saving the image
        path = os.path.join(app.config['UPLOAD_FOLDER'], uid + ".jpg")
        file.save(path)
        #saving the database
        db.commit()
        db.close()
        return redirect("/")
    else: 
        return render_template("index.html")


@app.route("/trades")
@login_required
def offers():
    db = sqlite3.connect("data.db",check_same_thread=False)
    data = db.execute("SELECT * FROM items").fetchall()
    db.close()
    print(data)
    return render_template("trades.html", trade_data = data)
"""
@app.route("/test", methods = ["POST" , "GET"])
def fileinput():
    if request.method == "POST":
        if 'file1' not in request.files:
            return "no file in form"
        file = request.files["file1"]
        path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(path)
        return "ok"
    else:
        return render_template("test.html")
"""

@app.route("/login", methods = ["POST", "GET"])
def login():
    session.clear()
    if request.method == "POST":
        if not request.form.get("username") or not request.form.get("password"):
            print("no username or password")
            return redirect("/login")
        username = request.form.get("username")
        password = request.form.get("password")

        print("username:" + str(username)); #you can delet
        print("password:" + str(password)); #you can delet

        #connect to db
        connection = sqlite3.connect("data.db",check_same_thread=False)
        db = connection.cursor()
        # Query database for username
        user_login_data = db.execute("SELECT * FROM users WHERE username = (?)", (username,)).fetchone()
        db.close()
        print(user_login_data)
        if user_login_data == None or password != user_login_data[2]:
            print("can t login")
            return redirect("/login")
        session["username_id"] = user_login_data[0]
        return redirect("/")
    else:
        return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    else: 
        name = request.form.get("username")
        password = request.form.get("password1")
        re_password = request.form.get("password2")
        if not name or not password or not re_password or password != re_password:
            print("error in input")
            return redirect("/register")
        print(name)
        print(password)
        print(re_password)
        #connect the the database and check if username alrady exists in database
        cursor = sqlite3.connect("data.db",check_same_thread=False)
        db = cursor.cursor()
        list_of_users = db.execute("SELECT * FROM users WHERE username = (?)",(name,)).fetchall()

        for i in list_of_users:
            if i[1] == name:
                print("user exist")
                db.close()
                return redirect("/register")
        #add user to db
        user_id = db.execute("INSERT INTO users (username,password) VALUES (?,?)", (str(name),str(password)))
        print("id = " + str(user_id.lastrowid))
        session["username_id"] = user_id.lastrowid
        #comit and close the db
        cursor.commit()
        cursor.close()

        return redirect("/")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")






if __name__ == "__main__":
    app.run(host="0.0.0.0")

