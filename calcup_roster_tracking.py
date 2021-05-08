import battlefy_data
from operator import itemgetter
from pathlib import Path
import datetime
import io

equivalent_teams_list = list()
equivalent_teams_list.append(["6037adda165e911e7771dc13", "5ff60103984b93119ee08efc"])  # Aces5 - Crimson Wings
equivalent_teams_list.append(["606bd790dc51de7852bfe371", "5ff606e51548ce11847dd936"])  # Krayt Science Team - Fracture
equivalent_teams = set(team for same_teams in equivalent_teams_list for team in same_teams)

equivalent_players_list = list()
equivalent_players_list.append(["608491177230f532c226fb98", "5ff4cc55cfb32f1192b7eed3"])  # DazuTheDevastator
equivalent_players = set(player for same_players in equivalent_players_list for player in same_players)

eventid_to_missing_userid = dict()
eventid_to_missing_userid['6037ea4fba62671bc0b8a8d9'] = '5ff4b461ffbe666f1fae1ef6'  # DarkKrieg
eventid_to_missing_userid['60380d621f0f9f1d35aa344b'] = '600311d0d9155d46db7f4b02'  # loserkid
eventid_to_missing_userid['6037ea4f3cc6e32afb733736'] = '60364e766e40911bb679b8ff'  # Alaric Kerensky
eventid_to_missing_userid['60960d10cf99e72a16a99f8b'] = '60956670938bed74f6ee7e6d' # fr0Zen

# TODO: Eventually may need to account for a team reset


def create_event_team_player_lists(event, player_event_count):
    event_player_team = dict()
    event_player_name = dict()
    event_teams = dict()

    for team in event['data'].tournament_data['teams']:
        persistent_team_id = event['data'].tournament_data['teams'][team]['persistentTeamID']
        if persistent_team_id in equivalent_teams:
            for dup_teams in equivalent_teams_list:
                if persistent_team_id in dup_teams:
                    persistent_team_id = dup_teams[0]
        event_teams[persistent_team_id] = event['data'].tournament_data['teams'][team]

        for player in event['data'].tournament_data['teams'][team]['players']:
            event['total_players'] += 1
            if 'userID' in player:
                event_player_team[player['userID']] = persistent_team_id
                event_player_name[player['userID']] = player['inGameName']
                if player['userID'] not in player_event_count:
                    player_event_count[player['userID']] = 1
                    event['new_players'] += 1
                else:
                    player_event_count[player['userID']] += 1

            else:
                if player['_id'] in eventid_to_missing_userid:
                    event_player_team[eventid_to_missing_userid[player['_id']]] = persistent_team_id
                    if 'userID' not in player_event_count:
                        player_event_count[eventid_to_missing_userid[player['_id']]] = 1
                    else:
                        player_event_count[eventid_to_missing_userid[player['_id']]] += 1
                else:
                    print("Missing userID for:", player['inGameName'], 'on team',
                          event['data'].tournament_data['teams'][team]['name'])
    return event_teams, event_player_team, event_player_name, player_event_count

def main():

    ccs_winter_minor_id = '5ff3354193edb53839d44d55'
    ccs_winter_major_id = '60019f8ebcc5ed46373408a1'
    ccs_spring_minor_id = '603c00fbfe4fb811b3168f5b'
    ccs_spring_major_id = '6061b764f68d8733c8455fcf'
    twin_suns_tourny_id = '60806876938bed74f6edea9e'

    event_list = list()
    event_list.append({
                        'data': battlefy_data.BattlefyData(ccs_winter_minor_id),
                        'qualify_stage': 0,
                        'qualify_number': 16,
                        'finalized': True,
                        'top_teams': dict(),
                        'new_players': 0,
                        'total_players': 0
                      })
    event_list.append({
                        'data': battlefy_data.BattlefyData(ccs_winter_major_id),
                        'qualify_stage': 2,
                        'qualify_number': 16,
                        'finalized': True,
                        'top_teams': dict(),
                        'new_players': 0,
                        'total_players': 0
                      })
    event_list.append({
                        'data': battlefy_data.BattlefyData(ccs_spring_minor_id),
                        'qualify_stage': 0,
                        'qualify_number': 16,
                        'finalized': True,
                        'top_teams': dict(),
                        'new_players': 0,
                        'total_players': 0
                      })
    event_list.append({
                        'data': battlefy_data.BattlefyData(ccs_spring_major_id),
                        'qualify_stage': 0,
                        'qualify_number': 16,
                        'finalized': True,
                        'top_teams': dict(),
                        'new_players': 0,
                        'total_players': 0
                      })
    event_list.append({
                        'data': battlefy_data.BattlefyData(twin_suns_tourny_id),
                        'qualify_stage': 0,
                        'qualify_number': 16,
                        'finalized': False,
                        'top_teams': dict(),
                        'new_players': 0,
                        'total_players': 0
                      })

    player_event_count = dict()

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
        event_player_name = dict()
        event_teams = dict()

        event_teams, event_player_team, event_player_name, player_event_count = \
            create_event_team_player_lists(event, player_event_count)

        for top_team in top_teams:
            old_team_name = top_teams[top_team]['name']
            # Rename top team to match name used in current event
            if top_team in event_teams:
                top_teams[top_team]['name'] = event_teams[top_team]['name']

            print("************************", top_teams[top_team]['name'], "************************")

            if old_team_name != top_teams[top_team]['name']:
                print("Team changed name from",
                      old_team_name, "to",
                      top_teams[top_team]['name'])

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
                              "as they transferred teams to",
                              event_teams[event_player_team[top_player['userID']]]['name'])
                        del top_teams[top_team]['players'][i]
                    else:
                        if top_teams[top_team]['players'][i]['inGameName'] != event_player_name[
                                                                                    top_player['userID']]:
                            print("Player changed in game name from",
                                  top_teams[top_team]['players'][i]['inGameName'], "to",
                                  event_player_name[top_player['userID']])
                            # Fix name
                            top_teams[top_team]['players'][i]['inGameName'] = \
                                event_player_name[top_player['userID']]

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

    print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
    print("Rostered in 1 event: ", str(sum(map((1).__eq__, player_event_count.values()))))
    print("Rostered in 2 events: ", str(sum(map((2).__eq__, player_event_count.values()))))
    print("Rostered in 3 events: ", str(sum(map((3).__eq__, player_event_count.values()))))
    print("Rostered in 4 events: ", str(sum(map((4).__eq__, player_event_count.values()))))
    print("Rostered in 5 events: ", str(sum(map((5).__eq__, player_event_count.values()))))
    print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
    for event in event_list:
        print(event['data'].tournament_data['name'], "had", str(event['total_players']), "players on",
              str(len(event['data'].tournament_data['teams'])), "teams with", str(event['new_players']),
              "new rostered players")


if __name__ == '__main__':
    main()
