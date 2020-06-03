Help on module PlayerScraper:

NAME
    PlayerScraper

CLASSES
    builtins.object
        PlayerScraper
    
    class PlayerScraper(builtins.object)
     |  Class used to scrape player data from baseball-reference.com
     |  ...
     |  Attributes
     |  ----------
     |  cahce : Dict[str, DataFrame]
     |  
     |  Methods
     |  -------
     |  scrape_batter_gamelog(player_id)
     |      scrapes the batting log for a player from baseball-reference.com
     |  
     |  scrape_pitcher_gamelog(player_id)
     |      scrapes the pitching log for a pitcher from baseball-reference.com
     |  
     |  get_batting_stats(player_id, game_date)
     |      calculates the players batting stats for the a given game
     |  
     |  get_pitching_stats(player_id, game_date)
     |      calculates the pitching stats for a pitcher given a game
     |  
     |  update_cache(player_id, gamelog)
     |      update the cache with the gamelog and player id
     |  
     |  Methods defined here:
     |  
     |  __init__(self)
     |      Initializes the cache
     |  
     |  get_batting_stats(self, player_id, game_date)
     |      calculates the batting stats for a batter for a given game record
     |      
     |      Parameters
     |      ----------
     |      player_id : str
     |          id of player for batting stats
     |      
     |      game_date : str
     |          a string witht data code for the game
     |      
     |      Returns
     |      ----------
     |      stats: Dict[str, str]
     |          a dictinary with the stat as the key and the statistic as the value
     |  
     |  get_pitching_stats(self, player_id, game_date)
     |      calculates the pitching stats for the pitcher for a given game
     |      
     |      Parameters
     |      ----------
     |      player_id : str
     |          id of player for pitching stats
     |      
     |      game_date : str
     |          a string with data code for the game
     |      
     |      Returns
     |      ----------
     |      stats: Dict[str, str]
     |          a dictinary with the stat as the key and the statistic as the value
     |  
     |  scrape_batter_gamelog(self, player_id:str)
     |      scrapes the batting gamelog for a given batter. will check for the gamelog
     |      is already in the cache.
     |      
     |      Parameters
     |      ---------
     |      player_id : str
     |          id of player for batting log to be scraped
     |  
     |  scrape_pitcher_gamelog(self, player_id:str)
     |      scrapes the pitching gamelog for a given pitcher.  Will check for the gamelog is already in the cache
     |      
     |      Parameters
     |      ---------
     |      player_id : str
     |          id of player for pitching log to be scraped
     |  
     |  update_cache(self, player_id, gamelog)
     |       adds a value to the cache and removes a different value
     |      
     |       Parameters
     |       -----------
     |       player_id : str
     |          the id of the player
     |      gamelog : DataFrame
     |          a dataframe containing the batting/pitching gamelog of a player
     |  
     |  ----------------------------------------------------------------------
     |  Data descriptors defined here:
     |  
     |  __dict__
     |      dictionary for instance variables (if defined)
     |  
     |  __weakref__
     |      list of weak references to the object (if defined)

FUNCTIONS
    calculate_fip(total_HR, total_HBP, total_BB, total_SO, total_IP)
        #caluclate FIP
    
    convert_gamelog_to_dataframe(url, table_id)
        #convert the soup object to a players gamelog dataframe
    
    create_game_dict(game_row)
        #convert the game row html into a dictionary
    
    format_batter_date_code(date)
        #format the game date to match the date code in the game id for a batter
    
    format_pitcher_date_code(date)
        #format the game date to tmatch the date in the game id for a pitcher

DATA
    MONTH_DICT = {'Apr': '04', 'Aug': '08', 'Jul': '07', 'Jun': '06', 'Mar...

FILE
    /Users/homefolder/Documents/Code/Python/retrosheet_data/PlayerScraper.py


