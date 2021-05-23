## Database connection
Ensure that database connections fields in db_utils.py are filled in appropriately

```python
# LOGIN DATABASE
# User only has SELECT, INSERT, UPDATE permissions
LOGIN_HOST = ""
LOGIN_USER = ""
LOGIN_PASSWORD = ""
LOGIN_DATABASE = ""

# PROJECT DATABASE - switch to this after login
PROJECT_HOST = ""
PROJECT_USER = ""
PROJECT_PASSWORD = ""
PROJECT_DATABASE = ""
```

## Running flask app
Since I split the flask up using blueprints, navigate to LeagueLogger's parent directory and run 

```console
export FLASK_APP=LeagueLogger
flask run
```
