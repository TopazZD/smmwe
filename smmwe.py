import requests, json, base64

BASE_HOST = "http://103.195.100.145:35566"

# -------------------- Exceptions -------------------- #

# ----- Login ----- #
class UserNotFound(Exception):
    pass

class IncorrectPassword(Exception):
    pass

class NotLoggedIn(Exception):
    pass

# -------------------- Classes -------------------- #

class Auth:
    code:str = None
    uid:str = None
    alias:str = None

class UserData:
    user_id:str
    easy_progress:int
    normal_progress:int
    hard_progress:int
    expert_progress:int
    easy_lives:int
    normal_lives:int
    hard_lives:int
    expert_lives:int
    easy_record:int
    normal_record:int
    hard_record:int
    expert_record:int
    is_banned:bool

# -------------------- Functions -------------------- #

class SMMWEClient():
    def __init__(self):
        self.auth = Auth()

    def login(self, username:str, password:str):
        """Logs into the SMM:WE server\n
        Most functions require to be logged in\n
        Can be executed multiple times to change accounts"""

        login_url = BASE_HOST+"/online/user/login"
        login_data = {
            "token":"ponkis16122",
            "alias": username,
            "password": password
        }

        login_response = requests.post(login_url, login_data, headers={"User-Agent":"GameMaker HTTP"}).text
        login_dict:dict = json.loads(login_response)
        if "error_type" in login_dict.keys():
            if login_dict["error_type"] == "006":
                raise UserNotFound(f"User '{username}' not found")

            if login_dict["error_type"] == "010":
                raise NotInEK("You must be in the Engine Kingdom server")

            if login_dict["error_type"].startswith("007"):
                raise IncorrectPassword(f"Password for '{username}' is incorrect")

            if login_dict["error_type"].startswith("401"):
                raise BlockedAccount("That account is blocked")

        self.auth.code = login_dict["auth_code"]
        self.auth.uid = login_dict["id"]
        self.auth.alias = login_dict["alias"]

    def upload_level_file(self, name:str, description:str, aparience:int, enviroment:int, tags:list[str,str], filepath:str):
        """Uploads a base64 encoded level file\n
        To upload raw data use upload_level_data()"""

        if self.auth.uid == None:
            raise NotLoggedIn("You must log in first")

        url = BASE_HOST+"/stage/upload"

        with open(filepath, "r") as lf:
            level_data = lf.read()

        data = {
            "token":"ponkis16122",
            "discord_id":self.auth.uid,
            "auth_code":self.auth.code,
            "name":name,
            "desc":description,
            "aparience":aparience,
            "entorno":enviroment,
            "tags":tags[0]+","+tags[1],
            "swe":level_data
        }

        return requests.post(url, data, proxies=[self.proxy])

    def upload_level_data(self, name:str, description:str, aparience:int, enviroment:int, tags:str, level_data:bytes | dict, encoded:bool = True):
        """Uploads a level in JSON data or encoded in base64\n
        To upload a level file use upload_level_file()"""

        if self.auth.uid == None:
            raise NotLoggedIn("You must log in first")
        url = BASE_HOST+"/stage/upload"

        if not encoded:
            level_data = base64.b64encode(json.dumps(level_data).encode())

        data = {
            "token":"ponkis16122",
            "discord_id":self.auth.uid,
            "auth_code":self.auth.code,
            "name":name,
            "desc":description,
            "aparience":aparience,
            "entorno":enviroment,
            "tags":tags,
            "swe":level_data
        }

        return requests.post(url, data, headers={"User-Agent":"GameMaker HTTP"})

    def level_url_from_id(self, id:str):
        """Get the Discord URL of a level file using its ID\n
        Does not require to be logged in"""

        url = BASE_HOST+"/load_link/"+id
        return requests.get(url, headers={"User-Agent":"GameMaker HTTP"}).text.replace("\"", "")

    def like_level(self, level_id:str):
        """Add a like to a level\n
        Only one like or dislike can be added to each level per account"""

        if self.auth.uid == None:
            raise NotLoggedIn("You must log in first")
        url = BASE_HOST+f"/stage/{level_id}/stats/likes"
        data = {
            "token":"ponkis16122",
            "auth_code":self.auth.code,
            "discord_id":self.auth.uid
        }
        return requests.post(url, data, headers={"User-Agent":"GameMaker HTTP"})

    def dislike_level(self, level_id:str):
        """Add a dislike to a level\n
        Only one like or dislike can be added to each level per account"""

        if self.auth.uid == None:
            raise NotLoggedIn("You must log in first")
        url = BASE_HOST+f"/stage/{level_id}/stats/dislikes"
        data = {
            "token":"ponkis16122",
            "auth_code":self.auth.code,
            "discord_id":self.auth.uid
        }
        return requests.post(url, data, headers={"User-Agent":"GameMaker HTTP"})

    def add_death(self, level_id:str):
        """Add a death count to a level"""
        if self.auth.uid == None:
            raise NotLoggedIn("You must log in first")
        url = BASE_HOST+f"/stage/{level_id}/stats/muertes"
        data = {
            "token":"ponkis16122",
            "auth_code":self.auth.code,
            "discord_id":self.auth.uid
        }
        return requests.post(url, data, headers={"User-Agent":"GameMaker HTTP"})

    def add_attempt(self, level_id:str):
        """Add an attempt count to a level"""

        if self.auth.uid == None:
            raise NotLoggedIn("You must log in first")
        url = BASE_HOST+f"/stage/{level_id}/stats/intentos"
        data = {
            "token":"ponkis16122",
            "auth_code":self.auth.code,
            "discord_id":self.auth.uid
        }
        return requests.post(url, data, headers={"User-Agent":"GameMaker HTTP"})

    def add_victory(self, level_id:str, time_ms:int):
        """Add a victory to a level\n
        However it doesn't seem to work"""
        if self.auth.uid == None:
            raise NotLoggedIn("You must log in first")
        url = BASE_HOST+f"/stage/{level_id}/stats/intentos"
        data = {
            "token":"ponkis16122",
            "auth_code":self.auth.code,
            "discord_id":self.auth.uid,
            "tiempo":str(time_ms)
        }
        return requests.post(url, data, headers={"User-Agent":"GameMaker HTTP"})

    def get_leaderboard(self, auth:Auth) -> dict:
        """Fetches the leaderboard as JSON data"""

        if auth.uid == None:
            raise NotLoggedIn("You must log in first")
        url = BASE_HOST+"/stages/records/leaderboard"
        data = {
            "token":"ponkis16122",
            "auth_code":auth.code,
            "discord_id":auth.uid
        }
        return requests.post(url, data, headers={"User-Agent":"GameMaker HTTP"}).json()

    def delete_level(self, level_id:str):
        """Deletes a level uploaded by the user"""

        if self.auth.uid == None:
            raise NotLoggedIn("You must log in first")
        url = BASE_HOST+f"/stage/{level_id}/delete"
        data = {
            "token":"ponkis16122",
            "auth_code":self.auth.code,
            "discord_id":self.auth.uid
        }
        return requests.post(url, data, headers={"User-Agent":"GameMaker HTTP"})

    def search_levels(self, page:int = 1, *, title:str = None, author_alias:str = None, author_id:str = None, tags:tuple[str,str] = ("", ""), liked_by:str = None) -> list:
        """Search levels with specified filters\n
        TODO: Add more search parameters"""

        if self.auth.uid == None:
            raise NotLoggedIn("You must log in first")
        url = BASE_HOST+"/stages/detailed_search"
        data = {
            "token": "ponkis16122",
            "discord_id": self.auth.uid,
            "auth_code": self.auth.code,
            "page":str(page),
        }
        if title:
            data.update({"title":title})
        if author_alias:
            data.update({"author":author_alias})
        if liked_by:
            data.update({"liked":liked_by})
        if tags != ("", ""):
            data.update({"tags":f"{tags[0]},{tags[1]}"})
        if author_id:
            data.update({"author_id":author_id})
        resp:dict = requests.post(url, data, headers={"User-Agent":"GameMaker HTTP"}).json()
        if "error_type" in resp.keys():
            return []
        else:
            return resp["result"]

    def save_level(self, id:str, path:str, decoded:bool = False):
        """Save a level to a file using its ID\n
        Does not require to be logged in
        Set decoded to True to decode and save it as JSON instead"""

        url = self.level_url_from_id(id)
        with open(path, "wb+") as lf:
            data = requests.get(url).content
            if decoded:
                data = base64.b64decode(data).decode()
                data = json.dumps(json.loads(data), indent=4).encode()
            lf.write(data, headers={"User-Agent":"GameMaker HTTP"})

    def get_user_data(self) -> UserData:
        """Fetches the user's data"""
        if self.auth.uid == None:
            raise NotLoggedIn("You must log in first")

        url = BASE_HOST+"/showdata"
        data = {
            "token":"ponkis16122",
            "auth_code":self.auth.code,
            "discord_id":self.auth.uid
        }
        raw_data:dict = requests.post(url, data, headers={"User-Agent":"GameMaker HTTP"}).json()
        user_data = UserData()
        user_data.user_id = raw_data["discord_id"]
        user_data.easy_progress = raw_data["easy_progress"]
        user_data.normal_progress = raw_data["normal_progress"]
        user_data.hard_progress = raw_data["hard_progress"]
        user_data.expert_progress = raw_data["expert_progress"]
        user_data.easy_lives = raw_data["easy_lives"]
        user_data.normal_lives = raw_data["normal_lives"]
        user_data.hard_lives = raw_data["hard_lives"]
        user_data.expert_lives = raw_data["expert_lives"]
        user_data.easy_record = raw_data["easy_record"]
        user_data.normal_record = raw_data["normal_record"]
        user_data.hard_record = raw_data["hard_record"]
        user_data.expert_record = raw_data["expert_record"]
        user_data.is_banned = raw_data["is_banned"]
        return user_data

    def set_dsm_record(self, mode:int, record:int, lives:int):
        """Modifies own's DSM record\n
        Records cannot be lowered\n
        Modes:\n
        0 = Easy\n
        1 = Normal\n
        2 = Hard\n
        3 = Expert\n
        An invalid mode defaults to easy"""
        if self.auth.uid == None:
            raise NotLoggedIn("You must log in first")

        url = BASE_HOST+"/setrecord"
        match mode:
            case 1:
                str_mode = "normal"
            case 2:
                str_mode = "hard"
            case 3:
                str_mode = "expert"
            case _:
                str_mode = "easy"
        data = {
            "token":"ponkis16122",
            "auth_code":self.auth.code,
            "discord_id":self.auth.uid,
            "mode":str_mode,
            "record":record,
            "lives":lives
        }
        r =  requests.post(url, data, headers={"User-Agent":"GameMaker HTTP"})
        if "error_type" in r.json().keys():
            return False
        return True

    def get_level_data(self, id:str) -> dict:
        """Fetches the data of a level using its ID"""
        if self.auth.uid == None:
            raise NotLoggedIn("You must log in first")

        url = BASE_HOST+"/stage/"+id
        data = {
            "token":"ponkis16122", 
            "auth_code":self.auth.code,
            "discord_id":self.auth.uid
        }
        return requests.post(url, data, headers={"User-Agent":"GameMaker HTTP"}).json()

# -----------------------------------------------------------------#

if __name__=="__main__":
    print("smmwe should be imported, not directly run")
