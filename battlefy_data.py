import urllib.request
import json

tournament_api = 'https://dtmwra1jsgyb0.cloudfront.net/'


def main():

    tourny_id = '5ff3354193edb53839d44d55'
    download_screenshots = False

    save_all_data(tourny_id, download_screenshots)


def save_all_data(id, dl_screenshots):
    tourny_data = get_tournament_data(id)
    with open(id + '_tourny.json', 'w') as f:
        json.dump(tourny_data, f, indent=4)

    team_data = get_team_data(id)
    with open(id + '_tourny_teams.json', 'w') as f:
        json.dump(team_data, f, indent=4)

    for stage_number, stage in enumerate(tourny_data['stageIDs']):
        stage_data = get_stage_info(stage)
        with open(id + '_' + str(stage_number) + '_stage_info.json', 'w') as f:
            json.dump(stage_data, f, indent=4)

        standings_data = get_stage_standings(stage)
        with open(id + '_' + str(stage_number) + '_stage_standings.json', 'w') as f:
            json.dump(standings_data, f, indent=4)

        matches_data = get_tournament_stage_matches(stage)
        with open(id + '_' + str(stage_number) + '_stage_matches.json', 'w') as f:
            json.dump(matches_data, f, indent=4)

        if dl_screenshots:
            get_screen_shots(matches_data, stage_number+1)


def get_tournament_data(id):
    with urllib.request.urlopen(tournament_api + 'tournaments/' + id) as url:
        data = json.loads(url.read().decode())
    return data


def get_team_data(id):
    with urllib.request.urlopen(tournament_api + 'tournaments/' + id + '/teams') as url:
        data = json.loads(url.read().decode())
    return data


def get_stage_info(stage):
    with urllib.request.urlopen(tournament_api + 'stages/' + stage) as url:
        data = json.loads(url.read().decode())
    return data


def get_tournament_stage_matches(stage):
    with urllib.request.urlopen(tournament_api + 'stages/' + stage + '/matches') as url:
        data = json.loads(url.read().decode())
    return data


def get_stage_standings(stage):
    with urllib.request.urlopen(tournament_api + 'stages/' + stage + '/latest-round-standings') as url:
        data = json.loads(url.read().decode())
    return data


def get_screen_shots(data, stage_number):
    for item in data:
        if 'screenshots' in item:
            for submitter in item['screenshots']:
                for game in item['screenshots'][submitter]:
                    urllib.request.urlretrieve(item['screenshots'][submitter][game][0], 'stage-' + str(stage_number)
                                               + '_round-' + str(item['roundNumber']) + '_match-'
                                               + str(item['matchNumber']) + '_' + game + '.png')


if __name__ == '__main__':
    main()
