import json, random, os, hashlib
from datetime import datetime

ALPHABET = "QWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasdfghjklzxcvbnm1234567890_-"
def generate_id():
    return "".join([random.choice(ALPHABET) for _ in range(10)])

def generate_salt():
    return "".join([random.choice(ALPHABET) for _ in range(32)])


email_to_id = {}
username_to_id = {}

def save_indexing():
    with open("users/indexing.json",'w') as f:
        json.dump({
            "email": email_to_id,
            "username": username_to_id
        })
def load_indexing():
    global email_to_id, username_to_id
    if not os.path.exists("users/indexing.json"): save_indexing()
    with open("users/indexing.json") as f:
        a = json.load(f)
        email_to_id = a["email"]
        username_to_id = a["username_to_id"]

class User:
    def __init__(self, id=""):
        if id!="":
            self.id=id
            self.load()
            return
        self.id = generate_id()
        self.username = ""
        self.email = ""
        self.hashed_pass = ""
        self.salt = ""
        self.solved_problems = []
        self.attempted_problems = []
        self.joined_contests = []
        self.date_created = datetime.now().strftime("%m-%d-%Y-%H-%M-%S")
        self.admin = False
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
            "meta": { "date-created": self.date_created }
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
        self.save()

    def set_hash_pass(self, hashed_pass):
        self.load()
        self.hashed_pass = hashed_pass
        self.save()

    def set_salt(self) -> str:
        if self.salt != "" and self.hashed_pass != "": raise Exception("Salt already set")
        self.salt = generate_salt()
        self.save()
        return self.salt

    def check_login(self, hashedpass):
        if self.hashed_pass == "": return False
        if hashedpass == self.hashed_pass: return True
        return False