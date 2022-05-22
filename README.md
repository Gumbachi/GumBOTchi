# GumBOTchi

Your other bots can't say howdy can they?

## Howdy
`/howdy` is the cooler version of `/ping` and you know it. Can be used to check GumBOTchi's pulse.  
![Bot Response with Howdy](res/img/showcase/howdyshowcase.png)  

## Pog  
Pog functionality is a random automatic response to someone saying "pog" or some variant of it. This can be used with messages or links.  
Responses are custom per discord server so you manage the responses yourself using `/pog` commands.  
![Bot Response with Poggers Gif](res/img/showcase/pogshowcase.png)
![Bot Response with Poggers Gif](res/img/showcase/pogshowcase2.png)  

## Sbonks  
Sbonks is a listener that responds with a graph after somebody types a stock symbol prefixed with a `$`  
There is also a `/sbonk` command that allows for timeframe and other things like a message   
![Day Chart for AAPL](res/img/showcase/sbonksimplicit.png)
![Year Chart for AAPL](res/img/showcase/sbonkstimeframe.png)  

## Craigslister  
Sweet will fill this section in I just know it  
![Sweet Need to Implement this](res/img/showcase/craigslist.png)  

## Games  
GumBOTchi has some games you can play against your friends or against GumBOTchi.  
You can do this by `right clicking your target > Apps > Game of Your Choice`  
You can also use each game's slash command if you prefer  
![Rock Paper Scissors](res/img/showcase/rpsshowcase.png)  
![TicTacToe](res/img/showcase/tttinprogress.png) 
![TicTacToe](res/img/showcase/tttfinished.png)  
![Connect4](res/img/showcase/connect4showcase.png)  

## Music
GumBOTchi has a very forward thinking music player. There is no `/play` command its just `/jukebox` once and go from there.  
Everything is controlled from the jukebox which reduces channel clutter  
Songs can be controlled and managed with the provided buttons  
 - Repeat button to cycle throught repeat types such as repeat and repeat one to loop the current queue
 - Play/Pause button to pause/resume the current song
 - Add button to add a song to the queue
 - Skip/Rewind to move to the next song or to reset the current song
 - Queue is paginated and can be navigated using the left/right buttons  

![GumBOTchi's Jukebox](res/img/showcase/jukeboxshowcase.png) 

## Running the bot yourself
If for some reason you would like to run this bot yourself then you will need to have certain environment variables set  
```env
# Required to run the bot
TOKEN=YourBotToken

# Optional -- Needed for Craigslist/Pog
MONGO_PASS=YourMongoDBPassword

# Optional -- Needed for Jukebox/Music
FFMPEG_PATH=PathToFFMPEGExecutable
```
The entry point is **main.py**


## Invite GumBOTchi

 - TODO
