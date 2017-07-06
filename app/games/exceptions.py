class CardExists(Exception):
    def __init__(self, card, existing_slack_username):
        super(CardExists, self).__init__(
            f'Card {card} exists in the database, it is registered under Slack user {existing_slack_username}.'
        )


class UnregisteredCardException(Exception):
    def __init__(self, card):
        super(UnregisteredCardException, self).__init__(f'Unregistered card tried to play: {card.get_uid()}')
