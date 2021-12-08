import urllib.request
import urllib.parse
import json
import os
import unicodedata
import re
from pathlib import Path

tournament_api = 'https://dtmwra1jsgyb0.cloudfront.net/'


def slugify(value, allow_unicode=False):
    """
    Taken from https://github.com/django/django/blob/master/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_')


class BattlefyData(object):
    def __init__(self, id):
        self.tournament_data = dict()
        self.tournament_id = id
        self.event_directory = Path('./event_data/')

    def load_tournament_data(self):
        try:
            with open(Path.joinpath(self.event_directory, self.tournament_id + '_tournament.json'), 'r') as f:
                self.tournament_data = json.load(f)
        except Exception:
            self.dl_tournament_data()

    def save_tournament_data(self):
        self.event_directory.mkdir(parents=True, exist_ok=True)
        with open(Path.joinpath(self.event_directory, self.tournament_id + '_tournament.json'), 'w') as f:
            json.dump(self.tournament_data, f, indent=4)

    def get_tournament_data_path(self):
        data_path = Path.joinpath(self.event_directory, slugify(self.tournament_data['name']) + '_' + self.tournament_id)
        return data_path

    def dl_tournament_data(self, reduce_teams=True):
        self.tournament_data = dict()
        with urllib.request.urlopen(tournament_api + 'tournaments/' + self.tournament_id
                                    + '?extend%5Bgame%5D=true'
                                    + '&extend%5Borganization%5D%5Bowner%5D=true'
                                    + '&extend%5Bstages%5D%5Bgroups%5D%5Bmatches%5D=true'
                                    + '&extend%5Bstages%5D%5Bmatches%5D=true') as url:
            self.tournament_data = json.loads(url.read().decode())[0]

        self.dl_stage_standings_data()

        # Team data must come after standings in order to reduce
        self.dl_teams_data(reduce_teams)

        self.save_tournament_data()

    def dl_teams_data(self, reduce_teams=True):
        self.tournament_data['teams'] = dict()
        with urllib.request.urlopen(tournament_api + 'tournaments/' + self.tournament_id + '/teams') as url:
            data = json.loads(url.read().decode())

        # modify the list to be a dictionary with ID as the key so the data is easier to access
        for eachElement in data:
            id = eachElement['_id']
            self.tournament_data['teams'][id] = dict()
            del eachElement['_id']
            self.tournament_data['teams'][id] = eachElement

        if reduce_teams:
            self.reduce_teams()

    def reduce_teams(self):
        # Purge teams not on the standings. This can happen if they failed to check-in
        participating_teams = set()
        for stage in self.tournament_data['stages']:
            for standing in stage['standings']:
                participating_teams.add(standing['teamID'])

        purge_teams = (self.tournament_data['teams'].keys() | set()).difference(participating_teams)
        for team_id in purge_teams:
            del self.tournament_data['teams'][team_id]

    def dl_stage_standings_data(self):
        for stage_number, stage_id in enumerate(self.tournament_data['stageIDs']):
            self.tournament_data['stages'][stage_number]['standings'] = list()
            standings = list()
            with urllib.request.urlopen(tournament_api + 'stages/' + stage_id + '/standings') as url:
                standings = json.loads(url.read().decode())
            if not standings:
                with urllib.request.urlopen(tournament_api + 'stages/' + stage_id + '/latest-round-standings') as url:
                    standings = json.loads(url.read().decode())

            self.tournament_data['stages'][stage_number]['standings'] = standings

    def dl_screen_shots(self):
        for stage_number, stage_id in enumerate(self.tournament_data['stageIDs']):
            for match in self.tournament_data['stages'][stage_number]['matches']:
                try:
                    team1 = slugify(self.tournament_data['teams'][match['top']['teamID']]['name'])
                except KeyError:
                    team1 = "unknown"

                try:
                    team2 = slugify(self.tournament_data['teams'][match['bottom']['teamID']]['name'])
                except KeyError:
                    team2 = "unknown"
                
                screenshot_count = 0
                
                if 'screenshots' in match:
                    for submitter in match['screenshots']:
                        for game in match['screenshots'][submitter]:
                            url = match['screenshots'][submitter][game][0]
                            # Add the battelfy filename to the end of the image filename to ensure it's a unique image
                            # This will help determine if a 2nd image has been uploaded to replace an older one.
                            filename = 'stage-' + str(stage_number+1) + '_round-'\
                                       + str(match['roundNumber']) + '_match-'\
                                       + str(match['matchNumber']) + '_' + game + '_'\
                                       + team1 + '_vs_' + team2 + '_'\
                                       + os.path.split(urllib.parse.unquote(urllib.parse.urlparse(url)[2]))[1]

                            directory = Path.joinpath(self.get_tournament_data_path(),
                                                      'stage-' + str(stage_number+1) + '/round-'
                                                      + str(match['roundNumber']))
                            directory.mkdir(parents=True, exist_ok=True)
                            new_image = Path.joinpath(directory, filename)
                            if not new_image.exists():
                                urllib.request.urlretrieve(url, new_image)
                            screenshot_count += 1
                
                if not team1 == 'unknown' and not team2 == 'unknown':
                    # print(str(stage_number+1) + "," + str(match['roundNumber']) + "," + team1 + "," + team2)
                    pass
                if not screenshot_count:
                    # print("MISSING SCREENSHOTS " + "Stage: " + str(stage_number+1) + " Round: " + str(match['roundNumber']) + " " + team1 + " vs " + team2)
                    pass
                elif screenshot_count == 2:
                    # print(str(screenshot_count) + " screenshots for " + "Stage: " + str(
                    #     stage_number + 1) + " Round: " + str(match['roundNumber']) + " " + team1 + " vs " + team2)
                    pass
                else:
                    # print(str(screenshot_count) + " screenshots for " + "Stage: " + str(stage_number+1) + " Round: " + str(match['roundNumber']) + " " + team1 + " vs " + team2)
                    pass

    def dl_team_logos(self):
        for team in self.tournament_data['teams']:
            url = self.tournament_data['teams'][team]['persistentTeam']['logoUrl']
            if url:
                directory = Path.joinpath(self.get_tournament_data_path(), 'team_logos')
                directory.mkdir(parents=True, exist_ok=True)

                extension = os.path.splitext(urllib.parse.urlparse(url)[2])[1]
                team_name = slugify(self.tournament_data['teams'][team]['name'])

                new_image = Path.joinpath(directory, team_name + extension)
                if not new_image.exists():
                    urllib.request.urlretrieve(url, new_image)


def main():

    tournament_id = '5ff3354193edb53839d44d55'
    event_data = BattlefyData(tournament_id)
    event_data.load_tournament_data()
    for team_id in event_data.tournament_data['teams']:
        print(event_data.tournament_data['teams'][team_id]['name'])

    # event_data.dl_screen_shots()


if __name__ == '__main__':
    main()
