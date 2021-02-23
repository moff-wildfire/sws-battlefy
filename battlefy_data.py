import urllib.request
import json

tournament_api = 'https://dtmwra1jsgyb0.cloudfront.net/'


class BattlefyData(object):
    def __init__(self, id):
        self.tournament_data = dict()
        self.tournament_id = id

    def load_tournament_data(self):
        try:
            with open(self.tournament_id + '_tournament.json', 'r') as f:
                self.tournament_data = json.load(f)
        except Exception:
            self.dl_tournament_data()

    def save_tournament_data(self):
        with open(self.tournament_id + '_tournament.json', 'w') as f:
            json.dump(self.tournament_data, f, indent=4)

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
            with urllib.request.urlopen(tournament_api + 'stages/' + stage_id + '/latest-round-standings') as url:
                self.tournament_data['stages'][stage_number]['standings'] = json.loads(url.read().decode())

    def dl_screen_shots(self):
        for stage_number, stage_id in enumerate(self.tournament_data['stageIDs']):
            for match in self.tournament_data['stages'][stage_number]['matches']:
                if 'screenshots' in match:
                    for submitter in match['screenshots']:
                        for game in match['screenshots'][submitter]:
                            urllib.request.urlretrieve(match['screenshots'][submitter][game][0],
                                                       'stage-' + str(stage_number+1) + '_round-'
                                                       + str(match['roundNumber']) + '_match-'
                                                       + str(match['matchNumber']) + '_' + game + '.png')


def main():

    tournament_id = '5ff3354193edb53839d44d55'
    event_data = BattlefyData(tournament_id)
    event_data.load_tournament_data()
    for team_id in event_data.tournament_data['teams']:
        print(event_data.tournament_data['teams'][team_id]['name'])

    # event_data.dl_screen_shots()


if __name__ == '__main__':
    main()
