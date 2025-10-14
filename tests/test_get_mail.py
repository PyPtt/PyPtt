import PyPtt

def test_get_newest_mail(ptt_bots):
    """Tests getting the newest mail from the mailbox."""
    for ptt_bot in ptt_bots:
        mail_index = ptt_bot.get_newest_index(PyPtt.NewIndex.MAIL)

        assert isinstance(mail_index, int)
        # If mail_index is 0, it means no mail, get_mail will raise error
        if mail_index == 0:
            print(f"Warning: No mail found for host {ptt_bot.host}, skipping get_mail test.")
            continue

        mail_info = ptt_bot.get_mail(mail_index)

        assert mail_info is not None, f'get_mail returned None for host {ptt_bot.host}'
        assert isinstance(mail_info, dict), f'mail_info is not a dict for host {ptt_bot.host}'

        assert PyPtt.MailField.author in mail_info
        assert PyPtt.MailField.title in mail_info
        assert PyPtt.MailField.date in mail_info
        assert PyPtt.MailField.content in mail_info

def test_get_recent_mails(ptt_bots):
    """Tests getting the 5 most recent mails."""
    for ptt_bot in ptt_bots:
        mail_index = ptt_bot.get_newest_index(PyPtt.NewIndex.MAIL)

        if mail_index == 0:
            print(f"Warning: No mail found for host {ptt_bot.host}, skipping get_mail test.")
            continue

        # Test getting the last 5 mails
        for i in range(min(5, mail_index)):
            current_index = mail_index - i
            mail_info = ptt_bot.get_mail(current_index)

            assert mail_info is not None, f'get_mail returned None for index {current_index} on host {ptt_bot.host}'
            assert isinstance(mail_info, dict), f'mail_info is not a dict for index {current_index} on host {ptt_bot.host}'
            assert PyPtt.MailField.title in mail_info