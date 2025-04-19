from csv import Error
import hashlib, uuid, json, os

'''
OK SO
client should hash it and send the salt

then we should store the hash and salt in the userdata file

ok but how store user?

just hash the email lol
'''

def hash_password(password):
    salt = uuid.uuid4().hex
    return hashlib.sha256(salt.encode() + password.encode()).hexdigest() + ':' + salt

def is_admin(email, username, hashedPass):
    if email == "jierueic@gmail.com" and username == "knosmos" and check_password("c8cd035724dd2cc48f87c17f21c4cb7f9bdf9cf767bc88e5fcefefbf8f73dd0f:533a7722507f4d1da1bdfca16bf70675", hashedPass):
        return True
    if email == "nicholas.d.hagedorn@gmail.com" and username == "Nickname" and check_password("6d6438706baee7793b76597a15628859cf9b47c0097f814d06187247d120ceb7:6316c3b35173482db353c2a2baa8301e", hashedPass):
        return True
    
def check_password(hashed_password, user_password):
    password, salt = hashed_password.split(':')
    return password == hashlib.sha256(salt.encode() + user_password.encode()).hexdigest()

class User:
    def __init__(self, email:str, username:str, password:str, salt:str):
        '''
        `email` is the raw email\n
        `username` is the raw username\n
        `password` is the hashed password (hashed with salt)\n
        `salt` is what was added to raw password to get hashed password
        '''

        '''
        omg wait
        this is gonna be the wildest interaction

        CREATE ACCOUNT:
        enter details on page
        client generate salt
        client sha256 password + salt
        client send email, username, hashed, salt
        ----
        server recieves email, username, hashed, salt
        server stores email, username, hashed, salt

        LOGIN:
        enter details on page
        client send email/username
        ---
        server recieves email/username --> convert username to email
        server sends salt
        ---
        client recieves salt
        client sha256 password + salt
        client send (email | username), hashed, salt to server
        ---
        server recieves (email | username), hashed, salt --> convert username to email
        server checks credentials for admin-ness
        server sends login confirmation

        ok lets do it!
        '''
        self.isAdmin = is_admin(email, username, password)
        self.credentials = [email, username, hash_password(password), salt, self.isAdmin]
        self.email = email
        self.username = username

    @staticmethod
    def from_json(json_dat):
        jsonned = json.loads(json_dat)
        return User(jsonned["email"], jsonned["username"], jsonned["password"], jsonned["salt"])

    def save(self):
        fp = "users/" + hashlib.sha256(self.email.encode()).hexdigest() + ".json"

def get_user(email:str) -> User:
    fp = "users/" + hashlib.sha256(email.encode()).hexdigest() + ".json"
    if not os.path.exists(fp): raise FileNotFoundError()

    usrdata = open(fp,'w')
    usr = User.from_json(usrdata)
    return usr
