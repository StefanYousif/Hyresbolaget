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
 
#Safetyfilen innehåller databasen login samt nyckeln till google maps api:et
#Den är dold så att ingen obehörig ska kunna ha tillträde till vår databas 
#Samt googles nyckel måste vara för oss själva och ej public
safety.googlekey
conn = psycopg2.connect(dbname=safety.DB_NAME, user=safety.DB_USER, password=safety.DB_PASS, host=safety.DB_HOST)

@app.route('/')
def home():
    #Kontrollerar ifall användaren är inloggad på hemsidan
    if 'loggedin' in session:
    
        #ifall personen är inloggad, fortsätt som användarens session
        return render_template('home.html', username=[session['username']])
    #Ej inloggad -> skickas tillbaka till loginsidan
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
            # If account exists in users table in out database
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
  
  #Var tvunget att ha denna funktionen för att kunna uppdatera id:et på garaget
# och id:et för bilden, så att de alltid hamnar på samma rad
# i sin tabell i databasen   
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
 
        #Skapar konto till hemsidan
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        account = cursor.fetchone()
        print(account)
        #kollar ifall kontot existerar och felaktigheter vid skapadet
        #så som fel tecken, email osv
        if account:
            flash('Kontot existerar redan!')
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash('Felaktig emailaddress!')
        elif not re.match(r'[A-Za-z0-9]+', username):
            flash('Användarnamet får bara innehålla bokstäver och siffror')
        elif not username or not password or not email:
            flash('Vänligen fyll i de tomma fälten!')
        else:
            #Ifall kontot ej finns, så skapar vi ett och lägger till i databasen
            cursor.execute("INSERT INTO users (fullname, username, password, email) VALUES (%s,%s,%s,%s)", (fullname, username, _hashed_password, email))
            conn.commit()

            flash('Du har registrerat dig, välkommen!')
    elif request.method == 'POST':
        flash('Vänligen fyll i de tomma fälten!')
    # Show registration form with message (if any)
    return render_template('register.html')
   
#Var tvunget att ha denna funktionen för att kunna uppdatera id:et på garaget
# och id:et för bilden, så att de alltid hamnar på samma rad
# i sin tabell i databasen   
update_garage_id()

#Loggar ut personen
@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))
   

#Den här funktionen visar upp alla garage på garagesidan   
@app.route('/garage', methods=['GET', 'POST'])
def garage():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("select * from garage order by id desc")
    data = cursor.fetchall()
    conn.commit()
    return render_template('garage.html',data=data)


#Den här funktionen visar upp mottagna meddelanden för personen
@app.route('/messages', methods=['GET'])
def show_messages():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("select * from messages where too = %s", [session['username']])
    data = cursor.fetchall()
    conn.commit()
    return render_template('messages.html',data=data)


#Funktionen för att kunna skicka meddelanden
#sedan sparas meddelandet i databasen
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
#Den här funktionen lägger till ett garage i databasen och sedan
#hämtar information från hemsidan i form av ett formulär + en bild.
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

#Den här funktionen skickar personen till profilsidan där de 
#kan se sina uppgifter
@app.route('/profile')
def profile(): 
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
   
    #Kollar ifall användaren är inloggad
    if 'loggedin' in session:
        cursor.execute('SELECT * FROM users WHERE id = %s', [session['id']])
        account = cursor.fetchone()
        # Show the profile page with account info
        return render_template('profile.html', account=account)
    # Ifall användaren inte är inloggad;
    return redirect(url_for('login'))

#Den här funktionen skulle visa upp alla garage för personen som har
#lagt upp garagen

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
  
  #De tillåtna filändelsena
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
  
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/home', methods=['GET', 'POST'])
def upload_image():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    #Säkerställer att filen läggs till
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
  

 #Den här koden visar upp bilden man nyss har laddat upp. 
@app.route('/display/<filename>')
def display_image(filename):
    #print('display_image filename: ' + filename)
    return redirect(url_for('static', filename='uploads/' + filename), code=301) 


#Runnar hela programmet
if __name__ == "__main__":
    app.run(debug=True)