from flask import Flask, render_template, redirect, request, send_file
from forms import SignUpForm, LoginForm, OTPForm, DocForm, InboxForm
import firebase_admin
from firebase_admin import db
import json
import random
from flask_mail import Mail, Message
import os
from datetime import datetime

cred_object = firebase_admin.credentials.Certificate('abcstore-6cca5-firebase-adminsdk-nqv72-76578d9748.json')
default_app = firebase_admin.initialize_app(cred_object, {
	'databaseURL': 'https://abcstore-6cca5-default-rtdb.asia-southeast1.firebasedatabase.app/'
})

DOWNLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__)) + '/downloads/'

app = Flask(__name__)

app.config['SECRET_KEY'] = 'eoivwnvgoiwbnrwnv'
app.config['MAIL_SERVER'] ='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'ajitestmail123@gmail.com'
app.config['MAIL_PASSWORD'] = 'fjejtcadroeypgau'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER
mail = Mail(app)

@app.route('/')
def index():
    return redirect('/login')

otp = 0
result = None
otpcount = 0

LoggedUser = None
LoggedEmail = None 

@app.route('/signup', methods=['GET','POST'])
def signup():
    fm = SignUpForm()
    if fm.is_submitted():
        global result
        result = request.form
        result = dict(result)
        # print(result)
        return redirect('/otpv')
        
    return render_template('signup.html', fm=fm)

def on_verify():
    msg = Message('Verification Success', sender = 'ajitestmail123@gmail.com', recipients = [result['email']])
    msg.body = f"Hello {result['username']}! Email has been verified 💯! Thank You for joining us😍😍. Store and save your documents safe and securely with REJOINDER🔐"
    mail.send(msg)
    global LoggedEmail, LoggedUser
    LoggedEmail = result['email']
    LoggedUser = result['username']
    os.mkdir(f'drive/{LoggedEmail}')
    os.mkdir(f'drive/{LoggedEmail}/inbox')
    os.mkdir(f'drive/{LoggedEmail}/outbox')
    f = open(f"drive/{LoggedEmail}/inlog.txt", "w")
    f.close()
    f = open(f"drive/{LoggedEmail}/outlog.txt", "w")
    f.close()
        

@app.route('/otpv', methods=['GET', 'POST'])
def otpv():
    # print("run_init")
    o = OTPForm()
    global otp, otpcount
    
    def store():
        ref = db.reference('/users/authinfo')
        ref.push().set({"Username":str(result['username']), "Passwd":str(result['password']), "Email": str(result['email'])})
        return "Entered"
    
    if o.is_submitted():
        # print('run3')
        res = request.form
        if str(res['recieved_otp'])==str(otp):
            otpcount = 0
            rep = store()
            on_verify()
            return redirect('/dashboard')
        return "Error"
    
    if(otpcount==0):
        otp = random.randrange(100000, 999999)    
        # print('running')
        msg = Message('OTP Verification', sender = 'ajitestmail123@gmail.com', recipients = [result['email']])
        msg.body = f"Hello {result['username']}! Thanks for registering😍😍! Your OTP for REJOINDER🔐 is {otp}"
        mail.send(msg)
        otpcount+=1
    
    return render_template('otp.html', form=o)

def validate(email, password):
    ref = db.reference('/users/authinfo')
    data = ref.get()
    # print(data)
    # print(email, password)
    for k, v in data.items():
        if v['Email']==email and v['Passwd']==password:
            global LoggedEmail, LoggedUser
            LoggedEmail = email
            LoggedUser = v['Username']
            print(LoggedEmail, LoggedUser)
            return True
    return False

@app.route('/login', methods=['GET','POST'])
def login():
    fm = LoginForm()
    if fm.is_submitted():
        result = request.form
        if(validate(result['email'], result['password'])):
            return redirect('/dashboard')
        return "Auth Failure"
    
    return render_template('login.html', fm=fm)

@app.route('/drive')
def drive():
    global LoggedUser
    if(LoggedUser==None):
        return redirect('/login')
    return render_template('drive.html')

@app.route('/dashboard')
def dashboard():
    global LoggedUser, LoggedEmail
    if(LoggedUser==None):
        return redirect('/login')
    
    arr = []
    with open(f"drive/{LoggedEmail}/outlog.txt", 'r') as f:
        lines = f.readlines()
    with open(f"drive/{LoggedEmail}/inlog.txt", 'r') as f:
        lines2 = f.readlines()
    shares = len(lines)
    tdocs = len(lines2) + shares
    
    return render_template('dashboard.html', CUser=LoggedUser, shares = shares, tdocs = tdocs)

@app.route('/newsfeed')
def newsfeed():
    global LoggedUser
    if(LoggedUser==None):
        return redirect('/login')
    
    return render_template('newsfeed.html')

@app.route('/inbox', methods=['GET','POST'])
def inbox():
    global LoggedUser, LoggedEmail
    if(LoggedUser==None):
        return redirect('/login')
    
    form = InboxForm()
    
    if form.is_submitted():
        # print(dict(request.form))
        sender_name = request.form['out']
        # print(sender_name)
        file_name = request.form['file_name']
        return send_file(f"drive/{sender_name}/outbox/"+file_name, as_attachment=True)
    
    arr = []
    with open(f"drive/{LoggedEmail}/inlog.txt", 'r') as f:
        lines = f.readlines()
    for line in lines:
        arr.append(line.split(','))
    
    arr.reverse()
       
    return render_template('inbox.html', indata=arr, form = form)

@app.route('/outbox')
def outbox():
    global LoggedUser, LoggedEmail
    if(LoggedUser==None):
        return redirect('/login')
    
    arr = []
    with open(f"drive/{LoggedEmail}/outlog.txt", 'r') as f:
        lines = f.readlines()
    for line in lines:
        arr.append(line.split(','))
    
    # arr.reverse()
    
    return render_template('outbox.html', outdata=arr)

@app.route('/documents', methods=['GET','POST'])
def documents():
    global LoggedUser
    if(LoggedUser==None):
        return redirect('/login')
        
    dform = DocForm()
    if dform.is_submitted():
        data = request.form
        fl = request.files['upfile']
        # print(fl)
        flname = fl.filename
        # print(flname)
        rcemail = data['email']
        fl.save(f'drive/{LoggedEmail}/outbox/{flname}')
        # fl.save(f'drive/{rcemail}/inbox/{flname}')
        
        with open(f'drive/{LoggedEmail}/outbox/{flname}', 'rb') as f:
            with open(f'drive/{rcemail}/inbox/{flname}', 'wb') as f2:
                f2.write(f.read())
        
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        with open(f"drive/{LoggedEmail}/outlog.txt", 'a') as f:
            f.write(f'{flname},{rcemail},{now}\n')
        
        with open(f"drive/{rcemail}/inlog.txt", 'a') as f:
            f.write(f'{flname},{LoggedEmail},{now}\n')
        
        return redirect('/dashboard')
        
    return render_template('documents.html', dform = dform)

@app.route('/logout')
def logout():
    global LoggedEmail, LoggedUser
    LoggedEmail = None
    LoggedUser = None
    return redirect('/login')


if __name__=="__main__":
    app.run(port=3000)   