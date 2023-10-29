import asyncio
from datetime import datetime
from dotenv import load_dotenv
from interactions import Client, Intents, listen, slash_command, SlashContext, OptionType, slash_option, ActionRow, Button, ButtonStyle, StringSelectMenu
from interactions.api.events import Component
import os
import uuid

load_dotenv()
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
    global signup_message
    match ctx.custom_id:
        case "signup":
            if party.has_user_signed_up(f"<@{ctx.author.id}>") and party.Multi == False:
                await ctx.author.send("You have already signed up for a role. Please remove your current role to switch roles.")
            else:
                components = StringSelectMenu(
                    "Starter", "Batter", "Froster", "Leafer", "Fruit Froster", "Oven/Spreader",
                    placeholder="Choose your role",
                    custom_id="role"
                    )
                signup_message = await ctx.send(components=components)
                await asyncio.sleep(30)
                try:
                    await signup_message.delete()
                except Exception as e:
                    pass

        case "unsignup":
            while party.has_user_signed_up(f"<@{ctx.author.id}>"): 
                party.remove_user_from_role(f"<@{ctx.author.id}>")
            await edit_message(ctx, party.MessageID)

        case "role":
            selected_role = ctx.values[0]
            party.set_user_id_for_role(selected_role, f"<@{ctx.author.id}>")
            await edit_message(ctx, party.MessageID)
            await signup_message.delete()


@slash_command(
        name="party",
        description="Used to manage Palia parties",
        sub_cmd_name="delete",
        sub_cmd_description="Delete a Palia Party"
)
@slash_option(
    name="id",
    description="Party ID",
    required=True,
    opt_type=OptionType.STRING
)
async def delete(ctx: SlashContext, id: str):
    await ctx.send(f"Party {id} deleted!")

bot.start(token)
