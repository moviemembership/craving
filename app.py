from flask import Flask, render_template, request, redirect
from flask_mail import Mail, Message
import os

app = Flask(__name__)

app.config["MAIL_SERVER"] = "smtp.hostinger.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USE_TLS"] = False
app.config["MAIL_USE_SSL"] = True
app.config["MAIL_TIMEOUT"] = 10
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")

mail = Mail(app)


@app.route("/")
def home():
    return redirect("/join-community")


@app.route("/join-community", methods=["GET", "POST"])
def join_community():
    if request.method == "POST":
        email = request.form.get("email")
        instagram = request.form.get("instagram")

        if not email:
            return "Email is required", 400

        msg = Message(
            subject="Welcome to Nayya Community",
            sender=("Nayya Community", "community@nayyastudio.com"),
            recipients=[email],
            body=f"""
Hello,

Thank you for joining Nayya Community.

We're happy to have you here.

Instagram username: {instagram if instagram else "Not provided"}

Love,
Nayya
"""
        )

        try:
            print("MAIL_USERNAME =", os.getenv("MAIL_USERNAME"))
            print("PASSWORD EXISTS =", bool(os.getenv("MAIL_PASSWORD")))
            mail.send(msg)
            return "success", 200

        except Exception as e:
            print("EMAIL ERROR:", e)
            return "Email failed", 500

    return render_template("join_community.html")

@app.route("/test")
def test():
    return {
        "gmail": os.getenv("MAIL_USERNAME"))"),
        "password_exists": bool(os.getenv("MAIL_PASSWORD"))
    }


if __name__ == "__main__":
    app.run(debug=True)
