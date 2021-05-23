from flask import Blueprint, render_template, session, redirect, url_for, request, flash
import LeagueLogger.db_utils as db_utils
# from .db_utils import switch_db_to_login, switch_db_to_project
import requests 
from .utils import upload_file

main = Blueprint('main', __name__)

@main.route('/')
def index():
    if "username" in session:
        username = session["username"]
        db_utils.switch_db_to_project()
    else:
        db_utils.switch_db_to_login()
        return redirect(url_for('auth.signin'))
   

    response_raw = requests.get('https://www.scorebat.com/video-api/v1/').json()


    return render_template('index.html',  raw = response_raw[:7])

@main.route('/myteams')
def my_teams_overview():
    if "username" not in session:
        db_utils.switch_db_to_login()
        return redirect(url_for('auth.signin'))
    
    db_utils.switch_db_to_project()

    # GOAL: List user's teams
    # Will have format (dreamID, created_at, name)
    my_teams = []
    with db_utils.db.cursor() as cursor:
        
        query = """
                SELECT dreamID, created_at, name 
                FROM DreamTeam
                WHERE
                dreamID = ANY(
                    SELECT dreamID
                    FROM UserCreatesDreamTeam
                    WHERE userID = %s
                )
                """
        cursor.execute(query, (session["id"], ))
        
        for team in cursor:
            my_teams.append(team)


    #  Replace with my_teams = None to simulate no teams
    
    return render_template('myteams.html', my_teams = my_teams)

@main.route('/myteams/<int:team_id>')
def my_team(team_id):
    if "username" not in session:
        db_utils.switch_db_to_login()
        return redirect(url_for('auth.signin'))

    db_utils.switch_db_to_project()

    # NOTE: team id is already stored from argument in url
    # team_id = str(url.split('/')[4])

    with db_utils.db.cursor() as cursor:
        query = """
        SELECT *
        FROM Player 
        WHERE playerID in (
            SELECT playerID 
            FROM DreamTeamMember 
            WHERE dreamID = %s
        )"""

        cursor.execute(query, (team_id, ))

        results = [_ for _ in cursor]

        query = """
        SELECT name, userID
        FROM DreamTeam
        WHERE dreamID = %s
        """

        cursor.execute(query, (team_id, ))
        
        results2 = [_ for _ in cursor]

        if results2:
            dt_name = results2[0][0]
            team_ownerID = results2[0][1]

            if team_ownerID == session["id"]:
                return render_template('dreamteam.html', team_id=team_id, team_name=dt_name, results=results)
    
    return redirect(url_for('main.my_teams_overview'))

@main.route('/myteams/<int:team_id>', methods=['POST'])
def my_team_remove_player(team_id):
    if "username" not in session:
        db_utils.switch_db_to_login()
        return redirect(url_for('auth.signin'))

    db_utils.switch_db_to_project()

    # Remove player from ID
    with db_utils.db.cursor() as cursor:
        query = """
        SELECT *
        FROM UserCreatesDreamTeam
        WHERE dreamID = %s AND userID = %s
        """

        cursor.execute(query, (team_id, session["id"]))

        results = [_ for _ in cursor]

        # Don't have access to the team!
        if not results:
            return redirect(url_for('main.my_teams_overview'))

        delete_id = int(request.form.get("delete_id"))

        query = """
        DELETE
        FROM DreamTeamMember
        WHERE dreamID = %s and playerID = %s
        """

        cursor.execute(query, (team_id, delete_id))
        db_utils.db.commit()

    return redirect(url_for('main.my_team', team_id=team_id))

@main.route('/players')
def players():
    db_utils.switch_db_to_project()
    if "username" not in session:
        db_utils.switch_db_to_login()
        return redirect(url_for('auth.signin'))
    else:
        with db_utils.db.cursor() as cursor:
            query = """
            SELECT *
            FROM Player 
            """
            cursor.execute(query)
            results = [_ for _ in cursor]

            query = """
            SELECT name, dreamID
            FROM DreamTeam
            WHERE userID = %s
            """
            cursor.execute(query, (session['id'], ))
            results2 = [_ for _ in cursor]

            query = """
            SELECT name
            FROM Game
            """
            cursor.execute(query)
            games = [_ for _ in cursor]

            query = """
            SELECT name
            FROM Team
            """
            cursor.execute(query)
            teams = [_ for _ in cursor]


    return render_template('players.html',results=results, dTeams=results2, games=games, teams=teams)

@main.route('/players', methods=['POST'])
def add_players():
    db_utils.switch_db_to_project()
    if "username" not in session:
        db_utils.switch_db_to_login()
        return redirect(url_for('auth.signin'))
    else:
        if "dreamID" in request.form:
            dreamID = request.form.get("dreamID")
            playerID = request.form.get("playerID")
            with db_utils.db.cursor() as cursor:
                query = """
                INSERT IGNORE INTO DreamTeamMember (dreamID, playerID)
                VALUES (%s, %s);
                """
                cursor.execute(query, (dreamID, playerID))
                db_utils.db.commit()
        
        elif "teamSelect" in request.form:
            teamSelect = request.form.get("teamSelect")
            gameSelect = request.form.get("gameSelect")
            with db_utils.db.cursor(buffered=True) as cursor:
                query = """
                SELECT name, dreamID
                FROM DreamTeam
                WHERE userID = %s
                """
                cursor.execute(query, (session['id'], ))
                results2 = [_ for _ in cursor]


                query = """
                SELECT name
                FROM Game
                """
                cursor.execute(query)
                games = [_ for _ in cursor]


                query = """
                SELECT name
                FROM Team
                """
                cursor.execute(query)
                teams = [_ for _ in cursor]


                cursor.callproc('FilterPlayers', (teamSelect, gameSelect))
                #cursor.execute(query, (teamSelect, gameSelect))

                players = [r.fetchall() for r in cursor.stored_results()][0]

                return render_template('players.html',results=players, dTeams=results2, games=games, teams=teams)
                

    return redirect(url_for('main.players'))

@main.route('/profile')
def profile():
    if "username" in session:
        username = session["username"]
        if "email" in session:
            email = session["email"]
        created = session["created_at"]
        bio = session['bio']
        pic_url = session['propic_url']
        db_utils.switch_db_to_project()
    else:
        db_utils.switch_db_to_login()
        return redirect(url_for('auth.signin'))

    return render_template('profile.html', username=username, email=email, created=created, bio=bio, pic_url=pic_url)

@main.route('/profile', methods=['POST'])
def update_bio():
    if "username" in session:
        db_utils.switch_db_to_login()
        # Switch to login database as that user is the only one who has access to the table
        username = session["username"]
        new_bio = request.form.get("bio_entry")
        with db_utils.db.cursor() as cursor:
            # NOTE: Which database to query?
            query = """
            UPDATE users
            SET bio = %s 
            WHERE username = %s 
            """
            cursor.execute(query, (new_bio, username ))
            db_utils.db.commit()
        session['bio'] = new_bio

        # Switch back to the project database for regular activities
        db_utils.switch_db_to_project()
        return redirect(url_for("main.profile"))
    else:
        db_utils.switch_db_to_login()
        return redirect(url_for('auth.signin'))

@main.route('/update_pic', methods=['POST'])
def update_pic():
    if "username" in session:
        db_utils.switch_db_to_login()
        # Switch to login database as that user is the only one who has access to the table
        username = session["username"]
        pic = request.files['profile_picture']

        uploaded, url = upload_file(pic, 'img'+username)
        if not uploaded:
            flash(f'Picture could not be uploaded at this time')
            return redirect(url_for('main.profile'))

        with db_utils.db.cursor() as cursor:
            # NOTE: Which database to query?
            query = """
            UPDATE users
            SET propic_url = %s 
            WHERE username = %s 
            """
            cursor.execute(query, (url, username))
            db_utils.db.commit()
        session['propic_url'] = url

        # Switch back to the project database for regular activities
        db_utils.switch_db_to_project()
        return redirect(url_for("main.profile"))
    else:
        db_utils.switch_db_to_login()
        return redirect(url_for('auth.signin'))

@main.route('/create_team')
def create_team():
    if "username" not in session:
        db_utils.switch_db_to_login()
        return redirect(url_for('auth.signin'))

    return render_template('createTeam.html')

@main.route('/create_team', methods=['POST'])
def create_team_post():
    db_utils.switch_db_to_project()

    team_name = request.form.get('teamname')

    if team_name == "": 
        flash(f'The team name field is required!')
        return redirect(url_for('main.create_team'))

    if "username" in session:
        userID = session["id"]
    else:
        db_utils.switch_db_to_login()
        return redirect(url_for('auth.signin'))

    with db_utils.db.cursor() as cursor:
        query = """
        SELECT *
        FROM DreamTeam 
        WHERE name = %s AND userID = %s
        """
        cursor.execute(query, (team_name, userID))
        results = [_ for _ in cursor]

        if results: # if a team is found, we want to redirect back to team creation page so user can try again
            flash(f'You already have a dream team named {team_name}!')
            "Already have the dream team!"
            return redirect(url_for('main.create_team'))

        # Stored procedure to insert into both tables
        procedure = "CALL CreateDreamTeam(%s, %s)"
        cursor.execute(procedure, (team_name, userID))
        db_utils.db.commit()

        query = """
        SELECT dreamID
        FROM DreamTeam 
        WHERE name = %s AND userID = %s
        """
        cursor.execute(query, (team_name, userID))
        results = [_ for _ in cursor]

        # Team creation failed
        if not results:
            print("Can't find team")
            return redirect(url_for('main.create_team'))
        
        dreamID = results[0][0]

    return redirect(url_for('main.my_team', team_id=dreamID))




@main.route('/live')
def live():
    if "username" not in session:
        db_utils.switch_db_to_login()
        return redirect(url_for('auth.signin'))


    return render_template('live_scores.html')