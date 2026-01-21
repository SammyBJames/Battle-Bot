import os
from flask import Flask, render_template, request, make_response, redirect, url_for, session, jsonify
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
    content = f'Don\'t want to forget these later. I\'ll just save them here for now. Nobody even checks this page.\n\nUsername: {username}\nPassword: {password}'
    response = make_response(content)
    response.headers['Content-Type'] = 'text/plain'
    return response


@app.route('/login', methods=['GET', 'POST'])
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


@app.route('/search', methods=['GET', 'POST'])
def search():
    if 'user_id' not in session:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
            return jsonify({"error": "Unauthorized"}), 401
        return redirect(url_for('login'))

    if request.cookies.get('searchEnabled') != 'true':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
             return jsonify({"error": "Search disabled"}), 403
        return redirect(url_for('dashboard'))

    # Handle standard GET/Form POST or JSON POST
    query = ''
    if request.is_json:
        query = request.json.get('q', '')
    else:
        query = request.values.get('q', '')
    
    # VULNERABLE SQL QUERY
    # We are directly concatenating the user input into the query string.
    # The target query allows UNION injection to fetch users.
    # Original query: SELECT * FROM items WHERE name LIKE '%{query}%'
    sql = f'SELECT * FROM items WHERE name LIKE \'%{query}%\''
    
    db = get_db()
    cursor = db.cursor()
    results = []
    
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Send the error details in the JSON response for the "client" (hacker) to see
            return jsonify({
                "status": "error",
                "message": "Something went wrong.",
                "debug_error": str(e)
            }), 500
        pass
        
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
        # Convert sqlite3.Row objects to list of dicts for JSON response
        # Note: keys will be those of the 'items' table even if UNION was used
        json_results = []
        for row in results:
            json_results.append({
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "category": row[3]
            })
        return jsonify(json_results)
        
    return render_template('dashboard.html', user=session, search_enabled=True, results=results)


@app.route('/move', methods=['POST'])
def move_robot():
    if 'user_id' not in session or session.get('role') != 'admin':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
            return jsonify({"status": "error", "message": "Unauthorized"}), 403
        return 'Unauthorized', 403
        
    # Handle JSON or Form data
    direction = ''
    if request.is_json:
        direction = request.json.get('direction', '')
    else:
        direction = request.form.get('direction', '')

    message = ''
    success = False
    if robot_controller.move(direction):
        message = f'Robot moving {direction}...'
        success = True
    else:
        message = 'Invalid direction.'
        
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
        return jsonify({"status": "success" if success else "error", "message": message})
        
    return render_template('dashboard.html', user=session, search_enabled=True, message=message)


if __name__ == '__main__':
    if not os.path.exists(DATABASE):
        init_db(app)
    else:
        init_db(app)
        
    app.run(host='0.0.0.0', port=5000, debug=True)
