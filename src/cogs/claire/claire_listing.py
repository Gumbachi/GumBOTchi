from datetime import datetime
from typing import List
import discord

class ClaireListing:
    def __init__(self,
                source: object,
                id: int,
                name: str,
                url: str,
                posted: datetime.date,
                price: float,
                images: List[str],
                details: str,
                attributes: List[str]) -> None:
        self.source = source
        self.id = id,
        self.name = name
        self.url = url
        self.posted = posted
        self.price = price
        self.images = images
        self.details = details
        self.attributes = attributes

    def main_photo(self):
        if self.images:
            for image in self.images:
                if "images" in image:
                    return image
        
    def clean(self):
        if self.details:
            try:
                # Removes links and short sentences from the body
                body = [sentence for sentence in self.details.split(
                        '\n') if 'http' not in sentence and len(sentence) > 2]
                body = '\n'.join(body)
            except Exception as e:
                print("Error", e)
            finally:
                self.body = body
        else:
            self.body = "Couldn't get details; post was probably deleted."
    
    def discord_embed(self):
        display_limit = 250 # Characters

        body = self.details
        if len(body) > display_limit:
            body = f"{body[0 : display_limit]}..."

        posted = self.posted.strftime('%m/%d at %H:%M')
        sent = datetime.now().strftime('%m/%d at %H:%M')

        # Formats and sends the embed
        embed = discord.Embed(
            title=f"{self.price} - {self.name.title()}",
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

        embed.set_footer(text=f"Posted: {posted}.\nSent: {sent}")

        return embed


