#27.0.0.1:5000
import os
import re
import pyodbc # type: ignore
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize the Flask application
app = Flask(__name__)

# SECURITY KEY: Required for Flask's session management
app.secret_key = 'super-secret-key-12345'

# SQL Server connection settings
DB_SERVER = 'DESKTOP-ELF0E72\\SQLEXPRESS'
DB_DATABASE = 'DosyaYonetimDB'

# File upload folder path
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def get_db_connection():
    """Establishes and returns a connection to the SQL Server."""
    try:
        conn_str = (
            'DRIVER={ODBC Driver 17 for SQL Server};'
            f'SERVER={DB_SERVER};'
            f'DATABASE={DB_DATABASE};'
            'Trusted_Connection=yes;'
            'TrustServerCertificate=yes;'
        )
        conn = pyodbc.connect(conn_str)
        return conn
    except pyodbc.Error as ex:
        sqlstate = ex.args[0]
        # Flash an error message with a category
        flash(f"Veritabanı bağlantı hatası: {sqlstate}. Lütfen sunucu ayarlarınızı kontrol edin.", 'error')
        return None

@app.route('/')
def index():
    """Redirects to the login page."""
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handles new user registration with strong password validation."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Backend password validation rules
        if len(password) < 8:
            flash("Şifre en az 8 karakter uzunluğunda olmalıdır.", "error")
            return redirect(url_for('register'))
        if not re.search(r"[a-z]", password):
            flash("Şifre en az bir küçük harf içermelidir.", "error")
            return redirect(url_for('register'))
        if not re.search(r"[A-Z]", password):
            flash("Şifre en az bir büyük harf içermelidir.", "error")
            return redirect(url_for('register'))
        if not re.search(r"[0-9]", password):
            flash("Şifre en az bir rakam içermelidir.", "error")
            return redirect(url_for('register'))
        if not re.search(r"[!@#$%^&*()_+={}\[\]|\\:;\"'<,>.?/`~]", password):
            flash("Şifre en az bir özel karakter içermelidir.", "error")
            return redirect(url_for('register'))

        # Check if passwords match
        if password != confirm_password:
            flash("Girdiğiniz şifreler eşleşmiyor. Lütfen tekrar deneyin.", "error")
            return redirect(url_for('register'))

        conn = get_db_connection()
        if not conn:
            return redirect(url_for('register'))
        
        cursor = conn.cursor()
        try:
            # Check if username already exists
            cursor.execute("SELECT UserID FROM Users WHERE Username = ?", (username,))
            if cursor.fetchone():
                flash("Bu kullanıcı adı zaten alınmış. Lütfen başka bir kullanıcı adı seçin.", "error")
                return redirect(url_for('register'))
            
            # If all checks pass, hash the password and insert the user
            hashed_password = generate_password_hash(password)
            cursor.execute("INSERT INTO Users (Username, Password) VALUES (?, ?)", (username, hashed_password))
            conn.commit()
            flash("Kayıt başarılı! Lütfen giriş yapın.", "success")
            return redirect(url_for('login'))
        except pyodbc.Error as e:
            conn.rollback()
            flash(f"Veritabanı hatası oluştu: {e}", "error")
        except Exception as e:
            flash(f"Beklenmedik bir hata oluştu: {e}", "error")
        finally:
            conn.close()

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handles user login."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        if not conn:
            return render_template('login.html')

        cursor = conn.cursor()
        cursor.execute("SELECT UserID, Password FROM Users WHERE Username = ?", (username,))
        user = cursor.fetchone()
        conn.close()
        
        if user and check_password_hash(user.Password, password):
            session['loggedin'] = True
            session['userid'] = user.UserID
            session['username'] = username
            flash("Başarıyla giriş yaptınız!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Yanlış kullanıcı adı veya şifre.", "error")

    return render_template('login.html')

@app.route('/logout')
def logout():
    """Terminates the user session."""
    session.pop('loggedin', None)
    session.pop('userid', None)
    session.pop('username', None)
    flash("Başarıyla çıkış yaptınız.", "success")
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    """Displays the user's dashboard and file list."""
    if 'loggedin' in session:
        files = []
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT Filename FROM Files WHERE UserID = ?", (session['userid'],))
                rows = cursor.fetchall()
                for row in rows:
                    files.append({"Filename": row.Filename})
            except Exception as e:
                flash(f"Dosyalar listelenirken bir hata oluştu: {e}", "error")
            finally:
                conn.close()
        return render_template('dashboard.html', files=files, username=session['username'])
    
    return redirect(url_for('login'))

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handles file uploads."""
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    if 'file' not in request.files:
        flash("Lütfen bir dosya seçin.", "error")
        return redirect(url_for('dashboard'))
    
    file = request.files['file']
    if file.filename == '':
        flash("Seçilen dosya adı geçersiz.", "error")
        return redirect(url_for('dashboard'))
    
    if file:
        filename = secure_filename(file.filename)
        user_folder = os.path.join(app.config['UPLOAD_FOLDER'], str(session['userid']))
        if not os.path.exists(user_folder):
            os.makedirs(user_folder)
        
        filepath = os.path.join(user_folder, filename)
        
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO Files (Filename, UserID) VALUES (?, ?)", (filename, session['userid']))
                conn.commit()
                file.save(filepath)
                flash("Dosya başarıyla yüklendi!", "success")
            except Exception as e:
                flash(f"Dosya veritabanına kaydedilirken bir hata oluştu: {e}", "error")
            finally:
                conn.close()

    return redirect(url_for('dashboard'))

@app.route('/delete/<string:filename>', methods=['POST'])
def delete_file(filename):
    """Handles file deletion."""
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT Filename FROM Files WHERE Filename = ? AND UserID = ?", (filename, session['userid']))
            file_record = cursor.fetchone()
            
            if file_record:
                cursor.execute("DELETE FROM Files WHERE Filename = ? AND UserID = ?", (filename, session['userid']))
                conn.commit()

                filepath = os.path.join(app.config['UPLOAD_FOLDER'], str(session['userid']), filename)
                if os.path.exists(filepath):
                    os.remove(filepath)
                
                flash(f"'{filename}' başarıyla silindi.", "success")
            else:
                flash("Silme işlemi başarısız. Dosya bulunamadı veya yetkiniz yok.", "error")
        except Exception as e:
            flash(f"Dosya silinirken bir hata oluştu: {e}", "error")
        finally:
            conn.close()

    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
