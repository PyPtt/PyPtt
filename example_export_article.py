#!/usr/bin/env python3
"""
Example: Export PTT2 Articles to Different Formats

This script demonstrates how to:
1. Connect to PTT2
2. Retrieve articles from a board
3. Export articles to Markdown, Plaintext, and CSV formats
"""

import PyPtt
from PyPtt import export_util

def main():
    # Configuration
    PTT2_ID = 'your_ptt2_id'  # Replace with your PTT2 ID
    PTT2_PASSWORD = 'your_ptt2_password'  # Replace with your PTT2 password
    BOARD = 'WhoAmI'  # PTT2 board to read from
    
    # Create PTT2 API instance
    print("Connecting to PTT2...")
    ptt_bot = PyPtt.API(host=PyPtt.HOST.PTT2)
    
    try:
        # Login to PTT2
        print(f"Logging in as {PTT2_ID}...")
        ptt_bot.login(
            ptt_id=PTT2_ID,
            password=PTT2_PASSWORD,
            kick_other_session=True
        )
        print("✓ Login successful!")
        
        # Example 1: Export a single post to all formats
        print(f"\n--- Example 1: Export Single Post ---")
        print(f"Fetching post from board '{BOARD}'...")
        
        # Get the first post
        post = ptt_bot.get_post(BOARD, index=1)
        
        if post:
            print(f"✓ Retrieved post: {post.get(PyPtt.PostField.title, 'Untitled')}")
            
            # Export to Markdown
            print("Exporting to Markdown...")
            export_util.export_post_to_markdown(post, 'exported_article.md')
            print("✓ Saved to: exported_article.md")
            
            # Export to Plaintext
            print("Exporting to Plaintext...")
            export_util.export_post_to_plaintext(post, 'exported_article.txt')
            print("✓ Saved to: exported_article.txt")
            
            # Export to CSV
            print("Exporting to CSV...")
            export_util.export_post_to_csv(post, 'exported_article.csv')
            print("✓ Saved to: exported_article.csv")
            
            # Alternative: Use the generic export function (auto-detects format)
            export_util.export_post(post, 'exported_article_auto.md')
            print("✓ Auto-detected format and saved to: exported_article_auto.md")
        
        # Example 2: Batch export multiple posts to CSV
        print(f"\n--- Example 2: Batch Export Multiple Posts ---")
        
        # Get newest index
        newest_index = ptt_bot.get_newest_index(PyPtt.NewIndex.BOARD, board=BOARD)
        print(f"Newest post index: {newest_index}")
        
        # Fetch last 5 posts
        posts = []
        start_index = max(1, newest_index - 4)
        print(f"Fetching posts {start_index} to {newest_index}...")
        
        for i in range(start_index, newest_index + 1):
            try:
                post = ptt_bot.get_post(BOARD, index=i)
                if post:
                    posts.append(post)
                    title = post.get(PyPtt.PostField.title, 'Untitled')
                    print(f"  [{i}] {title}")
            except Exception as e:
                print(f"  [{i}] Error: {e}")
        
        if posts:
            print(f"\nExporting {len(posts)} posts to CSV...")
            export_util.export_posts_to_csv(posts, 'exported_articles_batch.csv')
            print(f"✓ Saved {len(posts)} posts to: exported_articles_batch.csv")
        
        # Example 3: Export with search results
        print(f"\n--- Example 3: Export Search Results ---")
        
        try:
            # Search for posts with a keyword
            search_keyword = '[問題]'
            print(f"Searching for posts with keyword: {search_keyword}")
            
            search_index = ptt_bot.get_newest_index(
                PyPtt.NewIndex.BOARD,
                board=BOARD,
                search_type=PyPtt.SearchType.KEYWORD,
                search_condition=search_keyword
            )
            
            if search_index > 0:
                post = ptt_bot.get_post(
                    BOARD,
                    index=search_index,
                    search_type=PyPtt.SearchType.KEYWORD,
                    search_condition=search_keyword
                )
                
                if post:
                    title = post.get(PyPtt.PostField.title, 'Untitled')
                    print(f"✓ Found post: {title}")
                    
                    export_util.export_post_to_markdown(post, 'exported_search_result.md')
                    print("✓ Saved to: exported_search_result.md")
            else:
                print("No search results found.")
                
        except PyPtt.exceptions.NoSearchResult:
            print(f"No posts found with keyword: {search_keyword}")
        
        print("\n" + "=" * 60)
        print("Export completed successfully!")
        print("=" * 60)
        print("\nGenerated files:")
        print("  - exported_article.md (Markdown format)")
        print("  - exported_article.txt (Plaintext format)")
        print("  - exported_article.csv (CSV format)")
        print("  - exported_article_auto.md (Auto-detected format)")
        print("  - exported_articles_batch.csv (Batch CSV export)")
        print("  - exported_search_result.md (Search result)")
        
    except PyPtt.exceptions.LoginError:
        print("✗ Login failed! Please check your credentials.")
    except PyPtt.exceptions.NoSuchBoard:
        print(f"✗ Board '{BOARD}' not found on PTT2.")
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Always logout
        try:
            ptt_bot.logout()
            print("\n✓ Logged out from PTT2.")
        except:
            pass


if __name__ == '__main__':
    print("=" * 60)
    print("PTT2 Article Export Example")
    print("=" * 60)
    print("\nIMPORTANT: Please update PTT2_ID and PTT2_PASSWORD")
    print("in the script before running.\n")
    
    # Uncomment the line below to run the example
    # main()
    
    print("Please edit this file and uncomment main() to run the example.")
