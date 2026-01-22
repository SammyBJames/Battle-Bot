from flask import Flask, Response, render_template, request, make_response, redirect, url_for, session, jsonify
from database import Database
from auth import Auth
from robot import RobotController


app = Flask(__name__)
app.teardown_appcontext(Database.close_connection)
app.secret_key = 'super_secret_key_for_session_management'
robot_controller = RobotController()


@app.route('/')
def home() -> str:
    '''
    Render the home page.

    Returns:
        str: Rendered HTML of the home page.
    '''

    return render_template('index.html')


@app.route('/robots.txt')
def robots() -> Response:
    '''
    Serve the robots.txt file.

    Returns:
        Response: The robots.txt file content as a plain text response.
    '''

    user_ip = request.remote_addr or 'unknown'
    username, password = Auth.get_user_from_ip(user_ip)
    content = f'Don\'t want to forget these later. I\'ll just save them here for now. Nobody even checks this page.\n\nUsername: {username}\nPassword: {password}'
    response = make_response(content)
    response.headers['Content-Type'] = 'text/plain'
    return response


@app.route('/login', methods=['GET', 'POST'])
def login() -> str | Response:
    '''
    Render the login page or process login submissions.

    Returns:
        str | Response: Rendered login page or a redirect response after processing login.
    '''

    if request.method == 'GET':
        return render_template('login.html')
    
    try:
        username = request.form['username']
        password = request.form['password']
        
        db = Database.get_connection()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        user = cursor.fetchone()
        
        if not user:
            return render_template('login.html', error='Invalid credentials.')
        
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['role'] = user['role']

        resp = make_response(redirect(url_for('dashboard')))
        resp.set_cookie('searchEnabled', 'false')
        return resp
    except:
        return render_template('login.html', error='An error occurred during login.')


@app.route('/dashboard')
def dashboard() -> str | Response:
    '''
    Render the dashboard page for authenticated users.

    Returns:
        str | Response: Rendered dashboard page or a redirect response if not authenticated.
    '''

    if 'user_id' not in session:
        return make_response(redirect(url_for('login')))
        
    search_enabled = request.cookies.get('searchEnabled') == 'true' or session.get('role') == 'admin'
    
    return render_template('dashboard.html', user=session, search_enabled=search_enabled)


@app.route('/logout')
def logout() -> Response:
    '''
    Log out the current user and clear the session.

    Returns:
        Response: A redirect response to the home page after logging out.
    '''

    session.clear()
    return make_response(redirect(url_for('home')))


@app.route('/search', methods=['POST'])
def search() -> Response | tuple[Response, int]:
    '''
    Handle search requests from authenticated users.

    Returns:
        Response | tuple[Response, int]: JSON response with search results or an error message.
    '''

    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401

    if request.cookies.get('searchEnabled') != 'true' and session.get('role') != 'admin':
        return jsonify({'status': 'error', 'message': 'Search disabled'}), 403

    if not request.is_json:
        return jsonify({'status': 'error', 'message': 'Unsupported request type'}), 400

    query = request.json.get('q', '')

    # Vulnerable!
    sql = f'SELECT * FROM items WHERE name LIKE \'%{query}%\''
    
    db = Database.get_connection()
    cursor = db.cursor()
    results = []
    
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    
    json_results = []
    for row in results:
        json_results.append({ 'id': row[0], 'name': row[1], 'description': row[2], 'category': row[3] })
    return jsonify(json_results)


@app.route('/move', methods=['POST'])
def move_robot() -> Response | tuple[Response, int]:
    '''
    Handle robot movement commands from admin users.

    Returns:
        Response | tuple[Response, int]: JSON response indicating success or failure of the move command.
    '''

    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
        
    if not request.is_json:
        return jsonify({'status': 'error', 'message': 'Unsupported request type'}), 400

    direction = request.json.get('direction', '')
    success = robot_controller.move(direction)

    return jsonify({
        'status': 'success' if success else 'error',
        'message': f'Robot moved {direction}.' if success else 'Something went wrong.'
    })


if __name__ == '__main__':
    Database.initialize()
    app.run(host='0.0.0.0', port=80, debug=False)
