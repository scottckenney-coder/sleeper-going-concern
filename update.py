import json, datetime, pathlib, time, urllib.request

LEAGUE_ID = '1397672130383990784'
USERNAME = 'kenneysc'
BASE = 'https://api.sleeper.app/v1'
OUT = pathlib.Path('site')
OUT.mkdir(exist_ok=True)

def get(path):
    url = BASE + path
    last = None
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={'User-Agent':'SleeperPersonalDashboard/1.0'})
            with urllib.request.urlopen(req, timeout=45) as response:
                return json.load(response)
        except Exception as exc:
            last = exc
            time.sleep(2 * (attempt + 1))
    raise RuntimeError(f'Could not retrieve {url}: {last}')

league = get(f'/league/{LEAGUE_ID}')
users = get(f'/league/{LEAGUE_ID}/users')
rosters = get(f'/league/{LEAGUE_ID}/rosters')
state = get('/state/nfl')
user = next((u for u in users if u.get('username','').lower()==USERNAME.lower()), None)
if not user:
    user = get(f'/user/{USERNAME}')
if not user:
    raise RuntimeError('Sleeper username not found')
roster = next((r for r in rosters if r.get('owner_id') == user['user_id'] or user['user_id'] in (r.get('co_owners') or [])), None)
if not roster:
    raise RuntimeError('Team roster not matched to Sleeper user')
players = get('/players/nfl')

def info(pid):
    p = players.get(str(pid), {}) if pid else {}
    return {'id':str(pid), 'name':p.get('full_name') or p.get('search_full_name') or str(pid),
            'position':p.get('position') or '', 'team':p.get('team') or '',
            'status':p.get('injury_status') or p.get('status') or ''}

all_owned = {str(pid) for r in rosters for pid in (r.get('players') or [])}
owned = [info(pid) for pid in (roster.get('players') or [])]
starting = [info(pid) for pid in (roster.get('starters') or []) if pid and pid != '0']
reserves = [info(pid) for pid in (roster.get('reserve') or [])]
taxi = [info(pid) for pid in (roster.get('taxi') or [])]
bench = [p for p in owned if p['id'] not in {q['id'] for q in starting+reserves+taxi}]
# Free agents are not necessarily immediately claimable; league waiver rules still apply.
free_agents = []
for pid, p in players.items():
    if str(pid) in all_owned or not p or p.get('position') not in ('QB','RB','WR','TE','K','DEF'):
        continue
    if not (p.get('team') or p.get('position') == 'DEF'):
        continue
    if p.get('active') is False:
        continue
    free_agents.append(info(pid))
free_agents.sort(key=lambda p:(p['position'],p['name']))
week = state.get('week') or state.get('display_week') or 1
transactions = get(f'/league/{LEAGUE_ID}/transactions/{week}')
my_tx = []
for tx in transactions:
    if roster['roster_id'] not in (tx.get('roster_ids') or []):
        continue
    my_tx.append({'type':tx.get('type'), 'status':tx.get('status'), 'created':tx.get('created'),
                  'adds':[info(pid) for pid,rid in (tx.get('adds') or {}).items() if rid == roster['roster_id']],
                  'drops':[info(pid) for pid,rid in (tx.get('drops') or {}).items() if rid == roster['roster_id']]})

result = {
    'updated_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds'),
    'league':{'id':LEAGUE_ID,'name':league.get('name'),'season':league.get('season'),'roster_positions':league.get('roster_positions'), 'settings':league.get('settings'), 'scoring_settings':league.get('scoring_settings')},
    'team':{'name':(user.get('metadata') or {}).get('team_name') or user.get('display_name'), 'username':USERNAME,
            'roster_id':roster['roster_id'],'settings':roster.get('settings',{}), 'starters':starting,'bench':bench,'reserve':reserves,'taxi':taxi,'all_players':owned},
    'week':week, 'free_agents':free_agents, 'owned_player_ids':sorted(all_owned), 'recent_team_transactions':my_tx,
    'league_teams':[{
      'roster_id':r['roster_id'],
      'owner_id':r.get('owner_id'),
      'name': next(((u.get('metadata') or {}).get('team_name') or u.get('display_name') or u.get('username')) for u in users if u.get('user_id') == r.get('owner_id')), 'Unknown'),
      'record': {'wins':(r.get('settings') or {}).get('wins',0), 'losses':(r.get('settings') or {}).get('losses',0), 'ties':(r.get('settings') or {}).get('ties',0), 'points_for':round((r.get('settings') or {}).get('fpts',0) + (r.get('settings') or {}).get('fpts_decimal',0)/100,2)},
      'waiver_position':(r.get('settings') or {}).get('waiver_position'),
      'players':[info(pid) for pid in (r.get('players') or [])]
    } for r in rosters]
}
(OUT/'data.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(f'Updated roster ID {roster["roster_id"]}: {len(owned)} players; {len(free_agents)} free agents')
