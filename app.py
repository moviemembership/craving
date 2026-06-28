from flask import Flask, render_template, request, redirect
import os
import requests

app = Flask(__name__)

BREVO_API_KEY = os.getenv("BREVO_API_KEY")


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

        data = {
            "sender": {
                "name": "Nayya Community",
                "email": "community@nayyastudio.com"
            },
            "to": [
                {
                    "email": email
                }
            ],
            "subject": "Welcome to Nayya Community",
            "htmlContent": f"""
                <h2>Welcome to Nayya Community</h2>

                <p>Thank you for joining us.</p>

                <p>We're happy to have you here.</p>

                <p>Instagram username: {instagram if instagram else "Not provided"}</p>

                <p>Love,<br>Nayya</p>
            """
        }

        try:
            response = requests.post(
                "https://api.brevo.com/v3/smtp/email",
                headers={
                    "accept": "application/json",
                    "api-key": BREVO_API_KEY,
                    "content-type": "application/json"
                },
                json=data,
                timeout=10
            )

            print(response.status_code)
            print(response.text)

            if response.status_code in [200, 201, 202]:
                return "success", 200

            return "Email failed", 500

        except Exception as e:
            print("BREVO ERROR:", e)
            return "Email failed", 500

    return render_template("join_community.html")


if __name__ == "__main__":
    app.run(debug=True)
