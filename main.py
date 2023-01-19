
from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user

login_manager = LoginManager()

app = Flask(__name__)

app.config['SECRET_KEY'] = 'any-secret-key-you-choose'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# CREATE TABLE IN DB
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))


db.create_all()


# Line below only required once, when creating DB.
# db.create_all()


@app.route('/')
def home():
    # Every render_template has a logged_in variable set
    return render_template("index.html",logged_in=current_user.is_authenticated)


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":

        if User.query.filter_by(email=request.form.get('email')).first():
            # User already exists
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))
        salted_hashed_password = generate_password_hash(request.form["password"],
                                                        method='pbkdf2:sha256', salt_length=8)
        new_user = User(
            email=request.form.get('email'),
            name=request.form['name'],
            password=salted_hashed_password
        )
        db.session.add(new_user)
        db.session.commit()
        # Log in and authenticate user after adding details to database
        login_user(new_user)
        return redirect(url_for("secrets"))
    return render_template("register.html",logged_in=current_user.is_authenticated)


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')

        # Finding user by email entered
        user = User.query.filter_by(email=email).first()
        # Email does n't exist
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))
        # Password Incorrect
        elif not check_password_hash(user.password, password):
            flash("Password Incorrect, Please Try again.")
            return redirect(url_for('login'))
        # email exists and password is correct for the given email
        else:
            login_user(user)
            return redirect(url_for('secrets'))

    return render_template("login.html",logged_in=current_user.is_authenticated)


@app.route('/secrets')
@login_required
def secrets():
    print(current_user.name)
    return render_template("secrets.html", name=current_user.name, logged_in=True)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/download')
@login_required
def download():
    return send_from_directory('static', filename="files/cheat_sheet.pdf")


if __name__ == "__main__":
    app.run(host='127.0.0.1', port="5000", debug=True)
