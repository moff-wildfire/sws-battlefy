import battlefy_data
import battlefy_wiki_linkings
from datetime import datetime
from operator import itemgetter
from pathlib import Path

import calcup_roster_tracking


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
        '%Y-%m-%d') + '\n'
    try:
        sidebar += '|edate=' + datetime.strptime(data['lastCompletedMatchAt'], '%Y-%m-%dT%H:%M:%S.%fZ').strftime(
            '%Y-%m-%d') + '\n'
    except KeyError:
        sidebar += '|edate=\n'
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


def create_participants(data, bw_players, bw_teams, dynamic=[], sort_place=True):
    header = '{{TeamCardToggleButton}}\n'

    teams_ordered = ''

    # Use prior rounds as a tiebreaker for when multiple teams have the same place at the end
    for stage in data['stages']:
        for place, standing in enumerate(stage['standings']):
            if 'place' in standing:
                if 'place' not in data['teams'][standing['team']['_id']]:
                    data['teams'][standing['team']['_id']]['place'] = len(stage['standings']) + place
                else:
                    data['teams'][standing['team']['_id']]['place'] = \
                        standing['place'] + (1 - 1 / data['teams'][standing['team']['_id']]['place'])
            else:
                data['teams'][standing['team']['_id']]['place'] = len(stage['standings']) + place

    teams = list()
    for team_id in data['teams']:
        if 'place' in data['teams'][team_id]:
            place = data['teams'][team_id]['place']
        else:
            place = 0
        team_info = bw_teams.get_team_info(data['teams'][team_id]['persistentTeamID'], data['teams'][team_id]['name'])
        teams.append((team_id,
                      data['teams'][team_id]['name'],
                      place,
                      data['teams'][team_id]['persistentTeamID'],
                      team_info['name']
                      ))
    if sort_place:
        teams = sorted(teams, key=itemgetter(2, 4, 0))
    else:
        teams = sorted(teams, key=itemgetter(4, 0))

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
        team_info = bw_teams.get_team_info(team[3], team[1])

        teams_table += '|team=' + team_info['name'] + '\n'
        teams_table += '|image=' + team_info['image'] + '\n'
        for idx, player in enumerate(data['teams'][team[0]]['players']):
            player_tag = 'p' + str(idx + 1)
            if player['_id'] in calcup_roster_tracking.eventid_to_missing_userid:
                player['userID'] = calcup_roster_tracking.eventid_to_missing_userid[player['_id']]

            player_info = bw_players.get_player_info(player['userID'], player['inGameName'])

            teams_table += '|' + player_tag + '=' + player_info['name'] \
                           + ' |' + player_tag + 'flag=' + player_info['flag']
            if player_info['link']:
                teams_table += ' |' + player_tag + 'link=' + player_info['link']
            teams_table += '\n'

        # teams_table += '|c= |cflag=\n'
        # teams_table += '|qualifier=\n'
        teams_table += '}}\n'
        teams_ordered += teams_table

    footer = '{{TeamCard columns end}}\n'
    if dynamic:
        footer += '}}\n'
    return header + teams_ordered + footer


def create_swiss_table(stage, bw_teams):
    dropped_style = 'drop'

    swiss_table = '{{SwissTableLeague|rounds=' + str(stage['bracket']['roundsCount']) + '|diff=false\n'
    for i in range(stage['bracket']['teamsCount']):
        swiss_table += '|pbg' + str(i + 1) + '=down'
        if (i + 1) % 8 == 0:
            swiss_table += '\n'
    if '\n' not in swiss_table[-1]:
        swiss_table += '\n'

    for rank, record in enumerate(stage['standings']):
        if record['disqualified']:
            swiss_table += '|bg' + str(rank + 1) + '=' + dropped_style + ''
        else:
            swiss_table += '|bg' + str(rank + 1) + '=down'
        team_info = bw_teams.get_team_info(record['team']['persistentTeamID'], record['team']['name'])
        swiss_table += '|team' + str(rank + 1) + '=' + team_info['teamteamplate']
        swiss_table += '|temp_tie' + str(rank+1) + '=' + "{:7.3f}".format(record['opponentsMatchWinPercentage']) + '\n'

    swiss_table += '}}\n'

    return swiss_table


def create_swiss_matches(matches, teams, bw_teams):
    swiss_match_table = ''
    rounds = dict()

    for match in matches:
        match_line = create_match_maps(match, teams, bw_teams)
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
        swiss_match_table += '{{MatchListStart|width=450px|title=Round ' + str(i) + ' Matches|matchsection=Round ' \
                             + str(i) + '|hide=false}}\n'
        for match in rounds[str(i)]:
            swiss_match_table += match
        swiss_match_table += '{{MatchListEnd}}\n'
    swiss_match_table += '{{box|end}}\n'

    return swiss_match_table


def create_elim_bracket(stage, teams, bw_teams):
    if stage['bracket']['style'] == 'single':
        bracket = '{{' + str(stage['bracket']['teamsCount']) + 'SETeamBracket\n'
    elif stage['bracket']['style'] == 'double':
        bracket = '{{' + str(stage['bracket']['teamsCount']) + 'DETeamBracket\n'
    else:
        print('Unknown stage style: ' + stage['bracket']['style'])
        return

    # todo handle double elimination brackets

    # set up team number trackers
    team_previous_round = dict()

    # set up round-match count trackers
    round_max_win_match_count = [1] * len(stage['bracket']['series'])
    round_max_win_match_count[0] = 0
    round_max_loss_match_count = [1] * len(stage['bracket']['series'])
    round_max_loss_match_count[0] = 0

    # matches = sorted(stage['matches'], key=itemgetter('matchNumber'))
    matches = stage['matches']

    for match in matches:
        # TODO: this will need to get updated for non SE16 templates
        # In DE brackets D means the team dropped down from the previous round
        # In DE brackest W means the team won the previous round
        # So there are rounds where D vs L happen such as R2D1 vs R2W5 and R2D2 vs R2W6
        # Might want to key off match['inConsolationBracket']
        # May also just need to keep track of match['next'] and build up the D and W that way instead
        # Default first round to D and then future bracket type is defined by match['next']
        # Not exactly sure how to address round_team_number, in a 8 team DE the third winners bracket round is
        #   called the 4th round and in a 16 team DE the 4th winners bracket round is called the 6th round
        #   https://liquipedia.net/rainbowsix/Template:4DETeamBracket/doc
        #   https://liquipedia.net/rainbowsix/Template:8DETeamBracket/doc
        #   https://liquipedia.net/rainbowsix/Template:16DETeamBracket/doc

        if match['matchType'] == 'winner':
            round_max_win_match_count[match['roundNumber']] = max(match['matchNumber'],
                                                                  round_max_win_match_count[match['roundNumber']])
        elif match['matchType'] == 'loser':
            round_max_loss_match_count[match['roundNumber']] = max(match['matchNumber'],
                                                                  round_max_loss_match_count[match['roundNumber']])

        if not 'teamID' in match['top']:
            continue

        if match['top']['teamID'] in team_previous_round:
            if team_previous_round[match['top']['teamID']]:
                bracket_type = 'W'
            else:
                bracket_type = 'D'
        else:
            bracket_type = 'D'

        if match['matchType'] == 'winner':
            round_match_offset = -2 * round_max_win_match_count[match['roundNumber'] - 1]
        else:
            round_match_offset = -2 * round_max_loss_match_count[match['roundNumber'] - 1] \
                                 + (round_max_win_match_count[match['roundNumber']]
                                    - round_max_win_match_count[match['roundNumber'] - 1]) * 2

        bracket_indicator = '|R' + str(match['roundNumber']) + bracket_type \
                            + str(match['matchNumber'] * 2 - 1 + round_match_offset)

        if 'teamID' in match['top']:
            team_name = bw_teams.get_team_info(teams[match['top']['teamID']]['persistentTeamID'],
                                               teams[match['top']['teamID']]['name'])['teamteamplate']
            bracket += bracket_indicator + 'team=' + team_name + ' '
        else:
            bracket += bracket_indicator + 'literal=BYE '
        if 'score' in match['top']:
            bracket += bracket_indicator + 'score=' + str(match['top']['score']) + ' '
        if 'winner' in match['top'] and match['top']['winner']:
            bracket += bracket_indicator + 'win=1 '
            team_previous_round[match['top']['teamID']] = True
        else:
            team_previous_round[match['top']['teamID']] = False
        bracket += '\n'

        if 'teamID' in match['bottom']:
            if match['bottom']['teamID'] in team_previous_round:
                if team_previous_round[match['bottom']['teamID']]:
                    bracket_type = 'W'
                else:
                    bracket_type = 'D'
            else:
                bracket_type = 'D'
        else:
            bracket_type = 'D'

        bracket_indicator = '|R' + str(match['roundNumber']) + bracket_type \
                            + str(match['matchNumber'] * 2 + round_match_offset)

        if 'teamID' in match['bottom']:
            team_name = bw_teams.get_team_info(teams[match['bottom']['teamID']]['persistentTeamID'],
                                               teams[match['bottom']['teamID']]['name'])['teamteamplate']
            bracket += bracket_indicator + 'team=' + team_name + ' '
        else:
            bracket += bracket_indicator + 'literal=BYE '
        if 'score' in match['bottom']:
            bracket += bracket_indicator + 'score=' + str(match['bottom']['score']) + ' '
        if 'winner' in match['bottom'] and match['bottom']['winner']:
            bracket += bracket_indicator + 'win=2 '
            team_previous_round[match['bottom']['teamID']] = True
        elif 'teamID' in match['bottom']:
            team_previous_round[match['bottom']['teamID']] = False
        bracket += '\n'

    bracket += '}}\n'

    return bracket


def create_match_maps(match, teams, bw_teams):
    match_line = ''
    if not match['isComplete']:
        return match_line

    match_line = '{{MatchMaps\n'
    match_line += '|date=\n'

    if 'teamID' in match['top']:
        team_top = bw_teams.get_team_info(teams[match['top']['teamID']]['persistentTeamID'],
                                          teams[match['top']['teamID']]['name'])
    elif match['isBye']:
        team_top = bw_teams.get_team_info('0', 'BYE')

    if 'teamID' in match['bottom']:
        team_bot = bw_teams.get_team_info(teams[match['bottom']['teamID']]['persistentTeamID'],
                                          teams[match['bottom']['teamID']]['name'])
    elif match['isBye']:
        team_bot = bw_teams.get_team_info('0', 'BYE')

    match_line += '|team1=' + team_top['teamteamplate']
    match_line += '|team2=' + team_bot['teamteamplate']

    if match['top']['winner']:
        match_line += '|winner=1\n'
    elif match['bottom']['winner']:
        match_line += '|winner=2\n'
    else:
        match_line += '|winner=0\n'

    if match['isBye']:
        match_line += '|walkover=1'
        match_line += '|games1='
        if match['top']['winner']:
            match_line += 'W'
        else:
            match_line += 'FF'
        match_line += '|games2='
        if match['bottom']['winner']:
            match_line += 'W'
        else:
            match_line += 'FF'
    else:
        match_line += '|games1=' + str(match['top']['score'])
        match_line += '|games2=' + str(match['bottom']['score']) + '\n'
    match_line += '|details={{BracketMatchSummary\n'
    match_line += '|date=|finished=true\n'
    match_line += '|twitch= |youtube=\n'
    match_line += '|vod=\n'
    match_line += '}}\n'
    match_line += '}}\n'
    return match_line


def create_round_robin_tables(stage, teams, bw_teams, wiki_name, include_matches=True):
    tables = ''
    for group in stage['groups']:
        tables += '===={{HiddenSort|Group ' + group['name'] + '}}====\n'
        tables += '{{GroupTableLeague|title=Group ' + group['name'] + '|width=450px|show_p=false|date=|ties=true\n'
        tables += '|tournament=' + wiki_name + '\n'
        group_header = ''
        group_table = ''
        for pos, standing_id in enumerate(group['standingIDs']):
            group_header += '|pbg' + str(pos + 1) + '=down'
            for standing in stage['standings']:
                if standing_id == standing['_id']:
                    # if standing['disqualified']:
                    #     has_drop = True

                    team_info = bw_teams.get_team_info(teams[standing['team']['_id']]['persistentTeamID'],
                                                       teams[standing['team']['_id']]['name'])

                    group_table += '|bg' + str(pos + 1) + '=down|team' + str(pos + 1) + "=" \
                                   + team_info['teamteamplate'] + '\n'

        group_header += '|tiebreaker1=series\n'
        tables += group_header
        tables += group_table
        tables += "}}\n"

        if include_matches:
            match_table = '{{MatchListStart|title=Group ' + group['name'] + ' Matches|width=450px|hide=true}}\n'

            for match in group['matches']:
                match_line = create_match_maps(match, teams, bw_teams)
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
    ccs_winter_minor_id = '5ff3354193edb53839d44d55'
    ccs_winter_minor_wiki = 'Calrissian_Cup/Winter/Minor'
    ccs_winter_major_id = '60019f8ebcc5ed46373408a1'
    ccs_winter_major_wiki = 'Calrissian_Cup/Winter/Major'
    ccs_spring_minor_id = '603c00fbfe4fb811b3168f5b'
    ccs_spring_minor_wiki = 'Calrissian_Cup/Spring/Minor'
    ccs_spring_major_id = '6061b764f68d8733c8455fcf'
    ccs_spring_major_wiki = 'Calrissian_Cup/Spring/Major'
    ccs_summer_minor_id = '60b41961d35b1411a7b31d64'
    ccs_summer_minor_wiki = 'Calrissian_Cup/Summer/Minor'
    ccs_summer_major_id = '60dd319012cb9c33c2f63868'
    ccs_summer_major_wiki = 'Calrissian_Cup/Summer/Major'
    ccs_fall_minor_id = ''
    ccs_fall_minor_wiki = 'Calrissian_Cup/Fall/Minor'
    ccs_fall_major_id = ''
    ccs_fall_major_wiki = 'Calrissian_Cup/Fall/Major'


    twin_suns_tourny_id = '60806876938bed74f6edea9e'
    twin_suns_wiki = 'Twin_Suns_Tournament'
    gsl_s1_id = '5ff4b388fd124e11b18e185d'
    gsl_s1_wiki = 'Global_Squadrons_League/2021/Season_1'


    tournament_id = twin_suns_tourny_id
    wiki_name = twin_suns_wiki
    participant_tabs = [
        {'tab_name': 'Top 16',
         'count': 16},
        # {'tab_name': 'Top 32',
        #  'count': 32},
        {'tab_name': 'Other Notable Participants',
         'count': -1},
    ]

    bw_teams = battlefy_wiki_linkings.BattlefyWikiTeamLinkings()
    bw_players = battlefy_wiki_linkings.BattlefyWikiPlayerLinkings()

    event_data = battlefy_data.BattlefyData(tournament_id)
    event_data.load_tournament_data()

    event_path = event_data.get_tournament_data_path()
    event_path.mkdir(parents=True, exist_ok=True)
    filename = Path.joinpath(event_path, event_data.tournament_data['name'] + '.wiki')

    with open(filename, 'w+', newline='\n', encoding='utf-8') as f:
        display = '{{DISPLAYTITLE:' + event_data.tournament_data['name'] + '}}\n'
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
        teams = create_participants(event_data.tournament_data, bw_players, bw_teams,
                                    dynamic=participant_tabs, sort_place=True)
        f.write(teams)

        f.write('==Results==\n')
        for stage in event_data.tournament_data['stages']:
            if stage['bracket']['type'] == 'swiss':
                f.write('===Swiss Stage===\n')
                f.write('====Swiss Standings====\n')
                swiss_table = create_swiss_table(stage, bw_teams)
                f.write(swiss_table)
                f.write('====Swiss Match Results====\n')
                swiss_matches = create_swiss_matches(stage['matches'], event_data.tournament_data['teams'], bw_teams)
                f.write(swiss_matches)
            elif stage['bracket']['type'] == 'elimination':
                f.write('===Playoffs===\n')
                bracket = create_elim_bracket(stage, event_data.tournament_data['teams'], bw_teams)
                f.write(bracket)
            elif stage['bracket']['type'] == 'roundrobin':
                f.write('===' + stage['name'] + '===\n')
                round_robin_tables = create_round_robin_tables(stage, event_data.tournament_data['teams'], bw_teams,
                                                               wiki_name, include_matches=True)
                f.write(round_robin_tables)
            else:
                print('Unsupported bracket type of: ' + stage['bracket']['type'])


if __name__ == '__main__':
    main()
