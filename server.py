import asyncio
from datetime import datetime
from interactions import Client, Intents, listen, slash_command, SlashContext, OptionType, slash_option, ActionRow, Button, ButtonStyle, StringSelectMenu
from interactions.api.events import Component
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
import uuid

# Set environment variables
token= os.environ.get("DISCORD_TOKEN")
database_url = os.environ.get("DATABASE_URL")

# Create client for Discord and MongoDB
bot = Client(intents=Intents.DEFAULT)
mongo = MongoClient(database_url)

# Test connection to database
try:
    mongo.admin.command('ping')
    print("Pinged database. You have successfully connected to MongoDB!")
except Exception as e:
    print(e)

# Set database and collection
db = mongo.chapaa
parties_collection = db["parties"]

class Party:
    PartyTypeRoles = {
        "Cake": {
            "Starter": ["Open"],
            "Batter": ["Open"]*3,
            "Froster": ["Open"],
            "Leafer": ["Open"]*4,
            "Fruit Froster": ["Open"]*3,
            "Oven/Spreader": ["Open"]*3,
            "Flexible": ["Open"]*4,
        },
        "Chili Oil Dumpling": {
            "Starter": ["Open"],
            "Meat": ["Open"],
            "Vegetable": ["Open"],
            "Wheat": ["Open"],
            "Rice": ["Open"],
            "Pepper": ["Open"],
            "Oil": ["Open"],
            "Overprep": ["Open"]*4
        }
    }

    PartyTypeIngredients = {
        "Cake": {
            "Starter": ":blueberries: Blueberries",
            "Batter": ":butter: Butter, :egg: Eggs, <:flour:1168232067197317130> Flour",
            "Froster": ":milk: Milk, :butter: Butter",
            "Leafer": ":leaves: Sweet Leaves",
            "Fruit Froster": ":apple: Any Fruit, <:sugar:1171830932513234974> Sugar",
            "Flexible": "Ingredients TBD"
        },
        "Chili Oil Dumpling": {
            "Starter": "Spice Sprouts",
            "Meat": ":cut_of_meat: Any Red Meat",
            "Vegetable": ":potato: Any Vegetable",
            "Wheat": "<:wheat:1172680400276029541> Wheat",
            "Rice": ":rice: Rice",
            "Pepper": ":hot_pepper: Spicy Pepper",
            "Oil": "<:cooking_oil:1172680846856159263> Cooking Oil",
            "Overprep": "Any ingredient above"
        }
    }

    def __init__(self, ID, Type, Quantity, Host, Multi=None,Roles=None, MessageID=None, ChannelID=None, Responses=None, **kwargs):
        self.ID = ID
        self.Type = Type
        self.Quantity = Quantity
        self.Host = Host
        self.Multi = Multi if Multi is not None else True
        self.Roles = Roles if Roles is not None else self.PartyTypeRoles[Type]
        self.Roles.update(kwargs)
        self.MessageID = MessageID if MessageID is not None else ""
        self.ChannelID = ChannelID if ChannelID is not None else ""
        self.Responses = Responses if Responses is not None else []

    def __str__(self):
        return f"Party(ID={self.ID}, Type={self.Type}, Quantity={self.Quantity}, Host={self.Host}, Multi={self.Multi}, Roles={self.Roles}, MessageID={self.MessageID}, ChannelID={self.ChannelID}, Responses={self.Responses})"
    
    def has_user_signed_up(self, user_id):
        for role in self.Roles.values():
            if user_id in role:
                return True
        return False

    def set_user_id_for_role(self, role, user_id):
        if role in self.Roles:
            role_list = self.Roles[role]
            if "Open" in self.Roles[role]:
                open_index = role_list.index("Open")
                role_list[open_index] = user_id
    
    def remove_user_from_role(self, user_id):
       for role, role_list in self.Roles.items():
           if user_id in role_list:
               user_index = role_list.index(user_id)
               role_list[user_index] = "Open"
               return role
           
    def generate_description(self):
        description = f"Hosted by {self.Host}\n\n"
        
        required_ingredients = self.PartyTypeIngredients.get(self.Type, {})

        for role, members in self.Roles.items():
            description += f"**{role}:** {required_ingredients.get(role, 'No ingredients required')}\n"
            
            if members:
                for member in members:
                    description += f"- {member}\n"

        return description

async def edit_message(self, ctx, message_id: int):
    message = await ctx.channel.fetch_message(message_id)
    description = self.generate_description()
    embed = {
        "title": f"{self.Quantity}x {self.Type} Party\nID: {self.ID}",
        "description": description,
        "thumbnail": {
            "url": "https://emojiisland.com/cdn/shop/products/4_large.png",
            "height": 0,
            "width": 0
        },
        "footer": {
            "text": "Last updated"
        },
        "timestamp": f"{datetime.utcnow()}"
    }
    components: list[ActionRow] = [
        ActionRow(
            Button(
                style=ButtonStyle.GREEN,
                label="Sign Up",
                custom_id="signup",
            ),
            Button(
                style=ButtonStyle.RED,
                label="Unsign Up",
                custom_id="unsignup",
            )
        )
    ]
    await message.edit(embed=embed,components=components)

# Command create
@slash_command(
        name="party",
        description="Used to manage Palia parties",
        sub_cmd_name="create",
        sub_cmd_description="Create a Palia Party",
)
@slash_option(
    name="type",
    description="Type of party",
    required=True,
    opt_type=OptionType.STRING
)
@slash_option(
    name="quantity",
    description="Quantity to be made",
    required=True,
    opt_type=OptionType.STRING
)
@slash_option(
    name="host",
    description="In game name of host",
    required=True,
    opt_type=OptionType.STRING
)
@slash_option(
    name="multi",
    description="Whether player can have multiple roles (true/false)",
    required=False,
    opt_type=OptionType.BOOLEAN
)
async def create(ctx: SlashContext, type: str, quantity: str, host: str, multi: bool = True):
    global party

    if "cake" in type.lower():
        type = "Cake"
    elif "chili" in type.lower() or "dumpling" in type.lower():
        type = "Chili Oil Dumpling"
    else:
        error_post = await ctx.send(f"<@{ctx.author.id}>, sorry {type} party type is not supported.\nThe following party types are currently supported: Cake, Chili Oil Dumpling.")
        await asyncio.sleep(30)
        await error_post.delete()
        return

    party = Party(ID=str(uuid.uuid4()), Type=type, Quantity=quantity, Host=host, Multi=multi, Roles=None)
    description = party.generate_description()
    embed = {
        "title": f"{party.Quantity}x {party.Type} Party\nID: {party.ID}",
        "description": description,
        "thumbnail": {
            "url": "https://emojiisland.com/cdn/shop/products/4_large.png",
            "height": 0,
            "width": 0
        },
        "footer": {
            "text": "Last updated"
        },
        "timestamp": f"{datetime.utcnow()}"
    }
    
    components: list[ActionRow] = [
        ActionRow(
            Button(
                style=ButtonStyle.GREEN,
                label="Sign Up",
                custom_id="signup",
            ),
            Button(
                style=ButtonStyle.RED,
                label="Unsign Up",
                custom_id="unsignup",
            )
        )
    ]

    posting = await ctx.send(embed=embed,components=components)
    party.MessageID = posting.id
    party.ChannelID = posting.channel.id

    party_data = {
        "ID": party.ID,
        "Type": party.Type,
        "Quantity": party.Quantity,
        "Host": party.Host,
        "Multi": party.Multi,
        "Roles": party.Roles,
        "MessageID": party.MessageID,
        "ChannelID": party.ChannelID,
        "Responses": []
    }
    parties_collection.insert_one(party_data)
    party = None

@listen(Component)
async def on_component(event: Component):
    ctx = event.ctx
    signup_message = None
    party = None

    async def retrieve_party(message_id, action):
        nonlocal party
        if action == "signup" or action == "unsignup":
            result = parties_collection.find_one({"MessageID": message_id})
            party = Party(ID=result['ID'], Type=result['Type'], Quantity=result['Quantity'], Host=result['Host'], Multi=result['Multi'], Roles=None, MessageID=result['MessageID'], ChannelID=result['ChannelID'], Responses=result['Responses'])
            return party
        elif action == "role":
            result = parties_collection.find_one({"Responses": {"$elemMatch": {"$eq": message_id}}})
            party = Party(ID=result['ID'], Type=result['Type'], Quantity=result['Quantity'], Host=result['Host'], Multi=result['Multi'], Roles=result['Roles'], MessageID=result['MessageID'], ChannelID=result['ChannelID'], Responses=result['Responses'])
            return party
        
    async def set_deleted():
        nonlocal signup_message
        if signup_message:
            await signup_message.delete()
        signup_message = None

    match ctx.custom_id:
        case "signup":
            await retrieve_party(ctx.message.id, "signup")
            if party.has_user_signed_up(f"<@{ctx.author.id}>") and party.Multi == False:
                await ctx.author.send("You have already signed up for a role. Please remove your current role to switch roles.")
            else:
                if party.Type == "Cake":
                    roles_list = "Starter", "Batter", "Froster", "Leafer", "Fruit Froster", "Oven/Spreader","Flexible"
                elif party.Type == "Chili Oil Dumpling":
                    roles_list = "Starter", "Meat", "Vegetable", "Wheat", "Rice", "Pepper", "Oil", "Overprep"
                components = StringSelectMenu(
                    roles_list,
                    placeholder="Choose your role",
                    custom_id="role"
                    )
                signup_message = await ctx.send(f"<@{ctx.author.id}>",components=components)
                parties_collection.update_one({"MessageID": party.MessageID}, {"$push":{"Responses": signup_message.id}})
                await asyncio.sleep(15)
                await set_deleted()

        case "unsignup":
            await retrieve_party(ctx.message.id, "unsignup")
            while party.has_user_signed_up(f"<@{ctx.author.id}>"): 
                party.remove_user_from_role(f"<@{ctx.author.id}>")
            await edit_message(party, ctx, party.MessageID)
            parties_collection.update_one({"MessageID": party.MessageID}, {"$set":{"Roles": party.Roles}})
            confirmation = await ctx.send(f"<@{ctx.author.id}>, you have been removed from the party.")
            await asyncio.sleep(3)
            await confirmation.delete()

        case "role":
            await retrieve_party(ctx.message.id, "role")
            selected_role = ctx.values[0]
            party.set_user_id_for_role(selected_role, f"<@{ctx.author.id}>")
            await edit_message(party, ctx, party.MessageID)
            parties_collection.update_one({"MessageID": party.MessageID}, {"$set":{"Roles": party.Roles}})
            await set_deleted()
            confirmation = await ctx.send(f"<@{ctx.author.id}>, you have been added to {selected_role}")
            await asyncio.sleep(1)
            await confirmation.delete()

# Repost command
@slash_command(
        name="party",
        description="Used to manage Palia parties",
        sub_cmd_name="repost",
        sub_cmd_description="Reposts current Palia Party",
)
@slash_option(
    name="id",
    description="ID of party",
    required=True,
    opt_type=OptionType.STRING
)
async def repost(ctx: SlashContext, id: str):
    result = parties_collection.find_one({"ID": id})
    party = Party(ID=result['ID'], Type=result['Type'], Quantity=result['Quantity'], Host=result['Host'], Multi=result['Multi'], Roles=result['Roles'], MessageID=result['MessageID'], ChannelID=result['ChannelID'], Responses=result['Responses'])

    description = party.generate_description()
    embed = {
        "title": f"{party.Quantity}x {party.Type} Party\nID: {party.ID}",
        "description": description,
        "thumbnail": {
            "url": "https://emojiisland.com/cdn/shop/products/4_large.png",
            "height": 0,
            "width": 0
        },
        "footer": {
            "text": "Last updated"
        },
        "timestamp": f"{datetime.utcnow()}"
    }

    components: list[ActionRow] = [
        ActionRow(
            Button(
                style=ButtonStyle.GREEN,
                label="Sign Up",
                custom_id="signup",
            ),
            Button(
                style=ButtonStyle.RED,
                label="Unsign Up",
                custom_id="unsignup",
            )
        )
    ]

    oldchannel = bot.get_channel(party.ChannelID)
    target_message = await oldchannel.fetch_message(party.MessageID)
    await target_message.delete()
    
    posting = await ctx.send(embed=embed,components=components)
    party.MessageID = posting.id
    party.ChannelID = posting.channel.id
    parties_collection.update_one({"ID": party.ID}, {"$set":{"MessageID": party.MessageID,"ChannelID": party.ChannelID}})

# Notify command
@slash_command(
        name="party",
        description="Used to manage Palia parties",
        sub_cmd_name="notify",
        sub_cmd_description="Notify users that party is starting",
)
@slash_option(
    name="id",
    description="ID of party",
    required=True,
    opt_type=OptionType.STRING
)
async def notify(ctx: SlashContext, id: str):
    user_list = []

    result = parties_collection.find_one({"ID": id})
    party = Party(ID=result['ID'], Type=result['Type'], Quantity=result['Quantity'], Host=result['Host'], Multi=result['Multi'], Roles=result['Roles'], MessageID=result['MessageID'], ChannelID=result['ChannelID'], Responses=result['Responses'])


    for role_list in party.Roles.values():
        for role in role_list:
            if role != "Open" and role not in user_list:
                user_list.append(role)
    
    user_list_str = ', '.join(user_list)               

    await ctx.send(f"The party is starting now! Please add **{party.Host}** in game and report to their house. {user_list_str}")

# Bot is ready
@listen()
async def on_startup():
    print("Bot is ready and online!")

# Start bot
bot.start(token)
