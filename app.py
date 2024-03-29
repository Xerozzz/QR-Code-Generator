from flask import Flask, render_template, request, session, flash, redirect, send_file, url_for
import qrcode
import sqlite3
from PIL import Image
import io
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret' # Make sure to change this to your own value!!!
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)

@app.before_request
def check_login():
    if session.get("logged_in", default=False) == False and request.endpoint != 'login':
        return redirect(url_for('login'))

def db_connect():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/logout', methods=['GET'])
def logout():
    session.pop("logged_in")
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        if session.get("logged_in", default=False) == True:
            return redirect(url_for('index'))

        # Get form information
        username = request.form["username"]
        password = request.form["password"]
        option = request.form["option"]

        # Connect to database
        conn = db_connect()
        cur = conn.cursor()

        # Login Option
        if option == "login":
            cur.execute("SELECT * FROM users WHERE username = ?", [username])
            user = cur.fetchone()
            if user is None:
                flash("ERROR: USERNAME DOES NOT EXIST", "danger")
            else:
                if check_password_hash(user["password"], password):
                    session["username"] = username
                    session["logged_in"] = True
                    return render_template('index.html')
                else:
                    flash("ERROR: INCORRECT PASSWORD", "danger")

        # Register Option
        elif option == "register":
            password = generate_password_hash(password)
            cur.execute("SELECT * FROM users WHERE username = ?", [username])
            if cur.fetchone() is not None:
                flash("ERROR: USERNAME ALREADY EXISTS", "danger")
            else:
                cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", [username, password])
                conn.commit()
                flash("SUCCESS: ACCOUNT CREATED", "success")
        else:
            flash("ERROR: OPTION NOT VALID")
    return render_template('login.html')

@app.route('/', methods=['GET', 'POST'])
def index():
    
    return render_template('index.html')

@app.route('/qr', methods=['POST'])
def qr():
    file = request.files['file'].read()
    link = request.form['link']
    save = request.form['save']
    if save == "on":
        conn = db_connect()
        cur = conn.cursor()
        res = cur.execute("UPDATE users SET logo = ? WHERE username = ?", [file, session["username"]])
        conn.commit()
    # taking image which user wants
    # in the QR code center
    conn = db_connect()
    cur = conn.cursor()
    res = cur.execute("SELECT logo from USERS WHERE username = ?", [session["username"]]) 
    logo_blob = res.fetchone()[0]
    logo_bytes = bytes(logo_blob)

    # convert bytes to image
    logo = Image.open(io.BytesIO(logo_bytes))


    # taking base width
    basewidth = 60
    
    # adjust image size
    wpercent = (basewidth/float(logo.size[0]))
    hsize = int((float(logo.size[1])*float(wpercent)))
    logo = logo.resize((basewidth, hsize), Image.ANTIALIAS)
    QRcode = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_H
    )
    
    # taking url or text
    url = link
    
    # adding URL or text to QRcode
    QRcode.add_data(url)
    
    # generating QR code
    QRcode.make()
    
    # taking color name from user
    QRcolor = 'black'
    
    # adding color to QR code
    QRimg = QRcode.make_image(
        fill_color=QRcolor, back_color="white").convert('RGB')
    
    # set size of QR code
    pos = ((QRimg.size[0] - logo.size[0]) // 2,
        (QRimg.size[1] - logo.size[1]) // 2)
    QRimg.paste(logo, pos)
    
    # create an in-memory buffer to store the image data
    img_buffer = io.BytesIO()
    # save the QR code generated to the buffer
    QRimg.save(img_buffer, format='PNG')
    # move the buffer's position to the start
    img_buffer.seek(0)

    # return the image data as a response
    return send_file(
        img_buffer,
        mimetype='image/png',
        as_attachment=True,
        download_name="qr.png"
    )