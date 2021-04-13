import os
import csv


def sort_csv(csv_file):
    with open(csv_file, mode='r', encoding='utf-8', newline='') as f, open(csv_file + '_sorted', 'w', encoding='utf-8', newline='') as final:
        writer = csv.writer(final)
        reader = csv.reader(f)
        header = next(reader)
        writer.writerow(header)
        sorted2 = sorted(reader, key=lambda row: (row[1], row[0]))
        writer.writerows(sorted2)

    os.remove(csv_file)
    os.rename(csv_file + '_sorted', csv_file)


class BattlefyWikiPlayerLinkings(object):
    def __init__(self):
        self.battlefy_wiki_players = 'battlefy-wiki-players.csv'
        self.player_wiki_info = {}
        self.load_player_wiki_info()

    def load_player_wiki_info(self):
        with open(self.battlefy_wiki_players, 'r+', encoding='utf-8') as f:
            csvReader = csv.DictReader(f)
            for rows in csvReader:
                id = rows['id']
                self.player_wiki_info[id] = rows
                del self.player_wiki_info[id]['id']

    def sanitize_player_name(self, player_user_id, player_name):
        player_name_fixed = player_name.replace('[', '').replace(']', '_')
        player_name_fixed = player_name_fixed.replace('_ ', '_').replace(' _', '_')
        player_name_fixed = player_name_fixed.replace(' <', '_').replace('> ', '_')
        player_name_fixed = player_name_fixed.replace('<', '').replace('>', '')
        player_name_fixed = player_name_fixed.replace(' | ', ' ').replace('|', ' ')

        with open(self.battlefy_wiki_players, 'a+', newline='\n', encoding='utf-8') as bwp:
            bwp.write(player_user_id + ',' + player_name_fixed + ',,\n')
        sort_csv(self.battlefy_wiki_players)
        print("Adding player to Player-Wiki list", player_name_fixed)
        return player_name_fixed

    def get_player_info(self, player_user_id, player_name):
        player_info = {
            'name': '',
            'flag': '',
            'link': ''
        }
        if player_user_id in self.player_wiki_info:
            player_info['name'] = self.player_wiki_info[player_user_id]['name']
            player_info['flag'] = self.player_wiki_info[player_user_id]['flag']
            player_info['link'] = self.player_wiki_info[player_user_id]['link']
        else:
            player_info['name'] = self.sanitize_player_name(player_user_id, player_name)
            self.player_wiki_info[player_user_id] = player_info.copy()
        return player_info


class BattlefyWikiTeamLinkings(object):
    def __init__(self):
        self.battlefy_wiki_teams = 'battlefy-wiki-teams.csv'
        self.team_wiki_info = {}
        self.load_team_wiki_info()

    def load_team_wiki_info(self):
        with open(self.battlefy_wiki_teams, 'r+', encoding='utf-8') as f:
            csvReader = csv.DictReader(f)
            for rows in csvReader:
                id = rows['id']
                self.team_wiki_info[id] = rows
                del self.team_wiki_info[id]['id']

    def sanitize_team_name(self, team_id, team_name):
        team_name_fixed = team_name.replace(' | ', ' ').replace('|', ' ')
        team_name_fixed = team_name_fixed.replace('(', '').replace(')', '')
        team_name_fixed = team_name_fixed.replace(' - ', ' ')
        team_name_fixed = team_name_fixed.replace(' : ', ' ').replace(':', ' ')
        team_name_fixed = team_name_fixed.replace('[', '').replace(']', '')
        team_name_fixed = team_name_fixed.replace('  ', ' ')

        with open(self.battlefy_wiki_teams, 'a+', newline='\n', encoding='utf-8') as bwt:
            bwt.write(team_id + ',' + team_name_fixed + ',\n')
        sort_csv(self.battlefy_wiki_teams)
        print("Adding team to Team-Wiki list", team_name_fixed)
        return team_name_fixed

    def get_team_info(self, team_id, team_name):
        team_info = {
            'name': '',
            'image': ''
        }
        if team_id in self.team_wiki_info:
            team_info['name'] = self.team_wiki_info[team_id]['name']
            team_info['image'] = self.team_wiki_info[team_id]['image']
        else:
            team_info['name'] = self.sanitize_team_name(team_id, team_name)
            self.team_wiki_info[team_id] = team_info.copy()
        return team_info
