import battlefy_data
from datetime import datetime


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
        teams.append(data['teams'][team_id]['name'])
    teams.sort()
    for team_name in teams:
        teams_ordered += '* [[' + team_name.replace('|', '-') + ']]\n'

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


def main():
    tournament_id = '5ff3354193edb53839d44d55'
    event_data = battlefy_data. BattlefyData(tournament_id)
    event_data.load_tournament_data()

    with open(event_data.tournament_data['name'] + '.wiki', 'w+', newline='\n') as f:
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

        f.write('== Participants ==\n')
        teams = create_team_list(event_data.tournament_data)
        f.write(teams)


if __name__ == '__main__':
    main()
