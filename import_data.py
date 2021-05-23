import mysql.connector
import requests






HEADERS = {
           'X-Auth-Token': 'a0b756c21439434998c8e837793512d5'
           }


BASE_URL = 'http://api.football-data.org/v2'



# iterate competitions





def lookup(rel_url):
    response = requests.get(f"{BASE_URL}{rel_url}", headers=HEADERS)
    if response.status_code != 200:
        print('bad status code')
        print(response.status_code)
        print('url', rel_url)
        return None
    else:
        return response.json()



avail_comps = [2001, 2017, 2021, 2003, 2004, 2015, 2019, 2014]

for c_id in avail_comps:
    print('comp id: ', c_id)

    # populate DB accordingly
    


    # lookup on matches from comp
    matches_dump = lookup(f'/competitions/{c_id}/matches?matchday=1')

    # iterate teams
    if not matches_dump:
        print('poo')
        break
    for match in matches_dump['matches']:
        m_id = match['id']

        match_dump = lookup(f'/matches/{m_id}') 
        
        # populate db accordingly
        

        print('match ID', m_id)
        # iterate players on teams
        for player in match_dump['match']['homeTeam']['lineup']:
            p_id = player['id']
            # Populate DB accordingly
            print('player ID', p_id)
            break
        break
    break


