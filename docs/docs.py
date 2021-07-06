"""Holds documentation for the bot in dict form."""


def help_book(p):
    return [
        # Table of Contents
        {
            "title": "Table of Contents",
            "description": f"Ask salmon for help",
            "1. How Use Craiglister": ["Learn how use cl"],
            "2. Commands": ["Da commands"],
            "3. Listeners": ["Sbonks and Poggers for the slow"],
            "-----------------------------": ["[Github](https://github.com/Gumbachi/GumBOTchi)"]
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
                f"1. Add a query like thsi `{p}clme\nkeyword1, keyword2, ...\n <maxprice> <distance> <images?(yes/no)> <Pingme>`",
                f"Ex: `{p}clmedaddy [Apple TV, Apple, TV] 200 30 No Pingme`",
                f"2. View your queries with `{p}clinfo`"
            ],
            "Remove Queries": [
                f"1. Use `{p}unclmedaddy <query num>`",
            ],
            "Extra Notes": [
                "The bot will automatically check for new listings every 5 minutes",
                "You may not have more than 3 queries active at once",
                "**God speed**"
            ]
        },

        # Commands
        {
            "title": "The Commands",
            "description": "U kno",
            "Misc Commands": [
                f"`{p}howdy` -- all you need is a friend",
                f"`{p}mute <user>` -- think about it",
                f"`{p}supermute <user>` -- the same but more",
                f"`{p}unmute` -- take a guess"
            ],
            "Craigscommands": [
                f"`{p}clmedaddy <[keywords]> <max price> <distance> <images(yes/no)> <Pingme>` -- add a query",
                f"`{p}unclmedaddy <query num>` -- Remove a query",
                f"`{p}clinfo` -- Show queries"
            ]
        },

        # Listeners
        {
            "title": "Listeners",
            "description": f"Extra functionality",
            "Sbonks": [f"prefix a ticker with `$` like $AAL"],
            "Poggers": [f"Hit em with a `poggers` in the chat"]
        }
    ]
