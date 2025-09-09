import json, random, os, hashlib
from datetime import datetime
from config import EXTENDED_ALPHABET

def rand_short():
    return "".join([random.choice(EXTENDED_ALPHABET) for _ in range(10)])

def rand_long():
    return "".join([random.choice(EXTENDED_ALPHABET) for _ in range(32)])


class Users:
    email_to_id = {}
    username_to_id = {}

    @staticmethod
    def save_indexing():
        with open("users/indexing.json",'w') as f:
            json.dump({
                "email": Users.email_to_id,
                "username": Users.username_to_id
            },f)
            print({
                "email": Users.email_to_id,
                "username": Users.username_to_id
            })

    @staticmethod
    def load_indexing():
        if not os.path.exists("users/indexing.json"): Users.save_indexing()
        with open("users/indexing.json") as f:
            a = json.load(f)
            Users.email_to_id = a["email"]
            Users.username_to_id = a["username"]

    @staticmethod
    def del_empty():
        paths = os.listdir("users/")
        for path in paths:
            if path == "indexing.json" or path == "readme.md": continue
            try: user = User(path[:-5])
            except: os.remove("users/" + path)
            if user.hashed_pass == "": os.remove("users/" + path)

class User:
    def __init__(self, id=""):
        if id!="":
            self.id=id
            self.load()
            return
        self.id = rand_short()
        self.username = ""
        self.email = ""
        self.hashed_pass = ""
        self.salt = ""
        self.solved_problems:dict[str, str] = {}
        self.attempted_problems:dict[str,str] = {}
        self.joined_contests = []
        self.date_created = datetime.now().strftime("%m-%d-%Y-%H-%M-%S")
        self.admin = False
        self.tokens = []
        self.save()

    def to_json(self) -> dict:
        jsoned = {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "admin": self.admin,
            "login": {
                "password": self.hashed_pass,
                "salt": self.salt
            },
            "problems": {
                "attempted": self.attempted_problems,
                "solved": self.solved_problems
            },
            "contests": { "joined": self.joined_contests },
            "meta": { "date-created": self.date_created },
            "tokens": self.tokens
        }
        return jsoned
    
    def from_json(self, jsoned):
        self.id = jsoned["id"]
        self.username = jsoned["username"]
        self.email = jsoned["email"]
        self.admin = jsoned["admin"]
        self.hashed_pass = jsoned["login"]["password"]
        self.salt = jsoned["login"]["salt"]
        self.attempted_problems = jsoned["problems"]["attempted"]
        self.solved_problems = jsoned["problems"]["solved"]
        self.joined_contests = jsoned["contests"]["joined"]
        self.date_created = jsoned["meta"]["date-created"]
        self.tokens = []
        if "tokens" in jsoned: self.tokens=jsoned["tokens"]

    def load(self):
        if not os.path.exists(f"users/{self.id}.json"): raise FileNotFoundError

        with open(f"users/{self.id}.json") as f:
            self.from_json(json.load(f))

    def save(self):
        with open(f"users/{self.id}.json",'w') as f:
            json.dump(self.to_json(),f)

    def set_details(self, username, email):
        self.load()
        self.username = username
        self.email = email
        Users.load_indexing()
        Users.username_to_id[self.username] = self.id
        Users.email_to_id[self.email] = self.id
        Users.save_indexing()
        self.save()

    def set_hash_pass(self, hashed_pass):
        self.hashed_pass = hashed_pass
        self.save()

    def set_salt(self) -> str:
        self.load()
        if self.salt != "" and self.hashed_pass != "": return self.salt
        self.salt = rand_long()
        self.save()
        return self.salt
    
    def add_attempted(self, problem, id):
        self.load()
        self.attempted_problems[problem] = id
        self.save()

    def add_solved(self, problem, id):
        self.load()
        self.solved_problems[problem] = id
        self.save()

    def check_pass(self, hashedpass):
        '''
        Checks the login against `hashedpass` which SHOULD be hash(hash(pass)+[MM/YYYY]) --> auto expires at end of month
        '''
        
        def hash(text:str) -> str:
            encoded = text.encode()
            return hashlib.sha256(encoded).hexdigest()
        date = datetime.now().strftime("%m-%Y")
        if self.hashed_pass == "" or self.salt=="": return False
        if hashedpass == hash(self.hashed_pass + date): return True

        return False

    def remove_expired_tokens(self):
        self.load()
        i=len(self.tokens)-1
        removed=False
        month = datetime.now().month
        year = datetime.now().year
        while i>=0:
            if (month >= int(self.tokens[i]["date"][0]) or year > int(self.tokens[i]["date"][1])): 
                self.tokens.pop(i)
                removed=True
            i-=1
        if removed: self.save()

    def generate_token(self) -> str:
        self.load()
        token = rand_short()
        month = datetime.now().month
        year = datetime.now().year
        next_month = [month+1, year]
        if next_month[0] >= 12:
            next_month[0] = 0
            next_month[1]+=1
        self.tokens.append({"date":next_month,"value":token})
        self.save()
        
        return token

    def check_token(self, token) -> bool:
        self.remove_expired_tokens()
        for t in self.tokens:
            if token == t["value"]: return True
        return False

    def __str__(self)->str:
        return f"<User id: {self.id}, username: {self.username} {'admin' if self.admin else ''}>"