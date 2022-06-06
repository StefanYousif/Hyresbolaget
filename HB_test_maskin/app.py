from flask import Flask, request, session, redirect, url_for, render_template, flash
import psycopg2 
import psycopg2.extras
import re 
from werkzeug.security import generate_password_hash, check_password_hash
import safety
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = 'cairocoders-ednalan'
 
#The safety file contains the login database and the key to the google maps api
#It is hidden so that no unauthorized person can have access to our database
#As well as google's key must be for ourselves and not public.
safety.googlekey
conn = psycopg2.connect(dbname=safety.DB_NAME, user=safety.DB_USER, password=safety.DB_PASS, host=safety.DB_HOST)

@app.route('/')
def home():
    #Checks if the user is logged in to the website
    if 'loggedin' in session:
    
        #If the person is logged in, continue as the user's session
        return render_template('home.html', username=[session['username']])
    #Not logged in -> sent back to the login page
    return redirect(url_for('login'))

@app.route('/login/', methods=['GET', 'POST'])
def login():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
   
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        print(password)
 
        # Check if account exists using MySQL
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        # Fetch one record and return result
        account = cursor.fetchone()
 
        if account:
            password_rs = account['password']
            print(password_rs)
            # If account exists in users table in our database
            if check_password_hash(password_rs, password):
                # Create session data, we can access this data in other routes
                session['loggedin'] = True
                session['id'] = account['id']
                session['username'] = account['username']
                # Redirect to home page
                return redirect(url_for('home'))
            else:
                # Account doesnt exist or username/password incorrect
                flash('fel username/password')
        else:
            # Account doesnt exist or username/password incorrect
            flash('Felaktigt namn/lösenord')
 
    return render_template('login.html')
  
#Function for updating ID on garage
#And for updating ID for image, so that they end up on the same row 
#In the database   
def update_garage_id():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("UPDATE garage SET title = upload.title FROM upload WHERE garage.id = upload.id")
    conn.commit()


@app.route('/register', methods=['GET', 'POST'])
def register():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
 
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        fullname = request.form['fullname']
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
    
        _hashed_password = generate_password_hash(password)
 
        #Create profile on website
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        account = cursor.fetchone()
        print(account)
        #Looks if account exist or is spelled wrong
        #For example, wrong sign or email
        if account:
            flash('Kontot existerar redan!')
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash('Felaktig emailaddress!')
        elif not re.match(r'[A-Za-z0-9]+', username):
            flash('Användarnamet får bara innehålla bokstäver och siffror')
        elif not username or not password or not email:
            flash('Vänligen fyll i de tomma fälten!')
        else:
            #If account don't exist. Create and add in database
            cursor.execute("INSERT INTO users (fullname, username, password, email) VALUES (%s,%s,%s,%s)", (fullname, username, _hashed_password, email))
            conn.commit()

            flash('Du har registrerat dig, välkommen!')
    elif request.method == 'POST':
        flash('Vänligen fyll i de tomma fälten!')
    # Show registration form with message (if any)
    return render_template('register.html')
   
#Function for updating ID on garage
#And for updating ID for image, so that they end up on the same row 
#In the database    
update_garage_id()

#Logout function
@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))
   

#Functions shows all garages
@app.route('/garage', methods=['GET', 'POST'])
def garage():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("select * from garage order by id desc")
    data = cursor.fetchall()
    conn.commit()
    return render_template('garage.html',data=data)


#Function show received messages
@app.route('/messages', methods=['GET'])
def show_messages():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("select * from messages where too = %s", [session['username']])
    data = cursor.fetchall()
    conn.commit()
    return render_template('messages.html',data=data)


#Function for sending messages
#Then messages saves in database
@app.route('/messages', methods=['GET', 'POST'])
def messages():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    renter = session['username']
    fron = session['username']
    to = request.form.get('to')
    text = request.form.get('text')
    print("hej")    
    cursor.execute("INSERT INTO messages (users, fron, too, text)  VALUES (%s,%s,%s,%s)", (renter, fron, to, text))
    conn.commit()
    flash('Ditt meddelande har skickats!')
    return render_template('messages.html')

UPLOAD_FOLDER = 'static'
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
  
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
#Function adds garage in database and then
#Recieve information from website in the form of a form + a picture.
@app.route('/', methods=['GET', 'POST'])
def new_article():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    garagename = request.form.get('garagename',False)
    renter = session['username']
    gatuadress = request.form.get('gatuadress',False)
    postkod = request.form.get('postkod',False)
    stad = request.form.get('stad',False)
    beskrivning = request.form.get('beskrivning',False)
    pris = request.form.get('pris',False)
    cursor.execute("INSERT INTO garage (name, renter, gatuadress, description, price, zipcode, city)  VALUES (%s,%s,%s,%s,%s,%s,%s)", (garagename, renter, gatuadress, beskrivning, pris, postkod, stad ))
    conn.commit()
    flash('Ditt garage är nu uppe för uthyrning!')
    if 'file' not in request.files:
        flash('Ingen fil vald')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('Ingen bild vald för uppladdning')
        return redirect(request.url)
    try:
        file and allowed_file(file.filename)
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        cursor.execute("INSERT INTO upload (title) VALUES (%s)", (filename,))
        conn.commit()
        flash('Bild på garage har laddats upp!')
        return render_template('home.html', filename=filename)
    except:
        flash('Tillåtna bilder är - png, jpg, jpeg, gif')
        return redirect(request.url)
    finally:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("UPDATE garage SET title = upload.title FROM upload WHERE garage.id = upload.id")
        conn.commit()

#Function sends user to profilepage
#can see accountinformation
@app.route('/profile')
def profile(): 
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
   
    #Checks if user logged-in
    if 'loggedin' in session:
        cursor.execute('SELECT * FROM users WHERE id = %s', [session['id']])
        account = cursor.fetchone()
        # Show the profile page with account info
        return render_template('profile.html', account=account)
    # If user not logged in;
    return redirect(url_for('login'))

#Function should've shown all garages a user has added 

@app.route('/profile', methods=['GET', 'POST'])
def profile_garage():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("select * from garage where renter = %s", [session['username']])
    dota1 = cursor.fetchall()
    conn.commit()
    return render_template('profile.html',dota1=dota1)

UPLOAD_FOLDER = 'static/uploads'

app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
  
  #Allowed file extensions
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
  
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/home', methods=['GET', 'POST'])
def upload_image():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    #Ensures that the file is added
    if 'file' not in request.files:
        flash('Ingen fil vad')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('Ingen fil vad')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
 
        cursor.execute("INSERT INTO upload (title) VALUES (%s)", (filename,))
        conn.commit()
 
        flash('Image successfully uploaded and aisplayed below')
        return render_template('home.html', filename=filename)
    else:
        flash('Tillåtna filer är - png, jpg, jpeg, gif')
        return redirect(request.url)
  

 #This code shows the image user have just uploaded.
@app.route('/display/<filename>')
def display_image(filename):
    #print('display_image filename: ' + filename)
    return redirect(url_for('static', filename='uploads/' + filename), code=301) 


#Runs the programme
if __name__ == "__main__":
    app.run(debug=True)