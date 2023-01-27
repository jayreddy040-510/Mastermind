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

# test_func()

def generate_guess_feedback(self, validated_guess: str) -> str | dict[str, int]:

        """
        
        this function details the core logic behind allocating "correct number," "correct location," or
        "all incorrect" feedback info to give to user after each validated guess
        
        Example Arg(s):
            "1454" (str)
        Example Return:
            "Feedback for 1454: {'correct number': 2, 'correct location': 2}" (str)

        """

        ans = "0131"
        ans_counter: list = [0,0,0,0,0,0,0,0,0,0]
        guess_counter: list = [0,0,0,0,0,0,0,0,0,0]
        ret = {"correct number": 0, "correct location": 0}

        for x in range(4):
            ans_digit = int(ans[x])
            validated_guess_digit = int(validated_guess[x])

            if ans_char == validated_guess_char:
                ret["correct location"] += 1

            ans_counter[ans_digit] += 1
            guess_counter[validated_guess_digit] += 1

        for idx in range(10):
            ret["correct_number"] += min(ans_counter[idx], guess_counter[idx])
        ret["correct_number"] -= ret["correct_location"]
        
        ret = "all incorrect" if ret["correct location"] + ret["correct number"] == 0 else ret
        return f"Feedback for {validated_guess}: {ret}\n"
