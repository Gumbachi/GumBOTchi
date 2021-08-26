"""Holds documentation for the bot"""


def help_book(p):
    return [
        # Table of Contents
        {
            "title": "Table of Contents",
            "description": f"Ask Salmon for help",
            "1. Music": [f"Vibe with GumBOTchi"],
            "1. General Commands/Info": [f"Info for Sbonks, Poggers, and other bot behavior"],
            "2. How Use Craiglister": ["Learn how to use craigslister at your own risk"],
            "-----------------------------": ["[Github](https://github.com/Gumbachi/GumBOTchi)"]
        },

        # Music commands/details
        {
            "title": "Music Commands",
            "description": "We are out here vibing rn frfr",
            "Commands": [
                f"`{p}play <song>` -- Look up a song and play it",
                f"`{p}skip` -- Skip to the next song",
                f"`{p}queue` -- Shows the queueueueue",
                f"`{p}cycle` -- Repeats the queue",
                f"`{p}loop` -- Repeats the song",
                f"`{p}pause` -- Pause the song",
                f"`{p}resume` -- Unpauses the song",
                f"`{p}nowplaying` -- Display info about the song thats playing",
                f"`{p}connect` -- Have the bot join the voice channel",
                f"`{p}disconnect` -- Force the bot to leave. He cries afterwards",
            ],
            "Sound Clips": [
                f"`{p}bruh` -- Bruh Sound Effect #2",
                f"`{p}clingclang` -- Only permitted for goals below 50kph",
                f"`{p}gottem` -- Ladies and Gentlemen...",
                f"`{p}guh` -- Honey, we have to sell the house",
            ]
        },

        # General Commands
        {
            "title": "General Commands/Info",
            "description": "Learn to use Sbonks/Poggers",
            "General Commands": [
                f"`{p}howdy` -- You've got a friend in me",
                f"`{p}gumbotchiprefix` -- Change the prefix",
            ],
            "Sbonks": [
                "Look up a stock price/day graph by prefixing a symbol with `$`",
                "Ex. Type `$AAL` to display American Airlines stock info"
                "There is no command just type it in a text channel"
            ],
            "Poggers": ["Type `poggers` in the chat and see what happens"]
        },

        # Craigslister
        {
            "title": "Craigslist Me Daddy",
            "description": "",
            "Setup": [
                f"Set your site and zipcode using `{p}setzip <zip>` and `{p}setsite <site>`",
                "Find your site [here](https://www.craigslist.org/about/sites) and copy the tag in the URL",
                "For Washington DC the URL is `https://washingtondc.craigslist.org/` so the site would be `washingtondc`"
            ],
            "Add Queries": [
                f"1. Add a query like this `{p}clme\nkeyword1, keyword2, ...\nBudget\nDistance\nImages?(empty for no)\nPing?(empty for no)`",
                f"2. View an example query with `{p}clqr`",
                f"3. View your queries with `{p}queries`"
            ],
            "Delete Query": [
                f"1. Use `{p}delq <query num>`",
            ],
            "Extra Notes": [
                "The bot will automatically check for new listings every 5 minutes",
                "You may not have more than 3 queries active at once",
                "**God speed**"
            ]
        }
    ]
