import battlefy_data
from operator import itemgetter
from pathlib import Path
import datetime
import io

equivalent_teams_list = list()
equivalent_teams_list.append(["6037adda165e911e7771dc13", "5ff60103984b93119ee08efc"]) # Aces5 - Crimson Wings
equivalent_teams = set(team for same_teams in equivalent_teams_list for team in same_teams)

equivalent_players_list = list()
equivalent_players = set(player for same_players in equivalent_players_list for player in same_players)

eventid_to_missing_userid = dict()
eventid_to_missing_userid['6037ea4fba62671bc0b8a8d9'] = '5ff4b461ffbe666f1fae1ef6'  # DarkKrieg
eventid_to_missing_userid['60380d621f0f9f1d35aa344b'] = '600311d0d9155d46db7f4b02'  # loserkid
eventid_to_missing_userid['6037ea4f3cc6e32afb733736'] = '60364e766e40911bb679b8ff'  # Alaric Kerensky

# TODO: Handle player name changes, such as SSR42 who qualified with 1 name and then changed it


def main():

    ccs_winter_minor_id = '5ff3354193edb53839d44d55'
    ccs_winter_major_id = '60019f8ebcc5ed46373408a1'
    ccs_spring_minor_id = '603c00fbfe4fb811b3168f5b'

    event_list = list()
    event_list.append({
                        'data': battlefy_data.BattlefyData(ccs_winter_minor_id),
                        'qualify_stage': 0,
                        'qualify_number': 16,
                        'finalized': True,
                        'top_teams': dict()
                      })
    event_list.append({
                        'data': battlefy_data.BattlefyData(ccs_winter_major_id),
                        'qualify_stage': 2,
                        'qualify_number': 16,
                        'finalized': True,
                        'top_teams': dict()
                      })
    event_list.append({
                        'data': battlefy_data.BattlefyData(ccs_spring_minor_id),
                        'qualify_stage': 0,
                        'qualify_number': 16,
                        'finalized': True,
                        'top_teams': dict()
                      })

    # create top_teams list for each event
    for event in event_list:
        if event['finalized']:
            event['data'].load_tournament_data()
            for i in range(0, event['qualify_number']):
                team_id = event['data'].tournament_data['stages'][event['qualify_stage']]['standings'][i]['teamID']
                event['top_teams'][team_id] = event['data'].tournament_data['teams'][team_id]
        else:
            event['data'].dl_tournament_data(reduce_teams=False)
            event['top_teams'] = event['data'].tournament_data['teams'].copy()

    top_teams = dict()
    for event in event_list:
        print("------------------------------------------------------------------")
        print("Transfers for", event['data'].tournament_data['name'])
        print("------------------------------------------------------------------")

        event_player_team = dict()
        event_teams = dict()
        if top_teams:
            for team in event['data'].tournament_data['teams']:
                persistent_team_id = event['data'].tournament_data['teams'][team]['persistentTeamID']
                if persistent_team_id in equivalent_teams:
                    for dup_teams in equivalent_teams_list:
                        if persistent_team_id in dup_teams:
                            persistent_team_id = dup_teams[0]
                event_teams[persistent_team_id] = event['data'].tournament_data['teams'][team]

                for player in event['data'].tournament_data['teams'][team]['players']:
                    if 'userID' in player:
                        event_player_team[player['userID']] = persistent_team_id
                    else:
                        if player['_id'] in eventid_to_missing_userid:
                            event_player_team[eventid_to_missing_userid[player['_id']]] = persistent_team_id
                        else:
                            print("Missing userID for:", player['inGameName'], 'on team', event['data'].tournament_data['teams'][team]['name'])

            for top_team in top_teams:
                # Rename top team to match name used in current event
                if top_team in event_teams:
                    top_teams[top_team]['name'] = event_teams[top_team]['name']

                # TODO: Eventually may need to account for a team reset

                print("************************", top_teams[top_team]['name'], "************************")

                persistent_team_id = top_teams[top_team]['persistentTeamID']
                if persistent_team_id in equivalent_teams:
                    for dup_teams in equivalent_teams_list:
                        if persistent_team_id in dup_teams:
                            persistent_team_id = dup_teams[0]

                # Find all players that transferred to a new team
                for i, top_player in reversed(list(enumerate(top_teams[top_team]['players']))):
                    if top_player['userID'] in event_player_team:
                        if event_player_team[top_player['userID']] != persistent_team_id:
                            print("Removing", top_player['inGameName'], "from", top_teams[top_team]['name'],
                                  "as they transferred teams to", event_teams[event_player_team[top_player['userID']]]['name'])
                            del top_teams[top_team]['players'][i]

                # Find all players that joined a team and add them as a freeagent to the top_teams list
                # And purge all players not participating
                if top_team in event_teams:
                    team_list = list()
                    for player in top_teams[top_team]['players']:
                        team_list.append(player['userID'])

                    team_list_not_participating = team_list.copy()
                    for player in event_teams[top_team]['players']:

                        if 'userID' not in player:
                            if player['_id'] in eventid_to_missing_userid:
                                player['userID'] = eventid_to_missing_userid[player['_id']]
                            else:
                                print("Missing userID for:", player['inGameName'], 'on team',
                                      event['data'].tournament_data['teams'][team]['name'])
                                continue

                        if player['userID'] not in team_list:
                            print(player['inGameName'], 'joined', top_teams[top_team]['name'], 'as sub')
                            sub = player.copy()
                            sub['isFreeAgent'] = 'True'
                            top_teams[top_team]['players'].append(sub)
                        else:
                            team_list_not_participating.remove(player['userID'])

                    if team_list_not_participating:
                        for i, top_player in reversed(list(enumerate(top_teams[top_team]['players']))):
                            if top_player['userID'] in team_list_not_participating:
                                print('Removing', top_player['inGameName'], 'from', top_teams[top_team]['name'],
                                      'as they were removed from the roster')
                                del top_teams[top_team]['players'][i]

        # Next check the list of event['top_teams'] for any new teams and add them to top_teams dict
        for team in event['top_teams']:
            persistent_team_id = event['top_teams'][team]['persistentTeamID']

            if persistent_team_id in equivalent_teams:
                for dup_teams in equivalent_teams_list:
                    if persistent_team_id in dup_teams:
                        persistent_team_id = dup_teams[0]

            if persistent_team_id not in top_teams:
                top_teams[persistent_team_id] = event['top_teams'][team].copy()
                # Force free agent to be false
                for idx, player in enumerate(top_teams[persistent_team_id]['players']):
                    top_teams[persistent_team_id]['players'][idx]['isFreeAgent'] = False

    for top_team in top_teams:
        print("************************", top_teams[top_team]['name'], "************************")
        core_count = 0
        for player in top_teams[top_team]['players']:
            if player['isFreeAgent']:
                player_type = "Sub"
            else:
                player_type = "Core"
                core_count += 1
            print(player['inGameName'], player_type)
        print("# Core Team Members: ", str(core_count))
        if core_count < 3:
            print("!!!!!!!!!!!! Invalid # of Core Team Members !!!!!!!!!!!!")

    # # Create Team/Player CSV
    # event_path = event_data.get_tournament_data_path()
    # event_path.mkdir(parents=True, exist_ok=True)
    # filename = Path.joinpath(event_path, event_data.tournament_data['name'] + '_teams-players.csv')
    #
    # with io.open(filename, 'w+', newline='\n', encoding='utf-8') as f:
    #     teams = create_team_list(event_data.tournament_data)
    #     f.write(teams)


if __name__ == '__main__':
    main()
