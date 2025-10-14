import PyPtt
from PyPtt import exceptions
import pytest

# Data for test_get_post_without_condition
# (board, index_or_aid)
test_post_list_ptt1 = [
    ('Python', 1),
    ('Python', '1TJH_XY0'),
]

test_post_list_ptt2 = [
    ('WhoAmI', 1),
]

@pytest.mark.parametrize("board, index_or_aid", test_post_list_ptt1)
def test_get_post_without_condition_ptt1(ptt_bots, board, index_or_aid):
    """Tests getting a post without search conditions on PTT1."""
    ptt_bot = ptt_bots[0] # Assuming ptt_bots[0] is PTT1
    if ptt_bot.host != PyPtt.HOST.PTT1:
        pytest.skip("This test is for PTT1")

    if isinstance(index_or_aid, int):
        post = ptt_bot.get_post(board, index=index_or_aid)
        post_query = ptt_bot.get_post(board, index=index_or_aid, query=True)
    else:
        post = ptt_bot.get_post(board, aid=index_or_aid)
        post_query = ptt_bot.get_post(board, aid=index_or_aid, query=True)

    assert post is not None
    assert isinstance(post, dict)
    assert PyPtt.PostField.author in post
    assert PyPtt.PostField.title in post
    assert PyPtt.PostField.content in post

    assert post_query is not None
    assert isinstance(post_query, dict)
    assert PyPtt.PostField.author in post_query
    assert PyPtt.PostField.title in post_query
    assert PyPtt.PostField.content not in post_query or post_query[PyPtt.PostField.content] is None


@pytest.mark.parametrize("board, index_or_aid", test_post_list_ptt2)
def test_get_post_without_condition_ptt2(ptt_bots, board, index_or_aid):
    """Tests getting a post without search conditions on PTT2."""
    ptt_bot = ptt_bots[1] # Assuming ptt_bots[1] is PTT2
    if ptt_bot.host != PyPtt.HOST.PTT2:
         pytest.skip("This test is for PTT2")

    if isinstance(index_or_aid, int):
        post = ptt_bot.get_post(board, index=index_or_aid)
    else:
        post = ptt_bot.get_post(board, aid=index_or_aid)

    assert post is not None
    assert isinstance(post, dict)
    assert PyPtt.PostField.author in post
    assert PyPtt.PostField.title in post

def test_get_post_from_url_animation_case(ptt_bots):
    """Tests getting a post from a URL (animation control code case)."""
    ptt_bot = ptt_bots[0] # PTT1
    if ptt_bot.host != PyPtt.HOST.PTT1:
        pytest.skip("This test is for PTT1")

    url = 'https://www.ptt.cc/bbs/NCCU09_PSYCH/M.1322976839.A.0E3.html'
    board, aid = ptt_bot.get_aid_from_url(url)

    assert board == 'NCCU09_PSYCH'
    assert aid == '1EsmP73Z'

    post = ptt_bot.get_post(board, aid=aid)

    assert post is not None
    assert isinstance(post, dict)
    assert post[PyPtt.PostField.title] == '[活動] 系上學姐工商講座'


# Data for test_get_post_with_condition
# (board, search_type, condition)
search_list_ptt1 = [
    ('Python', PyPtt.SearchType.KEYWORD, '[公告]'),
    ('ALLPOST', PyPtt.SearchType.KEYWORD, '(Wanted)'),
    ('Wanted', PyPtt.SearchType.KEYWORD, '(本文已被刪除)'),
    ('Gossiping', PyPtt.SearchType.KEYWORD, '普悠瑪'),
]

search_list_ptt2 = [
    ('PttSuggest', PyPtt.SearchType.KEYWORD, '[問題]'),
    ('PttSuggest', PyPtt.SearchType.COMMENT, '10'),
]

@pytest.mark.parametrize("board, search_type, condition", search_list_ptt1)
def test_get_post_with_condition_ptt1(ptt_bots, board, search_type, condition):
    """Tests getting a post with search conditions on PTT1."""
    ptt_bot = ptt_bots[0]
    if ptt_bot.host != PyPtt.HOST.PTT1:
        pytest.skip("This test is for PTT1")

    try:
        index = ptt_bot.get_newest_index(
            PyPtt.NewIndex.BOARD,
            board,
            search_type=search_type,
            search_condition=condition
        )
    except exceptions.NoSearchResult:
        pytest.skip(f"No search result for {condition} in {board}")

    if index == 0:
        pytest.skip(f"No articles found for search in {board}")

    post = ptt_bot.get_post(
        board,
        index=index,
        search_type=search_type,
        search_condition=condition
    )

    assert post is not None
    assert isinstance(post, dict)
    assert 'post_status' in post

@pytest.mark.parametrize("board, search_type, condition", search_list_ptt2)
def test_get_post_with_condition_ptt2(ptt_bots, board, search_type, condition):
    """Tests getting a post with search conditions on PTT2."""
    ptt_bot = ptt_bots[1]
    if ptt_bot.host != PyPtt.HOST.PTT2:
        pytest.skip("This test is for PTT2")

    try:
        index = ptt_bot.get_newest_index(
            PyPtt.NewIndex.BOARD,
            board,
            search_type=search_type,
            search_condition=condition
        )
    except exceptions.NoSearchResult:
        pytest.skip(f"No search result for {condition} in {board}")

    if index == 0:
        pytest.skip(f"No articles found for search in {board}")

    post = ptt_bot.get_post(
        board,
        index=index,
        search_type=search_type,
        search_condition=condition
    )

    assert post is not None
    assert isinstance(post, dict)
    assert 'post_status' in post