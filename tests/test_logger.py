from PyPtt import log

def test_logger_info_level(caplog):
    """Tests that the logger, when set to INFO level, correctly logs INFO
    messages and ignores DEBUG messages."""
    logger = log.init(log.INFO)
    
    logger.info('info message')
    logger.debug('debug message')

    assert 'Info message' in caplog.text
    assert 'debug message' not in caplog.text
    assert 'Debug message' not in caplog.text

def test_logger_debug_level(caplog):
    """Tests that the logger, when set to DEBUG level, correctly logs both
    INFO and DEBUG messages."""
    logger = log.init(log.DEBUG)
    
    logger.info('info message')
    logger.debug('debug message')

    assert 'Info message' in caplog.text
    assert 'Debug message' in caplog.text

def test_logger_multiple_arguments(caplog):
    """Tests that the logger correctly handles multiple string arguments,
    concatenating them into a single space-separated string."""
    logger = log.init(log.DEBUG)

    logger.info('hello', 'world')
    logger.debug('first', 'second', 'third')

    assert 'Hello world' in caplog.text
    assert 'First second third' in caplog.text

def test_logger_warning_silent_mode(capsys):
    """Regression test: SILENT (NOTSET) must fully suppress warning() too.

    logging.Logger.isEnabledFor(WARNING) resolves NOTSET up to the root
    logger's default level (WARNING), so it incorrectly reports "enabled"
    under SILENT. warning() must not rely on that -- under SILENT, no
    output should reach stderr and the logger_callback must not fire.
    """
    calls = []
    logger = log.init(log.SILENT, logger_callback=calls.append)

    logger.warning('should not appear')

    captured = capsys.readouterr()
    assert captured.err == ''
    assert captured.out == ''
    assert calls == []
