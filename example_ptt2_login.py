#!/usr/bin/env python3
"""
Example script for connecting to PTT2 (ptt2.cc)

PTT2 (批踢踢兔) is a BBS service that focuses on personal boards and group boards.
Website: https://pttpedia.fandom.com/zh/wiki/PTT2
"""

import PyPtt

def main():
    # Create API instance for PTT2
    # Use PyPtt.HOST.PTT2 to connect to ptt2.cc instead of ptt.cc
    ptt_bot = PyPtt.API(host=PyPtt.HOST.PTT2)
    
    try:
        # Login to PTT2
        # Replace with your actual PTT2 credentials
        ptt_bot.login(
            ptt_id='your_ptt2_id',
            password='your_ptt2_password',
            kick_other_session=True  # Kick other sessions if already logged in
        )
        
        print("Successfully logged in to PTT2!")
        
        # Example: Get board information
        # PTT2 has different boards than PTT1
        # Some popular PTT2 boards: Ptt2Law, Amginevar, etc.
        board_info = ptt_bot.get_board_info('Ptt2Law')
        print(f"Board: {board_info.board}")
        print(f"Moderators: {board_info.moderators}")
        
        # Example: Get newest post index
        newest_index = ptt_bot.get_newest_index(PyPtt.NewIndex.BOARD, board='Ptt2Law')
        print(f"Newest post index: {newest_index}")
        
        # Example: Get post list
        if newest_index > 0:
            post_list = ptt_bot.get_post_list(
                board='Ptt2Law',
                start_index=max(1, newest_index - 10),
                end_index=newest_index
            )
            print(f"\nFound {len(post_list)} posts:")
            for post in post_list:
                print(f"  [{post.index}] {post.title} by {post.author}")
        
    except PyPtt.exceptions.LoginError:
        print("Login failed! Please check your credentials.")
    except PyPtt.exceptions.NoSuchBoard:
        print("Board not found on PTT2.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Always logout when done
        try:
            ptt_bot.logout()
            print("\nLogged out from PTT2.")
        except:
            pass

if __name__ == '__main__':
    main()
