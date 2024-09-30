import requests
import time
import json
import hmac
import hashlib
import random
from datetime import datetime
import pytz
import os
import sys
import math
from colorama import init, Fore, Style

# Initialize Colorama
init(autoreset=True)

def compute_score(i, s, a, o, d, g):
    st = (10 * i + max(0, 1200 - 10 * s) + 2000) * (1 + o / a) / 10
    return math.floor(st) + calculate_value(g)

def create_hash(key, message):
    try:
        hmac_obj = hmac.new(key.encode(), message.encode(), hashlib.sha256)
        return hmac_obj.hexdigest()
    except Exception as e:
        print(f"Hash generation error: {str(e)}")
        return None

def calculate_value(input_str):
    return sum(ord(char) for char in input_str) / 1e5

class ByBitGameBot:
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://api.bybitcoinsweeper.com/api"
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0"
        }
        self.info = {
            "score": 0  # Initialize user score
        }
        self.max_game_time = 10  # Default value
        self.min_game_time = 5    # Default value
        self.always_win = False    # Default value
        self.load_configuration()

    def load_configuration(self):
        config_file = 'config.json'
        try:
            with open(config_file, 'r') as file:
                config = json.load(file)
                self.max_game_time = config.get("max_game_time", 10)
                self.min_game_time = config.get("min_game_time", 5)
                self.always_win = config.get("always_win", False)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            self.log_message("Config Load Error", str(e), "ERROR")

    def log_message(self, description, details, level=""):
        levels = {
            "ERROR": Fore.RED,
            "SUCCESS": Fore.GREEN,
            "WARNING": Fore.YELLOW,
            "INFO": Fore.CYAN
        }
        level_color = levels.get(level, Fore.CYAN)
        details_colored = level_color + details
        print(f"[INFO] {description} - {details_colored}")

    def pause(self, sec):
        description = "Waiting"
        sys.stdout.write(f"[INFO] {description} - Sec")

        for i in range(sec, 0, -1):
            time.sleep(1)
            sys.stdout.write('\r' + f"[INFO] {description} - {i} Sec")
            sys.stdout.flush()

        print()

    def fetch_user_info(self):
        response = self.session.get(f"{self.base_url}/users/me", headers=self.headers)
        if response.ok:
            return response.json()
        self.log_message("Failed to retrieve user information.", "ERROR")
        return {}

    def execute_win(self):
        try:
            game_time = random.randint(self.min_game_time, self.max_game_time)
            playgame = self.session.post(f"{self.base_url}/games/start", json={}, headers=self.headers).json()
            if "message" in playgame and "expired" in playgame["message"]:
                self.log_message("Token Error", "Please Update Token.", "ERROR")
                sys.exit(0)

            gameid = playgame["id"]
            rewarddata = playgame["rewards"]
            started_at = playgame["createdAt"]
            userdata = self.fetch_user_info()
            balance = userdata.get('score', 0) + userdata.get('scoreFromReferrals', 0)
            self.log_message("Balance", str(balance), "INFO")
            unix_time_started = datetime.strptime(started_at, '%Y-%m-%dT%H:%M:%S.%fZ')
            unix_time_started = unix_time_started.replace(tzinfo=pytz.UTC)
            starttime = int(unix_time_started.timestamp() * 1000)
            self.log_message("Start Game", "Success!!", "INFO")
            self.pause(game_time)

            i = f"{userdata['id']}v$2f1"
            first = f"{i}-{gameid}-{starttime}"
            last = f"{game_time}-{gameid}"
            score = compute_score(45, game_time, 54, 9, True, gameid)  # Calculate score using compute_score

            game_data = {
                "bagCoins": rewarddata["bagCoins"],
                "bits": rewarddata["bits"],
                "gifts": rewarddata["gifts"],
                "gameId": gameid,
                'gameTime': game_time,
                "h": create_hash(first, last),
                'score': float(score)
            }
            res = self.session.post(f'{self.base_url}/games/win', json=game_data, headers=self.headers)
            if res.status_code == 201:
                self.info["score"] += score
                self.log_message("Update Status", "YOU WIN", "SUCCESS")
            elif res.status_code == 401:
                self.log_message("Token Error", "Please Update Token", "ERROR")
                return False
            self.pause(5)
        except requests.RequestException:
            self.log_message("Too Many Requests", "ERROR")
            self.pause(60)

    def execute_loss(self):
        try:
            game_time = random.randint(self.min_game_time, self.max_game_time)
            playgame = self.session.post(f"{self.base_url}/games/start", json={}, headers=self.headers).json()
            if "message" in playgame and "expired" in playgame["message"]:
                self.log_message("Token Error", "Please Update Token.", "ERROR")
                sys.exit(0)

            gameid = playgame["id"]
            rewarddata = playgame["rewards"]
            started_at = playgame["createdAt"]
            userdata = self.fetch_user_info()
            balance = userdata.get('score', 0) + userdata.get('scoreFromReferrals', 0)
            self.log_message("Balance", str(balance), "INFO")
            unix_time_started = datetime.strptime(started_at, '%Y-%m-%dT%H:%M:%S.%fZ')
            unix_time_started = unix_time_started.replace(tzinfo=pytz.UTC)
            self.log_message("Start Game", "Success!", "INFO")
            self.pause(game_time)

            game_data = {
                "bagCoins": rewarddata["bagCoins"],
                "bits": rewarddata["bits"],
                "gifts": rewarddata["gifts"],
                "gameId": gameid
            }
            res = self.session.post(f'{self.base_url}/games/lose', json=game_data, headers=self.headers)
            if res.status_code == 201:
                self.log_message("Update Status", "YOU LOSE", "ERROR")
            elif res.status_code == 401:
                self.log_message("Token Error", "Please Update Token", "ERROR")
                return False
            self.pause(5)
        except requests.RequestException:
            self.log_message("Too Many Requests", "ERROR")
            self.pause(60)

    def play_game(self):
        for _ in range(3):
            try:
                if self.always_win:  # Check if always_win is set
                    self.execute_win()
                else:  # Random mode
                    is_win = random.random() < 0.8  # 80% chance of winning
                    if is_win:
                        self.execute_win()
                    else:
                        self.execute_loss()
            except Exception as e:
                self.log_message("Error in scoring", str(e), "ERROR")
        return True

    def login(self, init_data):
        try:
            self.headers["tl-init-data"] = init_data
            
            response = self.session.post(
                f"{self.base_url}/auth/login",
                json={"initData": init_data},
                headers=self.headers
            )

            if response.status_code == 201:
                data = response.json()
                self.headers['Authorization'] = f"Bearer {data['accessToken']}"
                return True
            else:
                error_message = response.json().get('message', 'Unexpected error')
                self.log_message("Login Failed: " + error_message, "ERROR")
                return False

        except requests.RequestException as error:
            self.log_message("Request Error During Login: " + str(error), "ERROR")
            return False

    def load_init_data(self, filename):
        try:
            with open(filename, 'r') as file:
                return [line.strip() for line in file if line.strip()]
        except FileNotFoundError:
            self.log_message(f"File '{filename}' not found.", "ERROR")
            return []

    def run(self):
        print("=== ByBit Game Bot ===")
        init_data_list = self.load_init_data('data.txt')
        for init_data in init_data_list:
            if self.login(init_data):
                while True:  # Continue playing indefinitely
                    self.play_game()  # Play rounds based on scoring method
                    time.sleep(random.randint(4, 8))  # Random delay between rounds

if __name__ == "__main__":
    bot = ByBitGameBot()
    bot.run()
