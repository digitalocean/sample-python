PartyTypeInfo = {
    "Bouillabaisse": {
        "Aliases": ["bouillabaisse", "bouil"],
        "Roles": {
            "Starter": ["Open"],
            "Dough": ["Open"],
            "Potato": ["Open"],
            "Onion": ["Open"],
            "Sprouts": ["Open"],
            "Overprep": ["Open"] * 4
        },
        "Ingredients": {
            "Starter": ":fish: Any Bass, :oyster: Oyster Meat",
            "Dough": "<:wheat:1172680400276029541> Wheat",
            "Potato": ":potato: Potato",
            "Onion": ":onion: Onion",
            "Sprouts": "Spice Sprouts",
            "Overprep": "Any ingredient above"
        },
        "Image": "https://palia.wiki.gg/images/9/9d/Bouillabaisse.png"
    },
    "Celebration Cake": {
        "Aliases": ["celebration", "cake", "cakes"],
        "Roles": {
            "Starter": ["Open"],
            "Batter": ["Open"] * 3,
            "Froster": ["Open"],
            "Leafer": ["Open"] * 4,
            "Fruit Froster": ["Open"] * 3,
            "Oven/Spreader": ["Open"] * 3,
            "Flexible": ["Open"] * 4
        },
        "Ingredients": {
            "Starter": ":blueberries: Blueberries",
            "Batter": ":butter: Butter, :egg: Eggs, <:flour:1168232067197317130> Flour",
            "Froster": ":milk: Milk, :butter: Butter",
            "Leafer": ":leaves: Sweet Leaves",
            "Fruit Froster": ":apple: Any Fruit, <:sugar:1171830932513234974> Sugar",
            "Flexible": "Ingredients TBD"
        },
        "Image": "https://palia.wiki.gg/images/8/81/Celebration_Cake.png"
    },
    "Chili Oil Dumpling": {
        "Aliases": ["chili", "dumpling", "dumplings"],
        "Roles": {
            "Starter": ["Open"],
            "Meat": ["Open"],
            "Vegetable": ["Open"],
            "Wheat": ["Open"],
            "Rice": ["Open"],
            "Pepper": ["Open"],
            "Oil": ["Open"],
            "Overprep": ["Open"] * 4
        },
        "Ingredients": {
            "Starter": "Spice Sprouts",
            "Meat": ":cut_of_meat: Any Red Meat",
            "Vegetable": ":potato: Any Vegetable",
            "Wheat": "<:wheat:1172680400276029541> Wheat",
            "Rice": ":rice: Rice",
            "Pepper": ":hot_pepper: Spicy Pepper",
            "Oil": "<:cooking_oil:1172680846856159263> Cooking Oil",
            "Overprep": "Any ingredient above"
        },
        "Image": "https://palia.wiki.gg/images/c/c1/Chili_Oil_Dumplings.png"
    },
    "Crab Pot Pie": {
        "Aliases": ["crab", "pot"],
        "Roles": {
            "Starter": ["Open"],
            "Dough": ["Open"],
            "Onion": ["Open"],
            "Vegetable": ["Open"],
            "Crab": ["Open"],
            "Overprep": ["Open"] * 4
        },
        "Ingredients": {
            "Starter": ":butter: Butter, :corn: Corn",
            "Dough": "<:wheat:1172680400276029541> Wheat",
            "Onion": ":onion: Onion",
            "Vegetable": ":potato: Any Vegetable",
            "Crab": ":crab: Any Crab",
            "Overprep": "Any ingredient above"
        },
        "Image": "https://palia.wiki.gg/images/c/c3/Crab_Pot_Pie.png"
    }
}

def get_roles_list(party_type):
    return list(PartyTypeInfo.get(party_type, {}).get("Roles", {}).keys())

def resolve_party_type(user_input):
    for party_type, party_info in PartyTypeInfo.items():
        aliases = party_info.get("Aliases", [])
        if user_input.lower() in aliases:
            return party_type
    return None
