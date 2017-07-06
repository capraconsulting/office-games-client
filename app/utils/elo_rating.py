# From https://github.com/rshk/elo/blob/master/elo.py
def expected(a, b):
    """
    Calculate expected score of A in a match against B
    :param a: Elo rating for player A
    :param b: Elo rating for player B
    """
    return 1 / (1 + 10 ** ((b - a) / 400))


def elo(old, exp, score, k=32):
    """
    Calculate the new Elo rating for a player
    :param old: The previous Elo rating
    :param exp: The expected score for this match
    :param score: The actual score for this match
    :param k: The k-factor for Elo (default: 32)
    """
    return old + k * (score - exp)


def calculate_new_rating(player_rating, opponent_rating, player_won):
    return round(elo(
        player_rating,
        expected(player_rating, opponent_rating),
        1 if player_won else 0,
        k=32
    ))
