
import requests
from bs4 import BeautifulSoup
import pandas as pd

MONTH_DICT = {"Mar":'03',"Apr":"04", "May":"05", "Jun":"06", "Jul":"07", "Aug":"08", "Sep":"09", "Oct":"10", "Nov":"11"}

class PlayerScraper(object):
    """
        Class used to scrape player data from baseball-reference.com
        ...
        Attributes
        ----------
        cahce : Dict[str, DataFrame]

        Methods
        -------
        scrape_batter_gamelog(player_id)
            scrapes the batting log for a player from baseball-reference.com

        scrape_pitcher_gamelog(player_id)
            scrapes the pitching log for a pitcher from baseball-reference.com

        get_batting_stats(player_id, game_date)
            calculates the players batting stats for the a given game

        get_pitching_stats(player_id, game_date)
            calculates the pitching stats for a pitcher given a game

        update_cache(player_id, gamelog)
            update the cache with the gamelog and player id
    """
    def __init__(self):
        """
        Initializes the cache
        """
        self.cache = {}

################################################################################
### SCRPAING FUNCTION #########################################################
    # will scrape a batters gamelog for the 2019 season
    # checks if the gamelog is in the cache first
    def scrape_batter_gamelog(self, player_id:str):
        """
        scrape shte batting gamelog for a given batter. will check for the gamelog
        is already in the cache.

        Parameters
        ---------
        player_id : str
            id of player for batting log to be scraped
        """
        try:3
            #check to see if the gamelog is in the cache
            gamelog = self.cache[player_id]
            print("found the bating gamelog in the cache...")

        except KeyError:
            print("batting log not found in cache... scraping batting log")

            #the gamelog wasnt found in the cache and needs to be scraped
            url_pattern = "https://www.baseball-reference.com/players/gl.fcgi?id={}&t=b&year=2019"
            url = url_pattern.format(player_id)
            gamelog = convert_gamelog_to_dataframe(url, "batting_gamelogs")

            gamelog["date_game"] = gamelog.apply(lambda row: format_batter_date_code(row.date_game), axis=1)

            #update the cache
            self.update_cache(player_id, gamelog)

        return gamelog

    # will scrape a pitcher gamelog for 2019 season
    # checks if the gamelog is in cache
    def scrape_pitcher_gamelog(self, player_id:str):
        """
        scrapes the pitching gamelog for a given pitcher.  Will check for the gamelog is already in the cache

        Parameters
        ---------
        player_id : str
            id of player for pitching log to be scraped
        """
        try:
            gamelog = self.cache[player_id]
            print("found the pitching gameling in the cache...")

        except KeyError:
            print("pitching log not found in cache... scraping pitching gamelog")

            url_pattern = "https://www.baseball-reference.com/players/gl.fcgi?id={}&t=p&year=2019"
            url = url_pattern.format(player_id)
            gamelog = convert_gamelog_to_dataframe(url, "pitching_gamelogs")

            gamelog["date_game"] = gamelog.apply(lambda row: format_pitcher_date_code(row.date_game), axis=1)

            self.update_cache(player_id, gamelog)

        return gamelog

################################################################################
### GET PLAYER STATS FUNCTIONS #################################################
    #get the batting stats for
    def get_batting_stats(self, player_id, game_date):
        """
        calculates the batting stats for a batter for a given game record

        Parameters
        ----------
        player_id : str
            id of player for batting stats

        game_date : str
            a string witht data code for the game

        Returns
        ----------
        stats: Dict[str, str]
            a dictinary with the stat as the key and the statistic as the value
        """
        print("getting batting stats for ", player_id)

        gamelog = self.scrape_batter_gamelog(player_id)

        prev_game_idx = gamelog["date_game"].loc[lambda x: x==game_date].index[0] - 1

        #if this causes an error we have to return null
        prev_game_row = gamelog.iloc[prev_game_idx]

        return {"BA":  prev_game_row.batting_avg,
                "OBP": prev_game_row.onbase_perc,
                "SLG": prev_game_row.slugging_perc,
                "OPS": prev_game_row.onbase_plus_slugging
                }

    #get the pitching stats for the palyer_id
    def get_pitching_stats(self, player_id, game_date):
        """
        calculates the pitching stats for the pitcher for a given game

        Parameters
        ----------
        player_id : str
            id of player for pitching stats

        game_date : str
            a string with data code for the game

        Returns
        ----------
        stats: Dict[str, str]
            a dictinary with the stat as the key and the statistic as the value
        """
        print("getting pitching stats for ", player_id)

        gamelog = self.scrape_pitcher_gamelog(player_id)
        game_idx = gamelog["date_game"].loc[lambda x: x==game_date].index[0]

        #error check this here
        prev_game_row = gamelog.iloc[game_idx - 1]

        #get all the previous games for a pitcher
        prev_gamelog = gamelog.iloc[:game_idx].apply(pd.to_numeric, errors="ignore")

        #total some stats that we need for calculations
        total_BB = prev_gamelog["BB"].sum()
        total_HBP = prev_gamelog["HBP"].sum()
        total_H = prev_gamelog["H"].sum()
        total_IP = prev_gamelog["IP"].sum()
        total_HR = prev_gamelog["HR"].sum()
        total_K = prev_gamelog["SO"].sum()
        total_BF = prev_gamelog["batters_faced"].sum()

        #check if the pitcher actual has some experience
        if(total_IP != 0):
            FIP = calculate_fip(total_HR, total_HBP, total_BB, total_K, total_IP)
            WHIP = (total_BB + total_H)/total_IP
        else:
            FIP = -1
            WHIP = -1

        if(total_BF != 0):
            k_perc = total_K/total_BF
            bb_perc = total_BB/total_BF
        else:
            k_perc = -1
            bb_perc = -1

        return { "ERA": prev_game_row.earned_run_avg,
                "FIP": FIP,
                "WHIP": WHIP,
                "KO_perc": k_perc,
                "BB_perc": bb_perc,
        }

################################################################################
### CACHING FUNCTIONS ##########################################################
    # add a new gamelog to the cache
    # manage the size of the cache
    def update_cache(self, player_id, gamelog):
        """
         adds a value to the cache and removes a different value

         Parameters
         -----------
         player_id : str
            the id of the player
        gamelog : DataFrame
            a dataframe containing the batting/pitching gamelog of a player
        """
        print("updating the cache")

        if(len(self.cache) > 30): #the cache is too big and we need to remove an item
            print("Cache size ", len(self.cache), " removing item...")
            print(self.cache.popitem()[0]) #print the player id of the removed item
            self.cache[player_id] = gamelog
        else:
            #add the gamelog to the cache
            self.cache[player_id] = gamelog

################################################################################
# SCRAPING FORMATING HELPERS ##################################################
#convert the soup object to a players gamelog dataframe
def convert_gamelog_to_dataframe(url, table_id):
    response = requests.get(url)
    #check the status code of the response
    soup = BeautifulSoup(response.content, 'lxml')
    #find the table
    table = soup.find(id=table_id)
    print(table_id, url)

    #get the table headers and set them as columns
    header = table.find('thead').find_all('tr')[0]
    columns = [c["data-stat"] for c in header.find_all('th') if c['data-stat'] != 'x']
    dataframe = pd.DataFrame(columns=columns)

    #get the table rows
    body = table.find('tbody')
    games = [r for r in body.find_all('tr') if r.has_attr('id')]

    #build each row into a dictionary and add to the dataframe
    for g in games:
        game_dict = create_game_dict(g)
        dataframe = dataframe.append(game_dict, ignore_index=True)

    return dataframe

#convert the game row html into a dictionary
def create_game_dict(game_row):
    game_dict = {}

    for td in game_row.find_all('td'):
        key = td['data-stat']
        value = td.text

        game_dict[key] = value

    return game_dict

#format the game date to match the date code in the game id for a batter
def format_batter_date_code(date):
    date_lst = date.split(" ")
    try:
        month = MONTH_DICT[date_lst[0]]
        day = date_lst[1]
        game_no = '0'

        if(len(day) == 1):
            day = '0'+day

        if(len(date_lst) == 3):
            game_no = date_lst[2][1] #grab the number inbetween the parantheses

        date_code =  "".join([month, day, game_no])

    except KeyError:
        print(date_lst, print(date.split("\xa0")))
        return -1

    return date_code


#format the game date to tmatch the date in the game id for a pitcher
def format_pitcher_date_code(date):
    date_lst = date.split("\xa0")
    try:
        month = MONTH_DICT[date_lst[0]]

        #parse the day and game number
        if(date_lst[1].isdigit()):
            day = date_lst[1]
            game_no = '0'
        else:
            day = date_lst[1].split("(")[0]
            game_no = date_lst[1].split("(")[1][0]

        #add the zero the day if its a single digit
        if(len(day) == 1):
            day = '0'+day
        date_code = "".join([month, day, game_no])
    except KeyError:
        print("Error in formating pitcher date code")
        return -1

    return date_code

#caluclate FIP
def calculate_fip(total_HR, total_HBP, total_BB, total_SO, total_IP) :
    fip_hr = 13 * total_HR
    fip_bb_hbp = 3 * (total_HBP + total_BB)
    fip_k = 2 * total_SO
    fip_denom = fip_hr + fip_bb_hbp - fip_k

    #if the pitcher hasnt pitched return a sentinel value to mark it as a bad row
    if(total_IP == 0):
        return -1

    return (fip_denom/total_IP) + 3.2
