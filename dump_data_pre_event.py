import battlefy_data
from operator import itemgetter


def create_team_list(data):
    teams_ordered = 'Team Name, Country, has_logo, # Players, Discord Contact, Captain'
    teams_ordered += ', Player-2, Player-3, Player-4, Player-5, Player-6, Player-7\n'
    teams = list()
    for team_id in data['teams']:
        teams.append((team_id, data['teams'][team_id]['name']))
    teams = sorted(teams, key=itemgetter(1))

    for team in teams:
        team_row = team[1]
        team_row += ', ' + data['teams'][team[0]]['countryFlag']

        if data['teams'][team[0]]['persistentTeam']['logoUrl']:
            team_row += ', True'
        else:
            team_row += ', False'

        team_row += ', ' + str(len(data['teams'][team[0]]['players']))
        players = ''
        captain = ', '
        captain_id = ''
        discord = ', '
        if 'captain' in data['teams'][team[0]]:
            captain = ', ' + data['teams'][team[0]]['captain']['inGameName']
            captain_id = data['teams'][team[0]]['captain']['_id']
            
        for player in data['teams'][team[0]]['players']:
            if player['_id'] == captain_id:
                continue
            players += ', ' + player['inGameName']

        for custom_field in data['teams'][team[0]]['customFields']:
            if custom_field['_id'] == '5ff3354193edb53839d44d4d':
                discord = ', ' + custom_field['value']

        team_row += discord + captain + players + '\n'
        teams_ordered += team_row

    return teams_ordered


def main():
    tournament_id = '60019f8ebcc5ed46373408a1'
    event_data = battlefy_data. BattlefyData(tournament_id)
    event_data.load_tournament_data()

    # Pull a fresh set of data and don't reduce teams to just those in a non-existent standings list
    event_data.dl_tournament_data(reduce_teams=False)

    with open(event_data.tournament_data['name'] + '_teams-players.csv', 'w+', newline='\n') as f:
        teams = create_team_list(event_data.tournament_data)
        f.write(teams)

    event_data.dl_team_logos()


if __name__ == '__main__':
    main()
