from flask import Flask, render_template, request
import qrcode
from PIL import Image

app = Flask(__name__)

@app.route('/', methods=('GET', 'POST'))
def index():
    if request.method == "POST":
        content = request.form['link']
        QR(content)
        return render_template('index.html', submit=True)
    return render_template('index.html')

def QR(link):
    # taking image which user wants
    # in the QR code center
    Logo_link = 'logo.png'
    
    logo = Image.open(Logo_link)
    
    # taking base width
    basewidth = 150
    
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
    
    # save the QR code generated
    print("Done!")
    QRimg.save('./static/QR.png')