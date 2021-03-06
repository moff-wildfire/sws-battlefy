import battlefy_data
from datetime import datetime
from operator import itemgetter
from pathlib import Path


def create_sidebar(data):
    sidebar = '{{Liquipedia_Tournament' \
              + '|image1=[[File:Full Color (Circular).png | 200px]]' \
              + '|mode=Fleet Battles' \
              + '|maps=Galitan, Sissubo, Fostar Haven, Esseles, Yavin, Nadiri Dockyards, Zavian Abyss'

    sidebar += ' | prize_pool=' + data['prizes']
    sidebar += ' | start_date=' + datetime.strptime(data['checkInStartTime'],
                                                    '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y/%m/%d')
    sidebar += ' | end_date=' + datetime.strptime(data['lastCompletedMatchAt'],
                                                  '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y/%m/%d')

    team_num = len(data['teams'])

    sidebar += ' | number_of_teams=' + str(team_num)
    sidebar += '}}\n'
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


def create_team_list(data):
    teams_ordered = ''
    teams = list()
    for team_id in data['teams']:
        teams.append((team_id, data['teams'][team_id]['name']))
    teams = sorted(teams, key=itemgetter(1))

    for team in teams:
        teams_table = '{| class="wikitable mw-collapsible mw-collapsed"\n'
        teams_table += '|+ {{nowrap | ' + team[1].replace('|', '-') + ' - '
        teams_table += data['teams'][team[0]]['countryFlag'] + ' }}\n'
        for player in data['teams'][team[0]]['players']:
            teams_table += '|-\n| ' + player['inGameName'] + '\n'
        teams_table += '|}\n'
        teams_ordered += teams_table

    return teams_ordered


def create_swiss_table(standings):
    dropped_style = 'style="color:black; background-color:#ff6961;"'
    dropped_row_label = '|-\n| colspan="8" |\n|-\n| colspan="8" ' + dropped_style + '|Indicates Dropped\n'

    swiss_table = ''
    swiss_header = '{| class="wikitable"\n'
    swiss_header += '! Rank\n'
    swiss_header += '! Team\n'
    swiss_header += '! W\n'
    swiss_header += '! T\n'
    swiss_header += '! L\n'
    swiss_header += '! P\n'
    swiss_header += '! OW%\n'
    swiss_header += '! W%\n'

    for rank, record in enumerate(standings):
        if record['disqualified']:
            swiss_table += '|- ' + dropped_style + '\n'
        else:
            swiss_table += '|-\n'
        swiss_table += '|' + str(rank+1) + '\n'
        swiss_table += '|' + record['team']['name'] + '\n'
        swiss_table += '|' + str(record['wins']) + '\n'
        swiss_table += '|' + str(record['ties']) + '\n'
        swiss_table += '|' + str(record['losses']) + '\n'
        swiss_table += '|' + str(record['points']) + '\n'
        swiss_table += '|' + "{:7.3f}".format(record['opponentsMatchWinPercentage']) + '\n'
        swiss_table += '|' + "{:7.3f}".format(record['gameWinPercentage']) + '\n'

    if swiss_table:
        swiss_table = swiss_header + swiss_table + dropped_row_label + '|}\n'

    return swiss_table


def create_swiss_matches(matches, teams):
    swiss_match_table = ''
    rounds = dict()

    win_style = 'style="color:black; background-color:#DDF4DD;"'

    round_header = '{| class="wikitable"\n'
    round_header += '! colspan="4" | Round '

    for match in matches:
        match_line = '|-\n'

        if match['isBye']:
            match_line += '| ' + win_style + '| '
            match_line += teams[match['top']['teamID']]['name'] + '\n'
            match_line += '| \n| \n|Bye\n'
        else:

            if match['top']['winner']:
                match_line += '| ' + win_style + '| '
                score = "'''" + str(match['top']['score']) + "'''"
            else:
                match_line += '| '
                score = str(match['top']['score'])

            match_line += teams[match['top']['teamID']]['name'] + '\n'
            match_line += '| ' + score + '\n'

            team_name = ''
            if match['bottom']['winner']:
                team_name += '| ' + win_style + '| '
                score = "'''" + str(match['bottom']['score']) + "'''"
            else:
                team_name += '| '
                score = str(match['bottom']['score'])

            team_name += teams[match['bottom']['teamID']]['name'] + '\n'
            match_line += '| ' + score + '\n' + team_name

        try:
            rounds[str(match['roundNumber'])].append(match_line)
        except KeyError:
            rounds[str(match['roundNumber'])] = list()
            rounds[str(match['roundNumber'])].append(match_line)

    for i in range(1, len(rounds)+1):
        swiss_match_table += round_header + str(i) + '\n'
        for match in rounds[str(i)]:
            swiss_match_table += match
        swiss_match_table += '|}\n'

    return swiss_match_table


def create_elim_bracket(stage, teams):
    bracket = '{{#invoke: Team bracket | main\n'
    bracket += '|rounds=' + str(stage['bracket']['roundsCount'])
    # todo figure out how to auto set round byes
    bracket += '|byes=0'
    bracket += '|boldwinner=high|hideomittedscores=1\n'

    # set up team number trackers
    round_team_number = [1] * stage['bracket']['roundsCount']

    for match in stage['matches']:
        bracket += '|RD' + str(match['roundNumber'])
        bracket += '-seed' + str(round_team_number[match['roundNumber']-1])
        try:
            bracket += '=' + str(match['top']['seedNumber'])
        except KeyError:
            pass

        bracket += '|RD' + str(match['roundNumber'])
        bracket += '-team' + str(round_team_number[match['roundNumber']-1]) + '=' + teams[match['top']['teamID']]['name']
        bracket += '|RD' + str(match['roundNumber'])
        bracket += '-score' + str(round_team_number[match['roundNumber']-1]) + '=' + str(match['top']['score'])
        bracket += '\n'

        round_team_number[match['roundNumber']-1] += 1

        bracket += '|RD' + str(match['roundNumber'])
        bracket += '-seed' + str(round_team_number[match['roundNumber']-1])
        try:
            bracket += '=' + str(match['bottom']['seedNumber'])
        except KeyError:
            pass
        bracket += '|RD' + str(match['roundNumber'])
        bracket += '-team' + str(round_team_number[match['roundNumber']-1]) + '=' + teams[match['bottom']['teamID']]['name']
        bracket += '|RD' + str(match['roundNumber'])
        bracket += '-score' + str(round_team_number[match['roundNumber']-1]) + '=' + str(match['bottom']['score'])
        bracket += '\n'

        round_team_number[match['roundNumber'] - 1] += 1

    bracket += '}}\n'

    return bracket


def main():
    tournament_id = '5ff3354193edb53839d44d55'
    event_data = battlefy_data. BattlefyData(tournament_id)
    event_data.load_tournament_data()

    event_path = event_data.get_tournament_data_path()
    event_path.mkdir(parents=True, exist_ok=True)
    filename = Path.joinpath(event_path, event_data.tournament_data['name'] + '.wiki')

    with open(filename, 'w+', newline='\n') as f:
        sidebar = create_sidebar(event_data.tournament_data)
        f.write(sidebar)
        f.write('== Format ==\n')
        event_format = create_event_format(event_data.tournament_data)
        f.write(event_format)
        f.write('== Prize Pool ==\n')
        f.write(event_data.tournament_data['prizes'] + '\n')

        # Todo: figure out how to automate this better between swiss/group
        f.write('== Swiss Stage ==\n')
        f.write('=== Swiss Standings ===\n')
        swiss_table = create_swiss_table(event_data.tournament_data['stages'][0]['standings'])
        f.write(swiss_table)
        f.write('=== Swiss Matches ===\n')
        swiss_matches = create_swiss_matches(event_data.tournament_data['stages'][0]['matches'],
                                             event_data.tournament_data['teams'])
        f.write(swiss_matches)

        f.write('== Single Elimination Tournament ==\n')
        bracket = create_elim_bracket(event_data.tournament_data['stages'][1], event_data.tournament_data['teams'])
        f.write(bracket)

        f.write('== Participants ==\n')
        teams = create_team_list(event_data.tournament_data)
        f.write(teams)


if __name__ == '__main__':
    main()
