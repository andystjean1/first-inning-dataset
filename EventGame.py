import requests
from bs4 import BeautifulSoup

class EventGame(object):
    """
    """
    def __init__(self, id, info, events, home_lineup, away_lineup, ps):
        self.id = id.strip()
        self.info = info
        self.events = events
        self.home_lineup = home_lineup
        self.away_lineup = away_lineup
        self.player_scraper = ps

    ###########################################################################
    ### INFO DICTIONARY WRAPPERS ##############################################
    def visitor(self):
        return self.info["visteam"]

    def home_team(self):
        return self.info["hometeam"]

    def date(self):
        return self.info["date"]

    def temperature(self):
        return self.info["temp"]

    def wind_direction(self):
        return self.info["winddir"]

    def wind_speed(self):
        return self.info["windspeed"]

    #gets the date code from the id
    def date_code(self):
        return self.id[-5:]

    #get the total score for the first inning
    def get_first_inning_total(self):
        print("scraping the first inning total")

        team_id = self.id[:3]
        url_pattern = "https://www.baseball-reference.com/boxes/{}/{}.shtml"
        url = url_pattern.format(team_id, self.id)

        #scrape the first inning score from the boxscore
        resp = requests.get(url)
        soup = BeautifulSoup(resp.content, "html.parser")
        table = soup.find('table', {"class":"linescore nohover stats_table no_freeze"})
        rows = table.find('tbody').find_all('tr')

        first_inning_score = 0
        for r in rows:
            first_inning_score += int(r.find_all('td')[2].text)

        return first_inning_score

    ###########################################################################
    ### DATASET CREATOR #######################################################
    # creates the dictionary that will be used to add data to dataset
    def create_dataset_record(self):
        print("creating dataset record for ", self.id)

        print("getting stats for home team")
        # get the batting stats for the home players
        first_home_batter = self.get_home_batter_stats(1)
        second_home_batter = self.get_home_batter_stats(2)
        third_home_batter = self.get_home_batter_stats(3)

        home_pitcher = self.get_home_pitcher_stats()

        print("getting stats for away team")
        #get the batting stats for the away Players
        first_away_batter = self.get_away_batter_stats(1)
        second_away_batter = self.get_away_batter_stats(2)
        third_away_batter = self.get_away_batter_stats(3)

        away_pitcher = self.get_away_pitcher_stats()

        return {
            "date": self.date(),
            "home_team": self.home_team(),
            "away_team": self.visitor(),
            "temperature": self.temperature(),
            "wind_direction": self.wind_direction(),
            "wind_speed": self.wind_speed(),

            "first_home_ba": first_home_batter["BA"],
            "first_home_obp": first_home_batter["OBP"],
            "first_home_slg": first_home_batter["SLG"],
            "first_home_ops": first_home_batter["OPS"],
            "second_home_ba": second_home_batter["BA"],
            "second_home_obp": second_home_batter["OBP"],
            "second_home_slg": second_home_batter["SLG"],
            "second_home_ops": second_home_batter["OPS"],
            "third_home_ba": third_home_batter["BA"],
            "third_home_obp": third_home_batter["OBP"],
            "third_home_slg": third_home_batter["SLG"],
            "third_home_ops": third_home_batter["OPS"],

            "first_away_ba": first_away_batter["BA"],
            "first_away_obp": first_away_batter["OBP"],
            "first_away_slg": first_away_batter["SLG"],
            "first_away_ops": first_away_batter["OPS"],
            "second_away_ba": second_away_batter["BA"],
            "second_away_obp": second_away_batter["OBP"],
            "second_away_slg": second_away_batter["SLG"],
            "second_away_ops": second_away_batter["OPS"],
            "third_away_ba": third_away_batter["BA"],
            "third_away_obp": third_away_batter["OBP"],
            "third_away_slg": third_away_batter["SLG"],
            "third_away_ops": third_away_batter["OPS"],

            "home_ERA": home_pitcher["ERA"],
            "home_WHIP": home_pitcher["WHIP"],
            "home_FIP": home_pitcher["FIP"],
            "home_KOP": home_pitcher["KO_perc"],
            "home_BBP": home_pitcher["BB_perc"],
            "away_ERA": away_pitcher["ERA"],
            "away_WHIP": away_pitcher["WHIP"],
            "away_FIP": away_pitcher["FIP"],
            "away_KOP": away_pitcher["KO_perc"],
            "away_BBP": away_pitcher["BB_perc"],
            "first_inning_total" : self.get_first_inning_total()
        }

    #get the batting average for the first player in the batting lineup
    def get_home_batter_stats(self, bop):
        player_id = self.home_lineup[bop-1].split(",")[1]
        game_date = self.date_code()
        return self.player_scraper.get_batting_stats(player_id, game_date)

    #get the batting average for the first player in the batting lineup
    def get_away_batter_stats(self, bop):
        player_id = self.away_lineup[bop-1].split(",")[1]
        game_date = self.date_code()
        return self.player_scraper.get_batting_stats(player_id, game_date)

    #get the home pitching stats
    def get_home_pitcher_stats(self):
        #find the pitcher by position in the lineup
        for player in self.home_lineup:
            if(player.split(",")[5] == '1'):
                player_id = player.split(",")[1]

        game_date = self.date_code()
        return self.player_scraper.get_pitching_stats(player_id, game_date)

    #get the away pitching STATS
    def get_away_pitcher_stats(self):

        #find the pitcher by possistion in the lineup
        for player in self.away_lineup:
            if(player.split(",")[5] == '1'):
                player_id = player.split(",")[1]

        game_date = self.date_code()
        return self.player_scraper.get_pitching_stats(player_id, game_date)

    ### DEBUG STUFF ##########################################################
    def display(self):
        print("ID: ", self.id)
        print("INFO: ", self.info)
        print("EVENTS: ", self.events)
        print("HOME PLAYERS: ", self.home_lineup)
        print("AWAY PLAYERS: ", self.away_lineup)
