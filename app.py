from flask import *
from main import *
from cryptography.fernet import Fernet


app = Flask(__name__)
app.secret_key = "testing"

connection = create_db_connection("localhost", "root", "", "password_manager")
initialize_tables(connection)
cursor = connection.cursor()

@app.route('/')
def index():
    id = session.get('user_id')
    print(id)
    if id:
        query = f"""
        SELECT * FROM password
        WHERE user_id = {id}
        """
        passwords = read_query(connection, query)
        return render_template('index.html', passwords = passwords)
    return render_template('start.html')


# Login an Existing User to the database

## CHANGE APP ROUTE SO THAT SIGN UP AND LOGIN ARE ALL TOGETHER
## TWO FORMS IN ONE PAGE
@app.route('/login', methods = ["GET", "POST"])
def retrieve_login():
    if request.method == 'POST':
        username = request.form['username']
        password = hash(request.form['password'])

        try:
            id = login(connection, username, password)
            if id:
                session['user_id'] = id
                print(id)
                return redirect(url_for('index'))
            else:
                flash('Incorrect Username or Password. Please try again!', 'failure')
        except Error as err:
            flash(f'Error: {err}', 'error')

    return render_template('start.html')

# Adding a new user to the database
@app.route('/signup', methods = ["GET", "POST"])
def retrieve_signup():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = hash(request.form['password'])

        try:
            id = signup(connection, email, username, password)
            if id:
                session['user_id'] = id
                return redirect(url_for('index'))
            else:
                flash('Please try again', 'failure')
        except Error as err:
            flash(f'Error: {err}', 'error')
    return render_template('start.html')

@app.route('/add_password', methods = ["GET", "POST"])
def retrieve_new_password():
    if request.method == 'POST':
        website = request.form['website']
        username = request.form['username']
        password = request.form['new_password']
        confirm = request.form['new_confirm']
        # key = Fernet.generate_key()
        # f = Fernet(key)
        # password = f.encrypt(request.form['password'].encode())
        if password == confirm:
            print(website, username, password, session.get('user_id'))
            add_password(connection, session.get('user_id'), website, username, password)
    return redirect(url_for('index'))
        
@app.route('/logout', methods = ["GET", "POST"])
def logout():
    session['user_id'] = None
    print(session.get('user_id'))
    return redirect(url_for('index'))

@app.route('/edit', methods = ["GET", "POST"])
def edit():
    if request.method == 'POST':
        action = request.form['action']
        password_id = request.form['password_id']
        username = request.form['username']
        password = request.form['password']

        if action == "Submit":
            update_query = f"""
            UPDATE password
            SET username = %s, password = %s
            WHERE password_id = %s AND user_id = %s
            """
            cursor.execute(update_query, (username, password, password_id, session.get('user_id')))
            connection.commit()
            print("Updated:", username, password, password_id, session.get('user_id'))
            return redirect(url_for('index'))
        elif action == "Delete":
            del_query = f"""
            DELETE from password
            WHERE password_id = %s
            AND username = %s
            AND password = %s
            AND user_id = %s
            """
            cursor.execute(del_query, (password_id, username, password, session.get('user_id')))
            connection.commit()
            print('Deleted:', password_id, username, password, session.get('user_id'))
            return redirect(url_for('index'))
    return

if __name__ == "__main__":
    app.run(debug = True)