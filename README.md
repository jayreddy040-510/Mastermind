# Welcome to Jay Reddy's Implementation of MASTERMIND!

Hello, and welcome! In this brief README I will be discussing my implementation of the game commonly known as Mastermind.

I have designed an efficient version of Mastermind that is accessible through the command line and adds several features on top of the base level of gameplay.

Ultimately, I wanted to make a game that emulates the simple, addictive feel of text based command line games from the earliest generations of video games. 


# How to Run

Requires: python 3.10.x, git, bash/zsh

1. find where in your local filetree you want to clone the repository from the remote and run the following command:

2.     git clone https://github.com/jayreddy040-510/Mastermind.git

3. cd into root of project ```(../Mastermind/)```

4.      source virtual_env/bin/activate

5.	python3 -m pip install -r requirements.txt

6. check if shell is running inside virutal_env by seeing if (virtual_env) is at the beginning of your shell prompt. shell needs to run inside virtual_env to guarantee that all of the correct dependencies and their respective versions are being used. check python3 version is 3.10.x by running "python3 --version"

7.      python3 run.py

8. if SIGINT (ctrl + C) signal isn't working to close program, use SIGQUIT signal (ctrl + \\)

# Features Implemented

1. ```Core gameplay features``` - By default, the mastermind's answer is generated using the RNG API as delineated in the instructions. The user tries to guess the mastermind's answer, with appropriate feedback printed to the terminal after every user guess. The user can check the history of guesses through entering keyword "/guess_history" during the guessing phase. Guesses remaining is displayed every turn.

2. ```Variable difficulties``` - the 3 game difficulties offered are "hard," "harder," and "hardest." Each game mode alters the number of digits in the mastermind's answer and the number of hints the user is allowed to request.

3. ```Offline answer fetching``` - if the RNG API fails (e.g. there is no WiFi), program prints the error and accesses offline answer fetching which utilizes python's random module to generate an appropriate answer.

4. ```Error handling/Fault tolerance``` using ```try except``` blocks - although this may not be a direct feature of the game, I believe it is an important implementation of how fault tolerant backend code is written. Vulnerable parts of the code that would otherwise fail loudly (e.g. API call, file handling) are wrapped in ```try except``` blocks to catch errors and handle them, allowing the game to continue despite errors.

5. ```Input validation``` - fairly straightforwardly, all user input is validated against what is considered to be acceptable input. If the game requires a valid input to move forward, that section of code is wrapped in a while loop with a boolean flag that starts at False and flips to True upon receiving a valid input. In a previous iteration of the game, I had a retry_count initialized upon receiving invalid input - this count would be incremented with subsequent invalid inputs. When the retry_count equaled 3, I would penalize a guess from the user. Although a fine mechanic, this counter added another loop to the process and I ultimately decided to remove it in a desire to write cleaner, more readable code.

6. ```Hints``` - the game generates a number of hints which is correlated to difficulty chosen by the user. Hints are pulled from a total of 5 possible hint templates; thus, the user gets a randomly generated assortment of hints each game. The user can access a hint via entering the "/hint" keyword or see a history of hints via the "/hint_history" keyword during the guess phase.

7. ```User score``` - while this could be just as easily implemented using an RDBMS or NoSQL database, I opted for a simpler solution with less overhead as there weren't any clear security requirements to protecting the confidentiality of user score. I implement a score saving system via reading and writing to a file ```"score.txt"```. Upon winning, the score in the file is incremented by 1 and upon initialization of the game, the score is read from the file; thus, persisting a score over consecutive instances of the game. Score can be asked by entering the "/score" keyword during the guess phase of the game.

8. ```Replay``` - the user is asked if they wish to replay the game after winning or losing. Replaying the game resets all of the relevant instance attributes to allow for the same instance of the game to be a replay, without having to instantiate a new game (the latter approach would be problematic if the user were to replay 20 times).

# Features Considered (But Not Implemented)

1. ```Two player mode``` - two users can play at the same system, each taking turns being the mastermind for a game and separately incrementing their respective scores. Because answer fetching from the API is a core part of the game, a lot of instance attributes are set during initialization of the game instance and are relative to the difficulty and the answer. I could refactor the helper methods that determine those downstream attributes by passing a ```two_player=True``` boolean and creating separate conditional logic for setting instance variables in the two_player setting; however, I didn't think that was a distinctly different representation of my abilities. And, it makes the central logic harder to read by adding a conditional split of ```if two_player == True:``` to many helper methods.

2. ```Multithreading the API call``` - the code runs without pauses or slow downs except for one section. The RNG API call pauses the code for approximately 1 second while fetching the answer from the API. I considered using the python ```threading``` module to reorder processes and running the API call on a different thread so that 1 second pause is not perceived. However, doing so would require changing the order of many things as the answer is fetched from the API as soon as the user inputs their desired difficulty; and, many instance attributes are created downstream from there. Moreover, in general, I have learned that multithreading should be done very judiciously as it can unexpectedly threaten CPU resources. I decided to not go further down the multithreading path and in stead favored spending my efforts to clean up the code in other ways, making it more readable and thus maintainable.

3. ```Timer``` - one of the possible expansions offered in the instructions pdf is a timer between guesses. While this is a good idea, implementing it in the command line involves escape characters like "\r", a while loop, and more text printed to the terminal every turn. This felt like more of a UI/UX thought puzzle of how to implement a Timer in the command line as opposed to a backend thought exercise and thus I ended up not spending too much time on writing a timer.

# Miscellaneous

* If you are new to python you will know you are inside the virtual_env if you see (virtual_env) in front of your user@path at the bottom of your terminal.

* If you want to print the answer to the terminal at the beginning of the game to easily access some of the conditional logic in the winning conditional tree, simply pass show_ans=True into the instantiation of the Game class in run.py.

* The primary game logic is inside of game_class.py. Depending on which linter/IDE you're using, you may see some error highlights. These are mostly due to optional typing not aligning across some site packages and can be ignored. Additionally, some linters will not read python 3.10.x's match/case syntax and will highlight it as an error. 
