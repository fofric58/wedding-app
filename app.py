import zipfile
from flask import send_file
import os
from flask import Flask, render_template, request, redirect, session, send_from_directory
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecretkey"

UPLOAD_FOLDER = "uploads"
ADMIN_USER = "selenay"
ADMIN_PASS = "1105"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    if "files" not in request.files:
        return "Dosya yok"

    files = request.files.getlist("files")

    for file in files:
        if file.filename != "":
            filename = secure_filename(file.filename)
            time_prefix = datetime.now().strftime("%Y%m%d%H%M%S_")
            file.save(os.path.join(UPLOAD_FOLDER, time_prefix + filename))

    return "OK"


@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == ADMIN_USER and password == ADMIN_PASS:
            session["admin"] = True
            return redirect("/panel")

        return "Hatalı giriş"

    return render_template("admin_login.html")


@app.route("/panel")
def panel():
    if not session.get("admin"):
        return redirect("/admin")

    files = os.listdir(UPLOAD_FOLDER)
    return render_template("admin.html", files=files)


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

                
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/admin")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
@app.route("/download-all")
def download_all():
    if not session.get("admin"):
        return redirect("/admin")

    zip_path = "all_photos.zip"

    with zipfile.ZipFile(zip_path, "w") as zipf:
        for file in os.listdir(UPLOAD_FOLDER):
            file_path = os.path.join(UPLOAD_FOLDER, file)
            zipf.write(file_path, file)

    return send_file(zip_path, as_attachment=True)
