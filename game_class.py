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
URL=os.environ.get("RNG_URL")
PARAMS_FOR_DIFFICULTY_LEVEL_ZERO=json.loads(os.environ.get("RNG_PARAMS_FOR_DIFFICULTY_LEVEL_ZERO"))
PARAMS_FOR_DIFFICULTY_LEVEL_ONE=json.loads(os.environ.get("RNG_PARAMS_FOR_DIFFICULTY_LEVEL_ONE"))
PARAMS_FOR_DIFFICULTY_LEVEL_TWO=json.loads(os.environ.get("RNG_PARAMS_FOR_DIFFICULTY_LEVEL_TWO"))
KEYWORDS=["/guess_history", "/hint", "/hint_history", "/score"]
TITLE="""\r
 __  __           _____ _______ ______ _____  __  __ _____ _   _ _____  _ 
|  \/  |   /\    / ____|__   __|  ____|  __ \|  \/  |_   _| \ | |  __ \| |
| \  / |  /  \  | (___    | |  | |__  | |__) | \  / | | | |  \| | |  | | |
| |\/| | / /\ \  \___ \   | |  |  __| |  _  /| |\/| | | | | . ` | |  | | |
| |  | |/ ____ \ ____) |  | |  | |____| | \ \| |  | |_| |_| |\  | |__| |_|
|_|  |_/_/    \_\_____/   |_|  |______|_|  \_\_|  |_|_____|_| \_|_____/(_)
                                                                          
                                                                          
"""
LINE="\r---------------------------------------------------------------------------------------------------------------------------------"


#main game class
class Game:
    def __init__(self, show_ans: bool=False):
        self.play_welcome_animation()
        self.score = self.read_score_from_file()
        self.difficulty = self.input_user_difficulty()
        # self.ans = self.fetch_answer()
        self.ans = "1234"
        self.hints = self.generate_hints()
        self.hints_idx = 0
        self.digit_count = 4 + self.difficulty
        self.guesses_remaining = 10
        self.guess_history = []
        self.show_ans = show_ans
        print("\rSYS_MESSAGE: show_ans = True. Answer = ",self.ans,"\n") if show_ans == True else True
        print(f"MASTERMIND: I'm thinking of a {self.digit_count} digit number using digits between 0 and 7. Try and guess it, if you dare!\n")
        self.run_game()

    def play_welcome_animation(self, replay: bool=False) -> None:
        """

        # this function clears the terminal and prints the welcome animation to start the game. if replay boolean is true, function slightly alters welcome message.

        Args:
            None
        Returns:
            None

        """
        os.system("clear")

        if replay == False:
            print("Welcome! You have entered the lair of the...")
        else:
            print("Ah! I see you have returned. You have once again entered the lair of the...")
        time.sleep(2.0)
        print(TITLE)
        time.sleep(3.0)
        os.system("clear")
    
    def input_user_difficulty(self) -> int:
        """

        this function prompts the user to enter their desired difficulty as a string, validates it (re-prompting for input if failed validation), and returns it as an integer to be saves in an instance attribute

        Args:
            None
        Returns:
            0 (int)

        """
        print("MASTERMIND: Enter a difficulty (hard, harder, or hardest):\n")
        sys.stdout.write("Difficulty: ")
        verbose_difficulty = input()
        print("\n",LINE,"\n")
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

    def fetch_answer(self) -> str:
        """
        
        this function uses the random number generator API and the corresponding API parameters (different difficulties of game require different parameters) to generate an answer string that is returned and saved as the self.ans instance variable

        Args:
            None
        Returns:
            "1234" (str)

        """
        if self.difficulty == 1:
            raw_ans = requests.get(url=URL, params=PARAMS_FOR_DIFFICULTY_LEVEL_ONE)
        elif self.difficulty == 2:
            raw_ans = requests.get(url=URL, params=PARAMS_FOR_DIFFICULTY_LEVEL_TWO)
        else:
            raw_ans = requests.get(url=URL, params=PARAMS_FOR_DIFFICULTY_LEVEL_ZERO)

        ans = raw_ans.text.replace("\n","")

        return ans
    
    def read_score_from_file(self) -> int:
        """
        
        this function reads ../mastermind_lite/score.txt and checks the score. if file read fails for any reason, score is assigned as 0

        Args:
            None
        Returns:
            1 (int)
        
        """
        f = open("score.txt","r")
        score = 0
        try:
            score = int(f.read()[-1])
        except BaseException as e:
            pass
        finally:
            return score

    def increment_score_in_file(self) -> None:
        """
        
        this function reads the current score from the score instance variable, increments the score by 1 and rewrites score.txt to persist that change in score. finally it prints that score to the terminal

        Args:
            None
        Returns:
            None
        
        """
        self.score += 1
        try:
            f = open("score.txt", "w")
            f.write(f"Score: {self.score}")
            f.close()
        except BaseException as e:
            pass
        finally:
            sys.stdout.write(f"\n\rScore: {self.score}\n")

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
        """

        this function passes in the user's input_guess and validates it across 3 parameters:

        1. len of input_guess should be the same as the digit count instance attribute (ln 183)

        2. digits in input_guess should only be from 0-7, inclusive (ln 183)

        3. input_guess only contains chars that can be cast as an integer (ln 195)

        Args:
            input_guess: str = "1234"
        Returns:
            "1234"
            
        """    
        while True:

            if input_guess in KEYWORDS:
                return input_guess
            try:
                if len(input_guess) != self.digit_count or "8" in input_guess or "9" in input_guess:
                    print(f"\nMASTERMIND: I tire of your ignorance! Your guess must be {self.digit_count} digits, each between 0 and 7, inclusive!\n")
                    print(LINE,"\n")
                    print("Hints Remaining (type /hint to see a hint or /hint_history):", 3 - self.hints_idx - self.difficulty)
                    print("Guesses Remaining:",self.guesses_remaining)
                    sys.stdout.write("Guess: ")
                    input_guess = input()
                    if input_guess in KEYWORDS:
                        return input_guess
                int(input_guess)
            except ValueError as v:
                print(f"\nMASTERMIND: You fool - what do you mean, \"{input_guess}\"?! I demand that enter {self.digit_count} digits between 0-7, inclusive.\n")
                print(LINE,"\n")
                print("Hints Remaining (type /hint to see a hint):", 3 - self.hints_idx)
                print("Guesses Remaining:",self.guesses_remaining)
                sys.stdout.write("Guess: ")
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
        print("\n \rGuess History:\n")
        for idx in range(len(self.guess_history)):
            print(f"{idx+1}: ",self.guess_history[idx])
        print("\n \n")

    def handle_hint_commmand(self) -> None:
        if self.hints_idx > 2 - self.difficulty:
            print("\nMASTERMIND: YOU HAVE NO MORE HINTS!\n")
        else:
            latest_hint = self.hints[self.hints_idx]
            print(latest_hint, "\n")
            self.hints_idx += 1


    def handle_hint_history_command(self) -> None:
        if self.hints_idx-1 >= 0:
            print("\nHint History:")
            for idx in range(self.hints_idx):
                print(self.hints[idx])
            print("\n")
        else:
            print("\nYou haven't asked for any hints yet; enter the command /hint to ask for a hint.\n")

    def handle_score_command(self) -> None:
        sys.stdout.write(f"\n\rMASTERMIND: Hah! Your score is only {self.score}!\n")



    def handle_keyword(self, keyword: str):
        match keyword:
            case "/hint":
                self.handle_hint_commmand()
            case "/guess_history":
                self.handle_guess_history_command()
            case "/hint_history":
                self.handle_hint_history_command()
            case "/score":
                self.handle_score_command()
            case _:
                pass

    def handle_victory_and_ask_replay(self) -> bool:
        print("\nVICTORY\n")
        self.increment_score_in_file()
        if self.ask_user_replay() == True:
            return True
        else:
            print("\nMASTERMIND: I'll get you next time!!!")
            return False

    def ask_user_replay(self) -> bool:
        while True:
            sys.stdout.write("\nPlay again? (y/n): ")
            play_again_response = input()
            if play_again_response.lower() not in ["y", "n", "yes", "no"]:
                print("\nPlease answer y or n!")
            elif play_again_response in ["n", "no"]:
                return False
            else:
                return True

    def handle_replay(self) -> None:
        self.play_welcome_animation(replay=True)
        self.score = self.read_score_from_file()
        self.difficulty = self.input_user_difficulty()
        self.ans = self.fetch_answer()
        print("\rSYS_MESSAGE: show_ans = True. Answer = ",self.ans,"\n") if self.show_ans == True else True
        print(f"MASTERMIND: I'm thinking of a {self.digit_count} digit number using digits between 0 and 7. Try and guess it, if you dare!\n")
        self.hints = self.generate_hints()
        self.hints_idx = 0
        self.digit_count = 4 + self.difficulty
        self.guesses_remaining = 10
        self.guess_history = []
        return

    def run_game(self):
        while self.guesses_remaining > 0:
            print(LINE,"\n")
            try:
                print("Hints Remaining (enter /hint to see a hint or /hint_history to see Hint History):", 3 - self.hints_idx - self.difficulty)
                print("Guesses Remaining (enter /guess_history to see Guess History):",self.guesses_remaining)
                sys.stdout.write("Guess: ")
                guess = input()
                if guess in KEYWORDS:
                    self.handle_keyword(guess)
                elif guess == self.ans:
                    if self.handle_victory_and_ask_replay() == True:
                        self.handle_replay()
                        continue
                    else:
                        return
                else:
                    validated_guess = self.validate_guess(guess)
                    guess_feedback = self.generate_guess_feedback(validated_guess)
                    print(guess_feedback)
                    self.guess_history.append(guess_feedback)
                    self.guesses_remaining -= 1
                    pass
            except Exception as e:
                print("MASTERMIND: Try again...\n")
        print("\nYOU LOSE\n")




# def timer():
#     timer = 10
#     while timer > 0:
#         time.sleep(1.0)
#         sys.stdout.write(f"Timer: \r{timer}")
#         timer -=1

# # timer()



