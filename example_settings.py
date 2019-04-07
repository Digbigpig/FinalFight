# Fill out the variables and rename file to settings.py

PREFIX = ""
DESCRIPTION = """
Discord bot 
"""
EXTENSIONS = [
    'cogs.event',
    'cogs.common',
    'cogs.death_match'
]

KEY = ''
BROADCAST_ID = ''
OWNER_ID = int

DB_PASS = ''
DB_USER = ''
DB_NAME = ''
DB_ENDPOINT = ''

emojis = {'right': {0: 'HPGREENRIGHT', 1: 'HPHURTRIGHT1', 2: 'HPHURTRIGHT2', 3: 'HPHURTRIGHT3', 4: 'HPREDRIGHT'},
          'mid': {0: 'HPGREENMID', 1: 'HPHURTMID1', 2: 'HPHURTMID2', 3: 'HPHURTMID3', 4: 'HPHURTMID4', 5: 'HPREDMID'},
          'left': {4: 'HPGREENLEFT', 3: 'HPHURTLEFT1', 2: 'HPHURTLEFT2', 1: 'HPHURTLEFT3', 0: 'HPREDLEFT'}}

emoji_server = '376168624983113728'