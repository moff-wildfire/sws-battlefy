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

    team_num = 0
    for team_id in data['teams']:
        if 'checkedInAt' in data['teams'][team_id]:
            team_num += 1

    sidebar += ' | number_of_teams=' + str(team_num)
    sidebar += '}}\n'
    return sidebar


def create_team_list(data):
    teams_ordered = ''
    teams = list()
    for team_id in data['teams']:
        if 'checkedInAt' in data['teams'][team_id]:
            teams.append(data['teams'][team_id]['name'])
    teams.sort()
    for team_name in teams:
        teams_ordered += '* [[' + team_name + ']]\n'

    return teams_ordered


def main():
    tournament_id = '5ff3354193edb53839d44d55'
    event_data = battlefy_data. BattlefyData(tournament_id)
    event_data.load_tournament_data()

    with open(event_data.tournament_data['name'] + '.wiki', 'w+', newline='\n') as f:
        sidebar = create_sidebar(event_data.tournament_data)
        f.write(sidebar)
        f.write('== TEAMS ==\n')
        teams = create_team_list(event_data.tournament_data)
        f.write(teams)


if __name__ == '__main__':
    main()
