from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

import bd


app = FastAPI()
bd = bd.DataBase()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Replace with your React app's address
    allow_credentials=True,
    allow_methods=["*"],  # You can specify specific HTTP methods like ["GET", "POST"]
    allow_headers=["*"],  # You can specify specific headers if needed
)


@app.post("/users")
async def new_user(nickname: str):
    user_id = bd.create_user(nickname)
    return {"user_id": f"{user_id}"}


@app.get("/games")
async def list_games():
    from classes.Game import StatusType

    list_of_games = []
    for game_id in bd.games:
        game = bd.games[game_id]
        if len(game.users) >= game.max or game.status != StatusType.LOBBY:
            continue

        game_info = {
            "game_id": game_id,
            "game_name": game.name,
            "joined_users": [
                {
                    "user_id":  user_id,
                    "nickname": bd.users[(game_id, user_id)].nickname,
                    "creator": bd.users[(game_id, user_id)].is_creator
                }
                for user_id in game.users
            ]
        }

        list_of_games.append(game_info)

    return JSONResponse(content={"games": list_of_games})


@app.get("/games/{game_id}")
async def get_game(game_id: int):
    from classes.Game import StatusType

    game = bd.games[game_id]
    return JSONResponse(content={
        "min": game.min,
        "max": game.max,
        "users_count": len(game.users),
        "started": bd.games[game_id].status == StatusType.IN_GAME,
        "users": [
            {
                "nickname": user.nickname,
                "user_id": user.id
            }
            for user_id in game.users
            if (user := bd.users[(game_id, user_id)])
        ]
    })


@app.post("/games")
async def new_game(user_id: int, game_name: str, password: str = "", min: int = 4, max: int = 12):
    game_id = bd.create_game(game_name, password, min, max)

    user = bd.users[0, user_id]
    user.is_creator = True
    user.game_id = game_id
    bd.users.pop((0, user_id))
    bd.users[(game_id, user_id)] = user
    bd.games[game_id].users.append(user_id)

    return {"game_id": {game_id}}


@app.patch("/games")
async def join_user(user_id: int, game_id: int, password: str = ""):
    game = bd.games[game_id]
    if password != game.password:
        return {"message": "invalid password"}

    game.users.append(user_id)
    user = bd.users[(0, user_id)]
    user.is_creator = False
    user.game_id = game_id
    bd.users[(game_id, user_id)] = user
    bd.users.pop((0, user_id))

    return {"message": "OK"}


@app.post("/games/{game_id}")
async def start_game(game_id: int):
    from classes.Game import StatusType
    from classes.Player import CurrentPhase

    bd.games[game_id].status = StatusType.IN_GAME

    new_players(game_id)
    new_adjacencies(game_id)
    new_cards(game_id)
    deal_cards(game_id)

    for player_id in [y for (x,y) in bd.players if x == game_id]:
        player = bd.players[(game_id, player_id)]
        if player.current_phase == CurrentPhase.ACTIVE:
            bd.draw_card(game_id, player_id)
            break

    return {"message": "OK"}


@app.get("/games/{game_id}/players_order")
async def get_player_order(game_id: int):
    from classes.Game import OrderOfTurns
    from classes.Player import CurrentPhase

    game = bd.games[game_id]
    key = (lambda x: x.left_player) if game.order_of_turns == OrderOfTurns.CLOCKWISE else (lambda x: x.right_player)
    adjacencies = bd.adjacencies[game_id]
    adjacencies.sort(key=key)

    rows = [
        {
            "nickname": bd.users[(game_id, player.user)].nickname,
            "id": player.id,
            "active": player.current_phase == CurrentPhase.ACTIVE
        }
        for adjacency in adjacencies
        if (player := bd.players[(game_id, key(adjacency))]) and player.alive
    ]

    return JSONResponse(content={"order": rows})


@app.get("/games/{game_id}/{player_id}")
async def get_player_hand(game_id: int, player_id: int):
    return JSONResponse(content={"hand": [
        {
            "name": card_name,
            "description": bd.CARDS_METADATA[card_name].description
        }
        for card_name in bd.players[(game_id, player_id)].hand
    ]})


@app.get("/games/{game_id}/{player_id}/{card_index}")
async def get_choosable_players(game_id: int, player_id: int, card_name: str):
    player = bd.players[(game_id, player_id)]
    if card_name == "Lanzallamas":
        return {"choosable_players": [player.left_player, player.right_player]}

    return {"choosable_players": []}


@app.post("/games/{game_id}/{player_id}/{card_name}")
async def play_card(game_id: int, player_id: int, card_name: str, choosed_player_id: int):
    if card_name == "Lanzallamas":
        bd.kill(game_id, choosed_player_id)

    bd.discard_card(game_id, player_id, card_name)
    bd.complete_turn(game_id, player_id)

    return {"message": "OK"}


def new_players(game_id):
    import random
    from classes.Player import CurrentPhase, Rol

    users = [user for (x, user_id) in bd.users if (user := bd.users[(x, user_id)]) and x == game_id]
    player_ids = [bd.create_player(game_id, user.id) for user in users]
    for user, player_id in zip(users, player_ids): user.player_id = player_id

    index_first_turn = random.randint(0, len(player_ids) - 1)
    first_turn_id = player_ids[index_first_turn]
    bd.players[(game_id, first_turn_id)].current_phase = CurrentPhase.ACTIVE

    return


def new_adjacencies(game_id):
    from classes.Adjacency import Adjacency

    player_ids = [player_id for (x, player_id) in bd.players if x == game_id]
    bd.adjacencies[game_id] = adjacencies = []

    for i in range(len(player_ids)):
        right_player_id = player_ids[i]
        left_player_id = player_ids[i-1]

        adjacencies.append(Adjacency(left_player_id, right_player_id))

        right_player = bd.players[(game_id, right_player_id)]
        right_player.left_player = left_player_id
        left_player = bd.players[(game_id, left_player_id)]
        left_player.right_player = right_player_id

    return


def new_cards(game_id):
    from classes.Card import Card

    players_count = len(bd.games[game_id].users)
    bd.cards[game_id] = [
        Card(card_name, card_metadata.category, card_metadata.quantity)
        for card_name in bd.CARDS_METADATA
        if (card_metadata := bd.CARDS_METADATA[card_name]) and players_count >= card_metadata.number
    ]

    return


def deal_cards(game_id):
    from classes.Player import Rol
    import random

    game = bd.games[game_id]
    players = [bd.players[(game_id, user.player_id)] for user_id in game.users if (user := bd.users[(game_id, user_id)])]

    deck = []
    thing_card = None
    for card in bd.cards[game_id]:
        if card.name == "¡Infectado!":
            continue
        if card.name == "La Cosa":
            thing_card = card
            continue

        for i in range(card.amount_in_deck):
            deck.append(card)

    random.shuffle(deck)
    deck = deck[: 4 * len(players) - 1]
    deck.append(thing_card)
    random.shuffle(deck)

    for i in range(len(players)):
        hand = deck[4*i:4*(i+1)]
        for card in hand:
            players[i].hand.append(card.name)
            card.players_with_card.append(players[i].id)
            card.amount_in_deck -= 1
            if card.name == "La Cosa":
                players[i].rol = Rol.THE_THING

    return
