import random, html, pickle, time, os, sys, json

ALPHABET = "QWERTYUIOPASDFGHJKLZXCVBNM"

GAME_FILE = "games/game.pkl"
GAMES_PATH = "games"
# assert os.path.exists(GAME_FILE)

LOAD_INTERVAL = 10

def random_id():
    return "".join([random.choice(ALPHABET) for _ in range(6)])

def random_player_id():
    return "".join([random.choice(ALPHABET + ALPHABET.lower() + "1234567890") for _ in range(20)])

# def game_read(do):
#     def a(*args, **kwargs):
#         gmae.load_games()
#         res=do(*args, **kwargs)
#         return res
#     return a

# def game_write(do):
#     def a(*args, **kwargs):
#         gmae.load_games()
#         res=do(*args, **kwargs)
#         gmae.save_games()
#         return res
#     return a

class Player:
    def __init__(self, name:str="", num_problems:int=-1, player_json:dict={}):
        if player_json != {}:
            self.id = player_json["id"]
            self.name = player_json["name"]
            self.scores = player_json["scores"]
            self.results = player_json["results"]
            self.last_submit = player_json["last_submit"]
            return
        self.id = random_player_id()
        self.name = html.escape(name)
        self.scores = [0 for _ in range(num_problems)]
        self.results = {}
        self.last_submit=0
    
    def to_list(self):
        return [self.id, self.name, self.scores, self.results, self.last_submit]
    
    def to_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "scores": self.scores,
            "results": self.results,
            "last_submit": self.last_submit,
        }


class Game:
    def __init__(self, problems:list[str]=[], totalTime=0, tst:str="off", doTeams:bool=False, g_id=""):
        if g_id != "":
            assert os.path.exists(f"{GAMES_PATH}/{g_id}.json")
            self.id=g_id
            self.last_load=0
            self.load()
            return

        self.id = random_id()
        self.players:list[Player] = []
        self.status = "waiting"
        self.start_time = -1
        self.duration = -1

        self.last_load = 0
        '''Time is in minutes'''
        
        if totalTime > 0: self.duration=int(totalTime)*60

        self.problems = [problem.rstrip() for problem in problems]
        print("created game", self.id)
        print("problems:", problems)

    def to_json(self) -> str:
        jsoned = {
            "id":self.id,
            "players": list(map(Player.to_json,self.players)),
            "status": self.status,
            "start_time": self.start_time,
            "duration": self.duration,
            "problems": self.problems,
        }
        return jsoned
    
    def from_json(self, json_txt:dict) -> None:
        self.id = json_txt["id"]
        self.status = json_txt["status"]
        self.start_time = json_txt["start_time"]
        self.duration = json_txt["duration"]

        players_json = json_txt["players"]
        self.players = []
        for player_json in players_json:
            self.players.append(Player(player_json=player_json))
        self.problems = json_txt["problems"]
        # self.players = list(map(Player,*players_json))
    
    def save(self) -> None:
        jsoned = self.to_json()
        with open(f"{GAMES_PATH}/{self.id}.json",'w') as f:
            f.write(json.dumps(jsoned))
    
    def load(self) -> None:
        if time.time() - self.last_load < LOAD_INTERVAL: return

        if not os.path.exists(f"{GAMES_PATH}/{self.id}.json"): return
        with open(f"{GAMES_PATH}/{self.id}.json") as f:
            jsoned:dict = json.loads(f.read())
            self.from_json(jsoned)
        self.last_load = time.time()

    def _save_wrap(func):
        def a(self, *args):
            self.load()
            res = func(self, *args)
            self.save()
            return res
        return a
    
    def _load_wrap(func):
        def a(self, *args):
            self.load()
            return func(self, *args)
        return a
    
    @_save_wrap
    def add_player(self, name:str) -> str:

        name = self.unique_name(name)

        player = Player(name=name, num_problems=len(self.problems))
        self.players.append(player)
        print(self.players)
        return player.id
    
    @_load_wrap
    def unique_name(self, name:str) -> str:
        names = set([player.name for player in self.players])
        name=name.strip()
        if not name in names: return name
        num=1
        while f"name {num}" in names: num+=1
        return f"name {num}"
    
    def get_id(self):
        return self.id
    
    @_save_wrap
    def start(self):
        self.status = "started"
        self.start_time = time.time()
    
    @_save_wrap
    def give_points(self, player_id:str, problem, points:int):
        if self.time_remaining() < -1: raise Exception(f"Contest over")
        problem_idx = self.problems.index(problem)
        for player in self.players:
            if player.id != player_id: continue

            if points > 0: player.last_submit=time.time()
            player.scores[problem_idx] = max(player.scores[problem_idx], points)
            return
        raise KeyError()
    
    @_save_wrap
    def validate_players(self) -> None:
        for player in self.players: player.name = html.escape(player.name)

    @_load_wrap
    def get_player(self, player_id:str) -> Player:
        print(self.players)
        for player in self.players:
            print(player.id, player_id)
            print(player.id == player_id)
            if player.id == player_id: return player
        raise KeyError()
    def time_remaining(self):
        if self.duration == -1: return -1
        return self.duration - (time.time() - self.start_time)


games:dict[str,Game] = dict()

def get_game(id:str) -> Game:
    if id in games: return games[id]

    if os.path.exists(f"{GAMES_PATH}/{id}.json"):
        games[id] = Game(g_id=id)
        return games[id]
    
    raise FileNotFoundError(f"Game {id} cannot be found")        

#i lost the
# class Games:
#     __games:dict[Game] = {}
#     __last_update = 0

#     @staticmethod
#     def add_game(game:Game)->None:
#         Games.load_games()
#         print(Games.__games)
#         Games.__games.append(game)
#         print(Games.__games)
#         Games.save_games()

#     def get_games() -> list[Game]:
#         return Games.__games

#     @staticmethod
#     def save_games() -> None:
#         return
#         with open(GAME_FILE, "wb") as f: pickle.dump(Games.__games, f)

#     @staticmethod
#     def load_games() -> None:
#         return
#         if time.time()-Games.__last_update < LOAD_INTERVAL: return
#         if os.path.exists(GAME_FILE):
#             with open(GAME_FILE, "rb") as f:
#                 Games.__games = pickle.load(f)

#     @staticmethod
#     def get(index:int) -> Game:
#         Games.load_games()
#         if (int(index) < len(Games.__games)): return Games.__games[index]
#         raise IndexError()

#     @staticmethod
#     def get_id(id:str) -> Game:
#         Games.load_games()
#         for game in Games.__games:
#             if game.get_id() == id: return game
#         print(id)
#         raise KeyError()

#     @staticmethod
#     def get_latest() -> Game:
#         Games.load_games()
#         latest=Games.__games[0]
#         for game in Games.__games:
#             if game.start_time > latest.start_time or (game.start_time == latest.start_time and game.time_remaining() > latest.time_remaining()):
#                 latest=game
#         return Games.__games[latest]
    
#     @staticmethod
#     def apply_all(func) -> None:
#         for game in Games.__games:
#             func(game)

# gmae=Games

# WAIT NO WAY IVE DONE IT
# recursive aah class definitions
# hopefully this doesn't cause problems later

# Games.add_game(Game(["a"]))