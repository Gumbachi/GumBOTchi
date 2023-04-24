from datetime import datetime
from dateutil.parser import parse
from typing import List
import discord

class ClaireListing:
    def __init__(
            self,
            source: object,
            id: str,
            name: str,
            url: str,
            posted: datetime.date,
            price: float,
            images: List[str],
            body: str,
            attributes: List[str],
            **kwargs
            ) -> None:
        
        self.source = source
        self.id = id
        self.name = name
        self.url = url
        self.price = price
        self.images = images
        self.body = body
        self.attributes = attributes

        if isinstance(posted, str):
            self.posted = parse(posted)
        else:
            self.posted = posted

        if kwargs.get('spam'):
            self.spam = kwargs.get('spam')

    def main_photo(self):
        """Returns first image"""

        if self.images:
            for image in self.images:
                if "images" in image:
                    return image
        
    def clean(self):
        """Cleans up the body of the listing by removing short sentences and links"""

        if self.body:
            try:
                # Removes links and short sentences from the body
                body = [sentence for sentence in self.body.split(
                        '\n') if 'http' not in sentence and len(sentence) > 2]
                body = '\n'.join(body)
            except Exception as e:
                print("Error", e)
            finally:
                self.body = body
        else:
            self.body = "Couldn't get details; post might have been deleted."
    
    def discord_embed(self):
        """Creates embed for discord"""

        display_limit = 250 # Characters

        body = self.body if self.body else ''
        if len(body) > display_limit:
            body = f"{body[0 : display_limit]} ... (more on site)"

        posted = self.posted.strftime('%m/%d at %H:%M')
        sent = datetime.now().strftime('%m/%d at %H:%M')

        # Formats and sends the embed
        embed = discord.Embed(
            title=f"${self.price} - {self.name.title()}",
            color=discord.Color.blurple()
        )

        embed.add_field(
            name="Details",
            value=body,
            inline=False
        )

        for attribute in self.attributes:
            if len(attribute.split(": ")) == 1:
                continue

            kind = attribute.split(": ")[0]
            description = attribute.split(": ")[1]
            embed.add_field(
                name=kind.title(),
                value=description.title(),
                inline=True
            )

        embed.add_field(
            name="Site",
            value=f"[Link]({self.url})",
            inline=True
        )

        embed.set_author(name=self.source.title())

        photo = self.main_photo()
        if photo:
            embed.set_image(url=photo)

        embed.set_footer(text=f"Posted: {posted}.\nSent: {sent}\nAlleged Probability of Spam: {self.spam}%")

        return embed

    def set_spam_score(self, spam_model):
        self.spam = round(spam_model.probability_of_spam(self.body)*100, 2)
