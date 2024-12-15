from flask import Flask, render_template, request, redirect, flash, url_for
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from config import User, Message
from werkzeug.security import generate_password_hash, check_password_hash
from peewee import IntegrityError

app = Flask(__name__)
app.secret_key = "secret"  # 秘密鍵
login_manager = LoginManager()
login_manager.init_app(app)


# Flask-Loginがユーザー情報を取得するためのメソッド
@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)


# ログインしていないとアクセスできないページにアクセスがあった場合の処理
@login_manager.unauthorized_handler
def unauthorized_handler():
    # return redirect("/login")
    return redirect(url_for("login"))


# ユーザー登録フォームの表示
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # データの検証 未入力
        if not request.form["name"] or not request.form["password"] or not request.form["email"]:
            flash("未入力あり")
            return redirect(request.url)
        # 重複 名前
        if User.select().where(User.name == request.form["name"]):
            flash("名前重複")
            return redirect(request.url)
        # 重複 email
        if User.select().where(User.email == request.form["email"]):
            flash("email重複")
            return redirect(request.url)

        # ユーザー登録
        try:
            User.create(
                name=request.form["name"],
                email=request.form["email"],
                # password=request.form["password"],
                password=generate_password_hash(request.form["password"]),
            )
            return render_template("index.html")
        except IntegrityError as e:
            flash(f"{e}")

    return render_template("register.html")


# ログインフォームの表示
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # データの検証
        if not request.form["password"] or not request.form["email"]:
            flash("未入力の項目があります。")
            return redirect(request.url)

        # ここでユーザーを認証し、OKならログインする
        user = User.select().where(User.email == request.form["email"]).first()
        if user is not None and check_password_hash(user.password, request.form["password"]):
            login_user(user)
            flash(f"ようこそ！ {user.name} さん")
            return redirect(url_for("index"))

        # NGならフラッシュメッセージを設定
        flash("認証に失敗しました")

    return render_template("login.html")


# ログアウト処理
@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("ログアウトしました！")
    return redirect(url_for("index"))


# ユーザー削除処理
@app.route("/unregister")
@login_required
def unregister():
    current_user.delete_instance()
    logout_user()
    return redirect(url_for("index"))


# メッセージ登録フォームの表示・投稿・一覧表示
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST" and current_user.is_authenticated:
        Message.create(user=current_user, content=request.form["content"])

    messages = (
        Message.select()
        .where(Message.reply_to.is_null(True))
        .order_by(Message.pub_date.desc(), Message.id.desc())
    )
    return render_template("index.html", messages=messages)


# メッセージ削除
@app.route("/messages/<message_id>/delete/", methods=["POST"])
@login_required
def delete(message_id):
    if Message.select().where((Message.id == message_id) & (Message.user == current_user)).first():
        Message.delete_by_id(message_id)
    else:
        flash("無効な操作です")
    return redirect(request.referrer)


# 返信表示
@app.route("/messages/<message_id>/")
def show(message_id):
    messages = (
        Message.select()
        .where((Message.id == message_id) | (Message.reply_to == message_id))
        .order_by(Message.pub_date.desc())
    )
    if messages.count() == 0:
        return redirect(url_for("index"))

    return render_template("show.html", messages=messages, message_id=message_id)


# 返信登録
@app.route("/messages/<message_id>/", methods=["POST"])
@login_required
def reply(message_id):
    Message.create(user=current_user, content=request.form["content"], reply_to=message_id)
    return redirect(url_for("show", message_id=message_id))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)
