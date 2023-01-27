import requests
import os
import sys
import json
import time
import random
import re
from dotenv import load_dotenv
from collections import defaultdict
from hint_class import Hint

#loads env
load_dotenv()

#gets different RNG parameters from RNG API based off of difficulty level
URL=os.environ.get("RNG_URL")
PARAMS_FOR_DIFFICULTY_LEVEL_ZERO=json.loads(os.environ.get("RNG_PARAMS_FOR_DIFFICULTY_LEVEL_ZERO"))
PARAMS_FOR_DIFFICULTY_LEVEL_ONE=json.loads(os.environ.get("RNG_PARAMS_FOR_DIFFICULTY_LEVEL_ONE"))
PARAMS_FOR_DIFFICULTY_LEVEL_TWO=json.loads(os.environ.get("RNG_PARAMS_FOR_DIFFICULTY_LEVEL_TWO"))

#number of unique hint templates that can be used to create hints at the start of each game
NUM_UNIQUE_HINT_TEMPLATES=5

#keywords that user can input
KEYWORDS=["/guess_history", "/hint", "/hint_history", "/score"]

#various tools used for UI/UX
from uiux import TITLE, WIN_MSG, LOSE_MSG, LINE


#main game class
class Game:
    def __init__(self, show_ans: bool=False):
        self.print_welcome_animation()
        self.score: int = self.read_score_from_file()
        self.difficulty: int = self.input_user_difficulty()
        self.ans: str = self.fetch_answer()
        self.hints: list = self.generate_hints()
        self.hints_idx: int = 0
        self.digit_count: int = 4 + self.difficulty
        self.guesses_remaining: int = 10
        self.guess_history: list = []
        self.show_ans: bool = show_ans
        print("\rSYS_MESSAGE: show_ans = True. Answer = ",self.ans,"\n") if show_ans == True else True
        print(f"MASTERMIND: I'm thinking of a {self.digit_count} digit number using digits between 0 and 7. Try and guess it, if you dare!\n")
        self.run_game()

    def print_welcome_animation(self, replay: bool=False) -> None:

        """

        this function clears the terminal and prints the welcome animation to start the game. if replay boolean is true,
        function slightly alters welcome message.

        Example Arg(s):
            replay=False (default value is False) (bool)
        Example Return:
            None

        """

        os.system("clear")

        if replay == False:
            print("Welcome! You have entered the lair of the...")
        else:
            print("Ah! I see you have returned. You have once again entered the lair of the...")
        time.sleep(2.0)
        print(TITLE)
        time.sleep(2.0)
        os.system("clear")
    
    def input_user_difficulty(self) -> int:

        """

        this function prompts the user to enter their desired difficulty as a string, validates it (re-prompting 
        for input if failed validation), and returns it as an integer to be saved as an instance attribute

        Example Arg(s):
            None
        Example Return:
            0 (int)

        """

        verbose_difficulty_to_int_difficulty_mapping = {"hard":0, "harder":1, "hardest":2}

        print("MASTERMIND: Enter a difficulty (hard, harder, or hardest):\n")
        sys.stdout.write("Difficulty: ")
        verbose_difficulty = input()
        print("\n",LINE,"\n")
        while verbose_difficulty.lower() not in ["hard", "harder", "hardest"]:
            print("\nMASTERMIND: Ugh! I said choose between hard, harder, or hardest!!!\n")
            print("MASTERMIND: Enter a difficulty (hard, harder, or hardest):\n")
            sys.stdout.write("Difficulty: ")
            verbose_difficulty = input()
            print("\n",LINE,"\n")

        return verbose_difficulty_to_int_difficulty_mapping[verbose_difficulty]

    def fetch_answer(self) -> str:

        """
        
        this function uses the random number generator API and the corresponding API parameters (different
        difficulties of game require different parameters) to generate an answer string that is returned and
        saved as the self.ans instance variable

        Example Arg(s):
            None
        Example Return:
            "1234" (str)

        """
        try:
            if self.difficulty == 1:
                raw_ans = requests.get(url=URL, params=PARAMS_FOR_DIFFICULTY_LEVEL_ONE)
            elif self.difficulty == 2:
                raw_ans = requests.get(url=URL, params=PARAMS_FOR_DIFFICULTY_LEVEL_TWO)
            else:
                raw_ans = requests.get(url=URL, params=PARAMS_FOR_DIFFICULTY_LEVEL_ZERO)

            ans = raw_ans.text.replace("\n","")
        except BaseException as e:
            print(f"API FAILURE: {e}\n\nENTERING OFFLINE MODE...\n")
            ans = self.generate_offline_ans()
            

        return ans

    def generate_offline_ans(self) -> str:

        """
        
        this function is called if the RNG API can't be accessed and a random answer needs to be generated offline

        Example Arg(s):
            None
        Example Return:
            None
        
        """

        difficulty_digits_mapping = {0:4, 1:5, 2:6}
        offline_ans = ""
        for digit in range(difficulty_digits_mapping[self.difficulty]):
            offline_ans += str(random.randint(0,7))
        return offline_ans
    

    
    def read_score_from_file(self) -> int:

        """
        
        this function reads ../mastermind_lite/score.txt and checks the score. if file read fails for any reason,
        score is assigned as 0

        Example Arg(s):
            None
        Example Return:
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

        this function is called upon win condition being met (user guesses the MASTERMIND's number). it reads
        the current score from the score instance variable, increments the score by 1, and rewrites score.txt to
        persist that change in score. finally, it prints that score to the terminal

        Example Arg(s):
            None
        Example Return:
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


    def generate_hints(self) -> list[str]:

        """
        
        this function is used together with generate_hint() (ln 203) and python's random module to randomly generate
        a number which is then plugged into generate_hint which returns a hint and appends it to the hints list instance
        attribute (ln 266). NUM_UNIQUE_HINT_TEMPLATES is a variable that represents the total number of unique hint
        templates that hints can be made from (ln 21)

        Example Arg(s):
            None
        Example Return:
            ["hint_a", "hint_b", "hint_c"] (list[str])

        """

        num_unique_hint_templates = NUM_UNIQUE_HINT_TEMPLATES
        hints: list = []
        possible_hints = set(range(num_unique_hint_templates))
        while len(hints) < 3 - self.difficulty:
            random_hint_num = random.randint(0,num_unique_hint_templates-1)
            if random_hint_num in possible_hints:
                hints.append(Hint(ans=self.ans, hint_num=random_hint_num).description)
                possible_hints.remove(random_hint_num)
        return hints
        

    def validate_guess(self, input_guess: str) -> str:

        """

        this function passes in the user's input_guess and validates it using regex across 2 parameters,
        returning a validated guess:

        1.  len of input_guess should be the same as the digit count instance attribute which is set
            based on difficulty
            
        2.  chars in input_guess should only be digits and digits should only be from 0-7, inclusive

        if input_guess fails any of the above 2 validations, user is prompted again for a new input

        Example Arg(s):
            "1234" (str)
        Example Return:
            "1234" (str)
            
        """
        valid_guess = False

        while valid_guess == False:
            if input_guess in KEYWORDS:
                return input_guess
            elif input_guess == self.ans:
                return input_guess
            try:
                if re.match(r"^[0-7]{%s}$"%(self.digit_count), input_guess):
                    valid_guess = True
                    validated_guess = input_guess
                else:
                    print(f"\nMASTERMIND: You fool - what do you mean, \"{input_guess}\"?! I demand that you enter {self.digit_count} digits between 0-7, inclusive OR a valid keyword!!\n")
                    self.print_turn_intro()
                    input_guess = input()
                    continue
            except BaseException as e:
                pass   
            
        return validated_guess

    def generate_guess_feedback(self, validated_guess: str) -> str | dict[str, int]:

        """
        
        this function details the core logic behind allocating "correct number," "correct location," or
        "all incorrect" feedback info to give to user after each validated guess
        
        Example Arg(s):
            "1454" (str)
        Example Return:
            "Feedback for 1454: {'correct number': 2, 'correct location': 2}" (str)

        """

        ans = self.ans
        ans_counter: list = [0,0,0,0,0,0,0,0,0,0]
        guess_counter: list = [0,0,0,0,0,0,0,0,0,0]
        ret = {"correct number": 0, "correct location": 0}

        for x in range(4):
            ans_digit = int(ans[x])
            validated_guess_digit = int(validated_guess[x])

            if ans_digit == validated_guess_digit:
                ret["correct location"] += 1

            ans_counter[ans_digit] += 1
            guess_counter[validated_guess_digit] += 1

        for idx in range(10):
            ret["correct number"] += min(ans_counter[idx], guess_counter[idx])
        # ret["correct number"] -= ret["correct location"]
        
        ret = "all incorrect" if ret["correct location"] + ret["correct number"] == 0 else ret
        return f"Feedback for {validated_guess}: {ret}\n"

    def handle_guess_history_keyword(self) -> None:

        """
        
        this function handles the /guess_history keyword, printing every string in the guess_history
        list instance variable, which is a list of guess_feedback strings (one per valid user guess (ln 607))

        Example Arg(s):
            None
        Example Return:
            None
        
        """

        print("\n \rGuess History:\n")
        for idx in range(len(self.guess_history)):
            print(f"{idx+1}: ",self.guess_history[idx])
        print("\n \n")

    def handle_hint_keyword(self) -> None:

        """
        
        this function handles the /hint keyword, printing a new hint and keeping track of how many hints the user
        has requested via the hints_idx instance variable (an integer that increments every time the user asks for a hint)

        Example Arg(s):
            None
        Example Return:
            None
        
        """

        if self.hints_idx > 2 - self.difficulty:
            print("\nMASTERMIND: YOU HAVE NO MORE HINTS!\n")
        else:
            new_hint = self.hints[self.hints_idx]
            print(new_hint, "\n")
            self.hints_idx += 1


    def handle_hint_history_keyword(self) -> None:

        """
        
        this function handles the /hint_history keyword, printing hints already shown to the user. it uses the
        hints_idx (int) instance variable to keep track of how many hints the user has asked for

        Example Arg(s):
            None
        Example Return:
            None
        
        """

        if self.hints_idx-1 >= 0:
            print("\nHint History:")
            for idx in range(self.hints_idx):
                print(self.hints[idx])
            print("\n")
        else:
            print("\nMASTERMIND: Stop this foolishness! You haven't asked for any hints yet; enter the command /hint to ask for a hint.\n")

    def handle_score_keyword(self) -> None:

        """
        
        this function handles the /score keyword, printing the user's score - a reflection of how many times
        the user has won against the MASTERMIND

        Example Arg(s):
            None
        Example Return:
            None
        
        """

        sys.stdout.write(f"\n\rMASTERMIND: Hah! Your score is only {self.score}!\n")



    def handle_keyword(self, keyword: str) -> None:

        """
        
        this function accepts a keyword and is always called after a conditional check if a string is a keyword (ln 594-595).
        it then uses a dictionary to map the appropriate keyword handling function to the keyword called by the user

        Example Arg(s):
            "/hint_history" (str)
        Example Return:
            None
        
        """

        keyword_function_mapping = {
                                    "/hint":self.handle_hint_keyword,
                                    "/guess_history":self.handle_guess_history_keyword,
                                    "/hint_history":self.handle_hint_history_keyword,
                                    "/score":self.handle_score_keyword
                                    }

        try:
            keyword_function_mapping[keyword]()
        except BaseException as e:
            pass
        finally:
            return

    def handle_win_and_ask_replay(self) -> bool:

        """
        
        this function is called when user correctly guesses MASTERMIND's number, which is saved as self.ans.
        the function then increments the score in the naive database score.txt file by calling increment_score_in_file().
        it then calls ask_user_replay() to initiate a while loop that asks for a valid user response to replay question (ln 491-502). 
        handle_win_and_ask_replay() will then return True or False depending on whether user does or doesn't want to replay the game

        Example Arg(s):
            None
        Example Return:
            True
        
        """

        print(WIN_MSG)
        self.increment_score_in_file()
        if self.ask_user_replay() == True:
            return True
        else:
            return False

    def ask_user_replay(self) -> bool:

        """
        
        this function asks the user whether they want to replay the game after winning/losing. user input is validated against
        4 valid respones: "y", "yes", "n", or "no" (ln 494). if user doesn't want to replay, returns False; otherwise, returns True

        Example Arg(s):
            None
        Example Return:
            False
        
        """
        valid_response = False

        while valid_response == False:
            sys.stdout.write("\nPlay again? (y/n): ")
            replay_response = input()
            if replay_response.lower() in ["y", "n", "yes", "no"]:
                valid_response = True
            else:
                print("\nPlease answer y or n!")

        if replay_response.startswith("y"):
            return True
        else:
            return False

    def handle_replay(self) -> None:

        """
        
        this function handles the case when ask_user_replay() AND one of its two parent functions: handle_win_ask_replay()
        or handle_lose_ask_replay() return True (ln 598, ln 610), meaning the user does want to replay the game. it plays the welcome animation 
        slightly altered to reflect that user is replaying the game), resets all of the relevant instance variables to game starting values,
        asks for the user difficulty again, fetches a new RNG API answer based on the parameters that correlate to the user input difficulty level, 
        and generates new hints

        Example Arg(s):
            None
        Example Return:
            None
        
        """

        self.print_welcome_animation(replay=True)
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

    def print_turn_intro(self) -> None:

        """
        
        this function handles the several statements that are printed every time a new turn starts to give the user an
        update on their game state - prints information like keywords the user can try, hints remaining, and guesses remaining

        Example Arg(s):
            None
        Example Return:
            None
        
        """

        print(LINE,"\n")
        print(f"Keywords (try entering one of these during the guess phase): {KEYWORDS}")
        print("Hints Remaining:", 3 - self.hints_idx - self.difficulty)
        print("Guesses Remaining:",self.guesses_remaining)
        sys.stdout.write("Guess: ")

    def handle_lose_and_ask_replay(self) -> bool:

        """
        
        this function is called when the user loses (exhausts their remaining guesses in the run_game() while loop which runs
        the overall game logic). it then calls the ask_user_replay() function to ask whether the user wants to replay. 
        if the user does want to replay it returns True to run_game(), otherwise it returns False.

        Example Arg(s):
            None
        Example Return:
            False
        
        """

        print(LOSE_MSG)
        sys.stdout.write(f"\n\rScore: {self.score}\n")
        return True if self.ask_user_replay() == True else False

    def run_game(self) -> None:

        """
        
        this function runs the main game logic. it initializes a while loop that prints the intro to each new turn,
        decrements the guesses_remaining instance variable if the user's validated_guess doesn't match the ans instance variable
        or a user keyword, and handles if the user wins (validated_guess == self.ans) or loses (self.guesses_remaining == 0),
        asking the user if they want to replay the game after either of those outcomes

        Example Arg(s):
            None
        Example Return:
            None

        """
        
        while self.guesses_remaining > 0:
            self.print_turn_intro()
            try:
                guess = input()
                validated_guess = self.validate_guess(guess)
                if validated_guess in KEYWORDS:
                    self.handle_keyword(validated_guess)
                    continue
                elif validated_guess == self.ans:
                    if self.handle_win_and_ask_replay() == True:
                        self.handle_replay()
                        continue
                    else:
                        print("\nMASTERMIND: I'll get you next time!!!")
                        return
                else:
                    guess_feedback = self.generate_guess_feedback(validated_guess)
                    print(guess_feedback)
                    self.guess_history.append(guess_feedback)
                    self.guesses_remaining -= 1
                    if self.guesses_remaining == 0:
                        if self.handle_lose_and_ask_replay() == True:
                            self.handle_replay()
                            continue
                        else:
                            print("\nMASTERMIND: Pfft! What a sore loser! Until next time.")
                            return
            except Exception as e:
                print("MASTERMIND: Try again...\n")
                print(e)