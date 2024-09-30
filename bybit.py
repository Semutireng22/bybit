import requests
import time
import json
import hmac
import hashlib
import random
from datetime import datetime
import pytz
import sys

class ByBitGameBot:
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://api.bybitcoinsweeper.com/api"
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0"
        }
        self.user_data = {}
        self.info = {
            "score": 0  # Initialize user score
        }
        self.config = self.load_config()

    def load_config(self):
        try:
            with open('config.json', 'r') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"always_win": False}  # Default to not always win

    def log(self, title, message, level="INFO"):
        color_codes = {
            "INFO": "\033[94m",
            "SUCCESS": "\033[92m",
            "ERROR": "\033[91m",
            "WARNING": "\033[93m"
        }
        color = color_codes.get(level, "\033[94m")
        print(f"{color}{title}: {message}\033[0m")

    def wait(self, duration):
        print(f"Waiting for {duration} seconds...")
        for remaining in range(duration, 0, -1):
            time.sleep(1)
            print(f"{remaining} seconds remaining", end="\r")
        print("")

    def generate_hash(self, first, last):
        # Implement your hash generation logic here
        return hmac.new(first.encode(), last.encode(), hashlib.sha256).hexdigest()

    def userinfo(self):
        response = self.session.get(f"{self.base_url}/users/me", headers=self.headers)
        if response.ok:
            return response.json()
        self.log("Failed to retrieve user information.", "ERROR")
        return {}

    def score_win(self):
        try:
            min_game_time = 60
            max_game_time = 110
            game_time = random.randint(min_game_time, max_game_time)
            playgame = self.session.post(f"{self.base_url}/games/start", json={}, headers=self.headers).json()
            
            if "message" in playgame and "expired" in playgame["message"]:
                self.log("Token Error", "Please Update Token.", "ERROR")
                sys.exit(0)
                
            gameid = playgame["id"]
            rewarddata = playgame["rewards"]
            started_at = playgame["createdAt"]
            userdata = self.userinfo()
            balance = userdata.get('score', 0) + userdata.get('scoreFromReferrals', 0)
            self.log("Balance", str(balance), "")
            unix_time_started = datetime.strptime(started_at, '%Y-%m-%dT%H:%M:%S.%fZ')
            unix_time_started = unix_time_started.replace(tzinfo=pytz.UTC)
            starttime = int(unix_time_started.timestamp() * 1000)
            self.log("Start Game", "Success!!", "")
            self.wait(game_time)

            i = f"{userdata['id']}v$2f1"
            first = f"{i}-{gameid}-{starttime}"
            last = f"{game_time}-{gameid}"
            score = self.calculate_score(game_time)  # Calculate score based on game time

            game_data = {
                "bagCoins": rewarddata["bagCoins"],
                "bits": rewarddata["bits"],
                "gifts": rewarddata["gifts"],
                "gameId": gameid,
                'gameTime': game_time,
                "h": self.generate_hash(first, last),
                'score': float(score)
            }
            res = self.session.post(f'{self.base_url}/games/win', json=game_data, headers=self.headers)
            if res.status_code == 201:
                self.info["score"] += score
                self.log("Update Status", "YOU WIN", "SUCCESS")
            elif res.status_code == 401:
                self.log("Token Error", "Please Update Token", "ERROR")
                return False
            self.wait(5)
        except requests.RequestException:
            self.log("Too Many Requests", "ERROR")
            self.wait(60)

    def score_lose(self):
        try:
            min_game_time = 60
            max_game_time = 105
            game_time = random.randint(min_game_time, max_game_time)
            playgame = self.session.post(f"{self.base_url}/games/start", json={}, headers=self.headers).json()
            
            if "message" in playgame and "expired" in playgame["message"]:
                self.log("Token Error", "Please Update Token", "ERROR")
                sys.exit(0)

            gameid = playgame["id"]
            rewarddata = playgame["rewards"]
            started_at = playgame["createdAt"]
            userdata = self.userinfo()
            balance = userdata.get('score', 0) + userdata.get('scoreFromReferrals', 0)
            self.log("Balance", str(balance), "")
            unix_time_started = datetime.strptime(started_at, '%Y-%m-%dT%H:%M:%S.%fZ')
            unix_time_started = unix_time_started.replace(tzinfo=pytz.UTC)
            self.log("Start Game", "Success!", "")
            self.wait(game_time)

            game_data = {
                "bagCoins": rewarddata["bagCoins"],
                "bits": rewarddata["bits"],
                "gifts": rewarddata["gifts"],
                "gameId": gameid
            }
            res = self.session.post(f'{self.base_url}/games/lose', json=game_data, headers=self.headers)
            if res.status_code == 201:
                self.log("Update Status", "YOU LOSE", "ERROR")
            elif res.status_code == 401:
                self.log("Token Error", "Please Update Token", "ERROR")
                return False
            self.wait(5)
        except requests.RequestException:
            self.log("Too Many Requests", "ERROR")
            self.wait(60)

    def calculate_score(self, game_time):
        score = int((10 * 45 + max(0, 1200 - 10 * game_time) + 2000) * (1 + 9 / 54) / 10)
        return min(max(score, 0), 900)  # Clamp score between 0 and 900

    def score(self):
        for _ in range(3):
            try:
                is_win = random.random() < 0.8  # 80% chance to win
                if is_win:
                    self.score_win()
                else:
                    self.score_lose()
            except Exception as e:
                self.log("Error in scoring", str(e), "ERROR")
        return True

    def login(self, init_data):
        try:
            self.headers["tl-init-data"] = init_data
            
            response = self.session.post(
                "https://api.bybitcoinsweeper.com/api/auth/login",
                json={"initData": init_data},
                headers=self.headers
            )

            if response.status_code == 201:
                data = response.json()
                self.headers['Authorization'] = f"Bearer {data['accessToken']}"
                self.user_data = data  # Save user data
                return True
            else:
                error_message = response.json().get('message', 'Unexpected error')
                self.log("Login Failed: " + error_message, "ERROR")
                return False

        except requests.RequestException as error:
            self.log("Request Error During Login: " + str(error), "ERROR")
            return False

    def load_data(self, filename):
        try:
            with open(filename, 'r') as file:
                return [line.strip() for line in file if line.strip()]
        except FileNotFoundError:
            self.log(f"File '{filename}' not found.", "ERROR")
            return []

    def run(self):
        print("=== ByBit Game Bot ===")
        init_data_list = self.load_data('data.txt')
        for init_data in init_data_list:
            if self.login(init_data):
                while True:  # Continue playing indefinitely
                    self.score()  # Play rounds based on scoring method
                    time.sleep(random.randint(4, 8))  # Random delay between rounds

if __name__ == "__main__":
    bot = ByBitGameBot()
    bot.run()
