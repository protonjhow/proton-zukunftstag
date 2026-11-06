NOTIFY = {
    "early": "Early in the morning, around 7:00",
    "night": "In the evening, after 20:00",
    "depends": "In the afternoon, around 16:00",
    "sleepy": "In the afternoon, around 16:00",
}
VIDEOS = {
    "animals": "Funny animal videos",
    "gaming": "Gaming videos",
    "music": "Music videos",
    "crafts": "Crafts and DIY videos",
}
AD_GAME = {
    "minecraft": "A Minecraft skin pack",
    "roblox": "Robux",
    "mariokart": "A new Mario game",
    "board": "A new board game",
}
AD_SNACK = {
    "chips": "a chips advert",
    "fruit": "a smoothie advert",
    "chocolate": "a chocolate advert",
    "popcorn": "a cinema advert",
}
TYPE_NOUN = {"laugh": "Joker", "love": "Friend-Maker", "cool": "Adventurer", "think": "Thinker"}
TYPE_ADJ = {"fly": "High-Flying", "invisible": "Mysterious", "animals": "Wild", "time": "Curious"}
WEEKEND = {
    "sleep": "Sleeping in, then taking it easy",
    "outside": "Out and about as soon as you're up",
    "screens": "A game or a video before breakfast",
    "read": "Quiet time with a book or a drawing",
}


def make_guesses(answers: dict[str, str]) -> list[dict]:
    videos = VIDEOS[answers["video"]]
    if answers["pet"] != "neither":
        videos += " and cute pet clips"
    weekend = WEEKEND[answers["weekend"]]
    if answers["clock"] == "night" and answers["weekend"] == "sleep":
        weekend = "Sleeping in, because you stayed up late"
    return [
        {"label": "Best time to send you a notification", "value": NOTIFY[answers["clock"]]},
        {"label": "Videos we'd recommend", "value": videos},
        {"label": "An ad you'd probably click",
         "value": f"{AD_GAME[answers['game']]} (and {AD_SNACK[answers['snack']]})"},
        {"label": "Your type", "value": f"The {TYPE_ADJ[answers['power']]} {TYPE_NOUN[answers['emoji']]}"},
        {"label": "Your weekend", "value": weekend},
    ]
