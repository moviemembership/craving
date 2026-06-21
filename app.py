from flask import Flask, render_template, request, redirect
from flask_mail import Mail, Message
import os

app = Flask(__name__)

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.getenv("GMAIL_USER")
app.config["MAIL_PASSWORD"] = os.getenv("GMAIL_APP_PASSWORD")
app.config["MAIL_TIMEOUT"] = 10

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
            return "Email is required"

        # Send email to customer
        msg = Message(
            subject="Welcome to Nayya Community",
            sender=app.config["MAIL_USERNAME"],
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
            mail.send(msg)
            return "success", 200
        
        except Exception as e:
            print("EMAIL ERROR:", e)
            return "Email failed", 500

    return render_template("join_community.html")

if __name__ == "__main__":
    app.run(debug=True)
