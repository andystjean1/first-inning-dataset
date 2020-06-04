""" Retrosheet Event File Parser

This scipt will parse retrosheet event files and compile a dataset into a csv file
    - so far the dataset is being used for machine learning and is focused on the first innning
        - Target Columns: score total after the first innning
        - Feature Columns: refer to the variable DF_COLS

    - It will write the csv file somewhere

This script requiries the following libraries to installed
    import requests
    from bs4 import BeautifulSoup, Comment
    from EventGame import EventGame
    from PlayerScraper import PlayerScraper
    import pandas as pd
    from os import listdir

EventGame and PlayerScraper are two custom libraries that I need to figure out
how to package or whatever.
"""
import requests
from bs4 import BeautifulSoup, Comment
from EventGame import EventGame
from PlayerScraper import PlayerScraper
import pandas as pd
from os import listdir

DF_COLS = ['date', 'home_team', 'away_team', 'temperature', 'wind_direction',
   'wind_speed', 'first_home_ba', 'first_home_obp', 'first_home_slg',
   'first_home_ops', 'second_home_ba', 'second_home_obp',
   'second_home_slg', 'second_home_ops', 'third_home_ba', 'third_home_obp',
   'third_home_slg', 'third_home_ops', 'first_away_ba', 'first_away_obp',
   'first_away_slg', 'first_away_ops', 'second_away_ba', 'second_away_obp',
   'second_away_slg', 'second_away_ops', 'third_away_ba', 'third_away_obp',
   'third_away_slg', 'third_away_ops', 'home_ERA', 'home_WHIP', 'home_FIP',
   'home_KOP', 'home_BBP', 'away_ERA', 'away_WHIP', 'away_FIP', 'away_KOP',
   'away_BBP', 'first_inning_total']

PLAYER_SCRAPER = PlayerScraper()

# chunks the games from a retrosheet event file
# datafile - the event file to chunk up
# returns the list of string lists (the game)
def chunk_games(datafile:str):
    """ Parses a retrosheet event file into a list of EventGame objects

    Parameters
    ----------
    datafile : str
        The retrosheet eventfile to parse

    Returns
    ----------
    games
        a list of EventGames that represent the retrosheet file
    """
    #open the file
    with open(datafile) as file:
        lines = file.readlines()
        prev_start = 0
        start = 0
        games = []

        #chunk up the games from the file - skip the first row
        for i in range(len(lines[1:])):
            line = lines[i+1] #add one to fit the offset

            if(line.startswith("id")):
                end = i + 1

                #add the game chunk to the list
                game_chunk = lines[start: end]
                game = process_game_chunk(game_chunk)
                games.append(game)

                #update the starting index for the game chunk
                prev_start = start
                start = end

        #add the last game
        last_game = lines[start:]
        print("the last game ", lines[start])
        games.append(process_game_chunk(last_game))

    return games

# process the game chunk into an event game object
def process_game_chunk(game_chunk):
    """ Process a game chunk from a retroseet file

    Parameters
    ----------
    game_chunk : list of strings
        a chunk from the the retrosheet file that contains information about a baseball game

    Returns
    -------
        a new EventGame object with the information from the game_chunk
    """
    game_id = get_game_id(game_chunk)
    print("processing chunk ", game_id, " ...")
    info_dict = make_info_dict(game_chunk)
    game_events = get_game_events(game_chunk)

    roster_html = get_roster_html(game_id)

    home_lineup = get_lineup(game_chunk, roster_html, '1')
    away_lineup = get_lineup(game_chunk, roster_html, '0')

    return EventGame(game_id, info_dict, game_events, home_lineup, away_lineup, PLAYER_SCRAPER)

################################################################################
### DATA PARSERS FOR A GAME CHUNK ##############################################
#get the game id from a game chunk
def get_game_id(game_chunk):
    """ Parses the game_id from a game_chunk
    """
    id_row = game_chunk[0]
    return id_row.split(",")[1].strip()

#make the info dictinary from the game chunk
def make_info_dict(game_chunk):
    """ Parses the information data from a game_chunk
    """
    info_dict = {}
    info_rows = [x for x in game_chunk if x.startswith("info")]

    for row in info_rows:
        key = row.split(",")[1]
        value = row.split(",")[2]

        info_dict[key] = value.strip()

    return info_dict

#get the events for  a game chunk
def get_game_events(game_chunk):
    """Parses the events of a game from a game_chunk
    """
    return [x.strip() for x in game_chunk if x.startswith("play") or x.startswith("com") or x.startswith("sub")]

################################################################################
### BASEBALL-REFERENCE DATA PARSERS ############################################

#get html for the starting lineups
def get_roster_html(game_id:str):
    """scrapes the starting lineups of a game from baseball-reference.com

    Parameters
    ----------
    game_id : str
        the id of the game

    Returns
    -------
        a BeautifulSoup object containing the html of the starting lineup
    """
    #get the team abv from the game id
    team_abv = game_id[:3]

    #format the url
    url_pattern = "https://www.baseball-reference.com/boxes/{}/{}.shtml"
    url = url_pattern.format(team_abv, game_id.strip())

    #get all the comments
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'lxml')
    comments = soup.findAll(text=lambda text:isinstance(text, Comment))

    #find the lineup index
    lineup_idx = 0
    for i in range(len(comments)):
        if("div_lineups" in comments[i].string):
            lineup_idx = i

    lineups_html = comments[lineup_idx] #MAKE SURE THIS NUMBER IS THE SAME - MAKE IT NOT MAGIC

    return BeautifulSoup(lineups_html, 'lxml')

# get the line for the team
# game_chunk - game_chunk from retrosheet file
# roster_html - roster html from baseball-reference.com
# location - pass in 0 for the away team - pass in 1 for the home team
def get_lineup(game_chunk, roster_html, location):
    """Parses the lineups for a team from a game_chunk and swaps the retrosheet
        player_id with the baseball-reference.com id

      Parameters
      ---------
      game_chunk : [str]
        a list of strings representing a a retrosheet game

      roster_html : BeautifulSoup
        a BeautifulSoup object with the starting lineup html from baseball-reference.com

      location : str
        either a 1 or 0 indicates the home or the away team
    """
    lineup = []

    #find the lineup for the home or away team
    lineup_html = roster_html.find(id="lineups_1").find_all("a")
    if(location == '1'):
        lineup_html = roster_html.find(id="lineups_2").find_all("a")

    #pull the players from the game chunk
    starters = [x for x in game_chunk if x.startswith("start") and x.split(",")[3] == location]

    #combine the lineup with in from baseball-refernce
    for player, starter in zip(lineup_html, starters):
        #get the baseball_ref_id
        baseball_ref_id = player["href"].split("/")[3].split(".")[0]

        #special processing for CC Sabathia
        if(baseball_ref_id == "sabatc"):
            baseball_ref_id = "sabatc.01"

        #break up the starter list and swap in the baseball_ref_id
        starter_lst = starter.split(",")
        starter_lst[1] = baseball_ref_id

        #add the new info to the lineup
        lineup.append(",".join(starter_lst).strip())

    return lineup


#scrape_all the filess
def scrape_all_files():
    """  Convert all the event files in ./data/event_data and create a csv table
         of the first innning data
    """
    csv_dirpath = "./data/csv_data/"
    dir_path = "./data/event_data/"
    filenames = listdir(dir_path)

    #get all the event files
    for file in filenames:
        event_df = pd.DataFrame(columns=DF_COLS)
        print("adding file ", file, " ...")
        filepath = dir_path + file
        games = chunk_games(filepath)

        print("chunked games, adding to dataframe...")

        #add the record for each game to the row
        for game in games:
            record = game.create_dataset_record()
            print("adding record for game ", game.id)
            event_df = event_df.append(record, ignore_index=True)
            print('-'*50)

        #write the team frame to a csv file
        csv_filename = file.split(".")[0] + ".csv"
        csv_filepath = csv_dirpath + csv_filename

        print("writing ", event_df.shape[0], " rows to file ", csv_filepath)

        event_df.to_csv(csv_filepath, index=False)

################################################################################
### MAIN #######################################################################
if __name__ == "__main__":

    TEST = False

    if(TEST):
        csv_dirpath = "./data/csv_data/"
        filepath = "./data/event_data/2019BOS.EVA"
        testfile = "./data/test_data.txt"

        event_df = pd.DataFrame(columns=DF_COLS)

        games = chunk_games(filepath)
        print("chunked games, adding to dataframe...")

        #add the record for each game to the row
        for game in games:
            record = game.create_dataset_record()
            print("adding record for game ", game.id)
            event_df = event_df.append(record, ignore_index=True)
            print('-'*50)

        #write the team frame to a csv file
        csv_filename = "2019BOS.csv"
        csv_filepath = csv_dirpath + csv_filename

        print("writing ", event_df.shape[0], "rows to the file ", csv_filename)
        event_df.to_csv(csv_filepath, index=False)
        print(event_df.info())

    else:
        scrape_all_files()
        #filepath = "./data/event_data/2019BOS.EVA"
        #games = chunk_games(filepath)
        #print(games[-1])
