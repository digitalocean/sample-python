import asyncio
from datetime import datetime
from interactions import Client, Intents, listen, slash_command, SlashContext, OptionType, slash_option, ActionRow, Button, ButtonStyle, StringSelectMenu
from interactions.api.events import Component
import os
import uuid

token= os.environ.get("DISCORD_TOKEN")

bot = Client(intents=Intents.DEFAULT)

class Party:
    def __init__(self, Type, Quantity, Host, Multi=None, **kwargs):
        self.ID = str(uuid.uuid4())
        self.Type = Type
        self.Quantity = Quantity
        self.Host = Host
        self.Multi = Multi if Multi is not None else True
        self.Roles = {
            "Starter": ["Open"],
            "Batter": ["Open"]*3,
            "Froster": ["Open"],
            "Leafer": ["Open"]*4,
            "Fruit Froster": ["Open"]*3,
            "Oven/Spreader": ["Open"]*3,
            "Flexible (TBD)": ["Open"]*4,
        }
        self.Roles.update(kwargs)
        self.MessageID = None
    
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
        
        required_ingredients = {
            "Starter": ":blueberries: Blueberries",
            "Batter": ":butter: Butter, :egg: Eggs, 🌾 Flour",
            "Froster": ":milk: Milk, :butter: Butter",
            "Leafer": ":leaves: Sweet Leaves",
            "Fruit Froster": ":apple: Fruit, :ice_cube: Sugar"
        }

        for role, members in self.Roles.items():
            description += f"**{role}:** {required_ingredients.get(role, 'No ingredients required')}\n"
            
            if members:
                for member in members:
                    description += f"- {member}\n"

        return description

async def edit_message(ctx, message_id: int):
    message = await ctx.channel.fetch_message(message_id)
    description = party.generate_description()
    embed = {
        "title": f"{party.Quantity}x {party.Type} Party",
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
    party = Party(Type=type, Quantity=quantity, Host=host, Multi=multi)
    description = party.generate_description()
    embed = {
        "title": f"{party.Quantity}x {party.Type} Party",
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

@listen(Component)
async def on_component(event: Component):
    ctx = event.ctx
    signup_message = None

    async def set_deleted():
        nonlocal signup_message
        if signup_message:
            await signup_message.delete()
        signup_message = None

    match ctx.custom_id:
        case "signup":
            if party.has_user_signed_up(f"<@{ctx.author.id}>") and party.Multi == False:
                await ctx.author.send("You have already signed up for a role. Please remove your current role to switch roles.")
            else:
                components = StringSelectMenu(
                    "Starter", "Batter", "Froster", "Leafer", "Fruit Froster", "Oven/Spreader","Flexible (TBD)",
                    placeholder="Choose your role",
                    custom_id="role"
                    )
                signup_message = await ctx.send(f"<@{ctx.author.id}>",components=components)
                await asyncio.sleep(15)
                await set_deleted()

        case "unsignup":
            while party.has_user_signed_up(f"<@{ctx.author.id}>"): 
                party.remove_user_from_role(f"<@{ctx.author.id}>")
            await edit_message(ctx, party.MessageID)
            confirmation = await ctx.send(f"<@{ctx.author.id}>, you have been removed from the party.")
            await asyncio.sleep(3)
            await confirmation.delete()

        case "role":
            selected_role = ctx.values[0]
            party.set_user_id_for_role(selected_role, f"<@{ctx.author.id}>")
            await edit_message(ctx, party.MessageID)
            await set_deleted()
            confirmation = await ctx.send(f"<@{ctx.author.id}>, you have been added to {selected_role}")
            await asyncio.sleep(1)
            await confirmation.delete()

@slash_command(
        name="party",
        description="Used to manage Palia parties",
        sub_cmd_name="repost",
        sub_cmd_description="Reposts current Palia Party",
)
async def repost(ctx: SlashContext):
    description = party.generate_description()
    embed = {
        "title": f"{party.Quantity}x {party.Type} Party",
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

@slash_command(
        name="party",
        description="Used to manage Palia parties",
        sub_cmd_name="notify",
        sub_cmd_description="Reposts current Palia Party",
)
async def notify(ctx: SlashContext):
    user_list = []

    for role_list in party.Roles.values():
        for role in role_list:
            if role != "Open" and role not in user_list:
                user_list.append(role)
    
    user_list_str = ', '.join(user_list)               

    await ctx.send(f"The party is starting now! Please add **{party.Host}** in game and report to their house. {user_list_str}")   

bot.start(token)
