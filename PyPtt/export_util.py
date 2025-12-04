"""
PyPtt Article Export Utility

This module provides functions to export PTT/PTT2 articles to various formats:
- Markdown (.md or .markdown)
- Plaintext (.txt)
- CSV (.csv)

Usage:
    import PyPtt
    from PyPtt import export_util
    
    ptt_bot = PyPtt.API(host=PyPtt.HOST.PTT2)
    ptt_bot.login('username', 'password')
    
    # Export single post
    post = ptt_bot.get_post('board_name', index=1)
    export_util.export_post_to_markdown(post, 'output.md')
    
    # Export entire board
    export_util.export_board_to_markdown(ptt_bot, 'board_name', 'output_dir/')
"""

from __future__ import annotations

import csv
import json
import os
import re
from typing import Dict, List, Optional, Union

from . import data_type


def _safe_get(post_dict: Dict, field: data_type.PostField, default: str = '') -> str:
    """Safely get a field from post dictionary and convert to string."""
    value = post_dict.get(field, default)
    if value is None:
        return default
    return str(value)


def _format_comment_markdown(comment: Dict) -> str:
    """Format a single comment for Markdown output."""
    comment_type = comment.get(data_type.CommentField.type, '')
    author = comment.get(data_type.CommentField.author, 'Unknown')
    content = comment.get(data_type.CommentField.content, '')
    time = comment.get(data_type.CommentField.time, '')
    
    # Choose emoji based on comment type
    if comment_type == data_type.CommentType.PUSH:
        emoji = '👍'
    elif comment_type == data_type.CommentType.BOO:
        emoji = '👎'
    elif comment_type == data_type.CommentType.ARROW:
        emoji = '➡️'
    else:
        emoji = '💬'
    
    return f"- {emoji} **{author}** ({time}): {content}"


def _format_comment_plaintext(comment: Dict) -> str:
    """Format a single comment for plaintext output."""
    comment_type = comment.get(data_type.CommentField.type, '')
    author = comment.get(data_type.CommentField.author, 'Unknown')
    content = comment.get(data_type.CommentField.content, '')
    time = comment.get(data_type.CommentField.time, '')
    
    # Use text labels for comment type
    if comment_type == data_type.CommentType.PUSH:
        type_label = 'PUSH'
    elif comment_type == data_type.CommentType.BOO:
        type_label = 'BOO'
    elif comment_type == data_type.CommentType.ARROW:
        type_label = 'ARROW'
    else:
        type_label = 'COMMENT'
    
    return f"[{type_label}] {author} ({time}): {content}"


def export_post_to_markdown(post_dict: Dict, output_path: str) -> None:
    """
    Export a PTT post to Markdown format.
    
    Args:
        post_dict: Dictionary containing post data from get_post()
        output_path: Path to output .md or .markdown file
        
    Example:
        >>> post = ptt_bot.get_post('Python', index=1)
        >>> export_post_to_markdown(post, 'article.md')
    """
    # Extract post fields
    title = _safe_get(post_dict, data_type.PostField.title, 'Untitled')
    author = _safe_get(post_dict, data_type.PostField.author, 'Unknown')
    board = _safe_get(post_dict, data_type.PostField.board, 'Unknown')
    date = _safe_get(post_dict, data_type.PostField.date, '')
    content = _safe_get(post_dict, data_type.PostField.content, '')
    url = _safe_get(post_dict, data_type.PostField.url, '')
    ip = _safe_get(post_dict, data_type.PostField.ip, '')
    location = _safe_get(post_dict, data_type.PostField.location, '')
    comments = post_dict.get(data_type.PostField.comments, [])
    
    # Build Markdown content
    lines = [
        f"# {title}",
        "",
        f"**Author:** {author}  ",
        f"**Board:** {board}  ",
        f"**Date:** {date}  ",
    ]
    
    if url:
        lines.append(f"**URL:** {url}  ")
    if ip:
        ip_location = f"{ip} ({location})" if location else ip
        lines.append(f"**IP:** {ip_location}  ")
    
    lines.extend([
        "",
        "---",
        "",
        content,
        "",
    ])
    
    # Add comments section
    if comments and isinstance(comments, list) and len(comments) > 0:
        lines.extend([
            "---",
            "",
            f"## Comments ({len(comments)})",
            "",
        ])
        
        for comment in comments:
            if isinstance(comment, dict):
                lines.append(_format_comment_markdown(comment))
    
    # Write to file
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))


def export_post_to_plaintext(post_dict: Dict, output_path: str) -> None:
    """
    Export a PTT post to plain text format.
    
    Args:
        post_dict: Dictionary containing post data from get_post()
        output_path: Path to output .txt file
        
    Example:
        >>> post = ptt_bot.get_post('Python', index=1)
        >>> export_post_to_plaintext(post, 'article.txt')
    """
    # Extract post fields
    title = _safe_get(post_dict, data_type.PostField.title, 'Untitled')
    author = _safe_get(post_dict, data_type.PostField.author, 'Unknown')
    board = _safe_get(post_dict, data_type.PostField.board, 'Unknown')
    date = _safe_get(post_dict, data_type.PostField.date, '')
    content = _safe_get(post_dict, data_type.PostField.content, '')
    url = _safe_get(post_dict, data_type.PostField.url, '')
    ip = _safe_get(post_dict, data_type.PostField.ip, '')
    location = _safe_get(post_dict, data_type.PostField.location, '')
    comments = post_dict.get(data_type.PostField.comments, [])
    
    # Build plaintext content
    lines = [
        "=" * 80,
        f"Title: {title}",
        f"Author: {author}",
        f"Board: {board}",
        f"Date: {date}",
    ]
    
    if url:
        lines.append(f"URL: {url}")
    if ip:
        ip_location = f"{ip} ({location})" if location else ip
        lines.append(f"IP: {ip_location}")
    
    lines.extend([
        "=" * 80,
        "",
        "Content:",
        content,
        "",
    ])
    
    # Add comments section
    if comments and isinstance(comments, list) and len(comments) > 0:
        lines.extend([
            "=" * 80,
            f"Comments ({len(comments)}):",
            "",
        ])
        
        for comment in comments:
            if isinstance(comment, dict):
                lines.append(_format_comment_plaintext(comment))
        
        lines.append("=" * 80)
    
    # Write to file
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))


def export_post_to_csv(post_dict: Dict, output_path: str, append: bool = False) -> None:
    """
    Export a PTT post to CSV format.
    
    Args:
        post_dict: Dictionary containing post data from get_post()
        output_path: Path to output .csv file
        append: If True, append to existing file; if False, create new file
        
    Example:
        >>> post = ptt_bot.get_post('Python', index=1)
        >>> export_post_to_csv(post, 'article.csv')
    """
    # Extract post fields
    row = {
        'board': _safe_get(post_dict, data_type.PostField.board),
        'aid': _safe_get(post_dict, data_type.PostField.aid),
        'index': _safe_get(post_dict, data_type.PostField.index),
        'author': _safe_get(post_dict, data_type.PostField.author),
        'date': _safe_get(post_dict, data_type.PostField.date),
        'title': _safe_get(post_dict, data_type.PostField.title),
        'content': _safe_get(post_dict, data_type.PostField.content),
        'url': _safe_get(post_dict, data_type.PostField.url),
        'ip': _safe_get(post_dict, data_type.PostField.ip),
        'location': _safe_get(post_dict, data_type.PostField.location),
        'money': _safe_get(post_dict, data_type.PostField.money),
        'post_status': _safe_get(post_dict, data_type.PostField.post_status),
        'push_number': _safe_get(post_dict, data_type.PostField.push_number),
    }
    
    # Convert comments to JSON string for CSV storage
    comments = post_dict.get(data_type.PostField.comments, [])
    if comments and isinstance(comments, list):
        row['comments_count'] = str(len(comments))
        row['comments_json'] = json.dumps(comments, ensure_ascii=False)
    else:
        row['comments_count'] = '0'
        row['comments_json'] = '[]'
    
    # Define CSV columns
    fieldnames = [
        'board', 'aid', 'index', 'author', 'date', 'title', 
        'content', 'url', 'ip', 'location', 'money', 
        'post_status', 'push_number', 'comments_count', 'comments_json'
    ]
    
    # Write to CSV
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    
    mode = 'a' if append and os.path.exists(output_path) else 'w'
    write_header = mode == 'w' or not os.path.exists(output_path)
    
    with open(output_path, mode, encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        writer.writerow(row)


def export_posts_to_csv(post_list: List[Dict], output_path: str) -> None:
    """
    Export multiple PTT posts to a single CSV file.
    
    Args:
        post_list: List of post dictionaries from get_post()
        output_path: Path to output .csv file
        
    Example:
        >>> posts = []
        >>> for i in range(1, 11):
        ...     posts.append(ptt_bot.get_post('Python', index=i))
        >>> export_posts_to_csv(posts, 'articles.csv')
    """
    if not post_list:
        return
    
    # Export first post (creates file with header)
    export_post_to_csv(post_list[0], output_path, append=False)
    
    # Append remaining posts
    for post in post_list[1:]:
        export_post_to_csv(post, output_path, append=True)


def export_post(post_dict: Dict, output_path: str, format: Optional[str] = None) -> None:
    """
    Export a PTT post to the specified format (auto-detected from file extension if not specified).
    
    Args:
        post_dict: Dictionary containing post data from get_post()
        output_path: Path to output file
        format: Export format ('markdown', 'plaintext', or 'csv'). If None, auto-detect from extension.
        
    Example:
        >>> post = ptt_bot.get_post('Python', index=1)
        >>> export_post(post, 'article.md')  # Auto-detects Markdown
        >>> export_post(post, 'article.txt', format='plaintext')  # Explicit format
    """
    # Auto-detect format from file extension if not specified
    if format is None:
        ext = os.path.splitext(output_path)[1].lower()
        if ext in ['.md', '.markdown']:
            format = 'markdown'
        elif ext == '.txt':
            format = 'plaintext'
        elif ext == '.csv':
            format = 'csv'
        else:
            raise ValueError(f"Cannot auto-detect format from extension '{ext}'. "
                           "Please specify format parameter.")
    
    # Export based on format
    format = format.lower()
    if format == 'markdown':
        export_post_to_markdown(post_dict, output_path)
    elif format == 'plaintext':
        export_post_to_plaintext(post_dict, output_path)
    elif format == 'csv':
        export_post_to_csv(post_dict, output_path)
    else:
        raise ValueError(f"Unsupported format: {format}. "
                       "Supported formats: 'markdown', 'plaintext', 'csv'")


def _sanitize_filename(filename: str) -> str:
    """
    Sanitize a string to be used as a filename.
    
    Args:
        filename: Original filename string
        
    Returns:
        Sanitized filename safe for file systems
    """
    # Remove or replace invalid characters
    # Keep Chinese characters, alphanumeric, spaces, hyphens, underscores
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Replace multiple spaces/underscores with single underscore
    sanitized = re.sub(r'[\s_]+', '_', sanitized)
    
    # Remove leading/trailing spaces and underscores
    sanitized = sanitized.strip(' _')
    
    # Limit length (keep it reasonable for file systems)
    if len(sanitized) > 200:
        sanitized = sanitized[:200]
    
    return sanitized or 'untitled'


def export_board_to_markdown(ptt_bot, board: str, output_dir: str, 
                             start_index: Optional[int] = None,
                             end_index: Optional[int] = None,
                             progress_callback: Optional[callable] = None) -> Dict:
    """
    Export all articles from a PTT board to individual Markdown files.
    
    Args:
        ptt_bot: PyPtt API instance (must be logged in)
        board: Board name to export
        output_dir: Directory to save exported Markdown files
        start_index: Starting article index (default: 1)
        end_index: Ending article index (default: newest index)
        progress_callback: Optional callback function(current, total, post_title) for progress updates
        
    Returns:
        Dict with export statistics:
            - total: Total articles attempted
            - success: Successfully exported articles
            - failed: Failed exports
            - skipped: Skipped articles (deleted, etc.)
            - output_dir: Output directory path
            
    Example:
        >>> ptt_bot = PyPtt.API(host=PyPtt.HOST.PTT2)
        >>> ptt_bot.login('username', 'password')
        >>> 
        >>> # Export entire board
        >>> stats = export_board_to_markdown(ptt_bot, 'WhoAmI', 'exported_board/')
        >>> print(f"Exported {stats['success']} articles")
        >>> 
        >>> # Export specific range
        >>> stats = export_board_to_markdown(ptt_bot, 'WhoAmI', 'exported/', 
        ...                                   start_index=1, end_index=100)
        >>> 
        >>> # With progress callback
        >>> def show_progress(current, total, title):
        ...     print(f"[{current}/{total}] {title}")
        >>> stats = export_board_to_markdown(ptt_bot, 'WhoAmI', 'exported/',
        ...                                   progress_callback=show_progress)
    """
    # Import here to avoid circular dependency
    from . import data_type
    from . import exceptions
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Get board index range
    if end_index is None:
        try:
            end_index = ptt_bot.get_newest_index(data_type.NewIndex.BOARD, board=board)
        except Exception as e:
            raise ValueError(f"Failed to get newest index for board '{board}': {e}")
    
    if start_index is None:
        start_index = 1
    
    # Validate range
    if start_index < 1:
        start_index = 1
    if end_index < start_index:
        raise ValueError(f"end_index ({end_index}) must be >= start_index ({start_index})")
    
    # Statistics
    stats = {
        'total': end_index - start_index + 1,
        'success': 0,
        'failed': 0,
        'skipped': 0,
        'output_dir': os.path.abspath(output_dir)
    }
    
    # Export each article
    for index in range(start_index, end_index + 1):
        current = index - start_index + 1
        
        try:
            # Get post
            post = ptt_bot.get_post(board, index=index)
            
            if post is None:
                stats['skipped'] += 1
                if progress_callback:
                    progress_callback(current, stats['total'], f"[Skipped] Index {index}")
                continue
            
            # Check if post is deleted
            post_status = post.get(data_type.PostField.post_status, '')
            if 'DELETED' in str(post_status):
                stats['skipped'] += 1
                if progress_callback:
                    progress_callback(current, stats['total'], f"[Deleted] Index {index}")
                continue
            
            # Get post info
            title = _safe_get(post, data_type.PostField.title, f'Untitled_{index}')
            aid = _safe_get(post, data_type.PostField.aid, '')
            
            # Create filename from index, AID, and title
            # Format: {index}_{aid}_{sanitized_title}.md
            sanitized_title = _sanitize_filename(title)
            if aid:
                filename = f"{index:05d}_{aid}_{sanitized_title}.md"
            else:
                filename = f"{index:05d}_{sanitized_title}.md"
            
            output_path = os.path.join(output_dir, filename)
            
            # Export to markdown
            export_post_to_markdown(post, output_path)
            
            stats['success'] += 1
            
            if progress_callback:
                progress_callback(current, stats['total'], title)
                
        except exceptions.NoSuchPost:
            stats['skipped'] += 1
            if progress_callback:
                progress_callback(current, stats['total'], f"[Not Found] Index {index}")
        except Exception as e:
            stats['failed'] += 1
            if progress_callback:
                progress_callback(current, stats['total'], f"[Error] Index {index}: {str(e)[:50]}")
    
    return stats

