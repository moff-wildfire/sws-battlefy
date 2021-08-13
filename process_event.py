import battlefy_data
from operator import itemgetter
from pathlib import Path


def create_team_list(data):
    teams_ordered = 'Team Name, Country, has_logo, # Players, Discord Contact, Captain'
    teams_ordered += ', Player-2, Player-3, Player-4, Player-5, Player-6, Player-7\n'
    teams = list()
    for team_id in data['teams']:
        teams.append((team_id, data['teams'][team_id]['name']))
    teams = sorted(teams, key=itemgetter(1))

    for team in teams:
        team_row = team[1]
        if 'countryFlag' in data['teams'][team[0]]:
            team_row += ', ' + data['teams'][team[0]]['countryFlag']
        else:
            team_row += ', '

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

    # Todo: main should take in arguments
    #    event_id
    #    is_pre_event - used to determine if teams should be reduced to those in the standings
    #    dl_logos
    #    dl_screens
    #    force_battlefy_update - used to pull in a fresh set of data, will be set to true if is_pre_event
    #    generate_team_csv
    #    generate_wiki - really requires reduce_teams to be true, probably should force reduce_teams to run before gen

    ccs_winter_minor_id = '5ff3354193edb53839d44d55'
    ccs_winter_major_id = '60019f8ebcc5ed46373408a1'
    ccs_spring_minor_id = '603c00fbfe4fb811b3168f5b'
    ccs_spring_major_id = '6061b764f68d8733c8455fcf'
    twin_suns_tourny_id = '60806876938bed74f6edea9e'
    gsl_s1_id = '5ff4b388fd124e11b18e185d'
    ccs_summer_minor_id = '60b41961d35b1411a7b31d64'
    ccs_summer_major_id = '60dd319012cb9c33c2f63868'
    ccs_fall_minor_id = ''
    ccs_fall_major_id = ''
    tournament_id = ccs_fall_minor_id
    event_data = battlefy_data. BattlefyData(tournament_id)
    event_data.load_tournament_data()

    # Pull a fresh set of data and don't reduce teams to just those in a non-existent standings list
    event_data.dl_tournament_data(reduce_teams=False)

    # Create Team/Player CSV
    event_path = event_data.get_tournament_data_path()
    event_path.mkdir(parents=True, exist_ok=True)
    filename = Path.joinpath(event_path, event_data.tournament_data['name'] + '_teams-players.csv')

    with open(filename, 'w+', newline='\n') as f:
        teams = create_team_list(event_data.tournament_data)
        f.write(teams)

    event_data.dl_team_logos()

    event_data.dl_screen_shots()


if __name__ == '__main__':
    main()
