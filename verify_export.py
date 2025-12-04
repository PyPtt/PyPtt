#!/usr/bin/env python3
"""
Standalone verification script for export_util module
Tests all export functions without requiring pytest
"""

import os
import sys
import csv
import json
import tempfile

# Add parent directory to path to import PyPtt
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import PyPtt
from PyPtt import export_util


def create_sample_post():
    """Create a sample post for testing."""
    return {
        PyPtt.PostField.board: 'TestBoard',
        PyPtt.PostField.aid: '1ABC2DEF',
        PyPtt.PostField.index: '123',
        PyPtt.PostField.author: 'TestAuthor',
        PyPtt.PostField.date: '12/04 15:00',
        PyPtt.PostField.title: '[測試] 這是測試文章標題',
        PyPtt.PostField.content: '這是測試文章內容\n第二行內容\n第三行內容',
        PyPtt.PostField.url: 'https://www.ptt.cc/bbs/TestBoard/M.1234567890.A.123.html',
        PyPtt.PostField.ip: '1.2.3.4',
        PyPtt.PostField.location: '台灣',
        PyPtt.PostField.money: '0',
        PyPtt.PostField.post_status: 'EXISTS',
        PyPtt.PostField.push_number: '5',
        PyPtt.PostField.comments: [
            {
                PyPtt.CommentField.type: PyPtt.CommentType.PUSH,
                PyPtt.CommentField.author: 'User1',
                PyPtt.CommentField.content: '推推',
                PyPtt.CommentField.time: '12/04 15:01',
                PyPtt.CommentField.ip: '1.2.3.5'
            },
            {
                PyPtt.CommentField.type: PyPtt.CommentType.BOO,
                PyPtt.CommentField.author: 'User2',
                PyPtt.CommentField.content: '噓噓',
                PyPtt.CommentField.time: '12/04 15:02',
                PyPtt.CommentField.ip: '1.2.3.6'
            },
            {
                PyPtt.CommentField.type: PyPtt.CommentType.ARROW,
                PyPtt.CommentField.author: 'User3',
                PyPtt.CommentField.content: '→ 箭頭',
                PyPtt.CommentField.time: '12/04 15:03',
                PyPtt.CommentField.ip: '1.2.3.7'
            }
        ]
    }


def test_markdown_export():
    """Test Markdown export functionality."""
    print("Testing Markdown export...")
    
    post = create_sample_post()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = os.path.join(tmpdir, 'test.md')
        
        try:
            export_util.export_post_to_markdown(post, output_path)
            
            # Verify file exists
            assert os.path.exists(output_path), "Markdown file not created"
            
            # Read and verify content
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check essential elements
            assert '[測試] 這是測試文章標題' in content, "Title not found"
            assert 'TestAuthor' in content, "Author not found"
            assert 'Comments (3)' in content, "Comments section not found"
            assert '👍' in content, "Push emoji not found"
            
            print("  ✓ Markdown export test passed")
            return True
        except Exception as e:
            print(f"  ✗ Markdown export test failed: {e}")
            return False


def test_plaintext_export():
    """Test Plaintext export functionality."""
    print("Testing Plaintext export...")
    
    post = create_sample_post()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = os.path.join(tmpdir, 'test.txt')
        
        try:
            export_util.export_post_to_plaintext(post, output_path)
            
            # Verify file exists
            assert os.path.exists(output_path), "Plaintext file not created"
            
            # Read and verify content
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check essential elements
            assert 'Title: [測試] 這是測試文章標題' in content, "Title not found"
            assert 'Author: TestAuthor' in content, "Author not found"
            assert 'Comments (3):' in content, "Comments section not found"
            assert '[PUSH]' in content, "Push label not found"
            
            print("  ✓ Plaintext export test passed")
            return True
        except Exception as e:
            print(f"  ✗ Plaintext export test failed: {e}")
            return False


def test_csv_export():
    """Test CSV export functionality."""
    print("Testing CSV export...")
    
    post = create_sample_post()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = os.path.join(tmpdir, 'test.csv')
        
        try:
            export_util.export_post_to_csv(post, output_path)
            
            # Verify file exists
            assert os.path.exists(output_path), "CSV file not created"
            
            # Read and verify content
            with open(output_path, 'r', encoding='utf-8', newline='') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            
            assert len(rows) == 1, "Expected 1 row in CSV"
            row = rows[0]
            
            # Check essential fields
            assert row['board'] == 'TestBoard', "Board field incorrect"
            assert row['author'] == 'TestAuthor', "Author field incorrect"
            assert row['comments_count'] == '3', "Comments count incorrect"
            
            # Verify comments JSON
            comments = json.loads(row['comments_json'])
            assert len(comments) == 3, "Comments JSON incorrect"
            
            print("  ✓ CSV export test passed")
            return True
        except Exception as e:
            print(f"  ✗ CSV export test failed: {e}")
            return False


def test_batch_csv_export():
    """Test batch CSV export functionality."""
    print("Testing batch CSV export...")
    
    posts = [create_sample_post(), create_sample_post()]
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = os.path.join(tmpdir, 'batch.csv')
        
        try:
            export_util.export_posts_to_csv(posts, output_path)
            
            # Verify file exists
            assert os.path.exists(output_path), "Batch CSV file not created"
            
            # Read and verify content
            with open(output_path, 'r', encoding='utf-8', newline='') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            
            assert len(rows) == 2, f"Expected 2 rows, got {len(rows)}"
            
            print("  ✓ Batch CSV export test passed")
            return True
        except Exception as e:
            print(f"  ✗ Batch CSV export test failed: {e}")
            return False


def test_auto_detect_format():
    """Test auto-detection of export format."""
    print("Testing auto-detect format...")
    
    post = create_sample_post()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        try:
            # Test .md extension
            md_path = os.path.join(tmpdir, 'auto.md')
            export_util.export_post(post, md_path)
            assert os.path.exists(md_path), "Auto-detect MD failed"
            
            # Test .txt extension
            txt_path = os.path.join(tmpdir, 'auto.txt')
            export_util.export_post(post, txt_path)
            assert os.path.exists(txt_path), "Auto-detect TXT failed"
            
            # Test .csv extension
            csv_path = os.path.join(tmpdir, 'auto.csv')
            export_util.export_post(post, csv_path)
            assert os.path.exists(csv_path), "Auto-detect CSV failed"
            
            print("  ✓ Auto-detect format test passed")
            return True
        except Exception as e:
            print(f"  ✗ Auto-detect format test failed: {e}")
            return False


def test_directory_creation():
    """Test that export creates parent directories."""
    print("Testing directory creation...")
    
    post = create_sample_post()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        try:
            nested_path = os.path.join(tmpdir, 'a', 'b', 'c', 'test.md')
            export_util.export_post_to_markdown(post, nested_path)
            
            assert os.path.exists(nested_path), "Nested directory not created"
            
            print("  ✓ Directory creation test passed")
            return True
        except Exception as e:
            print(f"  ✗ Directory creation test failed: {e}")
            return False


def main():
    """Run all verification tests."""
    print("=" * 60)
    print("PyPtt Export Utility Verification")
    print("=" * 60)
    print()
    
    tests = [
        test_markdown_export,
        test_plaintext_export,
        test_csv_export,
        test_batch_csv_export,
        test_auto_detect_format,
        test_directory_creation,
    ]
    
    results = []
    for test in tests:
        results.append(test())
        print()
    
    print("=" * 60)
    print("Test Results")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("\n✓ All tests passed!")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
