#!/usr/bin/env python3
"""
Example: Export Entire PTT2 Board to Markdown Files

This script demonstrates how to export all articles from a PTT2 board,
with each article saved as an individual Markdown file.
"""

import PyPtt
from PyPtt import export_util


def main():
    # Configuration
    PTT2_ID = 'your_ptt2_id'  # Replace with your PTT2 ID
    PTT2_PASSWORD = 'your_ptt2_password'  # Replace with your PTT2 password
    BOARD = 'WhoAmI'  # PTT2 board to export
    OUTPUT_DIR = 'exported_board'  # Directory to save exported files
    
    # Create PTT2 API instance
    print("=" * 60)
    print("PTT2 Board Export to Markdown")
    print("=" * 60)
    print()
    
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
        print()
        
        # Example 1: Export entire board with progress tracking
        print(f"--- Example 1: Export Entire Board '{BOARD}' ---")
        print()
        
        def show_progress(current, total, title):
            """Progress callback to display export status."""
            # Truncate long titles for display
            display_title = title if len(title) <= 50 else title[:47] + "..."
            print(f"[{current:4d}/{total:4d}] {display_title}")
        
        stats = export_util.export_board_to_markdown(
            ptt_bot=ptt_bot,
            board=BOARD,
            output_dir=OUTPUT_DIR,
            progress_callback=show_progress
        )
        
        print()
        print("=" * 60)
        print("Export Complete!")
        print("=" * 60)
        print(f"Total articles:      {stats['total']}")
        print(f"Successfully exported: {stats['success']}")
        print(f"Skipped (deleted):   {stats['skipped']}")
        print(f"Failed:              {stats['failed']}")
        print(f"Output directory:    {stats['output_dir']}")
        print()
        
        # Example 2: Export specific range
        print(f"--- Example 2: Export Specific Range (1-10) ---")
        print()
        
        stats2 = export_util.export_board_to_markdown(
            ptt_bot=ptt_bot,
            board=BOARD,
            output_dir=f"{OUTPUT_DIR}_range",
            start_index=1,
            end_index=10,
            progress_callback=show_progress
        )
        
        print()
        print(f"✓ Exported {stats2['success']} articles from index 1-10")
        print(f"  Output: {stats2['output_dir']}")
        print()
        
        # Example 3: Export without progress callback (silent mode)
        print(f"--- Example 3: Silent Export (Last 5 Articles) ---")
        print()
        
        # Get newest index
        newest_index = ptt_bot.get_newest_index(PyPtt.NewIndex.BOARD, board=BOARD)
        start = max(1, newest_index - 4)
        
        stats3 = export_util.export_board_to_markdown(
            ptt_bot=ptt_bot,
            board=BOARD,
            output_dir=f"{OUTPUT_DIR}_recent",
            start_index=start,
            end_index=newest_index
        )
        
        print(f"✓ Exported {stats3['success']} recent articles (index {start}-{newest_index})")
        print(f"  Output: {stats3['output_dir']}")
        print()
        
        # Show file naming convention
        print("=" * 60)
        print("File Naming Convention")
        print("=" * 60)
        print()
        print("Files are named as: {index}_{aid}_{title}.md")
        print()
        print("Examples:")
        print("  00001_1ABC2DEF_[公告]_看板規則.md")
        print("  00123_1XYZ9ABC_Re_[問題]_如何使用.md")
        print()
        print("This ensures:")
        print("  - Files are sorted by index")
        print("  - Each file has a unique identifier (AID)")
        print("  - Titles are readable and filesystem-safe")
        
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
    print("\nIMPORTANT: Please update PTT2_ID and PTT2_PASSWORD")
    print("in the script before running.\n")
    
    # Uncomment the line below to run the example
    # main()
    
    print("Please edit this file and uncomment main() to run the example.")
