import PyPtt
import time
from PyPtt import PostField
from tests import util
import pytest

def test_post_and_reply(ptt_bots):
    """
    Tests posting an article and replying to it.
    """
    board = 'Test'
    title = 'PyPtt 程式貼文測試'
    content = '測試內文'
    reply_content = 'PyPtt 程式回覆測試'

    for ptt_bot in ptt_bots:
        # PTT2 does not support posting/replying to articles in the same way as PTT1
        # or there might be issues with the 'Test' board on PTT2.
        # The original script only tested PTT1 for this functionality.
        if ptt_bot.host == PyPtt.HOST.PTT2:
            # pytest.skip(f"Skipping post and reply test on PTT2 as it's not supported or configured for this test.")
            continue

        try:
            # 1. Post
            ptt_bot.post(board=board, title_index=1, title=title, content=content)
            time.sleep(2) # Give server time to process

            # 2. Find and Reply
            newest_index = ptt_bot.get_newest_index(index_type=PyPtt.NewIndex.BOARD, board=board)
            
            replied = False
            original_post_aid = None
            for i in range(5): # Search last 5 posts
                post_index = newest_index - i
                if post_index <= 0: continue
                
                post = ptt_bot.get_post(board=board, index=post_index)
                if not post or post.get(PostField.post_status) != PyPtt.PostStatus.EXISTS:
                    continue
                
                author = post.get(PostField.author, '').split(' ')[0]
                if author.lower() == ptt_bot.ptt_id.lower():
                    ptt_bot.reply_post(
                        reply_to=PyPtt.ReplyTo.BOARD,
                        board=board,
                        index=post_index,
                        content=reply_content
                    )
                    replied = True
                    original_post_aid = post.get(PostField.aid)
                    break
            
            assert replied, f"Failed to find and reply to the post on host {ptt_bot.host}"

            time.sleep(2) # Give server time to process reply

            # 3. Verify
            newest_index_after_reply = ptt_bot.get_newest_index(index_type=PyPtt.NewIndex.BOARD, board=board)
            
            my_posts = []
            for i in range(10): # Search last 10 posts
                post_index = newest_index_after_reply - i
                if post_index <= 0: continue

                # Use query=True for faster retrieval if only AID and title are needed
                post = ptt_bot.get_post(board=board, index=post_index, query=True) 
                if not post or post.get(PostField.post_status) != PyPtt.PostStatus.EXISTS:
                    continue

                author = post.get(PostField.author, '').split(' ')[0]
                if author.lower() == ptt_bot.ptt_id.lower():
                    my_posts.append(post)

            assert len(my_posts) >= 2, f"Expected at least 2 posts (original and reply), but found {len(my_posts)} on host {ptt_bot.host}"

            # Check titles
            expected_original_title = f'[測試] {title}'
            expected_reply_title = f'R: [測試] {title}'

            found_original = False
            found_reply = False

            for p in my_posts:
                if p.get(PostField.aid) == original_post_aid and p.get(PostField.title) == expected_original_title:
                    found_original = True
                elif p.get(PostField.title) == expected_reply_title:
                    found_reply = True
            
            assert found_original, f"Original post with title '{expected_original_title}' not found or title mismatch on host {ptt_bot.host}"
            assert found_reply, f"Reply post with title '{expected_reply_title}' not found on host {ptt_bot.host}"

        finally:
            # 4. Cleanup
            util.del_all_post(ptt_bot)
