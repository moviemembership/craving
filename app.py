from flask import Flask, render_template, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import requests

app = Flask(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")
BREVO_API_KEY = os.getenv("BREVO_API_KEY")

if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class CommunityMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    instagram = db.Column(db.String(150), nullable=False)
    birthday = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


with app.app_context():
    db.create_all()


@app.route("/", methods=["GET", "POST"])
def join_community():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        instagram = request.form.get("instagram")
        birthday = request.form.get("birthday")

        if not name or not email or not instagram or not birthday:
            return "All fields are required", 400

        member = CommunityMember(
            name=name,
            email=email,
            instagram=instagram,
            birthday=birthday
        )

        db.session.add(member)
        db.session.commit()

        data = {
            "sender": {
                "name": "Nayya Community",
                "email": "community@nayyastudio.com"
            },
            "to": [{"email": email}],
            "subject": "Welcome to Nayya Community",
            "htmlContent": f"""
                <h2>Welcome to Nayya Community</h2>
                <p>Hi {name},</p>
                <p>Thank you for joining us.</p>
                <p>We're happy to have you here.</p>
                <p><b>Instagram:</b> {instagram}</p>
                <p><b>Birthday:</b> {birthday}</p>
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

        except Exception as e:
            print("BREVO ERROR:", e)

        return "success", 200

    return render_template("join_community.html")


@app.route("/email-list")
def email_list():
    search = request.args.get("search", "")
    sort = request.args.get("sort", "latest")
    per_page = int(request.args.get("per_page", 10))
    page = int(request.args.get("page", 1))

    query = CommunityMember.query

    if search:
        keyword = f"%{search}%"
        query = query.filter(
            db.or_(
                CommunityMember.name.ilike(keyword),
                CommunityMember.email.ilike(keyword),
                CommunityMember.instagram.ilike(keyword)
            )
        )

    if sort == "oldest":
        query = query.order_by(CommunityMember.created_at.asc())
    elif sort == "name_az":
        query = query.order_by(CommunityMember.name.asc())
    elif sort == "name_za":
        query = query.order_by(CommunityMember.name.desc())
    elif sort == "email_az":
        query = query.order_by(CommunityMember.email.asc())
    elif sort == "email_za":
        query = query.order_by(CommunityMember.email.desc())
    elif sort == "instagram_az":
        query = query.order_by(CommunityMember.instagram.asc())
    elif sort == "instagram_za":
        query = query.order_by(CommunityMember.instagram.desc())
    else:
        query = query.order_by(CommunityMember.created_at.desc())

    members = query.paginate(page=page, per_page=per_page, error_out=False)

    total_members = CommunityMember.query.count()

    return render_template(
        "email_list.html",
        members=members,
        search=search,
        sort=sort,
        per_page=per_page,
        total_members=total_members
    )


@app.route("/delete-members", methods=["POST"])
def delete_members():
    ids = request.json.get("ids", [])

    if not ids:
        return jsonify({"success": False, "message": "No data selected"}), 400

    CommunityMember.query.filter(CommunityMember.id.in_(ids)).delete(synchronize_session=False)
    db.session.commit()

    return jsonify({"success": True})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
