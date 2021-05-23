from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import LeagueLogger.db_utils as db_utils
from .utils import upload_file

auth = Blueprint('auth', __name__)

@auth.route('/signin')
def signin():
    db_utils.switch_db_to_login()
    return render_template('signin.html')

@auth.route('/signin', methods=['POST'])
def signin_post():
    username = request.form.get('username')
    password = request.form.get('password')
    #remember = True if request.form.get('remember') else False

    with db_utils.db.cursor() as cursor:
        # NOTE: Which database to query?
        query = """
        SELECT id, email, password, bio, created_at, propic_url
        FROM users 
        WHERE username = %s 
        """
        cursor.execute(query, (username, ))

        # IF QUERY IS FOUND, RETURNS IN FORM [ (id, email, bio, created_at) ]
        results = [_ for _ in cursor]
        print(results)
        if not results or not check_password_hash(results[0][2], password): # if a user is found, we want to redirect back to signup page so user can try again
            flash('Please check your login details and try again.')
            return redirect(url_for('auth.signin')) # if the user doesn't exist or password is wrong, reload the page
        
        session['id'] = results[0][0]
        session['username'] = username
        session['email'] = results[0][1]
        session['bio'] = results[0][3]
        session['created_at'] = results[0][4]
        session['propic_url'] = results[0][5]

        # NOTE: Switch to project database here
    db_utils.switch_db_to_project()
    
    # if the above check passes, then we know the user has the right credentials
    return redirect(url_for('main.index'))

@auth.route('/signup')
def signup():
    return render_template('signup.html')


@auth.route('/signup', methods=['POST'])
def signup_post():
    first_name = request.form.get('firstname')
    last_name = request.form.get('lastname')
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    cpassword = request.form.get('cpassword')
    bio = request.form.get('bio')
    pic = request.files['profile_picture']

    if first_name == "": 
        flash(f'The first name field is required!')
        return redirect(url_for('auth.signup'))
    if last_name == "": 
        flash(f'The last name field is required!')
        return redirect(url_for('auth.signup'))
    if username == "": 
        flash(f'The username field is required!')
        return redirect(url_for('auth.signup'))
    if email == "": 
        flash(f'The email field is required!')
        return redirect(url_for('auth.signup'))
    if password == "": 
        flash(f'The password field is required!')
        return redirect(url_for('auth.signup'))

    if password != cpassword:
        flash(f'Passwords do not match!')
        return redirect(url_for('auth.signup'))

    if not pic:
        flash(f'Please upload a profile picture')
        return redirect(url_for('auth.signup'))


    # upload pic to s3
    uploaded, pic_url = upload_file(pic, 'img'+username)
    if not uploaded:
        flash(f'Please upload a profile picture')
        return redirect(url_for('auth.signup'))
    

    with db_utils.db.cursor() as cursor:
        query = """
        SELECT email, username 
        FROM users 
        WHERE email = %s 
        OR
        username = %s
        """
        cursor.execute(query, (email, username))
        results = [_ for _ in cursor]

        if results: # if a user is found, we want to redirect back to signup page so user can try again
            for (e, u) in results:
                if email == e:
                    flash(f'Account for email address {email} already exists!')
                    break
                elif username == u:
                    flash(f'Account with username {username} already exists!')
                    break

            return redirect(url_for('auth.signup'))
        
        insert_stmt = """
        INSERT INTO users 
        (username, email, first_name, last_name, password, bio, propic_url) 
        VALUES (%s, %s, %s, %s, %s, %s, %s) 
        """
        # create a new user with the form data. Hash the password so the plaintext version isn't saved.
        cursor.execute(
            insert_stmt, 
            (
                username, 
                email, 
                first_name,
                last_name,
                generate_password_hash(password, method='sha256'), 
                bio[:160], # Shorten bio to 160 characters
                pic_url
            )
        )
        db_utils.db.commit()

    flash(f'Account successfully created!')

    return redirect(url_for('auth.signin'))

@auth.route('/logout')
def logout():
    # Pop stored login
    session.pop('username', None)
    session.pop('email', None)
    session.pop('id', None)
    session.pop('created_at', None)
    session.pop('bio', None)
    try:
        session['propic_url'] = results[0][5]
    except:
        print("no profile pic")

    # Switch database back to login database
    db_utils.switch_db_to_login()
    return redirect(url_for('main.index'))
