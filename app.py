import os
import secrets
from flask import Flask, render_template, flash, redirect, url_for, request
from forms import RegistrationForm, LoginForm, UpdateAccountForm, PictureForm, DeletePictureForm, CommentForm, DeleteCommentForm, UpdatePasswordForm
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask import request
from flask_bcrypt import Bcrypt
from datetime import datetime
from flask_login import UserMixin, LoginManager
from flask_login import login_user, current_user, logout_user, login_required
from flask_ckeditor import CKEditor

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:admin@localhost:5432/licencjat_gallery"
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt()
login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
ckeditor = CKEditor(app)

app.config['SECRET_KEY'] = 'secretkey123456'

@app.route('/', methods=['POST', 'GET'])
def mainPage():
    return render_template('mainPage.html')

@app.route('/about')
def about():
    return render_template('about.html')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class Picture(db.Model):
    __tablename__ = 'picture'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), unique=True, nullable=False)
    link = db.Column(db.String(30), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    year = db.Column(db.Integer)
    origin = db.Column(db.String(80))
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
    comments = db.relationship('Comment', backref='picture', lazy=True)
    sizeh = db.Column(db.String(30), nullable=False, default='H')

    def __init__(self, name, description, year, origin, link, artist_id):
        self.name = name
        self.description = description
        self.year = year
        self.origin = origin
        self.link = link
        self.artist_id = artist_id

    def __repr__(self):
        return f"Picture('{self.name}')"


class Artist(db.Model):
    __tablename__ = 'artist'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True, nullable=False)
    pictures = db.relationship('Picture', backref='author', lazy=True)


    def __repr__(self):
        return f"Artist('{self.name}')"

class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    picture_id = db.Column(db.Integer, db.ForeignKey('picture.id'), nullable=False)
    # parent = relationship(Picture, cascade="all,delete", backref="children") , ondelete='CASCADE' passive_deletes=True,

    def __init__(self, content, user_id, picture_id):
        self.content = content
        self.user_id = user_id
        self.picture_id = picture_id


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(40), unique=True, nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    # avatar = db.Column(db.String(20), nullable=False, default='one.jpg')
    role = db.Column(db.String(20), nullable=False, default='USER')
    password = db.Column(db.String(60), nullable=False)
    comments = db.relationship('Comment', backref='author', lazy=True)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

    def __repr__(self):
        return f"User('{self.username}')"


@app.route('/gallery', methods=['POST', 'GET'])
def picturesMenu():
    if request.method == 'GET':
        page = request.args.get('page', 1, type=int)
        pictures = Picture.query.order_by(Picture.id.desc()).paginate(page=page, per_page=6)
        results = [
            {
                "id":picture.id,
                "name": picture.name,
                "description": picture.description,
                "year": picture.year,
                "origin" : picture.origin,
                "link" : picture.link,
                "artist": picture.author.name,
                "sizeh": picture.sizeh

            } for picture in pictures.items]
        return render_template('picturesMenu.html', results=results, pictures=pictures)


@app.route('/gallery/<int:artist_id>')
def gallery_artist(artist_id):
    page = request.args.get('page', 1, type=int)
    button = artist_id
    artist = Artist.query.filter_by(id=artist_id).first_or_404()
    pictures = Picture.query.filter_by(artist_id=artist.id).order_by(Picture.id.desc()).paginate(page=page, per_page=6)
    results = [
        {
            "id": picture.id,
            "name": picture.name,
            "description": picture.description,
            "year": picture.year,
            "origin": picture.origin,
            "link": picture.link,
            "sizeh":picture.sizeh
        } for picture in pictures.items]
    return render_template('picturesMenu.html', results=results, pictures=pictures, button=button)



@app.route('/picture/<int:id>', methods=['GET', 'PUT', 'POST', 'DELETE'])
def pictureOne(id):
    # Picture.query.filter(Picture.id==(id).first)
    picture = Picture.query.get_or_404(id)

    # artist = Artist.query.filter_by(artist_id).first_or_404()
    comments = Comment.query.all()
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(content=form.content.data, user_id=current_user.id, picture_id=id)
        db.session.add(comment)
        db.session.commit()
        flash('Comment has been added!', 'success')
        return redirect(url_for('pictureOne', id=picture.id))
    if request.method == 'GET':
        response = {
            "id": picture.id,
            "name": picture.name,
            "description": picture.description,
            "year": picture.year,
            "origin": picture.origin,
            "link": picture.link
        }
        return render_template('pictureOne.html', title=picture.name, picture=picture, form=form, comments=comments)
    elif request.method == 'PUT':
        data = request.get_json()
        picture.name = data['name']
        picture.description = data['description']
        picture.year = data['year']
        picture.name = data['name']
        picture.link = data['link']
        picture.origin = data['origin']
        db.session.add(picture)
        db.session.commit()
        return {"message": f"car {picture.name} successfully updated"}

    # elif request.method == 'DELETE':
    #     db.session.delete(picture)
    #     db.session.commit()
    #     return {"message": f"Car {picture.name} successfully deleted."}
    return render_template('pictureOne.html', title=picture.name, picture=picture)

@app.route('/picture/<int:picture_id>/comment/<int:id>/delete', methods=['GET', 'PUT', 'POST', 'DELETE'])
@login_required
def comment_delete(id, picture_id):
    if adminhe():
        comment = Comment.query.get_or_404(id)
        picture = Picture.query.get_or_404(picture_id)
        formone = DeleteCommentForm()
        if formone.is_submitted():
            db.session.delete(comment)
            db.session.commit()
            flash('Komentarz został usunięty', 'success')
            return redirect(url_for('pictureOne', id=picture_id))
        return render_template('commentDelete.html', comment=comment, picture=picture)
    else:
        return redirect(url_for('pictureOne', id=picture_id))

def adminhe():
    if current_user.role == 'ADMIN':
        return True
    elif current_user.role == 'USER':
        return False

@app.route('/picture/<int:id>/update', methods=['GET', 'POST', 'DELETE'])
def picture_update(id):
    if adminhe():
        picture = Picture.query.get_or_404(id)
        artists = db.session.query(Artist).all()
        artist_list = [(artist.id, artist.name) for artist in artists]
        # Picture.query.filter(Picture.id==(id).first)

        # if current_user.role != 'ADMIN':
        #     abort(403)
        form = PictureForm()
        form.artist.choices = artist_list
        if form.validate_on_submit():
            if form.picture.data:
                picture_file = save_picture(form.picture.data)
                picture.link = picture_file
            picture.name = form.name.data
            picture.description = form.description.data
            picture.year = form.year.data
            picture.origin = form.origin.data
            picture.artist_id = form.artist.data

            db.session.commit()
            flash('Edycja zapisana', 'success')
            return redirect(url_for('pictureOne', id=picture.id))
        elif request.method == 'GET':
            form.name.data = picture.name
            form.description.data = picture.description
            form.year.data = picture.year
            form.origin.data = picture.origin
            return render_template('pictureEdit.html', title='Update picture', form=form, legend='Update picture',
                                   artists=artists)

        return render_template('pictureEdit.html', title='Update picture', form=form, legend='Update picture',
                               artists=artists)
    else:
        return redirect(url_for('pictureOne', id=id))

# @app.route('/picture/<int:id>/update', methods=['GET', 'PUT', 'POST', 'DELETE'])
# def picture_update(id):
#     picture = Picture.query.get_or_404(id)
#     # if current_user.role != 'ADMIN':
#     #     abort(403)
#     form = PictureForm()
#     if form.validate_on_submit():
#         if form.picture.data:
#             picture_file = save_picture(form.picture.data)
#             picture.link = picture_file
#         picture.name = form.name.data
#         picture.description = form.description.data
#         picture.year = form.year.data
#         picture.origin = form.origin.data
#
#         db.session.commit()
#         flash('Your picture has been updated', 'success')
#         return redirect(url_for('pictureOne', id=picture.id))
#     elif request.method == 'GET':
#         form.name.data = picture.name
#         form.description.data = picture.description
#         form.year.data = picture.year
#         form.origin.data = picture.origin
#
#     return render_template('newPicture.html', title='Update picture', form=form, legend='Update picture')

@app.route('/picture/<int:id>/delete', methods=['GET', 'PUT', 'POST', 'DELETE'])
def picture_delete(id):
    if adminhe():
        picture = Picture.query.filter(Picture.id == id).first()
        form = DeletePictureForm()
        if form.is_submitted():
            if picture.comments:
                komentarze = Comment.query.filter(Comment.picture_id == id).all()
                print(komentarze)
                for a in komentarze:
                    db.session.delete(a)
            db.session.delete(picture)
            db.session.commit()
            flash('Obraz został usuniety', 'success')
            return redirect(url_for('picturesMenu'))
        return render_template('pictureDelete.html', picture=picture, form=form, css='delete.css')
    else:
        return redirect(url_for('pictureOne', id=id))

def save_picture(form_picture):
    randomHex = secrets.token_hex(8)
    #filename itself and an extension
    _, f_ext = os.path.splitext(form_picture.filename)
    #underscore here to throw away an unused variable
    picture_filename = randomHex + f_ext
    #making a path
    picture_path = os.path.join(app.root_path, 'static/img/pictures/', picture_filename)

    #this is to recize pic before saving
    # output_size = (300,200)
    # i = Image.open(form_picture)
    # i.thumbnail(output_size)
    # i.save(picture_path)

    form_picture.save(picture_path)
    return picture_filename


@app.route('/picture/new', methods=['POST', 'GET'])
def newPicture():
    if adminhe():
        artists = db.session.query(Artist).all()
        artist_list = [(artist.id, artist.name) for artist in artists]
        form = PictureForm()
        # Picture.query.filter(Picture.id==(id).first)

        form.artist.choices = artist_list
        # artist = (Artist.query.filter_by(name='').first()).id
        # if request.method == 'POST':
        #     artistid = Artist.query.filter(Artist.id==(form.artist.data)).first()

        if form.validate_on_submit():
            if form.picture.data:
                picture_file = save_picture(form.picture.data)

            picture = Picture(name=form.name.data, description=form.description.data, year=form.year.data,
                              origin=form.origin.data, link=picture_file, artist_id=form.artist.data)
            # picture.artist_id = int(form.artist.data)
            db.session.add(picture)
            db.session.commit()
            flash('Obraz został dodany!', 'success')
            return redirect(url_for('picturesMenu'))
        return render_template('newPicture.html', title='new picture', form=form, legend='Dodaj obraz', artists=artists)
    else:
      return redirect(url_for('picturesMenu'))



@app.route('/register', methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('picturesMenu'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Your account has been created! Hello and feel free to log in!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('picturesMenu'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next') #if next exists it will be the parameter
            return redirect(next_page) if next_page else redirect(url_for('mainPage'))
            # return redirect(url_for('picturesMenu'))
        else:
            flash(f'Nieudane logowanie', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('picturesMenu'))

@app.route("/account")
@login_required
def account():
    return render_template('account.html', title='Account')

@app.route('/account/<int:id>/edit', methods=['GET', 'PUT', 'POST', 'DELETE'])
@login_required
def accountEdit(id):
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Twoje dane zostały zapisane', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('accountEdit.html', title='Account', form=form)

@app.route('/account/<int:id>/editpassword', methods=['GET', 'PUT', 'POST', 'DELETE'])
@login_required
def passwordEdit(id):
    form = UpdatePasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        current_user.password = hashed_password
        db.session.commit()
        flash(f'Hasło zostało zmienione', 'success')
        return redirect(url_for('account'))
    return render_template('passwordEdit.html', title='Password', form=form)


if __name__ == '__main__':
    app.run()
