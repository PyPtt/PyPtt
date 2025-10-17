import pytest
import PyPtt
import threading
import time
from PyPtt import Service, PostField
from tests import config # Assuming config.py has PTT1_ID and PTT1_PW

@pytest.fixture(scope="module", autouse=True)
def service_instance():
    pyptt_init_config = {}
    service = Service(pyptt_init_config)
    try:
        # Login using credentials from config.py
        service.call('login', {
            'ptt_id': config.PTT1_ID,
            'ptt_pw': config.PTT1_PW,
            'kick_other_session': True
        })
        yield service
    finally:
        # Ensure logout and close are called
        try:
            service.call('logout')
        except Exception as e:
            print(f"Error during service logout: {e}")
        finally:
            service.close()

def test_service_read_operations_single_thread(service_instance):
    """Tests various read operations via the Service in a single thread."""
    # Test get_time
    result_time = service_instance.call('get_time')
    assert result_time is not None
    assert isinstance(result_time, str) # Assuming get_time returns a string like "HH:MM"

    # Test get_aid_from_url
    url = 'https://www.ptt.cc/bbs/Python/M.1565335521.A.880.html'
    result_aid = service_instance.call('get_aid_from_url', {'url': url})
    assert result_aid is not None

    assert isinstance(result_aid, tuple)
    assert len(result_aid) == 2
    assert result_aid[0] == 'Python'
    assert result_aid[1] == '1TJH_XY0'

    # Test get_newest_index
    result_newest_index = service_instance.call('get_newest_index', {'index_type': PyPtt.NewIndex.BOARD, 'board': 'Python'})
    assert result_newest_index is not None
    assert isinstance(result_newest_index, int)
    assert result_newest_index > 0

    # Test get_post (query mode for speed)
    result_post = service_instance.call('get_post', {
        'board': 'Python',
        'index': 1, # Assuming post index 1 exists
        'query': True
    })
    assert result_post is not None
    assert isinstance(result_post, dict)
    assert 'title' in result_post
    assert 'author' in result_post

def _threaded_read_task(thread_id, service, results):
    try:
        # Perform a few read operations
        result_time = service.call('get_time')
        assert result_time is not None, f"Thread {thread_id}: get_time failed"

        url = 'https://www.ptt.cc/bbs/Python/M.1565335521.A.880.html'
        result_aid = service.call('get_aid_from_url', {'url': url})
        assert result_aid is not None, f"Thread {thread_id}: get_aid_from_url failed"

        result_newest_index = service.call('get_newest_index', {'index_type': PyPtt.NewIndex.BOARD, 'board': 'Python'})
        assert result_newest_index is not None, f"Thread {thread_id}: get_newest_index failed"

        results.append(True) # Indicate success for this thread
    except Exception as e:
        results.append(f"Thread {thread_id} failed: {e}")

def test_service_read_operations_multi_thread(service_instance):
    """Tests concurrent read operations via the Service."""
    test_thread_num = 2
    threads = []
    results = [] # To collect results/errors from threads

    for i in range(test_thread_num):
        t = threading.Thread(target=_threaded_read_task, args=(i, service_instance, results))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    # Check if all threads completed successfully
    for res in results:
        assert res is True, f"One or more threads failed: {res}"
    assert len(results) == test_thread_num, "Not all threads reported a result."

def test_service_post_and_delete_single_thread(service_instance):
    """Tests posting and deleting an article via the Service in a single thread."""
    board = 'Test'
    title = 'PyPtt Service 單執行緒貼文測試'
    content = '測試內容'

    posted_aid = None
    try:
        # 1. Post an article
        service_instance.call('post', {
            'board': board,
            'title_index': 1,
            'title': title,
            'content': content,
            'sign_file': 0
        })
        time.sleep(2) # Give server time to process

        # 2. Find the posted article to get its AID
        newest_index = service_instance.call('get_newest_index', {'index_type': PyPtt.NewIndex.BOARD, 'board': board})
        
        found_post = None
        for i in range(5): # Search last 5 posts
            post_index = newest_index - i
            if post_index <= 0: continue
            
            post_info = service_instance.call('get_post', {'board': board, 'index': post_index, 'query': True})
            if post_info and post_info.get(PostField.author, '').startswith(service_instance._api.ptt_id) and post_info.get(PostField.title) == f'[測試] {title}':
                found_post = post_info
                posted_aid = post_info.get(PostField.aid)
                break
        
        assert found_post is not None, f"Failed to find the posted article '{title}'."

    finally:
        # 3. Delete the article if it was posted
        if posted_aid:
            try:
                service_instance.call('del_post', {'board': board, 'aid': posted_aid})
                time.sleep(1) # Give server time to process deletion
                # Optional: Verify deletion by trying to get the post again and asserting it's gone
            except Exception as e:
                pytest.fail(f"Failed to delete post {posted_aid}: {e}")
