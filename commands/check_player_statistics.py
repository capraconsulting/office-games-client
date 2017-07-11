from app.utils.elo_rating import calculate_new_rating
from app.utils.firebase import get_firebase


def check_player_statistics(game_slug):
    db = get_firebase().database()

    print('Grabbing players from Firebase')
    players = db.child('players').get().val()
    print('Grabbing player statistics from Firebase')
    player_statistics = db.child('games').child(game_slug).child('player_statistics').get().val()
    print('Grabbing game sessions from Firebase')
    game_sessions = db.child('games').child(game_slug).child('sessions').get().val()

    expected_player_statistics = {}
    for slack_user_id, player in players.items():
        expected_player_statistics[slack_user_id] = {
            'total_games': 0,
            'games_won': 0,
            'games_lost': 0,
            'elo_rating': 1200
        }

    player_keys = ['loser', 'winner']

    for session_id, game_session in game_sessions.items():
        print(f'Checking expected ratings for session: {session_id}')
        loser_slack_user_id = game_session['loser']['slack_user_id']
        loser_session_player = game_session['loser']

        winner_slack_user_id = game_session['winner']['slack_user_id']
        winner_session_player = game_session['winner']

        if loser_slack_user_id in expected_player_statistics:
            opponent_rating = expected_player_statistics[winner_slack_user_id]['elo_rating']

            expected_loser_elo_rating = calculate_new_rating(
                player_rating=expected_player_statistics[loser_slack_user_id]['elo_rating'],
                opponent_rating=opponent_rating,
                player_won=False
            )

            if expected_loser_elo_rating != loser_session_player['elo_rating']['after']:
                print(f'Expected loser rating {expected_loser_elo_rating} but was '
                      f'{loser_session_player["elo_rating"]["after"]}')
                exit(1)

        if winner_slack_user_id in expected_player_statistics:
            opponent_rating = expected_player_statistics[loser_slack_user_id]['elo_rating']

            expected_winner_elo_rating = calculate_new_rating(
                player_rating=expected_player_statistics[winner_slack_user_id]['elo_rating'],
                opponent_rating=opponent_rating,
                player_won=True
            )

            if expected_winner_elo_rating != winner_session_player['elo_rating']['after']:
                print(f'Expected winner rating {expected_winner_elo_rating} but was '
                      f'{winner_session_player["elo_rating"]["after"]}')
                exit(1)

        for player_key in player_keys:
            is_winner = player_key == 'winner'
            slack_user_id = game_session[player_key]['slack_user_id']
            session_player = game_session[player_key]
            # Update the local actual player statistics
            expected_player_statistics[slack_user_id]['total_games'] += 1
            expected_player_statistics[slack_user_id]['elo_rating'] = session_player['elo_rating']['after']
            if is_winner:
                expected_player_statistics[slack_user_id]['games_won'] += 1
            else:
                expected_player_statistics[slack_user_id]['games_lost'] += 1

    for slack_user_id, expected_player_statistic in expected_player_statistics.items():
        if expected_player_statistic['elo_rating'] != player_statistics[slack_user_id]['elo_rating']:
            print(f'elo_rating for slack_user_id {slack_user_id} does not equal the expected value.\n'
                  f'Expected: {expected_player_statistic["elo_rating"]}\n'
                  f'Actual: {player_statistics[slack_user_id]["elo_rating"]}\n')
        if expected_player_statistic['total_games'] != player_statistics[slack_user_id]['total_games']:
            print(f'total_games for slack_user_id {slack_user_id} does not equal the expected value.\n'
                  f'Expected: {expected_player_statistic["total_games"]}\n'
                  f'Actual: {player_statistics[slack_user_id]["total_games"]}\n')
        if expected_player_statistic['games_won'] != player_statistics[slack_user_id]['games_won']:
            print(f'games_won for slack_user_id {slack_user_id} does not equal the expected value.\n'
                  f'Expected: {expected_player_statistic["games_won"]}\n'
                  f'Actual: {player_statistics[slack_user_id]["games_won"]}\n')
        if expected_player_statistic['games_lost'] != player_statistics[slack_user_id]['games_lost']:
            print(f'games_lost for slack_user_id {slack_user_id} does not equal the expected value.\n'
                  f'Expected: {expected_player_statistic["games_lost"]}\n'
                  f'Actual: {player_statistics[slack_user_id]["games_lost"]}\n')

    """
    for card_uid, card in cards.items():
        if 'sessions' in card:
            #print(card)
            print(f'Removing sessions from card: {card_uid}')
            db.child('cards').child(card_uid).child('sessions').remove()
    """

    """
    for session_id, game_session in game_sessions.items():
        if 'elo_rating' not in game_session['loser'] or 'elo_rating' not in game_session['winner']:
            for player_key in player_keys:
                if 'slack_user_id' in game_session[player_key]:
                    slack_user_id = game_session[player_key]['slack_user_id']
                elif 'card_uid' not in game_session[player_key]:
                    print(f'Could not find card_uid in session #{session_id} for "{player_key}"')
                    sys.exit(1)
                else:
                    card_uid = game_session[player_key]['card_uid']
                    card_info = cards[card_uid]
                    slack_user_id = card_info['slack_user_id']
                player = players[slack_user_id]
                session_player = game_session[player_key]

                print(f'Updating session #{session_id} for player key "{player_key}" ({slack_user_id})')
                db.child('games').child(game_slug).child('sessions').child(session_id).child(player_key).set({
                    'slack_user_id': slack_user_id,
                    'elo_rating': {
                        'before': session_player['rating_before'],
                        'after': session_player['rating_after'],
                        'delta': session_player['rating_delta']
                    }
                })

                print(f'Adding session #{session_id} to player ({slack_user_id})')
                db.child('players').child(slack_user_id).child('sessions').child(game_slug).child(session_id).set({
                    'card_uid': card_uid,
                    'new_elo_rating': session_player['rating_after'],
                    'elo_rating_delta': session_player['rating_delta'],
                    'winner': player_key == 'winner'
                })

                # print(f'Removing session #{session_id} from card_uid ({card_uid})')
                # db.child('cards').child(card_uid).child('sessions').remove()
            #return
    """
    return

