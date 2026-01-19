import os
from flask import Flask, render_template, request, make_response, redirect, url_for, session
from database import get_db, close_connection, init_db, DATABASE
from auth import get_or_create_user_for_ip
from robot import robot_controller


app = Flask(__name__)
app.teardown_appcontext(close_connection)
app.secret_key = 'super_secret_key_for_session_management'


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/robots.txt')
def robots():
    user_ip = request.remote_addr
    username, password = get_or_create_user_for_ip(user_ip)
    content = f'''User-agent: *
Disallow: /secret-login-page

# CREDS: {username}:{password}
'''
    response = make_response(content)
    response.headers['Content-Type'] = 'text/plain'
    return response


@app.route('/secret-login-page', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    username = request.form['username']
    password = request.form['password']
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user = cursor.fetchone()
    
    if not user:
        return render_template('login.html', error='Invalid credentials')
    
    session['user_id'] = user['id']
    session['username'] = user['username']
    session['role'] = user['role']
    
    # Set default cookie if not present, but it should default to false effectively by absence
    resp = make_response(redirect(url_for('dashboard')))
    if 'searchEnabled' not in request.cookies:
            resp.set_cookie('searchEnabled', 'false')
    return resp


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    search_enabled_cookie = request.cookies.get('searchEnabled')
    
    return render_template('dashboard.html', user=session, search_enabled=search_enabled_cookie == 'true')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


@app.route('/search')
def search():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.cookies.get('searchEnabled') != 'true':
        return redirect(url_for('dashboard'))

    query = request.args.get('q', '')
    
    # VULNERABLE SQL QUERY
    # We are directly concatenating the user input into the query string.
    # The target query allows UNION injection to fetch users.
    # Original query: SELECT * FROM items WHERE name LIKE '%{query}%'
    sql = f'SELECT * FROM items WHERE name LIKE \'%{query}%\''
    
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
    except Exception as e:
        results = []
        pass
        
    return render_template('dashboard.html', user=session, search_enabled=True, results=results)


@app.route('/move/<direction>', methods=['POST'])
def move_robot(direction):
    if 'user_id' not in session or session.get('role') != 'admin':
        return 'Unauthorized', 403
        
    message = ''
    if robot_controller.move(direction):
        message = f'Robot moving {direction}...'
    else:
        message = 'Invalid direction.'
        
    return render_template('dashboard.html', user=session, search_enabled=True, message=message)


if __name__ == '__main__':
    if not os.path.exists(DATABASE):
        init_db(app)
    else:
        init_db(app)
        
    app.run(host='0.0.0.0', port=5000, debug=True)
