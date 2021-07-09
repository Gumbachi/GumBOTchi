"""Roast functionality."""
import discord
import random
from discord.ext import commands


class Roasts(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.roasts = [
            "My phone battery lasts longer than your relationships.",
            "Judging from your remarks, I can tell that inbreeding is prominent in your family.",
            "If I wanted a bitch, I would have bought a dog.",
            "It’s a shame you can’t Photoshop your personality.",
            "Acting like a prick doesn’t make yours grow bigger.",
            "The smartest thing that ever came out of your mouth was a penis.",
            "Calm down. Take a deep breath and then hold it for about twenty minutes.",
            "When karma comes back to punch you in the face, I want to be there in case it needs help.",
            "Sorry, sarcasm falls out of my mouth like bullshit falls out of yours.",
            "Don’t mistake my silence for weakness. No one plans a murder out loud.",
            "You should wear a condom on your head. If you’re going to be a dick, you might as well dress like one.",
            "Maybe you should eat make-up so you’ll be pretty on the inside too.",
            "Being a bitch is a tough job but someone has to do it.",
            "My middle finger gets a boner every time I see you.",
            "Whoever told you to be yourself gave you really bad advice.",
            "If I had a face like yours I’d sue my parents.",
            "I thought I had the flu, but then I realized your face makes me sick to my stomach.",
            "I’m jealous of people who don’t know you.",
            "I’m sorry, you seem to have mistaken me with a woman who will take your shit.",
            "I suggest you do a little soul searching. You might just find one.",
            "You should use a glue stick instead of chapstick.",
            "I’d smack you, but that would be animal abuse.",
            "Why is it acceptable for you to be an dumbass but not for me to point it out?",
            "If you’re going to be a smart ass, first you have to be smart, otherwise you’re just an ass.",
            "Your face is fine but you will have to put a bag over that personality.",
            "It’s scary to think people like you are allowed to vote.",
            "No, no. I am listening. It just takes me a moment to process so much stupid information all at once.",
            "I’m sorry, what language are you speaking? It sounds like bullshit. ",
            "Everyone brings happiness to a room. I do when I enter, you do when you leave.",
            "I keep thinking you can’t get any dumber and you keep proving me wrong. ",
            "Your stupid is showing. You might want to tuck it back in.",
            "I am not ignoring you. I am simply giving you time to reflect on what a dumbass you are being.",
            "I hide behind sarcasm because telling you to go fuck yourself is rude in most social situations.",
            "You’re not pretty enough to have such an ugly personality. ",
            "Your birth certificate is an apology letter from the condom manufacturer",
            "You have your entire life to be retarded. Why not take today off?",
            "Your ass must be pretty jealous of all the shit that comes out of your mouth.",
            "Some day you’ll go far—and I really hope you stay there.",
            "I’m trying my absolute hardest to see things from your perspective, but I just can’t get my head that far up my ass.",
            "Sometimes it’s better to keep your mouth shut and give the impression that you’re stupid than open it and remove all doubt.",
            "I’m not a proctologist, but I know an asshole when I see one.",
            "You only annoy me when you’re breathing, really.",
            "I don’t know what your problem is, but I’m guessing it’s hard to pronounce.",
            "Do your parents even realize they’re living proof that two wrongs don’t make a right?",
            "Remember that time I said I thought you were cool? I lied.",
            "Everyone’s entitled to act stupid once in awhile, but you really abuse the privilege.",
            "I can’t help imagining how much better the world would be if your dad had just pulled out.",
            "Do you ever wonder what life would be like if you’d gotten enough oxygen at birth?",
            "Please, save your breath. You’ll probably need it to blow up your next date.",
            "You're the reason the gene pool needs a lifeguard.",
            "Good story, but in what chapter do you shut the fuck up?",
            "Were you born on the highway? That is where most accidents happen.",
            "If I wanted to hear from an asshole, I’d fart.",
            "Jesus might love you, but nobody else does.",
            "The only way you’ll ever get laid is if you crawl up a chicken’s ass and wait.",
            "Are you always such an idiot, or do you just show off when I’m around?",
            "I could eat a bowl of alphabet soup and shit out a smarter statement than whatever you just said.",
            "I was pro life. Then I met you.",
            "You’re about as useful as a screen door on a submarine.",
            "It’s kind of hilarious watching you try to fit your entire vocabulary into one sentence.",
            "I’d tell you how I really feel, but I wasn’t born with enough middle fingers to express myself in this case.",
            "I’d tell you to go fuck yourself, but that would be cruel and unusual punishment.",
            "Your family tree must be a cactus ‘cause you’re all a bunch of pricks.",
            "You’re about as useful as an ashtray on a motorcycle.",
            "If I threw a stick, you’d leave, right?",
            "You’ll never be the man your mom is.",
            "You're a walking mental disability",
            "You're shittier than FinalMouse"
        ]

    @commands.command(name="roast", aliases=["roats"])
    async def roast_member(self, ctx, victim: discord.Member):
        """Roasts the living shit out of somebody. These roasts are absolutely devastating."""
        roast_embed = discord.Embed(
            title=f"Hey {victim.name}, {random.choice(self.roasts)}",
            color=discord.Color.orange()
        )
        await ctx.send(embed=roast_embed)


def setup(bot):
    bot.add_cog(Roasts(bot))
