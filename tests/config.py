import os
from dotenv import load_dotenv

load_dotenv()

PTT1_ID = os.environ['PTT1_ID']
PTT1_PW = os.environ['PTT1_PW']

PTT2_ID = os.environ['PTT2_ID']
PTT2_PW = os.environ['PTT2_PW']

TEST_USER = os.environ['TEST_USER']

# Board the bot moderates. Required by tests/test_mark_post.py,
# tests/test_set_board_title.py, tests/test_bucket.py — those tests
# skip themselves when MOD_BOARD is unset.
MOD_BOARD = os.environ.get('MOD_BOARD')