import unittest
import re
import threading
import requests
import time

# x = 4

# if re.match(r"^[0-7]{%s}$"%(x), "7341"):
#     print("lol")
# else:
#     print("no")

# def handle_hint_keyword():
#     print("hi")


# keyword_function_mapping = {
#                             "/hint":handle_hint_keyword(),
#                             "/guess_history":self.handle_guess_history_keyword(),
#                             "/hint_history":self.handle_hint_history_keyword(),
#                             "/score":self.handle_score_keyword()
#                             }


# print(keyword_function_mapping["/hint"])
def fetch_answer():
    print("starting API call")
    ans = requests.get(
                    url="https://www.random.org/integers/",
                    params={"num": 4, "min": 0, "max": 7, "col": 1, "base": 10, "format": "plain", "rnd": "new"}
                    )
    print("done", ans.text.replace("\n",""))
def test_func():
    thread = threading.Thread(target=fetch_answer)
    x = 0
    thread.start()
    while x < 100:
        x+=1
        print(x)
        time.sleep(1.0)

test_func()
