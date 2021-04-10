import battlefy_data
from datetime import datetime
from operator import itemgetter
from pathlib import Path
import os
import csv
import calcup_roster_tracking


def sort_csv(csv_file):
    with open(csv_file, mode='r', encoding='utf-8', newline='') as f, open(csv_file + '_sorted', 'w', encoding='utf-8', newline='') as final:
        writer = csv.writer(final)
        reader = csv.reader(f)
        header = next(reader)
        writer.writerow(header)
        sorted2 = sorted(reader, key=lambda row: (row[1], row[0], row[2]))
        writer.writerows(sorted2)

    os.remove(csv_file)
    os.rename(csv_file + '_sorted', csv_file)


def sanitize_team_name(team_name):
    team_name_fixed = team_name.replace(' | ', ' ').replace('|', ' ')
    team_name_fixed = team_name_fixed.replace('(', '').replace(')', '')
    team_name_fixed = team_name_fixed.replace(' - ', ' ')
    team_name_fixed = team_name_fixed.replace(' : ', ' ').replace(':', ' ')
    team_name_fixed = team_name_fixed.replace('[', '').replace(']', '')
    team_name_fixed = team_name_fixed.replace('  ', ' ')
    return team_name_fixed


def sanitize_player_name(player_name):
    player_name_fixed = player_name.replace('[', '').replace(']', '_')
    player_name_fixed = player_name_fixed.replace('_ ', '_').replace(' _', '_')
    player_name_fixed = player_name_fixed.replace(' <', '_').replace('> ', '_')
    player_name_fixed = player_name_fixed.replace('<', '').replace('>', '')
    player_name_fixed = player_name_fixed.replace(' | ', ' ').replace('|', ' ')
    return player_name_fixed


def create_sidebar(data, wiki_name):
    sidebar = '{{Infobox league' + '\n'
    sidebar += '|liquipediatier=' + '\n'
    sidebar += '|name=' + data['name'] + '\n'
    sidebar += '|shortname=' + data['name'] + '\n'
    sidebar += '|tickername=' + data['name'] + '\n'
    sidebar += '|image=' + '\n'
    sidebar += '|icon=' + '\n'
    sidebar += '|series=' + '\n'
    sidebar += '|organizer=' + data['organization']['name'] + '\n'
    sidebar += '|organizer-link=' + '\n'
    sidebar += '|sponsor=' + '\n'
    sidebar += '|localcurrency=' + '\n'
    sidebar += '|prizepool=' + data['prizes'] + '\n'
    sidebar += '|type=Online' + '\n'
    sidebar += '|platform=' + data['platform'] + '\n'
    sidebar += '|country=' + '\n'
    sidebar += '|format=' + '\n'
    sidebar += '|patch=' + '\n'
    sidebar += '|sdate=' + datetime.strptime(data['checkInStartTime'], '%Y-%m-%dT%H:%M:%S.%fZ').strftime(
        '%Y/%m/%d') + '\n'
    sidebar += '|edate=' + datetime.strptime(data['lastCompletedMatchAt'], '%Y-%m-%dT%H:%M:%S.%fZ').strftime(
        '%Y/%m/%d') + '\n'
    sidebar += '|web=' + '\n'
    sidebar += '|bracket=https://battlefy.com/' + data['organization']['slug'] + '/' + data['slug'] + '/' \
               + data['_id'] + '/bracket-list' + '\n'
    sidebar += '|rulebook=' + '\n'
    sidebar += '|twitter=' + '\n'
    sidebar += '|twitch=' + '\n'
    sidebar += '|instagram=' + '\n'
    sidebar += '|discord=' + '\n'
    sidebar += '|map1=' + '\n'
    sidebar += '|map2=' + '\n'
    sidebar += '|map3=' + '\n'
    sidebar += '|map4=' + '\n'
    sidebar += '|map5=' + '\n'
    sidebar += '|team_number=' + str(len(data['teams'])) + '\n'
    sidebar += '|previous=' + '\n'
    sidebar += '|next=' + '\n'
    sidebar += '}}\n'
    sidebar += '{{Upcoming matches tournament|' + wiki_name + '}}\n'
    return sidebar


def create_event_format(data):
    event_format = ''
    for stage in data['stages']:
        event_format += '* ' + stage['name'] + '\n'
        if stage['bracket']['type'] == "swiss":
            event_format += '** ' + str(stage['bracket']['roundsCount']) + '-round ' + stage['bracket']['type'] + '\n'
        elif stage['bracket']['type'] == "elimination":
            numGames = 0
            rounds = 0
            for match in stage['bracket']['series']:
                if match['numGames'] != numGames:
                    if rounds:
                        event_format += '** ' + str(rounds) + '-round ' \
                                        + stage['bracket']['seriesStyle'] + str(numGames) + '\n'
                    rounds = 1
                    numGames = match['numGames']
                else:
                    rounds += 1
            if rounds:
                event_format += '** ' + str(rounds) + '-round ' \
                                + stage['bracket']['seriesStyle'] + str(numGames) + '\n'

    return event_format


def create_participants(data, battlefy_liquipedia_players, battlefy_liquipedia_teams, dynamic=[]):
    header = '{{TeamCardToggleButton}}\n'

    teams_ordered = ''

    for stage in data['stages']:
        for place, standing in enumerate(stage['standings']):
            if 'place' in standing:
                data['teams'][standing['team']['_id']]['place'] = \
                    standing['place'] + (1 - 1 / data['teams'][standing['team']['_id']]['place'])
            else:
                data['teams'][standing['team']['_id']]['place'] = len(stage['standings']) + place

    teams = list()
    for team_id in data['teams']:
        teams.append((team_id, data['teams'][team_id]['name'], data['teams'][team_id]['place'], data['teams'][team_id]['persistentTeamID']))
    teams = sorted(teams, key=itemgetter(2, 1))

    player_wiki_info = {}
    with open(battlefy_liquipedia_players, 'r+', encoding='utf-8') as f:
        csvReader = csv.DictReader(f)
        for rows in csvReader:
            id = rows['id']
            player_wiki_info[id] = rows
            del player_wiki_info[id]['id']

    team_wiki_info = {}
    with open(battlefy_liquipedia_teams, 'r+', encoding='utf-8') as f:
        csvReader = csv.DictReader(f)
        for rows in csvReader:
            id = rows['id']
            team_wiki_info[id] = rows
            del team_wiki_info[id]['id']

    with open(battlefy_liquipedia_players, 'a+', newline='\n', encoding='utf-8') as blp:
        with open(battlefy_liquipedia_teams, 'a+', newline='\n', encoding='utf-8') as blt:
            dynamic_idx = 0
            if dynamic:
                header += '{{tabs dynamic\n'
                header += '|name' + str(dynamic_idx+1) + '=' + dynamic[dynamic_idx]['tab_name'] + '\n'
                header += '|This=1\n'
                header += '|content' + str(dynamic_idx+1) + '=' + '\n'
                header += '{{TeamCard columns start|cols=5|height=250}}\n'

            for team_num, team in enumerate(teams):
                if dynamic:
                    if team_num == dynamic[dynamic_idx]['count']:
                        teams_ordered += '{{TeamCard columns end}}\n'
                        dynamic_idx += 1
                        teams_ordered += '|name' + str(dynamic_idx + 1) + '=' + dynamic[dynamic_idx]['tab_name'] + '\n'
                        teams_ordered += '|content' + str(dynamic_idx+1) + '=' + '\n'
                        teams_ordered += '{{TeamCard columns start|cols=5|height=250}}\n'
                else:
                    if team_num == 0:
                        teams_ordered += '{{TeamCard columns start|cols=5|height=250}}\n'

                teams_table = '{{TeamCard\n'
                if team[3] in team_wiki_info:
                    team_name_fixed = team_wiki_info[team[3]]['name']
                    team_logo = team_wiki_info[team[3]]['image']
                else:
                    team_name_fixed = sanitize_team_name(team[1])
                    team_logo = ''
                    blt.write(team[3] + ',' + team_name_fixed + ',\n')
                    print("Adding team to Team-Wiki list", team_name_fixed)

                teams_table += '|team=' + team_name_fixed + '\n'
                teams_table += '|image=' + team_logo + '\n'
                for idx, player in enumerate(data['teams'][team[0]]['players']):
                    player_tag = 'p' + str(idx + 1)
                    if player['_id'] in calcup_roster_tracking.eventid_to_missing_userid:
                        player['userID'] = calcup_roster_tracking.eventid_to_missing_userid[player['_id']]

                    if player['userID'] in player_wiki_info:
                        player_name_fixed = player_wiki_info[player['userID']]['name']
                        player_flag = player_wiki_info[player['userID']]['flag']
                        player_link = player_wiki_info[player['userID']]['link']
                    else:
                        player_name_fixed = sanitize_player_name(player['inGameName'])
                        player_flag = ''
                        player_link = ''
                        blp.write(player['userID'] + ',' + player_name_fixed + ',\n')
                        print("Adding player to Player-Wiki list", player_name_fixed)

                    teams_table += '|' + player_tag + '=' + player_name_fixed \
                                   + ' |' + player_tag + 'flag=' + player_flag
                    if player_link:
                        teams_table += ' |' + player_tag + 'link=' + player_link
                    teams_table += '\n'

                # teams_table += '|c= |cflag=\n'
                # teams_table += '|qualifier=\n'
                teams_table += '}}\n'
                teams_ordered += teams_table

    footer = '{{TeamCard columns end}}\n'
    if dynamic:
        footer += '}}\n'
    return header + teams_ordered + footer


def create_swiss_table(stage):
    dropped_style = 'down'

    swiss_table = '{{SwissTableLeague|rounds=' + str(stage['bracket']['roundsCount']) + '|diff=false\n'
    for i in range(stage['bracket']['teamsCount']):
        swiss_table += '|pbg' + str(i + 1) + '='
        if (i + 1) % 8 == 0:
            swiss_table += '\n'
    if '\n' not in swiss_table[-1]:
        swiss_table += '\n'

    for rank, record in enumerate(stage['standings']):
        if record['disqualified']:
            swiss_table += '|bg' + str(rank + 1) + '=' + dropped_style + ''
        else:
            swiss_table += '|bg' + str(rank + 1) + '='
        swiss_table += '|team' + str(rank + 1) + '=' + sanitize_team_name(record['team']['name']) + '\n'

    swiss_table += '}}\n'

    return swiss_table


def create_swiss_matches(matches, teams):
    swiss_match_table = ''
    rounds = dict()

    round_header = ''

    for match in matches:
        match_line = create_match_maps(match, teams)
        if not match_line:
            continue
        try:
            rounds[str(match['roundNumber'])].append(match_line)
        except KeyError:
            rounds[str(match['roundNumber'])] = list()
            rounds[str(match['roundNumber'])].append(match_line)

    for i in range(1, len(rounds) + 1):
        if i == 1:
            swiss_match_table += '{{box|start|padding=2em}}\n'
        else:
            swiss_match_table += '{{box|break|padding=2em}}\n'
        swiss_match_table += '====={{HiddenSort|Round ' + str(i) + '}}=====\n'
        swiss_match_table += '{{MatchListStart|width=400px|title=Round ' + str(i) + ' Matches|matchsection=Round ' \
                             + str(i) + '|hide=false}}\n'
        for match in rounds[str(i)]:
            swiss_match_table += match
        swiss_match_table += '{{MatchListEnd}}\n'
    swiss_match_table += '{{box|end}}\n'

    return swiss_match_table


def create_elim_bracket(stage, teams):
    bracket = '{{#invoke: Team bracket | main\n'
    bracket += '|rounds=' + str(stage['bracket']['roundsCount'])
    # todo figure out how to auto set round byes
    # todo handle double elimination brackets
    bracket += '|byes=0'
    bracket += '|boldwinner=high|hideomittedscores=1\n'

    # set up team number trackers
    round_team_number = [1] * stage['bracket']['roundsCount']

    for match in stage['matches']:
        bracket += '|RD' + str(match['roundNumber'])
        bracket += '-seed' + str(round_team_number[match['roundNumber'] - 1])
        try:
            bracket += '=' + str(match['top']['seedNumber'])
        except KeyError:
            pass

        bracket += '|RD' + str(match['roundNumber'])
        if 'teamID' in match['top']:
            bracket += '-team' + str(round_team_number[match['roundNumber'] - 1]) + '=' + teams[match['top']['teamID']][
                'name']
        else:
            bracket += '-team' + str(round_team_number[match['roundNumber'] - 1]) + '=BYE'
        if 'score' in match['top']:
            bracket += '|RD' + str(match['roundNumber'])
            bracket += '-score' + str(round_team_number[match['roundNumber'] - 1]) + '=' + str(match['top']['score'])
        bracket += '\n'

        round_team_number[match['roundNumber'] - 1] += 1

        bracket += '|RD' + str(match['roundNumber'])
        bracket += '-seed' + str(round_team_number[match['roundNumber'] - 1])
        try:
            bracket += '=' + str(match['bottom']['seedNumber'])
        except KeyError:
            pass
        bracket += '|RD' + str(match['roundNumber'])
        if 'teamID' in match['bottom']:
            bracket += '-team' + str(round_team_number[match['roundNumber'] - 1]) + '=' + \
                       teams[match['bottom']['teamID']]['name']
        else:
            bracket += '-team' + str(round_team_number[match['roundNumber'] - 1]) + '=BYE'
        if 'score' in match['bottom']:
            bracket += '|RD' + str(match['roundNumber'])
            bracket += '-score' + str(round_team_number[match['roundNumber'] - 1]) + '=' + str(match['bottom']['score'])
        bracket += '\n'

        round_team_number[match['roundNumber'] - 1] += 1

    bracket += '}}\n'

    return bracket


def create_match_maps(match, teams):
    match_line = ''
    if match['isBye']:
        return match_line

    match_line = '{{MatchMaps\n'
    match_line += '|date=\n'

    match_line += '|team1=' + sanitize_team_name(teams[match['top']['teamID']]['name'])
    match_line += '|team2=' + sanitize_team_name(teams[match['bottom']['teamID']]['name'])

    if match['top']['winner']:
        match_line += '|winner=1\n'
    elif match['bottom']['winner']:
        match_line += '|winner=2\n'
    else:
        match_line += '|winner=0\n'

    match_line += '|games1=' + str(match['top']['score'])
    match_line += '|games2=' + str(match['bottom']['score']) + '\n'
    match_line += '|details={{BracketMatchSummary\n'
    match_line += '|date=|finished=true\n'
    match_line += '|twitch= |youtube=\n'
    match_line += '|vod=\n'
    match_line += '}}\n'
    match_line += '}}\n'
    return match_line


def create_round_robin_tables(stage, teams):
    tables = ''
    for group in stage['groups']:
        tables += '===={{HiddenSort|Group ' + group['name'] + '}}====\n'
        tables += '{{GroupTableLeague|title=Group' + group['name'] + '|width=450px|show_p=false\n'
        group_header = ''
        group_table = ''
        for pos, standing_id in enumerate(group['standingIDs']):
            group_header += '|pbg' + str(pos + 1) + '=down'
            for standing in stage['standings']:
                if standing_id == standing['_id']:
                    # if standing['disqualified']:
                    #     has_drop = True
                    group_table += '|bg' + str(pos + 1) + '=down|team' + str(pos + 1) + "=" \
                                   + standing['team']['name'] + '\n'

        group_header += '|tiebreaker1=series\n'
        tables += group_header
        tables += group_table
        tables += "}}\n"

        match_table = '{{MatchListStart|title=Group' + group['name'] + ' Matches|width=450px|hide=true}}\n'

        for match in group['matches']:
            match_line = create_match_maps(match, teams)
            match_table += match_line
        tables += match_table
        tables += '{{MatchListEnd}}\n'
        tables += '{{box|break|padding=2em}}\n'

    return tables


def create_prize_pool(prize):
    prize_pool = prize + '\n'
    prize_pool += '{{prize pool start}}\n'
    prize_pool += '{{prize pool slot |place=1 |usdprize=0 |tbd |lastvs1= |lastscore1= |lastvsscore1=}}\n'
    prize_pool += '{{prize pool slot |place=2 |usdprize=0 |tbd |lastvs1= |lastscore1= |lastvsscore1=}}\n'
    prize_pool += '{{prize pool slot |place=3-4 |usdprize=0\n'
    prize_pool += '|tbd |lastvs1= |lastscore1= |lastvsscore1=\n'
    prize_pool += '|tbd |lastvs2= |lastscore2= |lastvsscore2=\n'
    prize_pool += '}}\n'
    prize_pool += '{{prize pool slot |place=5-8 |usdprize=0\n'
    prize_pool += '|tbd |lastvs1= |lastscore1= |lastvsscore1=\n'
    prize_pool += '|tbd |lastvs2= |lastscore2= |lastvsscore2=\n'
    prize_pool += '|tbd |lastvs3= |lastscore3= |lastvsscore3=\n'
    prize_pool += '|tbd |lastvs4= |lastscore4= |lastvsscore4=\n'
    prize_pool += '}}\n'
    prize_pool += '{{Prize pool end}}\n'
    return prize_pool


def main():
    tournament_id = '5ff3354193edb53839d44d55'
    wiki_name = 'Calrissian Cup/Winter/Minor'
    participant_tabs = [
        {'tab_name': 'Top 16',
         'count': 16},
        {'tab_name': 'Top 32',
         'count': 32},
        {'tab_name': 'Other Notable Participants',
         'count': -1},
    ]

    battlefy_liquipedia_players = 'battlefy-liquipedia-players.csv'
    battlefy_liquipedia_teams = 'battlefy-liquipedia-teams.csv'

    event_data = battlefy_data.BattlefyData(tournament_id)
    event_data.load_tournament_data()

    event_path = event_data.get_tournament_data_path()
    event_path.mkdir(parents=True, exist_ok=True)
    filename = Path.joinpath(event_path, event_data.tournament_data['name'] + '.wiki')

    with open(filename, 'w+', newline='\n', encoding='utf-8') as f:
        display = '{{DISPLAYTITLE:' + event_data.tournament_data['name'] + '}}'
        f.write(display)
        sidebar = create_sidebar(event_data.tournament_data, wiki_name)
        f.write(sidebar)
        f.write('==About==\n')
        f.write('===Format===\n')
        event_format = create_event_format(event_data.tournament_data)
        f.write(event_format)
        f.write('===Broadcast Talent===\n')
        f.write('===Prize Pool===\n')
        prize_pool = create_prize_pool(event_data.tournament_data['prizes'])
        f.write(prize_pool)
        f.write('==Participants==\n')
        teams = create_participants(event_data.tournament_data, battlefy_liquipedia_players, battlefy_liquipedia_teams,
                                    dynamic=participant_tabs)
        f.write(teams)

        f.write('==Results==\n')
        for stage in event_data.tournament_data['stages']:
            if stage['bracket']['type'] == 'swiss':
                f.write('===Swiss Stage===\n')
                f.write('====Swiss Standings====\n')
                swiss_table = create_swiss_table(stage)
                f.write(swiss_table)
                f.write('====Swiss Match Results====\n')
                swiss_matches = create_swiss_matches(stage['matches'], event_data.tournament_data['teams'])
                f.write(swiss_matches)
            elif stage['bracket']['type'] == 'elimination':
                f.write('===Playoffs===\n')
                # bracket = create_elim_bracket(stage, event_data.tournament_data['teams'])
                # f.write(bracket)
            elif stage['bracket']['type'] == 'roundrobin':
                f.write('===' + stage['name'] + '===\n')
                round_robin_tables = create_round_robin_tables(stage, event_data.tournament_data['teams'])
                f.write(round_robin_tables)
    sort_csv(battlefy_liquipedia_players)
    sort_csv(battlefy_liquipedia_teams)

if __name__ == '__main__':
    main()
