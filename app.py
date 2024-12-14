from flask import Flask, render_template, request, redirect, flash, url_for
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from config import User
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
            flash("namaenasi")
            flash("3kaime")
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


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)
