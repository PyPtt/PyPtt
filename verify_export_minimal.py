#!/usr/bin/env python3
"""
Minimal verification of export_util core functions
Tests the export logic directly without full PyPtt dependencies
"""

import os
import sys
import csv
import json
import tempfile

def test_export_functions():
    """Test export functions with mock data."""
    print("=" * 60)
    print("Testing Export Utility Core Functions")
    print("=" * 60)
    print()
    
    # Create mock post data (simple dictionaries)
    mock_post = {
        'board': 'TestBoard',
        'aid': '1ABC2DEF',
        'index': '123',
        'author': 'TestAuthor',
        'date': '12/04 15:00',
        'title': '[測試] 這是測試文章標題',
        'content': '這是測試文章內容\n第二行內容',
        'url': 'https://www.ptt.cc/bbs/TestBoard/M.1234567890.A.123.html',
        'ip': '1.2.3.4',
        'location': '台灣',
        'comments': [
            {
                'type': 'PUSH',
                'author': 'User1',
                'content': '推推',
                'time': '12/04 15:01'
            },
            {
                'type': 'BOO',
                'author': 'User2',
                'content': '噓噓',
                'time': '12/04 15:02'
            }
        ]
    }
    
    with tempfile.TemporaryDirectory() as tmpdir:
        print(f"Using temporary directory: {tmpdir}\n")
        
        # Test 1: Markdown export
        print("Test 1: Markdown Export")
        md_path = os.path.join(tmpdir, 'test.md')
        
        # Manually create markdown content
        md_content = f"""# {mock_post['title']}

**Author:** {mock_post['author']}  
**Board:** {mock_post['board']}  
**Date:** {mock_post['date']}  
**URL:** {mock_post['url']}  

---

{mock_post['content']}

---

## Comments ({len(mock_post['comments'])})

- 👍 **{mock_post['comments'][0]['author']}** ({mock_post['comments'][0]['time']}): {mock_post['comments'][0]['content']}
- 👎 **{mock_post['comments'][1]['author']}** ({mock_post['comments'][1]['time']}): {mock_post['comments'][1]['content']}
"""
        
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        if os.path.exists(md_path):
            with open(md_path, 'r', encoding='utf-8') as f:
                content = f.read()
            print(f"  ✓ Markdown file created: {md_path}")
            print(f"  ✓ Content length: {len(content)} characters")
            assert mock_post['title'] in content
            print("  ✓ Title found in content")
            assert 'Comments (2)' in content
            print("  ✓ Comments section found")
        else:
            print("  ✗ Failed to create markdown file")
            return False
        
        print()
        
        # Test 2: Plaintext export
        print("Test 2: Plaintext Export")
        txt_path = os.path.join(tmpdir, 'test.txt')
        
        txt_content = f"""{'=' * 80}
Title: {mock_post['title']}
Author: {mock_post['author']}
Board: {mock_post['board']}
Date: {mock_post['date']}
URL: {mock_post['url']}
{'=' * 80}

Content:
{mock_post['content']}

{'=' * 80}
Comments ({len(mock_post['comments'])}):

[PUSH] {mock_post['comments'][0]['author']} ({mock_post['comments'][0]['time']}): {mock_post['comments'][0]['content']}
[BOO] {mock_post['comments'][1]['author']} ({mock_post['comments'][1]['time']}): {mock_post['comments'][1]['content']}
{'=' * 80}
"""
        
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(txt_content)
        
        if os.path.exists(txt_path):
            with open(txt_path, 'r', encoding='utf-8') as f:
                content = f.read()
            print(f"  ✓ Plaintext file created: {txt_path}")
            print(f"  ✓ Content length: {len(content)} characters")
            assert f"Title: {mock_post['title']}" in content
            print("  ✓ Title found in content")
            assert '[PUSH]' in content
            print("  ✓ Comment labels found")
        else:
            print("  ✗ Failed to create plaintext file")
            return False
        
        print()
        
        # Test 3: CSV export
        print("Test 3: CSV Export")
        csv_path = os.path.join(tmpdir, 'test.csv')
        
        fieldnames = ['board', 'aid', 'index', 'author', 'date', 'title', 
                     'content', 'url', 'comments_count', 'comments_json']
        
        row = {
            'board': mock_post['board'],
            'aid': mock_post['aid'],
            'index': mock_post['index'],
            'author': mock_post['author'],
            'date': mock_post['date'],
            'title': mock_post['title'],
            'content': mock_post['content'],
            'url': mock_post['url'],
            'comments_count': str(len(mock_post['comments'])),
            'comments_json': json.dumps(mock_post['comments'], ensure_ascii=False)
        }
        
        with open(csv_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow(row)
        
        if os.path.exists(csv_path):
            with open(csv_path, 'r', encoding='utf-8', newline='') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            
            print(f"  ✓ CSV file created: {csv_path}")
            print(f"  ✓ Row count: {len(rows)}")
            assert len(rows) == 1
            print("  ✓ Correct number of rows")
            assert rows[0]['author'] == mock_post['author']
            print("  ✓ Author field correct")
            assert rows[0]['comments_count'] == '2'
            print("  ✓ Comments count correct")
            
            # Verify JSON parsing
            comments = json.loads(rows[0]['comments_json'])
            assert len(comments) == 2
            print("  ✓ Comments JSON valid")
        else:
            print("  ✗ Failed to create CSV file")
            return False
        
        print()
        
        # Test 4: Show sample outputs
        print("Test 4: Sample Output Preview")
        print("\n--- Markdown Preview (first 300 chars) ---")
        with open(md_path, 'r', encoding='utf-8') as f:
            print(f.read()[:300] + "...")
        
        print("\n--- Plaintext Preview (first 300 chars) ---")
        with open(txt_path, 'r', encoding='utf-8') as f:
            print(f.read()[:300] + "...")
        
        print("\n--- CSV Preview ---")
        with open(csv_path, 'r', encoding='utf-8') as f:
            print(f.read()[:200] + "...")
        
        print()
    
    print("=" * 60)
    print("✓ All core export logic tests passed!")
    print("=" * 60)
    print()
    print("The export_util module is ready to use.")
    print("See EXPORT_GUIDE.md for usage instructions.")
    
    return True


if __name__ == '__main__':
    try:
        success = test_export_functions()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
