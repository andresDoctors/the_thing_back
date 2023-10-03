from typing import List, Dict


GameId = int
UserId = int
PlayerId = int
NULL_ID = 0


class DataBase:
    import CardMetadata
    CARDS_METADATA: Dict[str, CardMetadata.CardMetadata] = CardMetadata.CARDS_METADATA

    def __init__(self):
        from classes.Adjacency import Adjacency
        from classes.Card import Card
        from classes.Game import Game
        from classes.Player import Player
        from classes.User import User

        self.gamesId: GameId = 1
        self.usersId: UserId = 1
        self.playersId: PlayerId = 1

        self.games:   Dict[GameId, Game] = {}
        self.users:   Dict[tuple[GameId, UserId], User] = {}
        self.players: Dict[tuple[GameId, PlayerId], Player] = {}
        self.adjacencies: Dict[GameId, List[Adjacency]] = {}
        self.cards:       Dict[GameId, List[Card]] = {}

    def create_user(self, nickname):
        from classes.User import User

        user = User(self.usersId, nickname)
        self.usersId += 1
        self.users[(NULL_ID, user.id)] = user

        return user.id

    def create_game(self, game_name, password, min, max):
        from classes.Game import Game

        game = Game(self.gamesId, game_name, password, min, max)
        self.gamesId += 1
        self.games[game.id] = game

        return game.id

    def create_player(self, game_id, user_id):
        from classes.Player import Player

        player = Player(self.playersId, user_id)
        self.playersId += 1
        self.players[(game_id, player.id)] = player

        return player.id

    def create_adjacency(self, game_id, left_player_id, right_player_id):
        from classes.Adjacency import Adjacency

        adjacency = Adjacency(left_player_id, right_player_id)
        if game_id not in self.adjacencies:
            self.adjacencies[game_id] = []
        self.adjacencies[game_id].append(adjacency)

    def kill(self, game_id, player_id):

        for adjacency in self.adjacencies[game_id]:
            if adjacency.left_player == player_id:
                self.adjacencies[game_id].remove(adjacency)
            elif adjacency.right_player == player_id:
                adjacency.right_player = self.players[(game_id, player_id)].right_player

    def discard_card(self, game_id, player_id, card_name):
        hand = self.players[(game_id, player_id)].hand
        hand.remove(card_name)

        cards = self.cards[game_id]
        for card in cards:
            if card.name == card_name:
                card.players_with_card.remove(player_id)
                card.amount_discarded += 1
                break

    def complete_turn(self, game_id, player_id):
        from classes.Game import OrderOfTurns
        from classes.Player import CurrentPhase

        game = self.games[game_id]
        player = self.players[(game_id, player_id)]
        player.current_phase = CurrentPhase.INACTIVE

        next_player_id = 0
        for adjacency in self.adjacencies[game_id]:
            if game.order_of_turns == OrderOfTurns.CLOCKWISE and adjacency.right_player == player_id:
                next_player_id = adjacency.left_player
                break
            elif game.order_of_turns == OrderOfTurns.COUNTERCLOCKWISE and adjacency.left_player == player_id:
                next_player_id = adjacency.right_player
                break

        self.players[(game_id, next_player_id)].current_phase = CurrentPhase.ACTIVE
        self.draw_card(game_id, next_player_id)

    def draw_card(self, game_id, player_id):
        import random

        deck = self.cards[game_id]
        random.shuffle(deck)

        for card in deck:
            if card.amount_in_deck <= 0: continue
            player = self.players[(game_id, player_id)]

            player.hand.append(card.name)
            card.amount_in_deck -= 1
            card.players_with_card.append(player_id)
            break
