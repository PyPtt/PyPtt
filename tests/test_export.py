"""
Tests for PyPtt export_util module

Run with: pytest tests/test_export.py -v
"""

import os
import csv
import json
import tempfile
import pytest
import PyPtt
from PyPtt import export_util


@pytest.fixture
def sample_post():
    """Create a sample post dictionary for testing."""
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


@pytest.fixture
def sample_post_no_comments():
    """Create a sample post without comments."""
    return {
        PyPtt.PostField.board: 'TestBoard',
        PyPtt.PostField.author: 'TestAuthor',
        PyPtt.PostField.date: '12/04 15:00',
        PyPtt.PostField.title: '[測試] 無推文文章',
        PyPtt.PostField.content: '這是沒有推文的文章',
        PyPtt.PostField.comments: []
    }


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test outputs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


def test_export_to_markdown(sample_post, temp_dir):
    """Test exporting a post to Markdown format."""
    output_path = os.path.join(temp_dir, 'test_article.md')
    
    export_util.export_post_to_markdown(sample_post, output_path)
    
    # Verify file was created
    assert os.path.exists(output_path)
    
    # Read and verify content
    with open(output_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for essential elements
    assert '[測試] 這是測試文章標題' in content
    assert 'TestAuthor' in content
    assert 'TestBoard' in content
    assert '這是測試文章內容' in content
    assert 'Comments (3)' in content
    assert '👍 **User1**' in content
    assert '👎 **User2**' in content
    assert '➡️ **User3**' in content


def test_export_to_markdown_no_comments(sample_post_no_comments, temp_dir):
    """Test exporting a post without comments to Markdown."""
    output_path = os.path.join(temp_dir, 'test_no_comments.md')
    
    export_util.export_post_to_markdown(sample_post_no_comments, output_path)
    
    assert os.path.exists(output_path)
    
    with open(output_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    assert '[測試] 無推文文章' in content
    assert 'Comments' not in content


def test_export_to_plaintext(sample_post, temp_dir):
    """Test exporting a post to plaintext format."""
    output_path = os.path.join(temp_dir, 'test_article.txt')
    
    export_util.export_post_to_plaintext(sample_post, output_path)
    
    # Verify file was created
    assert os.path.exists(output_path)
    
    # Read and verify content
    with open(output_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for essential elements
    assert 'Title: [測試] 這是測試文章標題' in content
    assert 'Author: TestAuthor' in content
    assert 'Board: TestBoard' in content
    assert '這是測試文章內容' in content
    assert 'Comments (3):' in content
    assert '[PUSH] User1' in content
    assert '[BOO] User2' in content
    assert '[ARROW] User3' in content


def test_export_to_csv(sample_post, temp_dir):
    """Test exporting a post to CSV format."""
    output_path = os.path.join(temp_dir, 'test_article.csv')
    
    export_util.export_post_to_csv(sample_post, output_path)
    
    # Verify file was created
    assert os.path.exists(output_path)
    
    # Read and verify CSV content
    with open(output_path, 'r', encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    assert len(rows) == 1
    row = rows[0]
    
    # Check essential fields
    assert row['board'] == 'TestBoard'
    assert row['author'] == 'TestAuthor'
    assert row['title'] == '[測試] 這是測試文章標題'
    assert row['comments_count'] == '3'
    
    # Verify comments JSON
    comments = json.loads(row['comments_json'])
    assert len(comments) == 3
    assert comments[0][PyPtt.CommentField.author] == 'User1'


def test_export_posts_to_csv_batch(sample_post, sample_post_no_comments, temp_dir):
    """Test batch exporting multiple posts to CSV."""
    output_path = os.path.join(temp_dir, 'test_batch.csv')
    
    posts = [sample_post, sample_post_no_comments]
    export_util.export_posts_to_csv(posts, output_path)
    
    # Verify file was created
    assert os.path.exists(output_path)
    
    # Read and verify CSV content
    with open(output_path, 'r', encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    # Should have 2 rows
    assert len(rows) == 2
    assert rows[0]['title'] == '[測試] 這是測試文章標題'
    assert rows[1]['title'] == '[測試] 無推文文章'
    assert rows[0]['comments_count'] == '3'
    assert rows[1]['comments_count'] == '0'


def test_export_post_auto_detect_markdown(sample_post, temp_dir):
    """Test auto-detecting Markdown format from file extension."""
    output_path = os.path.join(temp_dir, 'test_auto.md')
    
    export_util.export_post(sample_post, output_path)
    
    assert os.path.exists(output_path)
    
    with open(output_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    assert '# [測試] 這是測試文章標題' in content


def test_export_post_auto_detect_plaintext(sample_post, temp_dir):
    """Test auto-detecting plaintext format from file extension."""
    output_path = os.path.join(temp_dir, 'test_auto.txt')
    
    export_util.export_post(sample_post, output_path)
    
    assert os.path.exists(output_path)
    
    with open(output_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    assert 'Title: [測試] 這是測試文章標題' in content


def test_export_post_auto_detect_csv(sample_post, temp_dir):
    """Test auto-detecting CSV format from file extension."""
    output_path = os.path.join(temp_dir, 'test_auto.csv')
    
    export_util.export_post(sample_post, output_path)
    
    assert os.path.exists(output_path)
    
    with open(output_path, 'r', encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    assert len(rows) == 1


def test_export_post_explicit_format(sample_post, temp_dir):
    """Test explicitly specifying export format."""
    output_path = os.path.join(temp_dir, 'test_explicit.dat')
    
    # Should work even with non-standard extension
    export_util.export_post(sample_post, output_path, format='markdown')
    
    assert os.path.exists(output_path)


def test_export_post_invalid_format(sample_post, temp_dir):
    """Test error handling for invalid format."""
    output_path = os.path.join(temp_dir, 'test.xyz')
    
    with pytest.raises(ValueError):
        export_util.export_post(sample_post, output_path)


def test_export_post_invalid_explicit_format(sample_post, temp_dir):
    """Test error handling for invalid explicit format."""
    output_path = os.path.join(temp_dir, 'test.txt')
    
    with pytest.raises(ValueError):
        export_util.export_post(sample_post, output_path, format='invalid')


def test_export_creates_directory(sample_post):
    """Test that export creates parent directories if they don't exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = os.path.join(tmpdir, 'subdir', 'nested', 'test.md')
        
        export_util.export_post_to_markdown(sample_post, output_path)
        
        assert os.path.exists(output_path)


def test_export_special_characters(temp_dir):
    """Test handling of special characters in post content."""
    post = {
        PyPtt.PostField.title: '特殊字元測試 <>&"\'',
        PyPtt.PostField.author: 'Test',
        PyPtt.PostField.board: 'Test',
        PyPtt.PostField.content: '內容包含特殊字元：\n<script>alert("test")</script>\n& < > " \'',
        PyPtt.PostField.comments: []
    }
    
    output_path = os.path.join(temp_dir, 'special_chars.md')
    export_util.export_post_to_markdown(post, output_path)
    
    assert os.path.exists(output_path)
    
    with open(output_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    assert '<script>' in content  # Should preserve special chars


def test_csv_append_mode(sample_post, sample_post_no_comments, temp_dir):
    """Test CSV append mode."""
    output_path = os.path.join(temp_dir, 'test_append.csv')
    
    # First export
    export_util.export_post_to_csv(sample_post, output_path, append=False)
    
    # Append second post
    export_util.export_post_to_csv(sample_post_no_comments, output_path, append=True)
    
    # Read and verify
    with open(output_path, 'r', encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    assert len(rows) == 2


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
