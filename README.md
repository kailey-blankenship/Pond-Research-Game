# Pond-Research-Game
This app was made to be run by streamer.bot and used in twitch streams as an interactive community collection game. It includes a randomized "hunt" for fish, bugs, and plants that you might find at a pond and stores discoveries in its own database.

## How It's Made
This was coded in python with a heavy reliance on SQL to craft databases. I have already preloaded csv files with fish, bugs, and plants and the needed information. The program then makes them into tables using sqlit3. In this project, the random module was used to actually create the randomized "hunt" that takes place. The datetime module was used to create a more realistic aspect to the game that involved seasonal discoveries. The seasons are based on the month of your local machine. The os module was also used in order to get environment variables that will be passed by streamer.bot, such as the hunt type and twitch username that redeemed the hunt.

