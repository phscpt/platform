import random, html, time, os, json

ALPHABET = "QWERTYUIOPASDFGHJKLZXCVBNM"

GAMES_PATH = "games"
LOAD_INTERVAL = 30

def random_id():
    return "".join([random.choice(ALPHABET) for _ in range(6)])

def random_player_id():
    return "".join([random.choice(ALPHABET + ALPHABET.lower() + "1234567890") for _ in range(20)])

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
        self.scores:list[float] = [0 for _ in range(num_problems)]
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

def save_game(func):
    def a(self:"Game", *args):
        self.load()
        res = func(self, *args)
        self.save()
        return res
    return a
    
def load_game(func):
    def a(self:"Game", *args):
        self.load()
        return func(self, *args)
    return a

class Game:
    def __init__(self, problems:list[str]=[], totalTime=0, tst:"str|None"="off", doTeams:bool=False, g_id=""):
        if g_id != "":
            assert os.path.exists(f"{GAMES_PATH}/{g_id}.json")
            self.id=g_id
            self.last_load=0
            self.load()
            return
        if tst == None: tst="off"
        if not isinstance(doTeams,bool): doTeams=False
        self.id = random_id()
        self.players:list[Player] = []
        self.status = "waiting"
        self.start_time = -1
        self.duration = -1
        '''Time is in minutes'''

        self.last_load = 0
        
        if totalTime > 0: self.duration=int(totalTime)*60

        self.problems = [problem.rstrip() for problem in problems]
        print("created game", self.id)
        print("problems:", problems)

    def to_json(self) -> dict:
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

    @save_game
    def add_player(self:"Game", name:str) -> str:

        name = self.unique_name(name)

        player = Player(name=name, num_problems=len(self.problems))
        self.players.append(player)
        print(self.players)
        return player.id
    
    @load_game
    def unique_name(self, name:str) -> str:
        names = set([player.name for player in self.players])
        name=name.strip()
        if not name in names: return name
        num=1
        while f"name {num}" in names: num+=1
        return f"name {num}"
    
    def get_id(self):
        return self.id
    
    @save_game
    def start(self):
        self.status = "started"
        self.start_time = time.time()
    
    @save_game
    def give_points(self, player_id:str, problem, points:float):
        if self.time_remaining() < -1: raise Exception(f"Contest over")
        problem_idx = self.problems.index(problem)
        for player in self.players:
            if player.id != player_id: continue

            if points > 0: player.last_submit=time.time()
            player.scores[problem_idx] = max(player.scores[problem_idx], points)
            return
        raise KeyError()
    
    @save_game
    def validate_players(self) -> None:
        for player in self.players: player.name = html.escape(player.name)

    @load_game
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
