# System constants used across BBE

# General
NUM_OF_SIMS = 1
NUM_OF_COMPETITORS = 5
NUM_OF_EXCHANGES = 3
PRE_RACE_BETTING_PERIOD_LENGTH = 12
IN_PLAY_CUT_OFF_PERIOD = 2
SESSION_SPEED_MULTIPLIER = 5

# Data Store Attributes
RACE_DATA_FILENAME = 'data/race_event_core.csv'

# Message Protocol Numbers
EXCHANGE_UPDATE_MSG_NUM = 1
RACE_UPDATE_MSG_NUM = 2

# Exchange Attributes
MIN_ODDS = 1.1
MAX_ODDS = 20.00

# Print-Outs
TBBE_VERBOSE = False
SIM_VERBOSE = False
EXCHANGE_VERBOSE = False

# Event Attributes
# average horse races are between 5 and 12 (1005 - 2414) furlongs or could go min - max (400 - 4000)
MIN_RACE_LENGTH = 400
MAX_RACE_LENGTH = 4000

MIN_RACE_UNDULATION = 0
MAX_RACE_UNDULATION = 100

MIN_RACE_TEMPERATURE = 0
MAX_RACE_TEMPERATUE = 50
