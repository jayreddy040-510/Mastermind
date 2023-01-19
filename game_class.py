import requests
import os
import sys
import json
import time
import random
import re
from dotenv import load_dotenv
from collections import defaultdict

#loads env
load_dotenv()

#gets different RNG parameters from RNG API based off of difficulty level
URL = os.environ.get("RNG_URL")
PARAMS_FOR_DIFFICULTY_LEVEL_ZERO = json.loads(os.environ.get("RNG_PARAMS_FOR_DIFFICULTY_LEVEL_ZERO"))
PARAMS_FOR_DIFFICULTY_LEVEL_ONE = json.loads(os.environ.get("RNG_PARAMS_FOR_DIFFICULTY_LEVEL_ONE"))
PARAMS_FOR_DIFFICULTY_LEVEL_TWO = json.loads(os.environ.get("RNG_PARAMS_FOR_DIFFICULTY_LEVEL_TWO"))
KEYWORDS = ["/guess_history", "/hint", "/hint_history"]
TITLE="""  
  __  __           _____ _______ ______ _____  __  __ _____ _   _ _____  _ 
 |  \/  |   /\    / ____|__   __|  ____|  __ \|  \/  |_   _| \ | |  __ \| |
 | \  / |  /  \  | (___    | |  | |__  | |__) | \  / | | | |  \| | |  | | |
 | |\/| | / /\ \  \___ \   | |  |  __| |  _  /| |\/| | | | | . ` | |  | | |
 | |  | |/ ____ \ ____) |  | |  | |____| | \ \| |  | |_| |_| |\  | |__| |_|
 |_|  |_/_/    \_\_____/   |_|  |______|_|  \_\_|  |_|_____|_| \_|_____/(_)
                                                                           
                                                                           
"""


#main game class
class Game:
    def __init__(self, cheater: bool=False):
        self.generate_welcome_animation()
        self.score = self.read_score_from_file()
        self.difficulty = self.input_user_difficulty()
        self.ans = self.fetch_answer(self.difficulty)
        self.hints = self.generate_hints()
        self.hints_history_idx = 0
        self.digit_count = 4 + self.difficulty
        self.guesses_remaining = 10
        self.guess_history = []
        print("\n","\rSYS_MESSAGE: ~Cheater, cheater, pumpkin eater:",self.ans,"\n") if cheater == True else True
        print(f"MASTERMIND: I'm thinking of a {self.digit_count} digit number using digits between 0 and 7. Try and guess it, if you dare!\n")
        self.run_game()

    def generate_welcome_animation(self):
        os.system("clear")
        print("Welcome! You have entered the lair of the...")
        time.sleep(2.0)
        print(TITLE)
        time.sleep(2.0)
        os.system("clear")
    
    def input_user_difficulty(self) -> int:
        print("MASTERMIND: Enter a difficulty (hard, harder, or hardest):\n")
        verbose_difficulty = input()
        while verbose_difficulty.lower() not in ["hard", "harder", "hardest"]:
            print("\nMASTERMIND: Ugh! I said choose between hard, harder, or hardest!!!\n")
            print("Enter a difficulty (hard, harder, or hardest):")
            verbose_difficulty = input()
        if verbose_difficulty.lower() == "hard":
            difficulty = 0
        elif verbose_difficulty.lower() == "harder":
            difficulty = 1
        else:
            difficulty = 2
        return difficulty

    def fetch_answer(self, difficulty) -> str:
        if difficulty == 1:
            raw_ans = requests.get(url=URL, params=PARAMS_FOR_DIFFICULTY_LEVEL_ONE)
        elif difficulty == 2:
            raw_ans = requests.get(url=URL, params=PARAMS_FOR_DIFFICULTY_LEVEL_TWO)
        else:
            raw_ans = requests.get(url=URL, params=PARAMS_FOR_DIFFICULTY_LEVEL_ZERO)

        ans = raw_ans.text.replace("\n","")

        return ans
    
    def read_score_from_file(self) -> int:
        f = open("score.txt","r")
        score = 0
        try:
            score = int(f.read()[-1])
        except BaseException as e:
            pass
        finally:
            return score

    def increment_score_in_file(self) -> None:
        try:
            f = open("score.txt", "r")
            x = (int(f.read()[-1]))
            f.close()
        except BaseException as e:
            x = 0
        finally:
            f = open("score.txt", "w")
            f.write(f"score: {x+1}")
            f.close()
            f = open("score.txt", "r")
            print(f.read())
            f.close()

    def generate_hint(self, hint_num: int) -> str:
        match hint_num:
            case 0:
                return f"\nMASTERMIND: A hint?! Really?! You need a hint?! Fine. The last digit of the number in my head is {self.ans[-1]}"
            case 1:
                sum = 0
                for idx in range(len(self.ans)):
                    sum += int(self.ans[idx])
                return f"\nMASTERMIND: FINE. The sum of the digits for the number in my head is {sum}"
            case 2:
                less_than_equal_3_count = 0
                for idx in range(len(self.ans)):
                    if int(self.ans[idx]) <= 3:
                        less_than_equal_3_count += 1
                return f"\nMASTERMIND: There are {less_than_equal_3_count} digits in the number in my head that are less than or equal to 3"
            case 3:
                product = 1
                for idx in range(len(self.ans)):
                    product *= int(self.ans[idx])
                return f"\nMASTERMIND: FINE. The product of the digits for the number in my head is {product}"
            case 4:
                 while True:
                    hint = str(random.randint(0,7))
                    if hint not in self.ans:
                        return f"\nMASTERMIND: {hint} is not a digit in the number I am thinking of"
        return ""

    def generate_hints(self) -> list:
        # num_total_hints_in_hints_bank = number of total possible hints that hints are being chosen from
        num_hints_in_hints_bank = 5
        hints = []
        possible_hints = set(range(num_hints_in_hints_bank))
        while len(hints) < 3 - self.difficulty:
            random_hint_num = random.randint(0,num_hints_in_hints_bank-1)
            if random_hint_num in possible_hints:
                hints.append(self.generate_hint(random_hint_num))
                possible_hints.remove(random_hint_num)
        return hints
        

    def validate_guess(self, input_guess: str) -> str:
            
        valid_guess = False
        while valid_guess == False:
            #guess_history, hint, and hint_history commands inside guess validation failure loop
            if input_guess in KEYWORDS:
                return input_guess
            try:
                #checks for length = digit_count (varies based on difficulty) and whether digits are between 0-7
                #if input is not in proper format, asks for input again.
                if len(input_guess) != self.digit_count or "8" in input_guess or "9" in input_guess:
                    print(f"\nMASTERMIND: I tire of your ignorance! Your guess must be {self.digit_count} digits, each between 0 and 7, inclusive!\n")
                    print("Hints Remaining (type /hint to see a hint):", 3 - self.hints_history_idx - self.difficulty)
                    print("Guesses Remaining:",self.guesses_remaining)
                    sys.stdout.write("Guess:\t")
                    input_guess = input()
                    if input_guess in KEYWORDS:
                        return input_guess
                int(input_guess)
            except ValueError as v:
                print(f"\nMASTERMIND: You fool - what do you mean, \"{input_guess}\"?! I demand that you only enter digits between 0-7, inclusive.\n")
                print("Hints Remaining (type /hint to see a hint):", 3 - self.hints_history_idx)
                print("Guesses Remaining:",self.guesses_remaining)
                sys.stdout.write("Guess:\t")
                input_guess = input()
            else:
                return f"{input_guess}"

    def generate_guess_feedback(self, guess: str) -> str | dict[str, int]:
        if guess in KEYWORDS:
            return guess
        guess = self.validate_guess(guess)
        ans = self.ans
        ret = {"correct number": 0, "correct location": 0}
        ans_count = defaultdict(int)
        guess_count = defaultdict(int)

        for x in range(self.digit_count):
            if ans[x] == guess[x]:
                ret["correct location"] += 1
            ans_count[ans[x]] += 1
            guess_count[guess[x]] += 1
        
        for key in ans_count:
            if guess_count[key] > 0:
                ret["correct number"] += min(ans_count[key], guess_count[key])
        
        ret = "all incorrect" if ret["correct location"] + ret["correct number"] == 0 else ret
        return f"Feedback for {guess}: {ret}\n"

    def handle_guess_history_command(self) -> None:
        print("\n \rGuess History:")
        for idx in range(len(self.guess_history)):
            print(f"{idx+1}: ",self.guess_history[idx])
        print("\n \n")

    def handle_hint_commmand(self) -> None:
        if self.hints_history_idx > 2 - self.difficulty:
            print("\nMASTERMIND: YOU HAVE NO MORE HINTS!\n")
        else:
            latest_hint = self.hints[self.hints_history_idx]
            print(latest_hint, "\n")
            self.hints_history_idx += 1


    def handle_hint_history_command(self) -> None:
        if self.hints_history_idx-1 >= 0:
            print("\nHint History:")
            for idx in range(self.hints_history_idx):
                print(self.hints[idx])
            print("\n")
        else:
            print("\nYou haven't asked for any hints yet; enter the command /hint to ask for a hint.\n")

    def handle_keyword(self, keyword: str):
        if keyword == "/hint":
            self.handle_hint_commmand()
        elif keyword == "/guess_history":
            self.handle_guess_history_command()
        elif keyword == "/hint_history":
            self.handle_hint_history_command()
        else:
            pass

    # def turn(self):
    #     try:
    #         print("Hints Remaining (type /hint to see a hint):", 3 - self.hints_history_idx)
    #         print("Guesses Remaining (type /guess_history to see Guess History):",self.guesses_remaining)
    #         sys.stdout.write("Guess:\t")
    #         guess = input()
    #         if guess in KEYWORDS:
    #             return guess
    #         if guess == self.ans:
    #             return "victory"
    #         guess_feedback = self.guess_feedback(guess)

    #         if guess_feedback in KEYWORDS:
    #             return guess_feedback
    #         else:
    #             print(guess_feedback)
    #             self.guess_history.append(guess_feedback)
    #     except Exception as e:
    #         print("Try again...")

    def run_game(self):
        while self.guesses_remaining > 0:
            try:
                print("Hints Remaining (type /hint to see a hint):", 3 - self.hints_history_idx - self.difficulty)
                print("Guesses Remaining (type /guess_history to see Guess History):",self.guesses_remaining)
                sys.stdout.write("Guess:\t")
                guess = input()
                if guess in KEYWORDS:
                    self.handle_keyword(guess)
                elif guess == self.ans:
                    print("\nVICTORY\n")
                    self.increment_score_in_file()
                else:
                    validated_guess = self.validate_guess(guess)
                    guess_feedback = self.generate_guess_feedback(validated_guess)
                    print(guess_feedback)
                    self.guess_history.append(guess_feedback)
                    self.guesses_remaining -= 1
                    pass
            except Exception as e:
                print("Try again...")
        print("\nYOU LOSE\n")



g = Game(cheater=True)



# def timer():
#     timer = 10
#     while timer > 0:
#         time.sleep(1.0)
#         sys.stdout.write(f"Timer: \r{timer}")
#         timer -=1

# # timer()



