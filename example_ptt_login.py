#!/usr/bin/env python3
"""
Example script for connecting to PTT (ptt.cc)

PTT (批踢踢實業坊) is the largest BBS service in Taiwan.
Website: https://www.ptt.cc/
"""

import PyPtt

def main():
    # Create API instance for PTT1 (ptt.cc)
    # Use PyPtt.HOST.PTT1 to connect to ptt.cc
    ptt_bot = PyPtt.API(host=PyPtt.HOST.PTT1)
    
    try:
        # Login to PTT
        # Replace with your actual PTT credentials
        ptt_bot.login(
            ptt_id='your_ptt_id',
            password='your_ptt_password',
            kick_other_session=True  # Kick other sessions if already logged in
        )
        
        print("Successfully logged in to PTT!")
        
        # Example: Get board information
        # Some popular PTT boards: Gossiping, Stock, Baseball, etc.
        board_info = ptt_bot.get_board_info('Python')
        print(f"Board: {board_info.board}")
        print(f"Moderators: {board_info.moderators}")
        
        # Example: Get newest post index
        newest_index = ptt_bot.get_newest_index(PyPtt.NewIndex.BOARD, board='Python')
        print(f"Newest post index: {newest_index}")
        
        # Example: Get post list
        if newest_index > 0:
            post_list = ptt_bot.get_post_list(
                board='Python',
                start_index=max(1, newest_index - 10),
                end_index=newest_index
            )
            print(f"\nFound {len(post_list)} posts:")
            for post in post_list:
                print(f"  [{post.index}] {post.title} by {post.author}")
        
    except PyPtt.exceptions.LoginError:
        print("Login failed! Please check your credentials.")
    except PyPtt.exceptions.NoSuchBoard:
        print("Board not found on PTT.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Always logout when done
        try:
            ptt_bot.logout()
            print("\nLogged out from PTT.")
        except:
            pass

if __name__ == '__main__':
    main()
