import os
from flask import Flask, abort, render_template, redirect, request, make_response, jsonify, url_for
from flask_login import login_user, logout_user, login_required, current_user, LoginManager
from flask_restful import reqparse, abort, Api, Resource
from werkzeug.utils import secure_filename
from loginform import LoginForm
from registerform import RegisterForm
from data import db_session
from data.users import Users
from data.news import News
from data.category import Category
from data.comments import Comments
from newsform import NewsForm
from commentform import CommentForm
from changeform import ChangeForm
import news_resources

app = Flask(__name__)
app.config['SECRET_KEY'] = 'pasiloy_key'
login_manager = LoginManager()
login_manager.init_app(app)
api = Api(app)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route("/", methods=['GET', 'POST'])
def index():
    session = db_session.create_session()
    comments = session.query(Comments).all()
    q = request.args.get('q')
    if current_user.is_authenticated and q:
        news = session.query(News).filter((News.users == current_user) | (News.is_private != True)).filter((News.title.contains(q)) | (News.content.contains(q)) | (News.tag_id.contains(q)))
    elif q:
        news = session.query(News).filter(News.is_private != True).filter(News.title.contains(q) | (News.content.contains(q)) | (News.tag_id.contains(q)))
    elif current_user.is_authenticated:
        news = session.query(News).filter((News.users == current_user) | (News.is_private != True))
    else:
        news = session.query(News).filter(News.is_private != True)
    return render_template("index.html", news=news, comments=comments)


@app.route('/profile/<string:name>',  methods=['GET', 'POST'])
def profile(name):
    session = db_session.create_session()
    user = session.query(Users).filter(Users.name == name).first()
    return render_template('profile.html', user=user)


@app.route('/change/<string:name>',  methods=['GET', 'POST'])
def change(name):
    form = ChangeForm()
    session = db_session.create_session()
    user = session.query(Users).filter(Users.name == name).first()
    if request.method == "GET":
        form.name.data = user.name
        form.email.data = user.email
    if form.validate_on_submit():
        if user and user.check_password(form.old_password.data):
            if len(session.query(Users).filter(Users.name == form.name.data).all()) > 1:
                return render_template('change.html', user=user, form=form, message='Это имя уже занято')
            else:
                comments = session.query(Comments).filter(Comments.user_id == user.name)
                user.name = form.name.data
                for i in comments:
                    i.user_id = form.name.data
            if len(session.query(Users).filter(Users.email == form.email.data).all()) > 1:
                return render_template('change.html', user=user, form=form, message='Эта почта уже занята')
            else:
                user.email = form.email.data
            if form.about.data:
                user.about = form.about.data
            if form.new_password.data:
                user.set_password(form.new_password.data)
            session.commit()
            return redirect('/profile/' + str(user.name))
        else:
            return render_template('change.html', user=user, form=form, message='Неправильный старый пароль')
    return render_template('change.html', user=user, form=form)


@app.route('/comment/<int:id>',  methods=['GET', 'POST'])
@login_required
def comment(id):
    form = CommentForm()
    session = db_session.create_session()
    news = session.query(News).filter(News.id == id).first()
    if form.validate_on_submit():
        comments = Comments()
        comments.content = form.content.data
        f = form.photo.data
        if f:
            filename = secure_filename(f.filename)
            f.save(os.path.join(app.static_folder, 'img', filename))
            comments.photo = f.filename
        comments.news_id = id
        comments.user_id = current_user.name
        session.add(comments)
        session.commit()
        return redirect('/')
    return render_template('comments.html', form=form, news=news)


@app.route('/commentedit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_comment(id):
    form = CommentForm()
    if request.method == "GET":
        session = db_session.create_session()
        comment = session.query(Comments).filter(Comments.id == id).first()
        news = session.query(News).filter(News.id == Comments.news_id).first()
        if comment:
            form.content.data = comment.content
        else:
            abort(404)
    if form.validate_on_submit():
        session = db_session.create_session()
        comment = session.query(Comments).filter(Comments.id == id).first()
        news = session.query(News).filter(News.id == Comments.news_id).first()
        if comment:
            comment.content = form.content.data
            f = form.photo.data
            if f:
                filename = secure_filename(f.filename)
                f.save(os.path.join(app.static_folder, 'img', filename))
                comment.photo = f.filename
            session.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('commentedit.html', form=form, news=news)


@app.route('/comment_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def comment_delete(id):
    session = db_session.create_session()
    comment = session.query(Comments).filter(Comments.id == id).first()
    if comment:
        session.delete(comment)
        session.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/news',  methods=['GET', 'POST'])
@login_required
def add_news():
    form = NewsForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        news = News()
        news.title = form.title.data
        news.content = form.content.data
        f = form.photo.data
        if f:
            filename = secure_filename(f.filename)
            f.save(os.path.join(app.static_folder, 'img', filename))
            news.photo = f.filename
        news.is_private = form.is_private.data
        lst = []
        tags = []
        for e in session.query(Category.name):
            lst.append(*e)
        for i in form.tag.data.split():
            if i not in lst:
                tag = Category(name=i)
                session.add(tag)
            tags.append(i)
        news.tag_id = ' '.join(tags)
        current_user.news.append(news)
        session.merge(current_user)
        session.commit()
        return redirect('/')
    return render_template('news.html', title='Добавление новости',
                           form=form)


@app.route('/news/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    form = NewsForm()
    if request.method == "GET":
        session = db_session.create_session()
        news = session.query(News).filter(News.id == id, News.users == current_user).first()
        if news:
            form.title.data = news.title
            form.content.data = news.content
            form.is_private.data = news.is_private
            form.tag.data = news.tag_id

        else:
            abort(404)
    if form.validate_on_submit():
        session = db_session.create_session()
        news = session.query(News).filter(News.id == id,
                                          News.users == current_user).first()
        if news:
            news.title = form.title.data
            news.content = form.content.data
            news.is_private = form.is_private.data
            lst = []
            tags = []
            for e in session.query(Category.name):
                lst.append(*e)
            for i in form.tag.data.split():
                if i not in lst:
                    tag = Category(name=i)
                    session.add(tag)
                tags.append(i)
            news.tag_id = ' '.join(tags)
            f = form.photo.data
            if f:
                filename = secure_filename(f.filename)
                f.save(os.path.join(app.static_folder, 'img', filename))
                news.photo = f.filename
            session.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('news.html', title='Редактирование новости', form=form)


@app.route('/news_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    session = db_session.create_session()
    news = session.query(News).filter(News.id == id,
                                      News.users == current_user).first()
    if news:
        comments = session.query(Comments).filter(Comments.news_id == id)
        for i in comments:
            session.delete(i)
        session.delete(news)
        session.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(Users).filter(Users.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        session = db_session.create_session()
        if session.query(Users).filter(Users.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        if session.query(Users).filter(Users.name == form.name.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Это имя уже занято")
        user = Users(name=form.name.data, email=form.email.data, about=form.about.data)
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route("/cookie_test")
def cookie_test():
    visits_count = int(request.cookies.get("visits_count", 0))
    if visits_count:
        res = make_response(f"Вы пришли на эту страницу {visits_count + 1} раз")
        res.set_cookie("visits_count", str(visits_count + 1),
                       max_age=60 * 60 * 24 * 365 * 2)
    else:
        res = make_response(
            "Вы пришли на эту страницу в первый раз за последние 2 года")
        res.set_cookie("visits_count", '1',
                       max_age=60 * 60 * 24 * 365 * 2)
    return res


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(Users).get(user_id)


if __name__ == '__main__':
    db_session.global_init("db/blogs.sqlite")
    api.add_resource(news_resources.NewsListResource, '/api/news')
    api.add_resource(news_resources.NewsResource, '/api/news/<int:news_id>')
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
