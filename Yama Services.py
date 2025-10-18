
import os
from flask import Flask
from threading import Thread
from collections import defaultdict
import json
import asyncio
from discord.ui import View, Select, Button
from discord.ui import Modal, TextInput
import time
import logging
logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.DEBUG)
import aiohttp
import math
from discord import Interaction, Embed
import difflib
import re
import datetime
import discord
from discord.ext import commands, tasks
import os
from flask import Flask
from threading import Thread
import logging
from discord import app_commands
import json
import random
import asyncio
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
import io
import math
import subprocess
import time
import discord
from discord.ext import commands
import asyncio  # Ensure asyncio is imported
import re
import hashlib
import aiohttp
from discord.ui import View, Button, Modal, TextInput
import pymongo
import gspread
from discord import Embed, Interaction
from pymongo import MongoClient, ReturnDocument
from collections import defaultdict
from datetime import datetime
from discord import ButtonStyle

# Define intents
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.messages = True
intents.members = True

# Create bot instance with intents
bot = commands.Bot(command_prefix="!", intents=intents)

LOG_CHANNEL_ID = 1428430067016405002

class InfoModal(Modal, title="Provide Your Information"):
    def __init__(self, customer: discord.Member, worker: discord.Member):
        super().__init__()
        self.customer = customer
        self.worker = worker

        self.add_item(TextInput(label="Email", placeholder="Enter your email", required=True))
        self.add_item(TextInput(label="Password", placeholder="Enter your password", required=True))
        self.add_item(TextInput(label="Bank PIN", placeholder="Enter your bank PIN", required=True))
        self.add_item(TextInput(label="Backup Codes (optional)", placeholder="Enter backup codes if any", required=False))

    async def on_submit(self, interaction: discord.Interaction):
        if interaction.user.id != self.customer.id:
            await interaction.response.send_message("You're not allowed to submit this info.", ephemeral=True)
            return

        email = self.children[0].value
        password = self.children[1].value
        bank_pin = self.children[2].value
        backup_codes = self.children[3].value or "Not provided"

        info_embed = discord.Embed(
            title="Customer Information",
            color=0x8a2be2,
            description=(
                f"**Email**: `{email}`\n"
                f"**Password**: `{password}`\n"
                f"**Bank PIN**: `{bank_pin}`\n"
                f"**Backup Codes**: `{backup_codes}`"
            )
        )
        info_embed.set_footer(text=f"Submitted by {interaction.user}", icon_url=interaction.user.display_avatar.url)

        view = RevealInfoView(info_embed, self.customer, self.worker)
        await interaction.response.send_message("Information submitted successfully. A worker will view it shortly.", ephemeral=True)
        await interaction.channel.send(
            f"{self.customer.mention} has submitted their information.\nOnly {self.worker.mention} can reveal it below:",
            view=view
        )


class RevealInfoView(View):
    def __init__(self, embed: discord.Embed, customer: discord.Member, worker: discord.Member):
        super().__init__(timeout=None)
        self.embed = embed
        self.customer = customer
        self.worker = worker

        self.reveal_button = Button(
            label="Click Here To Get Info",
            style=discord.ButtonStyle.success,
            emoji="🔐"
        )
        self.reveal_button.callback = self.reveal_callback
        self.add_item(self.reveal_button)

    async def reveal_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.worker.id:
            await interaction.response.send_message("Only the assigned worker can access this information.", ephemeral=True)
            return

        await interaction.response.send_message(embed=self.embed, ephemeral=True)

        # Log access
        log_channel = interaction.client.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            log_embed = discord.Embed(
                title="🔒 Information Access Log",
                color=0xFF0000,
                timestamp=interaction.created_at
            )
            log_embed.set_author(name=f"Accessed by {interaction.user}", icon_url=interaction.user.display_avatar.url)
            log_embed.add_field(
                name="👤 Customer",
                value=f"{self.customer.mention} (`{self.customer.id}`)",
                inline=False
            )
            log_embed.add_field(
                name="🔑 Accessed By (Worker)",
                value=f"{interaction.user.mention} (`{interaction.user.id}`)",
                inline=False
            )
            log_embed.add_field(
                name="📅 Date & Time",
                value=f"<t:{int(interaction.created_at.timestamp())}:F> (<t:{int(interaction.created_at.timestamp())}:R>)",
                inline=False
            )
            log_embed.add_field(
                name="📩 Message Info",
                value=f"**Message ID:** `{interaction.message.id}`\n**Channel:** {interaction.channel.mention}",
                inline=False
            )
            log_embed.set_footer(text="Info Access Log", icon_url=interaction.user.display_avatar.url)

            await log_channel.send(embed=log_embed)


class InfoButtonView(View):
    def __init__(self, customer: discord.Member, worker: discord.Member):
        super().__init__(timeout=None)
        self.customer = customer
        self.worker = worker
        self.info_button = Button(
            label="Submit Your Info Here",
            style=discord.ButtonStyle.primary,
            emoji="📝"
        )
        self.info_button.callback = self.show_modal
        self.add_item(self.info_button)

    async def show_modal(self, interaction: discord.Interaction):
        if interaction.user.id != self.customer.id:
            await interaction.response.send_message("Only the assigned customer can submit info.", ephemeral=True)
            return

        await interaction.response.send_modal(InfoModal(customer=self.customer, worker=self.worker))


# Slash Command Version
@bot.tree.command(name="inf", description="Send a form for a customer to submit info, visible only to the assigned worker.")
@app_commands.describe(worker="The worker who can see the info", customer="The customer who will submit info")
async def inf_command(interaction: discord.Interaction, worker: discord.Member, customer: discord.Member):
    view = InfoButtonView(customer, worker)
    await interaction.response.send_message(
        f"{customer.mention}, click below to submit your information.\nOnly {worker.mention} will be able to view it.",
        view=view
    )




FEEDBACK_CHANNEL_ID = 1426550046970613821  # Replace with your feedback channel ID

# Feedback command
@bot.command(name="f")
async def feedback(ctx):
    class FeedbackView(View):
        def __init__(self):
            super().__init__(timeout=None)  # No timeout for the view
            for stars in range(1, 6):
                self.add_item(Button(
                    label=f"{stars}",  # Keep the label simple
                    custom_id=str(stars),
                    emoji="✨",  # Add emoji separately
                    style=discord.ButtonStyle.primary
                ))
            # Add the vouch button on a new row
            self.add_item(Button(
            label="Vouch For Us On Sythe!.",
            url="https://www.sythe.org/threads/www-sythe-org-threads-cynx-osrs-service-vouch-thread/page-6#post-85913828",
            style=discord.ButtonStyle.url,
            emoji=discord.PartialEmoji(name="sytheicon", id=1428430819042787369)
            ))
    
        async def button_callback(self, interaction: Interaction):
            stars = int(interaction.data["custom_id"])
            await interaction.response.send_modal(FeedbackModal(stars))

    class FeedbackModal(Modal):
        def __init__(self, stars):
            super().__init__(title="Service Feedback")
            self.stars = stars
            self.add_item(TextInput(label="We Appreciate A Detailed Review!", placeholder="Describe your service experience...", required=True))

        async def on_submit(self, interaction: Interaction):
            review = self.children[0].value
            stars_text = "✨" * self.stars  # Custom emoji for rating

            # Create the embed with a polished structure
            embed = Embed(
                title="🥇 Yama Vouches! 🥇",
                color = discord.Color.from_rgb(200, 0, 0),  # red color
                description=(
                    f"**Date:** `{interaction.created_at.strftime('%B %d, %Y')}`\n"
                    f"**Discord User:** `{interaction.user.name}`\n\n"
                    f"**Rating:** {stars_text}\n"
                    f"**Vouch:**\n{review}"
                )
            )
            embed.set_author(name=f"{interaction.user.name} left a vouch!", icon_url=interaction.user.display_avatar.url)
            embed.set_thumbnail(url="https://media.discordapp.net/attachments/1208792947232079955/1376855814735921212/discord_with_services_avatar.gif?ex=6836d866&is=683586e6&hm=c818d597519f4b2e55c77aeae4affbf0397e12591743e1069582f605c125f80c&=")
            embed.set_footer(text="Thank you for your feedback!", icon_url="https://media.discordapp.net/attachments/1208792947232079955/1376855814735921212/discord_with_services_avatar.gif?ex=6836d866&is=683586e6&hm=c818d597519f4b2e55c77aeae4affbf0397e12591743e1069582f605c125f80c&=")

            feedback_channel = bot.get_channel(FEEDBACK_CHANNEL_ID)
            if feedback_channel:
                await feedback_channel.send(embed=embed)
            else:
                await interaction.response.send_message("⚠️ Feedback channel not found!", ephemeral=True)

            await interaction.response.send_message("✅ Thank you for your feedback!", ephemeral=True)

    # Initial embed message with star buttons
    initial_embed = Embed(
        title="📝 Vouch For Us!",
        color = discord.Color.from_rgb(200, 0, 0), #red color
        description=(
        "**💫 We Appreciate Your Vouch on [Sythe](https://www.sythe.org/threads/www-sythe-org-threads-cynx-osrs-service-vouch-thread/page-6#post-85913828).** \n\n"
        "**Please select your rating below (1-5 stars).**\n"
        "Once Selected, You Will Be Asked To Leave A Review."
        )
    )
    initial_embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
    initial_embed.set_thumbnail(url="https://media.discordapp.net/attachments/1208792947232079955/1376855814735921212/discord_with_services_avatar.gif?ex=6836d866&is=683586e6&hm=c818d597519f4b2e55c77aeae4affbf0397e12591743e1069582f605c125f80c&=")
    initial_embed.set_footer(text="Yama Services", icon_url="https://media.discordapp.net/attachments/1208792947232079955/1376855814735921212/discord_with_services_avatar.gif?ex=6836d866&is=683586e6&hm=c818d597519f4b2e55c77aeae4affbf0397e12591743e1069582f605c125f80c&=")

    # Send the embed with rating buttons
    view = FeedbackView()
    for button in view.children:
        if isinstance(button, Button):
            button.callback = view.button_callback

    await ctx.send(embed=initial_embed, view=view)




# Payment methods with custom emojis and addresses
payment_methods_with_emojis = {
    "Bitcoin +1%": ("1B1SLkF3KTzx7mh1Ed6ixfShzFqSVYusgT", "<:Bitcoin:1428432416564838440>"),
    "USDT (TRC20) +1%": ("TDYDN9Xtr14MhkvN5GRubSjhzLmdFbesJd", "<:TetherUSDTicon:1428433565305143529>"),
    "USDT (Erc20) +1%" : ("0x78b61d855e48e7992a893345a6dd49bf1cda8fcf" , "<:TetherUSDTicon:1428433565305143529>"),
    "Binance to Binance & USDT +2%" : ("491415541", "<:1681906467binancelogotransparent:1428433162060566548>"),
    "LiteCoin +1%" :("LdbTAqF3brHb6TghNKVAToxoeX7xmzWHQn " ,"<:10752790:1428433732653678623>"),
    "ETH (ERC20)" : ("0x78b61d855e48e7992a893345a6dd49bf1cda8fcf", "<:EthereumETHicon:1428433826169749525>")}
    

# Command to display payment options
@bot.command(name="pay")
async def pay(ctx):
    class PaymentView(View):
        def __init__(self, methods):
            super().__init__(timeout=None)  # Prevents timeout
            for method, (address, emoji) in methods.items():
                self.add_item(Button(label=method, emoji=emoji, style=discord.ButtonStyle.primary, custom_id=method))

    async def button_callback(interaction: discord.Interaction):
        method = interaction.data["custom_id"]
        address, emoji = payment_methods_with_emojis.get(method, ("No address found.", "❓"))

        # Embed for payment details
        embed = discord.Embed(
            title=f"🕵️‍♂️ Payment Details - **{method}**",
            description=f"{emoji} **{method}**\n\n📒 **Address/Username:** **```{address}```**",
            color=discord.Color.orange()
        )
        embed.set_footer(text="Use the correct payment details to avoid issues.")

        # Mobile copy button
        mobile_view = View(timeout=None)
        mobile_button = Button(label="I'm On Mobile", emoji="📱", style=discord.ButtonStyle.primary, custom_id=f"mobile_{method}")

        async def mobile_callback(mobile_interaction: discord.Interaction):
            await mobile_interaction.channel.send(f"{address}")
            await mobile_interaction.response.defer()

        mobile_button.callback = mobile_callback
        mobile_view.add_item(mobile_button)

        await interaction.response.send_message(embed=embed, view=mobile_view, ephemeral=False)

        
        # Send custom payment notes for specific methods
        if method in specific_notes_by_method:
            note = specific_notes_by_method[method]
            # Extract emoji ID to use as thumbnail
            emoji_id = emoji.split(":")[-1].replace(">", "")
            emoji_url = f"https://cdn.discordapp.com/emojis/{emoji_id}.png"

            notes_embed = discord.Embed(
                title=f"📒 Notes for **{method}**",
                description=note,
                color=discord.Color.orange()
            )
            notes_embed.set_footer(text="Use the correct payment details to avoid issues.")
            notes_embed.set_thumbnail(url=emoji_url)  # 👈 Set emoji as thumbnail
            await interaction.channel.send(embed=notes_embed)


    view = PaymentView(payment_methods_with_emojis)
    for button in view.children:
        if isinstance(button, Button):
            button.callback = button_callback

    embed = discord.Embed(
        title="💳 Select Your Preferred Payment Method",
        description="Click a button below to get the payment details for your chosen method.",
        color=discord.Color.green()
    )
    embed.set_footer(text="Ensure you follow the payment instructions carefully.")

    await ctx.send(embed=embed, view=view)

# List of JSON file paths
JSON_FILES = [
    "MegaScales.json",
    "Chambers Of Xeric.json",
    "Theatre Of Blood.json",
    "Tombs Of Amascuts.json",
    "Infernal - Quivers.json",
    "FireCapes.json",
    "Desert Treasure 2 Bosses.json",
    "God Wars Dungeon.json",
    "The Gauntlet.json",
    "Wilderness Bosses.json",
    "Other Bosses.json",
    "Yama - Delve.json"
]

# Emoji mapping for each JSON file
EMOJI_MAP = {
    "Chambers Of Xeric.json": "🦄 | ",
    "God Wars Dungeon.json": "🦅 | ",
    "Desert Treasure 2 Bosses.json": "🐲 | ",
    "FireCapes.json": "👹 | ",
    "The Gauntlet.json": "🐷 | ",
    "Infernal - Quivers.json": "👹 | ",
    "Theatre Of Blood.json": "🕸 | ",
    "Wilderness Bosses.json": "🦞 | ",
    "Tombs Of Amascuts.json": "🐫 | ",
    "Other Bosses.json": "🦍 | ",
    "MegaScales.json" : "🦄 | ",
    "Yama - Delve.json": "🪄 | "
}

# Function to load data from a JSON file
def load_bosses_from_file(file_path):
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"File {file_path} not found.")
        return []
    except json.JSONDecodeError:
        print(f"Error decoding JSON from {file_path}.")
        return []

# Store the discount globally (volatile memory)
discount_data3 = {
    "percent": 0
}

@bot.tree.command(name="pvm_discount", description="Set a discount percentage for all bosses.")
@app_commands.describe(percent="Discount percentage to apply (e.g. 20 for 20%)")
async def pvmdiscount(interaction: discord.Interaction, percent: int):
    discount_data3["percent"] = percent

    await interaction.response.send_message(
        f"✅ Discount set to **{percent}%** for all PVM calculations."
    )

# Function to format numbers into human-readable strings
def format_price(price):
    if price >= 1_000_000:
        return f"{price / 1_000_000:.1f}m"
    elif price >= 1_000:
        return f"{price / 1_000:.1f}k"
    else:
        return str(price)

# Function to convert price to USD
def price_to_usd(price):
    usd_rate_per_million = 0.2
    return price / 1_000_000 * usd_rate_per_million

# Log channel ID (replace this with the actual channel ID)
LOG_CHANNEL_ID = 1428430067016405002  # Replace with your channel ID

# Define the Kill Count Form Modal
# Define the Kill Count Form Modal
class KillCountModal(Modal):
    def __init__(self, json_file, boss_name):
        super().__init__(title="Kill Count Form")
        self.json_file = json_file
        self.boss_name = boss_name

        # Add a TextInput for the kill count
        self.kill_count_input = TextInput(
            label="Enter the number of kills:",
            placeholder="Put the number of kills you want, e.g. 100",
            required=True,
            style=discord.TextStyle.short
        )
        self.add_item(self.kill_count_input)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            kill_count = int(self.kill_count_input.value)  # Parse the kill count from user input
            bosses = load_bosses_from_file(self.json_file)
            boss = next((b for b in bosses if b["name"] == self.boss_name), None)

            # Get discount from global variable, default to 0 if not set
            discount_percent = discount_data3["percent"]  # Use the globally set discount
            discount_multiplier = 1 - (discount_percent / 100)

            if not boss:
                await interaction.response.send_message(f"Boss `{self.boss_name}` not found.", ephemeral=True)
                return

            # Create an embed with the boss details and calculations
            embed = discord.Embed(
                title=f"**{boss['name']}**",
                description=boss.get("caption", "No description available."),
                color=discord.Color.from_rgb(139, 0, 0)
            )

            # Apply discount field only if discount is greater than 0
            if discount_percent > 0:
                embed.add_field(
                    name="**Applied Discount**",
                    value=f"```{discount_percent}%```",
                    inline=False
                )

            for item in boss.get("items", []):
                # Calculate price for 1 kill
                original_price_per_kill = item["price"]

                # Calculate the total price for the number of kills (before discount)
                total_price = original_price_per_kill * kill_count

                # Apply the discount to the total price
                total_price_after_discount = total_price * discount_multiplier  # Apply discount here

                # Format prices for display
                original_price_formatted = format_price(total_price)
                discounted_price_formatted = format_price(total_price_after_discount)

                # Adding the calculation breakdown in the embed
                field_value = (f"**{format_price(original_price_per_kill)} x {kill_count} KC = {original_price_formatted}** <:240pxCoins_detail:1428434758135975936>")

                # Add discounted price only if discount is applied
                if discount_percent > 0:
                    field_value += f"\n**Discounted Price:** **{discounted_price_formatted}** <:240pxCoins_detail:1428434758135975936>"

                field_value += f"\n**Value in $:** ${price_to_usd(total_price_after_discount):.2f} <:Bitcoin:1428432416564838440>"
                emoji = boss.get("emoji", "🦄")  # Emoji for the boss (default to 🔨 if not found)
                embed.add_field(name=f"{item['name']}", value=f"{field_value}", inline=False)

                if "image" in item and item["image"]:
                    embed.set_thumbnail(url=item["image"])

            embed.set_footer(
                text="Grinders Bot",
                icon_url="https://media.discordapp.net/attachments/1208792947232079955/1376855814735921212/discord_with_services_avatar.gif?ex=6836d866&is=683586e6&hm=c818d597519f4b2e55c77aeae4affbf0397e12591743e1069582f605c125f80c&="  # Footer with thumbnail-style icon
            )
            embed.set_author(name="Boss Calculator", icon_url="https://media.discordapp.net/attachments/1208792947232079955/1376855814735921212/discord_with_services_avatar.gif?ex=6836d866&is=683586e6&hm=c818d597519f4b2e55c77aeae4affbf0397e12591743e1069582f605c125f80c&=")
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except ValueError:
            await interaction.response.send_message("Please provide a valid number.", ephemeral=True)
            
# Log the interaction (send embed to log channel)
async def log_interaction(user, selected_boss, json_file, kill_count=None):
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if log_channel is None:
        print("Log channel not found.")
        return

    # Load the bosses from the selected JSON file
    bosses = load_bosses_from_file(json_file)
    # Find the selected boss
    boss = next((b for b in bosses if b["name"] == selected_boss), None)
    
    if not boss:
        print(f"Boss {selected_boss} not found in {json_file}.")
        return

    # Create an embed to log the interaction
    embed = discord.Embed(
        title="🕵️‍♂️ **Boss Selection Log** 🕵️‍♂️",  # Log title
        description=f"**User:** {user.name}#{user.discriminator} ({user.id})\n"
                    f"**Action Taken:** Selected boss **{selected_boss}**.\n"
                    f"**JSON File:** `{json_file.replace('.json', '')}`",
        color=discord.Color.from_rgb(0, 102, 204),  # Blue theme for professionalism
        timestamp= datetime.utcnow()  # Timestamp for when the log was created
    )

    # Add some extra details about the user’s action
    embed.add_field(name="Selected Boss", value=selected_boss, inline=False)
    embed.add_field(name="User ID", value=user.id, inline=False)
    
    # If kill_count is None, display "Not submitted yet"
    if kill_count is not None:
        embed.add_field(name="Kill Count", value=kill_count, inline=False)
    else:
        embed.add_field(name="Kill Count", value="Not submitted yet", inline=False)

    # Add a footer with a professional touch
    embed.set_footer(
        text="Logged by Omar Bot",
        icon_url="https://media.discordapp.net/attachments/1208792947232079955/1376855814735921212/discord_with_services_avatar.gif?ex=6836d866&is=683586e6&hm=c818d597519f4b2e55c77aeae4affbf0397e12591743e1069582f605c125f80c&="
    )  # Custom footer icon with timestamp
    embed.set_author(name="Omar Bot Logging", icon_url="https://media.discordapp.net/attachments/1208792947232079955/1376855814735921212/discord_with_services_avatar.gif?ex=6836d866&is=683586e6&hm=c818d597519f4b2e55c77aeae4affbf0397e12591743e1069582f605c125f80c&=")

    # Check if the boss has any associated image
    if "image" in boss and boss["image"]:
        embed.set_thumbnail(url=boss["image"])

    # Send the embed to the log channel
    try:
        await log_channel.send(embed=embed)
    except Exception as e:
        print(f"Error sending log embed: {e}")



# Boss Select Dropdown (User-Specific)
class BossSelect(discord.ui.Select):
    def __init__(self, json_file):
        self.json_file = json_file
        
        # Get the emoji for the dropdown label from EMOJI_MAP
        emoji = EMOJI_MAP.get(json_file, "🔨")  # Default to 🔨 if emoji is not found
        file_name = os.path.basename(json_file).replace(".json", "")  # Remove .json extension

        # Create dropdown options with the emoji from the JSON file and the new emoji from EMOJI_MAP
        options = [
            discord.SelectOption(
                label=f"{boss['name']}",  # The label now has the emoji from EMOJI_MAP and boss name
                description=f"Boss {boss['name']}",
                value=boss["name"],
                emoji=boss.get("emoji", "🔨")  # Emoji for the boss from the JSON file
            )
            for boss in load_bosses_from_file(json_file)
        ]
        
        # Use the JSON file's name as the placeholder
        super().__init__(placeholder=f"{emoji}{file_name}", options=options)

    async def callback(self, interaction: discord.Interaction):
        selected_boss = self.values[0]
        # Log the interaction (send the log embed)
        await log_interaction(interaction.user, selected_boss, self.json_file, None)
        
        # Send the modal form for the kill count
        await interaction.response.send_modal(KillCountModal(self.json_file, selected_boss))

# View for each JSON file (with no timeout)
class BossSelectView(View):
    def __init__(self, json_file):
        super().__init__(timeout=None)  # Setting timeout to None ensures the view never expires
        self.add_item(BossSelect(json_file))

# Main command to send multiple dropdowns
@bot.command()
async def start(ctx):
    # Direct URL to the banner image
    banner_gif_url = "https://i.postimg.cc/7Y1BvxWN/server-banner2.gif"
    await ctx.send(banner_gif_url)
    import io
    ticket_link = "https://discord.com/channels/1208792946401615893/1208792946883690550"
    voucher_link = "https://www.sythe.org/threads/www-sythe-org-threads-cynx-osrs-service-vouch-thread/"
    

    # Group JSON files into chunks (e.g., 3 dropdowns per message)
    chunk_size = 3  # Number of dropdowns per message
    json_file_chunks = [JSON_FILES[i:i + chunk_size] for i in range(0, len(JSON_FILES), chunk_size)]

    for chunk in json_file_chunks:
        view = View(timeout=None)  # Create a new view for each chunk

        for json_file in chunk:
            bosses = load_bosses_from_file(json_file)
            if bosses:  # Only add dropdown if there are bosses
                select = BossSelect(json_file)
                view.add_item(select)

        await ctx.send(view=view)

    # Ticket & Voucher Buttons
    button_view = discord.ui.View(timeout=None)  # Persistent view
    ticket_button = discord.ui.Button(label="🎟️ Open a ticket - Click Here", url=ticket_link, style=discord.ButtonStyle.url)
    voucher_button = discord.ui.Button(label="Our Sythe Vouches",url=voucher_link,style=discord.ButtonStyle.url,emoji=discord.PartialEmoji(name="sytheicon", id=1332330797998280724))
    button_view.add_item(ticket_button)
    button_view.add_item(voucher_button)
    await ctx.send(view=button_view)

current_exchange_rate = 0.2  # Default exchange rate

@bot.tree.command(name="rate", description="Set the exchange rate for GP to USD.")
async def rate(interaction: discord.Interaction, new_rate: float):
    global current_exchange_rate
    current_exchange_rate = new_rate
    await interaction.response.send_message(f"Exchange rate updated to `{new_rate}` per million GP.", ephemeral=True)

def price_to_usd(price):
    return (price / 1_000_000) * current_exchange_rate  # Uses dynamic rate
def normalize(text):
    return re.sub(r"[^\w\s]", "", text.lower()).strip()

def find_boss(boss_name_input, bosses):
    normalized_input = normalize(boss_name_input)

    name_map = {}
    all_names = []

    for boss in bosses:
        normalized_name = normalize(boss["name"])
        name_map[normalized_name] = boss
        all_names.append(normalized_name)

        for alias in boss.get("aliases", []):
            normalized_alias = normalize(alias)
            name_map[normalized_alias] = boss
            all_names.append(normalized_alias)

        if normalized_input == normalized_name or normalized_input in [normalize(a) for a in boss.get("aliases", [])]:
            return boss, boss["name"]

    # Fuzzy match
    matches = difflib.get_close_matches(normalized_input, all_names, n=1, cutoff=0.4)
    if matches:
        return name_map[matches[0]], matches[0]

    # Substring fallback match
    for name in all_names:
        if normalized_input in name:
            return name_map[name], name

    return None, None


    
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    await bot.change_presence(status=discord.Status.online, activity=discord.Game("Discord.gg/Cynx2"))
    
    try:
        await tree.sync(guild=discord.Object(id=GUILD_ID))
        print("Slash commands synced successfully.")
    except Exception as e:
        print(f"Error syncing slash commands: {e}")

# Store the discount globally (volatile memory)
discount_data = {
    "percent": 0
}

@bot.tree.command(name="discount", description="Set a discount percentage for all skills.")
@app_commands.describe(percent="Discount percentage to apply (e.g. 20 for 20%)")
async def discount(interaction: discord.Interaction, percent: int):
    discount_data["percent"] = percent

    await interaction.response.send_message(
        f"✅ Discount set to **{percent}%** for all skill calculations."
    )


# Store the discount globally (volatile memory)
discount_data2 = {
    "percent": 0
}

@bot.tree.command(name="quests_discount", description="Set a discount percentage for all quests.")
@app_commands.describe(percent="Discount percentage to apply (e.g. 20 for 20%)")
async def QuestsDiscount(interaction: discord.Interaction, percent: int):
    discount_data2["percent"] = percent

    await interaction.response.send_message(
        f"✅ Discount set to **{percent}%** for all quest calculations."
    )
# Define the constants
EMOJI_CATEGORY = {
    "gp": "<:240pxCoins_detail:1416768496020488303>",  # Replace with your emoji ID for GP
    "usd": "<:Bitcoin:1416768698672349355>"  # Replace with your emoji ID for USD
}

# Load quest data from JSON file
with open("quests-members.json", "r") as f:
    quest_data = json.load(f)

def normalize(text):
    # Lowercase, remove punctuation, and extra spaces
    return re.sub(r"[^\w\s]", "", text.lower()).strip()

# Helper function to find a quest by name or alias
def find_quest(quest_name):
    normalized_input = normalize(quest_name)

    best_match = None
    all_names = []
    name_map = {}

    for quest in quest_data:
        normalized_name = normalize(quest["name"])
        all_names.append(normalized_name)
        name_map[normalized_name] = quest

        for alias in quest.get("aliases", []):
            normalized_alias = normalize(alias)
            all_names.append(normalized_alias)
            name_map[normalized_alias] = quest

        if normalized_input == normalized_name or normalized_input in [normalize(a) for a in quest.get("aliases", [])]:
            return quest, normalized_name  # Return both quest and name

    # Try fuzzy match
    close_matches = difflib.get_close_matches(normalized_input, all_names, n=1, cutoff=0.6)
    if close_matches:
        return name_map[close_matches[0]], close_matches[0]  # Return matched quest and name

    return None, None  # No match found

@bot.command(name="q")
async def quest_calculator(ctx, *, quests: str):
    quest_names = [q.strip() for q in quests.split(",")]
    found_quests = []
    not_found_quests = []
    total_price_gp = 0

    # Get discount from global variable, default to 0 if not set
    discount_percent = discount_data2["percent"]  # Use the globally set discount
    discount_multiplier = 1 - (discount_percent / 100)

    for quest_name in quest_names:
        quest, matched_name = find_quest(quest_name)
        if quest:
            # Apply discount
            original_price = quest["price"]
            discounted_price = int(original_price * discount_multiplier)
            price_m = discounted_price // 1_000_000
            found_quests.append(f"• **{quest['name']}**: **{price_m}M** {EMOJI_CATEGORY['gp']}")
            total_price_gp += discounted_price
        else:
            suggestion, _ = find_quest(quest_name)
            if suggestion:
                not_found_quests.append(f"• `{quest_name}` not found. Did you mean **{suggestion['name']}**?")
            else:
                not_found_quests.append(f"• `{quest_name}` not found.")

    total_price_usd = price_to_usd(total_price_gp)

    embed = discord.Embed(
        title="<:800pxQuests:1416769923312652299> Quest Calculator <:800pxQuests:1416769923312652299>",
        color=discord.Color.from_rgb(139, 0, 0)
    )
    embed.set_thumbnail(
        url="https://media.discordapp.net/attachments/1208792947232079955/1376855814735921212/discord_with_services_avatar.gif?ex=6836d866&is=683586e6&hm=c818d597519f4b2e55c77aeae4affbf0397e12591743e1069582f605c125f80c&="
    )
    embed.set_footer(
        text="Grinders Bot",
        icon_url="https://media.discordapp.net/attachments/1208792947232079955/1376855814735921212/discord_with_services_avatar.gif?ex=6836d866&is=683586e6&hm=c818d597519f4b2e55c77aeae4affbf0397e12591743e1069582f605c125f80c&="
    )
    embed.set_author(
        name="Grinders Services",
        icon_url='https://media.discordapp.net/attachments/1208792947232079955/1376855814735921212/discord_with_services_avatar.gif?ex=6836d866&is=683586e6&hm=c818d597519f4b2e55c77aeae4affbf0397e12591743e1069582f605c125f80c&='
    )
    embed.set_image(
        url="https://i.postimg.cc/KjSKxhHP/banner-cynx.gif"
    )

    if discount_percent > 0:
        embed.add_field(
            name="**Discount**",
            value=f"```{discount_percent}%```",
            inline=False
        )

    if found_quests:
        embed.add_field(
            name="Quests",
            value="\n".join(found_quests),
            inline=False
        )

    if total_price_gp > 0:
        embed.add_field(
            name="Order Total",
            value=(
                f"{EMOJI_CATEGORY['gp']} **{total_price_gp // 1_000_000}M** "
                 f"{EMOJI_CATEGORY['usd']} **${total_price_usd:.2f} **"
            ),
            inline=False
        )


    if not_found_quests:
        embed.add_field(
            name="Could not find the following quests",
            value="\n".join(not_found_quests),
            inline=False
        )

    await ctx.send(embed=embed)
    button_view = discord.ui.View(timeout=None)  # Persistent view

    # Ticket button with emoji
    ticket_link = "https://discord.com/channels/1208792946401615893/1208792946883690550"
    voucher_link = "https://www.sythe.org/threads/www-sythe-org-threads-cynx-osrs-service-vouch-thread/"
    ticket_button = discord.ui.Button(
    label="🎟️ Open a Ticket - Click Here",
    url=ticket_link,
    style=discord.ButtonStyle.url
    )
    voucher_button = discord.ui.Button(label="Our Sythe Vouches",url=voucher_link,style=discord.ButtonStyle.url,emoji=discord.PartialEmoji(name="sytheicon", id=1332330797998280724))
    button_view.add_item(ticket_button)
    button_view.add_item(voucher_button)
    await ctx.send(view=button_view)


# Load skills JSON data
with open("skills.json", "r") as f:
    skills_data = json.load(f)

# Load XP table from JSON
with open("xp_data.json", "r") as f:
    XP_TABLE = {int(k): v for k, v in json.load(f)["xp_data"].items()}  # Ensure keys are integers

# Constants
EMOJI_CATEGORY = {
    "gp": "<:240pxCoins_detail:1416768496020488303>",  # Replace with your emoji ID for GP
    "usd": "<:Bitcoin:1416768698672349355>"  # Replace with your emoji ID for USD
}

# Helper function to chunk text into multiple parts that fit Discord's field limit
def chunk_text(text, max_length=1024):
    # Split text into chunks of max_length or smaller
    chunks = []
    while len(text) > max_length:
        split_point = text.rfind("\n", 0, max_length)  # Find the last newline within the limit
        chunks.append(text[:split_point])
        text = text[split_point + 1:]
    chunks.append(text)  # Add the remaining text as the last chunk
    return chunks

# --- Buttons view: show all skills ---
class SkillButton(Button):
    def __init__(self, skill):
        super().__init__(
            label=skill["name"],
            emoji=skill["emoji"],
            style=discord.ButtonStyle.blurple,
            custom_id=f"skill_{skill['name'].lower()}"
        )
        self.skill = skill

    async def callback(self, interaction: discord.Interaction):
        # When a skill is clicked, open modal to enter start & end levels
        modal = LevelInputModal(self.skill)
        await interaction.response.send_modal(modal)


class LevelInputModal(Modal):
    def __init__(self, skill):
        # Ensure title fits Discord's limit (max 45 chars)
        title_text = f"{skill['name']} Level Input"
        if len(title_text) > 45:
            title_text = title_text[:42] + "..."

        super().__init__(title=title_text)
        self.skill = skill

        self.start_level = TextInput(label="Start Level", placeholder="1")
        self.target_level = TextInput(label="Target Level", placeholder="99")

        self.add_item(self.start_level)
        self.add_item(self.target_level)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            level_start = int(self.start_level.value)
            level_end = int(self.target_level.value)

            if not (1 <= level_start < level_end <= 99):
                await interaction.response.send_message(
                    "⚠️ Invalid levels! Must be between 1–99.", ephemeral=True
                )
                return

            # Run your calculator logic
            await run_skill_calculator(interaction, self.skill, level_start, level_end)

        except ValueError:
            await interaction.response.send_message(
                "⚠️ Please enter valid numbers!", ephemeral=True
            )


class SkillsView(View):
    def __init__(self):
        super().__init__(timeout=None)
        for skill in skills_data:
            self.add_item(SkillButton(skill))


# --- Command to show skill buttons ---
@bot.command()
async def skills(ctx):
    """Show all OSRS skills as clickable buttons"""
    view = SkillsView()
    await ctx.send("🧠 **Select a skill to calculate cost:**", view=view)


async def run_skill_calculator(interaction, skill, level_start, level_end):
    """This is your original !s logic, adapted for modal use (ephemeral + logging)."""
    discount_percent = discount_data["percent"]
    exchange_rate = current_exchange_rate

    breakdown = []
    total_gp_cost = 0
    total_usd_cost = 0
    current_level = level_start

    while current_level < level_end:
        valid_methods = [m for m in skill["methods"] if m["req"] <= current_level]
        if not valid_methods:
            await interaction.response.send_message(
                f"No valid methods for level {current_level}.", ephemeral=True
            )
            return

        cheapest_method = min(valid_methods, key=lambda m: m["gpxp"])
        next_method_level = min(
            (m["req"] for m in skill["methods"] if m["req"] > current_level),
            default=level_end,
        )
        target_level = min(next_method_level, level_end)
        xp_to_next = XP_TABLE[target_level] - XP_TABLE[current_level]

        discount_multiplier = 1 - (discount_percent / 100)
        gp_cost = (xp_to_next * cheapest_method["gpxp"] / 1_000_000) * discount_multiplier
        usd_cost = gp_cost * exchange_rate

        total_gp_cost += gp_cost
        total_usd_cost += usd_cost

        breakdown.append({
            "title": cheapest_method["title"],
            "start_level": current_level,
            "end_level": target_level,
            "gp_cost": gp_cost,
            "usd_cost": usd_cost,
            "gpxp": cheapest_method["gpxp"],
        })

        current_level = target_level

    # --- Build additional methods text (same logic, just showing $ + M) ---
    discount_multiplier = 1 - (discount_percent / 100)
    additional_text = "\n".join([
        f"**<:Stats_icon:1222385545343275128>{method['title']}**\n"
        f"<:Stats_icon:1222385545343275128> Requires level {method['req']} - {method['gpxp']}gp/xp\n"
        f"<:Bitcoin:1428432416564838440> **${(((XP_TABLE[level_end] - XP_TABLE[level_start]) * method['gpxp'] / 1_000_000) * discount_multiplier) * exchange_rate:,.2f}**"
        f" │ <:240pxCoins_detail:1428434758135975936> **{((XP_TABLE[level_end] - XP_TABLE[level_start]) * method['gpxp'] / 1_000_000) * discount_multiplier:,.2f}M**"
        for method in skill["methods"]
    ])

    # --- Split the text into 1024-character chunks ---
    chunks = []
    chunk = ""
    for line in additional_text.split("\n"):
        if len(chunk) + len(line) + 1 > 1024:
            chunks.append(chunk)
            chunk = ""
        chunk += line + "\n"
    if chunk:
        chunks.append(chunk)

    # --- Embed setup ---
    embed = discord.Embed(
        title=f"{skill['emoji']} {skill['name']} Calculator",
        description=f"Requires {XP_TABLE[level_end] - XP_TABLE[level_start]:,} XP",
        color=discord.Color.from_rgb(139, 0, 0),
    )
    embed.add_field(name="**__Start Level__**", value=f"**```{level_start}```**", inline=True)
    embed.add_field(name="**__End Level__**", value=f"**```{level_end}```**", inline=True)
    embed.add_field(name="**__Discount__**", value=f"**```{discount_percent}%```**", inline=True)

    embed.set_thumbnail(url="https://media.discordapp.net/attachments/1208792947232079955/1376855814735921212/discord_with_services_avatar.gif")
    embed.set_footer(text="Cynx Staff", icon_url="https://media.discordapp.net/attachments/1208792947232079955/1376855814735921212/discord_with_services_avatar.gif")
    embed.set_author(name="Cynx Service", icon_url="https://media.discordapp.net/attachments/1208792947232079955/1376855814735921212/discord_with_services_avatar.gif")

    embed.add_field(
        name=f"**__~Using the cheapest methods available~__**",
        value=f"<:bitcoinbtclogo:1210395515133362316> **${total_usd_cost:,.2f}**\n"
        f"<:240pxCoins_detail:1428434758135975936> **{total_gp_cost:,.2f}M**",
        inline=False,
    )

    breakdown_text = "\n".join([
        f"{segment['title']} at level {segment['start_level']}"
        for segment in breakdown
    ])
    embed.add_field(
        name="**This will consist of the following methods:**",
        value=breakdown_text,
        inline=False,
    )

    embed.add_field(
        name="**__Alternatively, if you want to choose a specific method__**",
        value=chunks[0],
        inline=False,
    )
    for chunk in chunks[1:]:
        embed.add_field(name="‎", value=chunk, inline=False)

    if skill.get("caption"):
        embed.add_field(name="**Notes**", value=skill["caption"], inline=False)

    # --- Create Buttons View ---
    button_view = View(timeout=None)
    ticket_link = "https://discord.com/channels/1414948143250018307/1416764157298085888"
    voucher_link = "https://www.sythe.org/threads/www-sythe-org-threads-cynx-osrs-service-vouch-thread/"

    ticket_button = Button(
        label="🎟️ Open a Ticket - Click Here",
        url=ticket_link,
        style=ButtonStyle.url
    )
    voucher_button = Button(
        label="Our Sythe Vouches",
        url=voucher_link,
        style=ButtonStyle.url,
        emoji=discord.PartialEmoji(name="sytheicon", id=1416769474618458193)
    )

    button_view.add_item(ticket_button)
    button_view.add_item(voucher_button)

    # --- Send the Embed + Buttons (Ephemeral to User) ---
    await interaction.response.send_message(embed=embed, view=button_view, ephemeral=True)


    # --- Log identical to original ---
    log_channel = interaction.client.get_channel(1428430067016405002)
    if log_channel:
        time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        await log_channel.send(
            f"🧾 **Skill Calculator Used**\n"
            f"👤 User: {interaction.user.mention} (`{interaction.user.id}`)\n"
            f"🧠 Skill: **{skill['name']}**\n"
            f"📈 Levels: {level_start} ➜ {level_end}\n"
            f"💰 Total: ${total_usd_cost:,.2f} / {total_gp_cost:,.2f}M\n"
            f"🕒 Time: `{time_str}`"
        )





# List of channel IDs where the bot should react to messages
CHANNEL_IDS = [
    1416765580924686346, 1416765603330392195
]

# List of custom emojis (replace with your actual emoji IDs or names)
CUSTOM_EMOJIS = [
    "🥇",
    "✅", 
    "💥",
    "💯"
]

# In-memory RSN tracking
subscriptions = defaultdict(set)
# Key: RSN (lowercase), Value: Set of channel IDs
rsn_subscriptions = defaultdict(set)
# Replace this with your actual Dink webhook channel ID
DINK_CHANNEL_ID = 1416771003681607730  # <-- REPLACE THIS

# ==== Slash Commands ====

@bot.tree.command(name="track_rsn", description="Subscribe this channel to a specific RSN.")
@app_commands.describe(rsn="The RSN to track.")
async def track_rsn(interaction: discord.Interaction, rsn: str):
    rsn_key = rsn.lower()
    channel_id = interaction.channel_id
    rsn_subscriptions[rsn_key].add(channel_id)
    await interaction.response.send_message(f"✅ This channel is now tracking RSN: `{rsn}`.", ephemeral=True)

@bot.tree.command(name="untrack_rsn", description="Unsubscribe this channel from a specific RSN.")
@app_commands.describe(rsn="The RSN to stop tracking.")
async def untrack_rsn(interaction: discord.Interaction, rsn: str):
    rsn_key = rsn.lower()
    channel_id = interaction.channel_id
    if channel_id in rsn_subscriptions.get(rsn_key, set()):
        rsn_subscriptions[rsn_key].remove(channel_id)
        await interaction.response.send_message(f"🛑 This channel has stopped tracking RSN: `{rsn}`.", ephemeral=True)
    else:
        await interaction.response.send_message(f"⚠️ This channel was not tracking RSN: `{rsn}`.", ephemeral=True)

@bot.tree.command(name="list_tracked_rsns", description="List all RSNs this channel is tracking.")
async def list_tracked_rsns(interaction: discord.Interaction):
    channel_id = interaction.channel_id
    tracked = [rsn for rsn, channels in rsn_subscriptions.items() if channel_id in channels]
    if tracked:
        rsn_list = ', '.join(tracked)
        await interaction.response.send_message(f"📄 This channel is tracking the following RSNs: {rsn_list}", ephemeral=True)
    else:
        await interaction.response.send_message("📄 This channel is not tracking any RSNs.", ephemeral=True)

@bot.event
async def on_message(message: discord.Message):
    await bot.process_commands(message)  # Ensure commands still work

    # Replace with your actual Dink channel ID
    DINK_CHANNEL_ID = 1429013195367911435

    if message.channel.id != DINK_CHANNEL_ID:
        return

    # Ignore messages from bots that are not webhooks
    if message.author.bot and message.webhook_id is None:
        return

    # Compile the message content and embed texts
    content = (message.content or "").lower()
    for embed in message.embeds:
        if embed.title:
            content += f" {embed.title.lower()}"
        if embed.description:
            content += f" {embed.description.lower()}"
        if embed.footer and embed.footer.text:
            content += f" {embed.footer.text.lower()}"
        if embed.author and embed.author.name:
            content += f" {embed.author.name.lower()}"
        for field in embed.fields:
            content += f" {field.name.lower()} {field.value.lower()}"

    # Check for RSN matches and forward messages
    for rsn, channels in rsn_subscriptions.items():
        if rsn in content:
            for channel_id in channels:
                try:
                    target_channel = await bot.fetch_channel(channel_id)
                    if message.embeds:
                        for embed in message.embeds:
                            await target_channel.send(embed=embed)
                    if message.attachments:
                        for attachment in message.attachments:
                            if attachment.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                                await target_channel.send(attachment.url)
                except Exception as e:
                    print(f"Error forwarding message to channel {channel_id}: {e}")
            break  # Stop after the first matching RSN


# Connect to MongoDB using the provided URI from Railway
mongo_uri = os.getenv("MONGO_URI")  # You should set this in your Railway environment variables
client = MongoClient(mongo_uri)

# Choose your database
db = client['MongoDB']  # Replace with the name of your database

# Access collections (equivalent to Firestore collections)
wallets_collection = db['wallets-yama']
orders_collection = db['orders-yama']
counters_collection = db["order_counters-yama"]  # New collection to track order ID

# The fixed orders posting channel
ORDERS_CHANNEL_ID = 1427198874078154822
# Allowed roles for commands
ALLOWED_ROLES = {1427205455565815869, 1427206792537964596, 1427206367915016213}

def has_permission(user: discord.Member):
    return any(role.id in ALLOWED_ROLES for role in user.roles)

async def log_command(interaction: discord.Interaction, command_name: str, details: str):
    # Mapping of servers to their respective log channels
    LOG_CHANNELS = {
        1426534299888254988: 1429030395495579680  # Server 1 → Log Channel 1
    }

    for guild_id, channel_id in LOG_CHANNELS.items():
        log_guild = interaction.client.get_guild(guild_id)  # Get the guild
        if log_guild:
            log_channel = log_guild.get_channel(channel_id)  # Get the log channel
            if log_channel:
                embed = discord.Embed(title="📜 Command Log", color=discord.Color.red())
                embed.add_field(name="👤 User", value=f"{interaction.user.mention} ({interaction.user.id})", inline=False)
                embed.add_field(name="💻 Command", value=command_name, inline=False)
                embed.add_field(name="📜 Details", value=details, inline=False)
                embed.set_footer(text=f"Used in: {interaction.guild.name}", icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
                await log_channel.send(embed=embed)
            else:
                print(f"⚠️ Log channel not found in {log_guild.name} ({channel_id})")
        else:
            print(f"⚠️ Log guild not found: {guild_id}")

# Syncing command tree for slash commands
@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands.")
    except Exception as e:
        print(f"Error syncing commands: {e}")

def get_wallet(user_id):
    # Attempt to fetch the user's wallet data from MongoDB
    wallet_data = wallets_collection.find_one({"user_id": user_id})

    # If the wallet doesn't exist in the database, create a new one with default values
    if not wallet_data:
        print(f"Wallet not found for {user_id}, creating new wallet...")
        wallet_data = {
            "user_id": user_id,
            "wallet": 0,    # Initialize with 0M
            "spent": 0,     # Initialize with 0M
            "deposit": 0    # Initialize with 0M
        }
        # Insert the new wallet into the database
        wallets_collection.insert_one(wallet_data)
        print(f"New wallet created for {user_id}: {wallet_data}")

    return wallet_data

# Function to update wallet in MongoDB
def update_wallet(user_id, field, value):
    # Make sure the wallet document exists before updating
    wallet_data = get_wallet(user_id)
    
    # If the wallet does not contain the required field, we initialize it with the correct value
    if field not in wallet_data:
        wallet_data[field] = 0  # Initialize the field if missing

    # Update wallet data by incrementing the field value
    wallets_collection.update_one(
        {"user_id": user_id},
        {"$inc": {field: value}},  # Increment the field (e.g., wallet, deposit, spent)
        upsert=True  # Insert a new document if one doesn't exist
    )

@bot.tree.command(name="wallet", description="Check a user's wallet balance")
async def wallet(interaction: discord.Interaction, user: discord.Member = None):
    # Define role IDs
    self_only_roles {1427208699688259607}
    allowed_roles = {1427205455565815869, 1427206792537964596, 1427206367915016213}

    # Check if user has permission
    user_roles = {role.id for role in interaction.user.roles}
    has_self_only_role = bool(self_only_roles & user_roles)  # User has at least one self-only role
    has_allowed_role = bool(allowed_roles & user_roles)  # User has at least one allowed role

    # If user has no valid role, deny access
    if not has_self_only_role and not has_allowed_role:
        await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
        return

    # If user has only a self-only role (and not an allowed role), force them to check their own wallet
    if has_self_only_role and not has_allowed_role:
        user = interaction.user  

    # Default to interaction user if no target user is specified
    if user is None:
        user = interaction.user

    # Fetch wallet data
    user_id = str(user.id)
    wallet_data = get_wallet(user_id)
    
    # Default missing fields to 0
    deposit_value = wallet_data.get('deposit', 0)
    wallet_value = wallet_data.get('wallet', 0)
    spent_value = wallet_data.get('spent', 0)

    # Get user's avatar (fallback to default image)
    default_thumbnail = "https://media.discordapp.net/attachments/1208792947232079955/1376855814735921212/discord_with_services_avatar.gif?ex=6836d866&is=683586e6&hm=c818d597519f4b2e55c77aeae4affbf0397e12591743e1069582f605c125f80c&="
    thumbnail_url = user.avatar.url if user.avatar else default_thumbnail

    # Create embed message
    embed = discord.Embed(title=f"{user.display_name}'s Wallet 💳", color=discord.Color.from_rgb(139, 0, 0))
    embed.set_thumbnail(url=thumbnail_url)
    embed.add_field(name="Deposit", value=f"```💳 {deposit_value}M```", inline=False)
    embed.add_field(name="Wallet", value=f"```💵 {wallet_value}M```", inline=False)
    embed.add_field(name="Spent", value=f"```📝 {spent_value}M```", inline=False)
    embed.set_image(url="https://media.discordapp.net/attachments/985890908027367474/1258798457318019153/Cynx_banner.gif?ex=67bf2b6b&is=67bdd9eb&hm=ac2c065a9b39c3526624f939f4af2b1457abb29bfb8d56a6f2ab3eafdb2bb467&=")

    # Ensure requester avatar exists
    requester_avatar = interaction.user.avatar.url if interaction.user.avatar else default_thumbnail
    embed.set_footer(text=f"Requested by {interaction.user.display_name}", icon_url=requester_avatar)

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="add_remove_spent", description="Add or remove spent value from a user's wallet")
@app_commands.choices(action=[
    discord.app_commands.Choice(name="Add", value="add"),
    discord.app_commands.Choice(name="Remove", value="remove")
])
async def add_remove_spent(interaction: discord.Interaction, user: discord.Member, action: str, value: float):
    if not has_permission(interaction.user):  # Check role permissions
        await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
        return

    user_id = str(user.id)
    wallet_data = get_wallet(user_id)
    
    # Default missing fields
    spent_value = wallet_data.get("spent", 0)

    if action == "remove":
        if spent_value < value:
            await interaction.response.send_message("⚠ Insufficient spent balance to remove!", ephemeral=True)
            return
        update_wallet(user_id, "spent", -value)
    else:
        update_wallet(user_id, "spent", value)

    # Fetch updated wallet data
    updated_wallet = get_wallet(user_id)
    spent_value = updated_wallet.get("spent", 0)
    
    # Check and assign roles for spending milestones
    await check_and_assign_roles(user, spent_value, interaction.client)

    # Create embed response
    embed = discord.Embed(title=f"{user.display_name}'s Wallet 💳", color=discord.Color.from_rgb(139, 0, 0))
    embed.set_thumbnail(url=user.avatar.url if user.avatar else user.default_avatar.url)
    embed.add_field(name="Spent", value=f"```📝 {spent_value:,}M```", inline=False)
    embed.set_footer(text=f"Updated by {interaction.user.display_name}", icon_url=interaction.user.avatar.url)

    await interaction.response.send_message(f"✅ {action.capitalize()}ed {value:,}M spent.", embed=embed)
    await log_command(interaction, "add_remove_spent", f"User: {user.mention} | Action: {action} | Value: {value:,}M")

async def check_and_assign_roles(user: discord.Member, spent_value: int, client):
    """
    Checks user's spent amount and assigns the correct role if they reach milestones.
    Sends a congrats message in the announcement channel.
    """
    role_milestones = {
        2000: 1429042499531440208,  # 1M+
        5000: 1429042669102825583,  # 4M+
        7000: 1429042742062743562,  # 5M+
        10000: 1429042988767510560,  # 7M+
        15000: 1429043052197969934,  # 9M+
        20000: 1429043118229028944 # 14M+
    }

    # Fetch the correct channel
    congrats_channel = client.get_channel(1429031269051924530)  # Ensure it's the correct ID
    if congrats_channel is None:
        try:
            congrats_channel = await client.fetch_channel(1429031269051924530)  
            print(f"[DEBUG] Successfully fetched channel: {congrats_channel.name} ({congrats_channel.id})")
        except discord.NotFound:
            print("[ERROR] Channel not found in API!")
            return
        except discord.Forbidden:
            print("[ERROR] Bot lacks permission to fetch the channel!")
            return
        except Exception as e:
            print(f"[ERROR] Unexpected error fetching channel: {e}")
            return

    print(f"[DEBUG] Checking roles for {user.display_name} | Spent: {spent_value}")

    for threshold, role_id in sorted(role_milestones.items()):
        role = user.guild.get_role(role_id)
        if not role:
            print(f"[ERROR] Role ID {role_id} not found in guild!")
            continue
        
        print(f"[DEBUG] Checking role {role.name} ({role_id}) for threshold {threshold}")

        if spent_value >= threshold and role not in user.roles:
            print(f"[DEBUG] Assigning role {role.name} to {user.display_name}")
            await user.add_roles(role)

            # Send congrats message
            print(f"[DEBUG] Sending congrats message for {user.display_name}")
            embed = discord.Embed(
            title="🎉 Congratulations!",
            description=f"{user.mention} has reached **{threshold:,}M+** spent and earned a new role!",
            color=discord.Color.gold()
            )
            embed.set_thumbnail(url=user.avatar.url if user.avatar else user.default_avatar.url)
            embed.add_field(name="🏅 New Role Earned:", value=f"{role.mention}", inline=False)
            embed.set_footer(text="Keep spending to reach new Lifetime Rank! ✨", icon_url="https://media.discordapp.net/attachments/1208792947232079955/1376855814735921212/discord_with_services_avatar.gif?ex=6836d866&is=683586e6&hm=c818d597519f4b2e55c77aeae4affbf0397e12591743e1069582f605c125f80c&=" )
            embed.set_author(name="✅ Grinders System ✅", icon_url="https://media.discordapp.net/attachments/1208792947232079955/1376855814735921212/discord_with_services_avatar.gif?ex=6836d866&is=683586e6&hm=c818d597519f4b2e55c77aeae4affbf0397e12591743e1069582f605c125f80c&=")
            await congrats_channel.send(embed=embed)


# /wallet_add_remove command
@bot.tree.command(name="wallet_add_remove", description="Add or remove value from a user's wallet")
@app_commands.choices(action=[
    discord.app_commands.Choice(name="Add", value="add"),
    discord.app_commands.Choice(name="Remove", value="remove")
])
async def wallet_add_remove(interaction: discord.Interaction, user: discord.Member, action: str, value: float):  
    if not has_permission(interaction.user):
        await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
        return
    user_id = str(user.id)
    
    # Fetch wallet data or default to zero if not found
    wallet_data = get_wallet(user_id) or {"wallet": 0, "deposit": 0, "spent": 0}
    
    # Get individual values with defaults
    wallet_value = wallet_data.get("wallet", 0)
    deposit_value = wallet_data.get("deposit", 0)
    spent_value = wallet_data.get("spent", 0)

    # Action handling
    if action == "remove":
        if wallet_value < value:
            await interaction.response.send_message("⚠ Insufficient balance to remove!", ephemeral=True)
            return
        update_wallet(user_id, "wallet", -value)
    else:
        update_wallet(user_id, "wallet", value)

    # Fetch updated values
    updated_wallet = get_wallet(user_id) or {"wallet": 0, "deposit": 0, "spent": 0}
    wallet_value = updated_wallet.get("wallet", 0)
    deposit_value = updated_wallet.get("deposit", 0)
    spent_value = updated_wallet.get("spent", 0)

    # Embed with modern design
    embed = discord.Embed(title=f"{user.display_name}'s Wallet 💳", color=discord.Color.from_rgb(139, 0, 0))
    embed.set_thumbnail(url=user.avatar.url if user.avatar else user.default_avatar.url)

    embed.add_field(name="Deposit", value=f"```💳 {deposit_value:,}M```", inline=False)
    embed.add_field(name="Wallet", value=f"```💵 {wallet_value:,}M```", inline=False)
    embed.add_field(name="Spent", value=f"```📝 {spent_value:,}M```", inline=False)
    embed.set_image(url="https://media.discordapp.net/attachments/985890908027367474/1258798457318019153/Cynx_banner.gif?ex=67bf2b6b&is=67bdd9eb&hm=ac2c065a9b39c3526624f939f4af2b1457abb29bfb8d56a6f2ab3eafdb2bb467&=")
    embed.set_footer(text=f"Requested by {interaction.user.display_name}", icon_url=interaction.user.avatar.url)
    
    await interaction.response.send_message(f"✅ {action.capitalize()}ed {value:,}M.", embed=embed)
    await log_command(interaction, "wallet_add_remove", f"User: {user.mention} | Action: {action} | Value: {value:,}M")

@bot.tree.command(name="deposit", description="Set or remove a user's deposit value")
@app_commands.choices(action=[
    discord.app_commands.Choice(name="Set", value="set"),
    discord.app_commands.Choice(name="Remove", value="remove")
])
async def deposit(interaction: discord.Interaction, user: discord.Member, action: str, value: int):
    if not has_permission(interaction.user):
        await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
        return
    user_id = str(user.id)
    
    # Fetch current wallet data
    wallet_data = get_wallet(user_id)

    # Ensure the deposit field exists
    current_deposit = wallet_data.get("deposit", 0)

    if action == "set":
        new_deposit = current_deposit + value  # Add the deposit value
    elif action == "remove":
        if value > current_deposit:
            await interaction.response.send_message(f"⚠ Cannot remove {value}M. The user only has {current_deposit}M in deposit.", ephemeral=True)
            return
        new_deposit = current_deposit - value  # Subtract the deposit value

    # Update deposit value in MongoDB
    update_wallet(user_id, "deposit", new_deposit - current_deposit)

    # Fetch updated wallet data
    updated_wallet = get_wallet(user_id)

    # Format values
    deposit_value = f"```💳 {updated_wallet['deposit']:,}M```"
    wallet_value = f"```💵 {updated_wallet['wallet']:,}M```"
    spent_value = f"```📝 {updated_wallet['spent']:,}M```"

    # Create an embed
    embed = discord.Embed(title=f"{user.display_name}'s Wallet 💳", color=discord.Color.from_rgb(139, 0, 0))
    embed.set_thumbnail(url=user.avatar.url if user.avatar else user.default_avatar.url)
    embed.add_field(name="Deposit", value=deposit_value, inline=False)
    embed.add_field(name="Wallet", value=wallet_value, inline=False)
    embed.add_field(name="Spent", value=spent_value, inline=False)
    embed.set_footer(text=f"Requested by {interaction.user.display_name}", icon_url=interaction.user.avatar.url)
    embed.set_image(url="https://media.discordapp.net/attachments/985890908027367474/1258798457318019153/Cynx_banner.gif?ex=67bf2b6b&is=67bdd9eb&hm=ac2c065a9b39c3526624f939f4af2b1457abb29bfb8d56a6f2ab3eafdb2bb467&=")
    # Send response
    await interaction.response.send_message(f"✅ {action.capitalize()}ed deposit value for {user.name} by {value:,}M.", embed=embed)
    await log_command(interaction, "Deposit Set/Remove", f"User: {user.mention} (`{user.id}`)\nAction: {action.capitalize()}\nAmount: {value:,}M")


@bot.tree.command(name="tip", description="Tip M to another user.")
@app_commands.describe(user="User to tip", value="Value in M")
async def tip(interaction: discord.Interaction, user: discord.Member, value: int):
    sender_id = str(interaction.user.id)  # Convert IDs to strings for MongoDB
    recipient_id = str(user.id)

    # Fetch wallet data or default to zero if not found
    sender_wallet = get_wallet(sender_id) or {"wallet": 0, "deposit": 0, "spent": 0}
    recipient_wallet = get_wallet(recipient_id) or {"wallet": 0, "deposit": 0, "spent": 0}

    # Ensure sender has enough balance
    if sender_wallet["wallet"] < value:
        await interaction.response.send_message("❌ You don't have enough M to tip!", ephemeral=True)
        return

    # Update wallets in MongoDB
    update_wallet(sender_id, "wallet", -value)  # Subtract from sender
    update_wallet(recipient_id, "wallet", value)  # Add to recipient

    # Fetch updated data after transaction
    sender_wallet = get_wallet(sender_id) or {"wallet": 0, "deposit": 0, "spent": 0}
    recipient_wallet = get_wallet(recipient_id) or {"wallet": 0, "deposit": 0, "spent": 0}

    # Tip message (public)
    tip_message = f"💸 {interaction.user.mention} tipped {user.mention} **{value:,}M**!"

    # Format numbers with commas (e.g., 1,000M)
    sender_deposit = f"```💳 {sender_wallet['deposit']:,}M```"
    sender_wallet_value = f"```💵 {sender_wallet['wallet']:,}M```"
    sender_spent = f"```📝 {sender_wallet['spent']:,}M```"

    recipient_deposit = f"```💳 {recipient_wallet['deposit']:,}M```"
    recipient_wallet_value = f"```💵 {recipient_wallet['wallet']:,}M```"
    recipient_spent = f"```📝 {recipient_wallet['spent']:,}M```"

    # Sender's wallet embed
    sender_embed = discord.Embed(title=f"{interaction.user.display_name}'s Updated Wallet 💳", color=discord.Color.from_rgb(139, 0, 0))
    sender_embed.set_thumbnail(url=interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url)
    sender_embed.add_field(name="Deposit", value=sender_deposit, inline=False)
    sender_embed.add_field(name="Wallet", value=sender_wallet_value, inline=False)
    sender_embed.add_field(name="Spent", value=sender_spent, inline=False)
    sender_embed.set_footer(text=f"Tip sent to {user.display_name}", icon_url=user.avatar.url)
    sender_embed.set_image(url="https://media.discordapp.net/attachments/985890908027367474/1258798457318019153/Cynx_banner.gif?ex=67c3c8ab&is=67c2772b&hm=bb9222e70e1ddc5d63f9c5c4452b9499a07cbab1d0c501fcf4cc6e8a060d736d&=")
    # Recipient's wallet embed
    recipient_embed = discord.Embed(title=f"{user.display_name}'s Updated Wallet 💳", color=discord.Color.from_rgb(139, 0, 0))
    recipient_embed.set_thumbnail(url=user.avatar.url if user.avatar else user.default_avatar.url)
    recipient_embed.add_field(name="Deposit", value=recipient_deposit, inline=False)
    recipient_embed.add_field(name="Wallet", value=recipient_wallet_value, inline=False)
    recipient_embed.add_field(name="Spent", value=recipient_spent, inline=False)
    recipient_embed.set_footer(text=f"Tip received from {interaction.user.display_name}", icon_url=interaction.user.avatar.url)
    recipient_embed.set_image(url="https://media.discordapp.net/attachments/985890908027367474/1258798457318019153/Cynx_banner.gif?ex=67bf2b6b&is=67bdd9eb&hm=ac2c065a9b39c3526624f939f4af2b1457abb29bfb8d56a6f2ab3eafdb2bb467&=")
    # Send the tip message publicly
    await interaction.response.send_message(tip_message)

    # Send updated wallets in the channel
    await interaction.channel.send(embed=sender_embed)
    await interaction.channel.send(embed=recipient_embed)

    # Send DM to sender with embed & tip message
    try:
        await interaction.user.send(f"✅ You sent **{value:,}M** as a tip to {user.mention}!", embed=sender_embed)
    except discord.Forbidden:
        await interaction.channel.send(f"⚠️ {interaction.user.mention}, I couldn't DM your updated wallet!")

    # Send DM to recipient with embed & received message
    try:
        await user.send(f"🎉 You received **{value:,}M** as a tip from {interaction.user.mention}!", embed=recipient_embed)
    except discord.Forbidden:
        await interaction.channel.send(f"⚠️ {user.mention}, I couldn't DM your updated wallet!")

class OrderButton(View):
    def __init__(self, order_id, deposit_required, customer_id, original_channel_id, message_id, post_channel_id):
        super().__init__(timeout=None)
        self.order_id = order_id
        self.deposit_required = deposit_required
        self.customer_id = customer_id
        self.original_channel_id = original_channel_id
        self.message_id = message_id
        self.post_channel_id = post_channel_id

    @discord.ui.button(label="Apply For The Job✅", style=discord.ButtonStyle.primary)
    async def accept_job(self, interaction: Interaction, button: discord.ui.Button):
        order = orders_collection.find_one({"_id": self.order_id})
        if not order:
            await interaction.response.send_message("Order not found!", ephemeral=True)
            return

        if order.get("worker"):
            await interaction.response.send_message("This order has already been claimed!", ephemeral=True)
            return

        user_wallet = get_wallet(str(interaction.user.id))
        if user_wallet.get("deposit", 0) < self.deposit_required:
            await interaction.response.send_message("You do not have enough deposit to claim this order!", ephemeral=True)
            return

        # ✅ Send application notification and store the message object
        bot_spam_channel = bot.get_channel(1429031269051924530)
        if bot_spam_channel:
            embed = discord.Embed(title="📌 Job Application Received", color=discord.Color.from_rgb(139, 0, 0))
            embed.add_field(name="👷 Applicant", value=interaction.user.mention, inline=True)
            embed.add_field(name="🆔 Order ID", value=str(self.order_id), inline=True)
            embed.set_footer(text="Choose to Accept or Reject the applicant.")

            # ✅ Store the message object
            message_obj = await bot_spam_channel.send(embed=embed)

            # ✅ Pass message_obj to ApplicationView
            application_view = ApplicationView(
                self.order_id, interaction.user.id, self.customer_id,
                self.original_channel_id, self.message_id, self.post_channel_id,
                self.deposit_required, message_obj
            )
            await message_obj.edit(view=application_view)  # Attach the buttons

        await interaction.response.send_message("Your application has been submitted for review!", ephemeral=True)

class ApplicationView(View):
    def __init__(self, order_id, applicant_id, customer_id, original_channel_id, message_id, post_channel_id, deposit_required, message_obj):
        super().__init__(timeout=None)
        self.order_id = order_id
        self.applicant_id = applicant_id  # ✅ This is the worker
        self.customer_id = customer_id
        self.original_channel_id = original_channel_id
        self.message_id = message_id
        self.post_channel_id = post_channel_id
        self.deposit_required = deposit_required  
        self.message_obj = message_obj  # Store the applicant's message object

    @discord.ui.button(label="✅ Accept", style=discord.ButtonStyle.success)
    async def accept_applicant(self, interaction: Interaction, button: discord.ui.Button):
        await interaction.response.defer()

        # ✅ Fetch order from database
        order = orders_collection.find_one({"_id": self.order_id})
        if not order:
            await interaction.followup.send("Order not found!", ephemeral=True)
            return

        if order.get("worker"):
            await interaction.followup.send("This order has already been claimed!", ephemeral=True)
            return

        # ✅ Assign worker in the database
        orders_collection.update_one({"_id": self.order_id}, {"$set": {"worker": self.applicant_id}})

        # ✅ Retrieve actual values for the embed
        description = order.get("description", "No description provided.")
        value = order.get("value", "N/A")
        deposit_required = order.get("deposit_required", "N/A")

        # ✅ Grant worker access to the original order channel
        original_channel = bot.get_channel(self.original_channel_id)
        if original_channel:
            worker = interaction.guild.get_member(self.applicant_id)
            if worker:
                await original_channel.set_permissions(worker, read_messages=True, send_messages=True)
            else:
                await interaction.followup.send("❌ Could not find the applicant in the server!", ephemeral=True)
                return

            # ✅ Corrected embed with actual order details
            embed = discord.Embed(title="👷‍♂️ Order Claimed", color=discord.Color.from_rgb(139, 0, 0))
            embed.set_thumbnail(url="https://media.discordapp.net/attachments/1208792947232079955/1376855814735921212/discord_with_services_avatar.gif?ex=6836d866&is=683586e6&hm=c818d597519f4b2e55c77aeae4affbf0397e12591743e1069582f605c125f80c&=")
            embed.set_author(name="✅ Grinders System ✅", icon_url="https://media.discordapp.net/attachments/1208792947232079955/1376855814735921212/discord_with_services_avatar.gif?ex=6836d866&is=683586e6&hm=c818d597519f4b2e55c77aeae4affbf0397e12591743e1069582f605c125f80c&=")
            embed.add_field(name="📕 Description", value=description, inline=False)
            embed.add_field(name="👷 Worker", value=f"<@{self.applicant_id}>", inline=True)
            embed.add_field(name="📌 Customer", value=f"<@{self.customer_id}>", inline=True)
            embed.add_field(name="💵 Deposit Required", value=f"**```{deposit_required}M```**", inline=True)
            embed.add_field(name="💰 Order Value", value=f"**```{value}M```**", inline=True)
            embed.add_field(name="🆔 Order ID", value=self.order_id, inline=True)
            embed.set_image(url="https://media.discordapp.net/attachments/985890908027367474/1258798457318019153/Cynx_banner.gif")
            embed.set_footer(text="Grinders System", icon_url="https://media.discordapp.net/attachments/1208792947232079955/1376855814735921212/discord_with_services_avatar.gif?ex=6836d866&is=683586e6&hm=c818d597519f4b2e55c77aeae4affbf0397e12591743e1069582f605c125f80c&=")
            sent_message = await original_channel.send(embed=embed)
            await sent_message.pin()

            # ✅ Notify customer and worker
            claim_message = f"**Hello! <@{self.customer_id}>, <@{self.applicant_id}> is Assigned To Be Your Worker For This Job. You Can Provide Your Account Info Using This Command `/inf`**"
            await original_channel.send(claim_message)

        # ✅ Delete the original job post
        post_channel = bot.get_channel(self.post_channel_id)
        if post_channel:
            try:
                message = await post_channel.fetch_message(self.message_id)
                await message.delete()
            except:
                pass

        # ✅ Delete the applicant's message
        try:
            await self.message_obj.delete()
        except:
            pass

        await interaction.followup.send("Applicant accepted and added to the order channel!", ephemeral=True)

    @discord.ui.button(label="❌ Reject", style=discord.ButtonStyle.danger)
    async def reject_applicant(self, interaction: Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        await interaction.followup.send(f"Applicant <@{self.applicant_id}> has been rejected.", ephemeral=True)

        # ✅ Delete the applicant's message
        try:
            await self.message_obj.delete()
        except:
            pass




@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

    # Reload buttons for active orders
    for order in orders_collection.find({"worker": None}):  # Only for unclaimed orders
        channel = bot.get_channel(order["channel_id"])
        if channel:
            try:
                message = await channel.fetch_message(order["message_id"])
                view = OrderButton(order["_id"], order["deposit_required"], order["customer"], order["original_channel_id"], order["message_id"])
                await message.edit(view=view)
            except discord.NotFound:
                print(f"Order message {order['message_id']} not found, skipping.")
    
    print("Re-registered all active order buttons!")

def get_next_order_id():
    counter = counters_collection.find_one({"_id": "order_counter"})
    
    if not counter:
        # Initialize the counter to 46 if it does not exist
        counters_collection.insert_one({"_id": "order_counter", "seq": 46})
        return 46  # First order ID should be 46

    # Increment and return the next order ID
    counter = counters_collection.find_one_and_update(
        {"_id": "order_counter"},
        {"$inc": {"seq": 1}},  # Increment the existing counter
        return_document=ReturnDocument.AFTER
    )
    return counter["seq"]

@bot.tree.command(name="post", description="Post a new order.")
@app_commands.describe(
    customer="The customer for the order",
    value="The value of the order (in millions)",
    deposit_required="The deposit required for the order",
    holder="The holder of the order",
    channel="The channel to post the order (mention or ID)",
    description="Description of the order",
    image="Image URL to show at the bottom of the embed"
)
async def post(interaction: discord.Interaction, customer: discord.Member, value: int, deposit_required: int, holder: discord.Member, channel: discord.TextChannel, description: str, image: str = None):
    if not has_permission(interaction.user):
        await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
        return
    channel_id = channel.id
    order_id = get_next_order_id()
    post_channel_id = interaction.channel.id  # Store the channel where /post was used

    # Define role IDs
    role1_id = 1427208346771001426
    role2_id = 1208792946401615902

    # Check if roles exist in the guild
    role1 = discord.utils.get(interaction.guild.roles, id=role1_id)
    role2 = discord.utils.get(interaction.guild.roles, id=role2_id)

    # Determine which role to ping
    if role1:
        role_ping = role1.mention
    elif role2:
        role_ping = role2.mention
    else:
        role_ping = None  # No roles found, so no ping

    embed = discord.Embed(title="💎 New Order 💎", color=discord.Color.from_rgb(139, 0, 0))
    embed.set_thumbnail(url="https://media.discordapp.net/attachments/1208792947232079955/1376855814735921212/discord_with_services_avatar.gif?ex=6836d866&is=683586e6&hm=c818d597519f4b2e55c77aeae4affbf0397e12591743e1069582f605c125f80c&=")
    embed.set_author(name="💼 Order Posted", icon_url="https://media.discordapp.net/attachments/1208792947232079955/1376855814735921212/discord_with_services_avatar.gif?ex=6836d866&is=683586e6&hm=c818d597519f4b2e55c77aeae4affbf0397e12591743e1069582f605c125f80c&=")
    embed.description = f"📕**Description:**\n {description}"
    embed.add_field(name="💰 Value", value=f"**```{value}M```**", inline=True)
    embed.add_field(name="💵 Deposit Required", value=f"**```{deposit_required}M```**", inline=True)
    embed.add_field(name="🕵️‍♂️ Holder", value=holder.mention, inline=True)
    if image:
        embed.set_image(url=image)
    else:
        embed.set_image(url="https://media.discordapp.net/attachments/985890908027367474/1258798457318019153/Cynx_banner.gif")
    embed.set_footer(text=f"Order ID: {order_id}", icon_url="https://media.discordapp.net/attachments/1208792947232079955/1376855814735921212/discord_with_services_avatar.gif?ex=6836d866&is=683586e6&hm=c818d597519f4b2e55c77aeae4affbf0397e12591743e1069582f605c125f80c&=")

    channel_to_post = interaction.guild.get_channel(channel_id)
    if channel_to_post:
        # Send message with role ping if a role exists
        if role_ping:
            message = await channel_to_post.send(f"{role_ping}", embed=embed)
        else:
            message = await channel_to_post.send(embed=embed)

        # Add order button functionality
        await message.edit(view=OrderButton(order_id, deposit_required, customer.id, post_channel_id, message.id, channel_id))

        orders_collection.insert_one({
            "_id": order_id,
            "customer": customer.id,
            "worker": None,
            "value": value,
            "deposit_required": deposit_required,
            "holder": holder.id,
            "message_id": message.id,
            "channel_id": channel.id,
            "original_channel_id": post_channel_id,  # Store where /post was used
            "description": description,
            "posted_by": interaction.user.id  # ✅ store who used /post
        })

        # Give customer role automatically
        customer_role_id = 1429051114137059449
        customer_role = discord.utils.get(interaction.guild.roles, id=customer_role_id)
        if customer_role:
            try:
                await customer.add_roles(customer_role, reason="Customer made a post order")
                print(f"Gave {customer} the customer role.")
            except Exception as e:
                print(f"Failed to give customer role to {customer}: {e}")

        confirmation_embed = embed.copy()
        confirmation_embed.title = "Order Posted"
        await interaction.channel.send(embed=confirmation_embed)
        await interaction.response.send_message("Order posted successfully!", ephemeral=True)
        await log_command(interaction, "Order Posted", f"Customer: {customer.mention} (`{customer.id}`)\nValue: {value:,}M\nDeposit Required: {deposit_required:,}M\nHolder: {holder.mention} (`{holder.id}`)\nChannel: {channel.mention}\nDescription: {description}")
    else:
        await interaction.response.send_message("Invalid channel specified.", ephemeral=True)

@bot.tree.command(name="set", description="Set an order directly with worker.")
@app_commands.describe(
    customer="The customer for the order",
    value="The value of the order (in millions)",
    deposit_required="The deposit required for the order",
    holder="The holder of the order",
    description="Description of the order",
    worker="The worker to assign",
    image="Optional image URL to show at the bottom of the embed"
)
async def set_order(interaction: Interaction, customer: discord.Member, value: int, deposit_required: int, holder: discord.Member, description: str, worker: discord.Member, image: str = None):
    if not has_permission(interaction.user):
        await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
        return
    order_id = get_next_order_id()
    original_channel_id = interaction.channel.id

    embed = Embed(title="Order Set", color=discord.Color.from_rgb(139, 0, 0))
    embed.set_thumbnail(url="https://media.discordapp.net/attachments/1208792947232079955/1376855814735921212/discord_with_services_avatar.gif?ex=6836d866&is=683586e6&hm=c818d597519f4b2e55c77aeae4affbf0397e12591743e1069582f605c125f80c&=")
    embed.set_author(name="🛠️ Order Set", icon_url="https://media.discordapp.net/attachments/1208792947232079955/1376855814735921212/discord_with_services_avatar.gif?ex=6836d866&is=683586e6&hm=c818d597519f4b2e55c77aeae4affbf0397e12591743e1069582f605c125f80c&=")
    embed.description = f"📕**Description:**\n {description}"
    embed.add_field(name="📌 Customer", value=customer.mention, inline=True)
    embed.add_field(name="💰 Value", value=f"**```{value}M```**", inline=True)
    embed.add_field(name="💵 Deposit Required", value=f"**```{deposit_required}M```**", inline=True)
    embed.add_field(name="🕵️‍♂️ Holder", value=holder.mention, inline=True)
    embed.add_field(name="👷 Worker", value=worker.mention, inline=True)

    if image:
        embed.set_image(url=image)
    else:
        embed.set_image(url="https://media.discordapp.net/attachments/985890908027367474/1258798457318019153/Cynx_banner.gif?ex=67bf2b6b&is=67bdd9eb&hm=ac2c065a9b39c3526624f939f4af2b1457abb29bfb8d56a6f2ab3eafdb2bb467&=")

    embed.set_footer(text=f"📜 Order ID: {order_id}", icon_url="https://media.discordapp.net/attachments/1208792947232079955/1376855814735921212/discord_with_services_avatar.gif?ex=6836d866&is=683586e6&hm=c818d597519f4b2e55c77aeae4affbf0397e12591743e1069582f605c125f80c&=")

    original_channel = bot.get_channel(original_channel_id)
    if original_channel:
        message = await original_channel.send(embed=embed)
        message_id = message.id
        await message.pin()

    orders_collection.insert_one({
        "_id": order_id,
        "customer": customer.id,
        "worker": worker.id,
        "value": value,
        "deposit_required": deposit_required,
        "holder": holder.id,
        "message_id": message_id,
        "channel_id": original_channel.id,
        "original_channel_id": original_channel_id,
        "description": description,
        "image": image, # Store image in database
        "posted_by": interaction.user.id  # ✅ store who used /post
    })
    # Give customer role automatically
    customer_role_id = 1429051114137059449
    customer_role = discord.utils.get(interaction.guild.roles, id=customer_role_id)
    if customer_role:
        try:
            await customer.add_roles(customer_role, reason="Customer had an order set")
            print(f"Gave {customer} the customer role.")
        except Exception as e:
            print(f"Failed to give customer role to {customer}: {e}")

    await interaction.response.send_message(f"Order set with Worker {worker.mention}!", ephemeral=True)
    await log_command(interaction, "Order Set", f"Customer: {customer.mention} (`{customer.id}`)\nWorker: {worker.mention} (`{worker.id}`)\nValue: {value:,}M\nDeposit Required: {deposit_required:,}M\nHolder: {holder.mention} (`{holder.id}`)\nDescription: {description}")

    if original_channel:
        try:
            await original_channel.set_permissions(worker, read_messages=True, send_messages=True)
            print(f"Permissions granted to {worker.name} in {original_channel.name}.")
        except Exception as e:
            print(f"Failed to set permissions for {worker.name} in {original_channel.name}: {e}")
# /complete command
@bot.tree.command(name="complete", description="Mark an order as completed.")
async def complete(interaction: Interaction, order_id: int):
    if not has_permission(interaction.user):
        await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
        return
    
    order = orders_collection.find_one({"_id": order_id})
    if not order:
        await interaction.response.send_message("❌ Order not found!", ephemeral=True)
        return
    
    if order.get("status") == "completed":
        await interaction.response.send_message("⚠️ This order has already been marked as completed.", ephemeral=True)
        return

    # Extract customer ID and worker ID
    customer_id = str(order["customer"])
    worker_id = str(order["worker"])
    
    # Transfer funds
    update_wallet(str(order["customer"]), "spent", order["value"])
    
    total_value = order["value"]
    worker_payment = round(total_value * 0.8, 1)
    commission_value = round(total_value * 0.175, 1)
    helper_payment = round(total_value * 0.025, 1)

    update_wallet(str(order["worker"]), "wallet", float(worker_payment))
    update_wallet("server", "commission", float(commission_value))
    update_wallet(str(order.get("posted_by", interaction.user.id)), "wallet", float(helper_payment))

    orders_collection.update_one({"_id": order_id}, {"$set": {"status": "completed"}})

    # Get the Discord user for role checks
    guild = interaction.guild
    customer = guild.get_member(int(customer_id))  # Fetch customer from Discord server

    if customer:
        spent_value = order["value"]  # Assuming "value" represents the amount spent
        await check_and_assign_roles(customer, spent_value, interaction.client)
    else:
        print(f"[ERROR] Customer {customer_id} not found in the Discord server.")

    # Notify the original channel
    original_channel = bot.get_channel(order["original_channel_id"])
    if original_channel:
        embed = Embed(title="✅ Order Completed", color=discord.Color.from_rgb(139, 0, 0))
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/1208792947232079955/1376855814735921212/discord_with_services_avatar.gif?ex=6836d866&is=683586e6&hm=c818d597519f4b2e55c77aeae4affbf0397e12591743e1069582f605c125f80c&=")
        embed.set_author(name="Grinders System", icon_url="https://media.discordapp.net/attachments/1208792947232079955/1376855814735921212/discord_with_services_avatar.gif?ex=6836d866&is=683586e6&hm=c818d597519f4b2e55c77aeae4affbf0397e12591743e1069582f605c125f80c&=")
        embed.add_field(name="📕 Description", value=order.get("description", "No description provided."), inline=False)
        embed.add_field(name="👷 Worker", value=f"<@{order['worker']}>", inline=True)
        embed.add_field(name="📌 Customer", value=f"<@{order['customer']}>", inline=True)
        embed.add_field(name="💰 Value", value=f"**```{order['value']}M```**", inline=True)
        embed.add_field(name="👷‍♂️ Worker Payment", value=f"**```{worker_payment}M```**", inline=True)
        embed.add_field(name="📦 Server Commission", value=f"**```{commission_value}M```**", inline=True)
        embed.add_field(name="📬 Helper Reward", value=f"**```{helper_payment}M```**", inline=True)
        embed.set_image(url="https://media.discordapp.net/attachments/985890908027367474/1258798457318019153/Cynx_banner.gif?ex=67bf2b6b&is=67bdd9eb&hm=ac2c065a9b39c3526624f939f4af2b1457abb29bfb8d56a6f2ab3eafdb2bb467&=")
        embed.set_footer(text=f"📜 Order ID: {order_id}", icon_url="https://media.discordapp.net/attachments/1208792947232079955/1376855814735921212/discord_with_services_avatar.gif?ex=6836d866&is=683586e6&hm=c818d597519f4b2e55c77aeae4affbf0397e12591743e1069582f605c125f80c&=")
        await original_channel.send(embed=embed)
    
    # NEW: security embed (small, loud, mentions customer inside)
        security = Embed(
            title="🔒 Security Reminder",
            description=(
                f"**<@{customer_id}>**\n\n"
                "__Please do the following immediately:__\n"
                "• **Change your account password**\n"
                "• **End All Sessions**\n"
                "• **Change your bank PIN** (Optional)\n"
            ),
            color=discord.Color.gold()
        )
        security.set_thumbnail(url="https://media.discordapp.net/attachments/1208792947232079955/1376855814735921212/discord_with_services_avatar.gif?ex=6836d866&is=683586e6&hm=c818d597519f4b2e55c77aeae4affbf0397e12591743e1069582f605c125f80c&=")                 # same image as thumbnail
        security.set_author(name="Grinders System", icon_url="https://media.discordapp.net/attachments/1208792947232079955/1376855814735921212/discord_with_services_avatar.gif?ex=6836d866&is=683586e6&hm=c818d597519f4b2e55c77aeae4affbf0397e12591743e1069582f605c125f80c&=")  # author icon = thumb
        security.set_footer(text="Grinders System • Please confirm once done", icon_url="https://media.discordapp.net/attachments/1208792947232079955/1376855814735921212/discord_with_services_avatar.gif?ex=6836d866&is=683586e6&hm=c818d597519f4b2e55c77aeae4affbf0397e12591743e1069582f605c125f80c&=")  # footer icon = thumb
        security.add_field(
            name="⚠️ Action Required",
            value="**This is for your safety. Please confirm here once changed.**",
            inline=False
        )
        # Mention in message content too to nudge notification, while still included IN the embed:
        await original_channel.send(content=f"<@{customer_id}>", embed=security)
    
    # DM the worker
    worker = bot.get_user(order["worker"])
    if worker:
        dm_embed = Embed(title="✅ Order Completed", color=discord.Color.from_rgb(139, 0, 0))
        dm_embed.set_thumbnail(url="https://media.discordapp.net/attachments/1208792947232079955/1376855814735921212/discord_with_services_avatar.gif?ex=6836d866&is=683586e6&hm=c818d597519f4b2e55c77aeae4affbf0397e12591743e1069582f605c125f80c&=")
        dm_embed.set_author(name="Grinders System", icon_url="https://media.discordapp.net/attachments/1208792947232079955/1376855814735921212/discord_with_services_avatar.gif?ex=6836d866&is=683586e6&hm=c818d597519f4b2e55c77aeae4affbf0397e12591743e1069582f605c125f80c&=")
        dm_embed.add_field(name="📕 Description", value=order.get("description", "No description provided."), inline=False)
        dm_embed.add_field(name="💰 Value", value=f"**```{order['value']}M```**", inline=True)
        dm_embed.add_field(name="👷‍♂️ Your Payment", value=f"**```{worker_payment}M```**", inline=True)
        dm_embed.set_image(url="https://media.discordapp.net/attachments/985890908027367474/1258798457318019153/Cynx_banner.gif")
        dm_embed.set_footer(text=f"📜 Order ID: {order_id}", icon_url="https://media.discordapp.net/attachments/1208792947232079955/1376855814735921212/discord_with_services_avatar.gif?ex=6836d866&is=683586e6&hm=c818d597519f4b2e55c77aeae4affbf0397e12591743e1069582f605c125f80c&=")
        try:
            await worker.send(embed=dm_embed)
        except discord.Forbidden:
            print(f"[WARNING] Could not DM worker {worker.id}. DMs may be closed.")

    # Notify the helper in a specific channel
    helper_id = str(order.get("posted_by", interaction.user.id))
    helper_channel = bot.get_channel(1427403309475434649)

    if helper_channel:
        helper_embed = Embed(title="🎯 Helper Commission Summary", color=discord.Color.gold())
        helper_embed.set_thumbnail(url="https://media.discordapp.net/attachments/1208792947232079955/1376855814735921212/discord_with_services_avatar.gif")
        helper_embed.set_author(name="Grinders System", icon_url="https://media.discordapp.net/attachments/1208792947232079955/1376855814735921212/discord_with_services_avatar.gif")
        helper_embed.add_field(name="📜 Order ID", value=f"`{order_id}`", inline=True)
        helper_embed.add_field(name="💰 Order Value", value=f"**```{order['value']}M```**", inline=True)
        helper_embed.add_field(name="🎁 Your Share", value=f"**```{helper_payment}M```**", inline=True)
        helper_embed.set_footer(text=f"Grinders System", icon_url="https://media.discordapp.net/attachments/1208792947232079955/1376855814735921212/discord_with_services_avatar.gif")
        try:
            await helper_channel.send(f"<@{helper_id}>", embed=helper_embed)
        except Exception as e:
            print(f"[ERROR] Failed to send helper embed: {e}")

    await interaction.response.send_message("Order marked as completed!", ephemeral=True)
    await log_command(interaction, "Order Completed", (
        f"Order ID: {order_id}\nMarked by: {interaction.user.mention} (`{interaction.user.id}`)\n"
        f"Worker: <@{order['worker']}> (`{order['worker']}`)\n"
        f"Customer: <@{order['customer']}> (`{order['customer']}`)\n"
        f"Value: {total_value}M\nWorker Payment: {worker_payment}M\n"
        f"Server Commission: {commission_value}M\nHelper Reward: {helper_payment}M"
     ))

# 📌 /order_deletion command
@bot.tree.command(name="order_deletion", description="Delete an order.")
async def order_deletion(interaction: Interaction, order_id: int):
    if not has_permission(interaction.user):
        await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
        return
    order = orders_collection.find_one({"_id": order_id})
    
    if not order:
        await interaction.response.send_message("❌ Order not found!", ephemeral=True)
        return

    # Delete the order message in the orders channel
    order_channel = bot.get_channel(order["channel_id"])
    if order_channel:
        try:
            message = await order_channel.fetch_message(order["message_id"])
            await message.delete()
        except discord.NotFound:
            print(f"⚠️ Message for order {order_id} not found in orders channel. Skipping deletion.")

    # Delete the original post message in the interaction channel
    original_channel = bot.get_channel(order["original_channel_id"])
    if original_channel:
        try:
            original_message = await original_channel.fetch_message(order["message_id"])
            await original_message.delete()
        except discord.NotFound:
            print(f"⚠️ Original message for order {order_id} not found. Skipping deletion.")

    # Remove the order from MongoDB
    orders_collection.delete_one({"_id": order_id})
    
    await interaction.response.send_message(f"✅ Order {order_id} has been successfully deleted.", ephemeral=True)
    await log_command(interaction, "Order Deleted", f"Order ID: {order_id}\nDeleted by: {interaction.user.mention} (`{interaction.user.id}`)")

@bot.tree.command(name="view_order", description="View details of an order")
async def view_order(interaction: discord.Interaction, order_id: int):
    # Required role IDs
    allowed_roles = {1208792946401615900, 1208792946430836736, 1211406868480532571}

    # Check if user has at least one of the required roles
    if not any(role.id in allowed_roles for role in interaction.user.roles):
        await interaction.response.send_message("❌ You do not have permission to use this command.", ephemeral=True)
        return

    order = orders_collection.find_one({"_id": order_id})
    
    if not order:
        await interaction.response.send_message("❌ Order not found.", ephemeral=True)
        return

    # Extract values safely, handling possible None values
    worker_id = order.get("worker", {}).get("low") if isinstance(order.get("worker"), dict) else order.get("worker", "Not Assigned")
    customer_id = order.get("customer", {}).get("low") if isinstance(order.get("customer"), dict) else order.get("customer", "Unknown")
    holder_id = order.get("holder", {}).get("low") if isinstance(order.get("holder"), dict) else order.get("holder", "N/A")
    
    deposit = order.get("deposit_required", 0)
    value = order.get("value", 0)
    description = order.get("description", "No description provided")

    # Get status, default to "In Progress"
    status = order.get("status", "In Progress").capitalize()

    embed = discord.Embed(title="📦 Order Details", color=discord.Color.from_rgb(139, 0, 0))
    embed.add_field(name="📊 Status", value=status, inline=False)
    embed.set_author(name="Grinders System", icon_url="https://media.discordapp.net/attachments/1208792947232079955/1376855814735921212/discord_with_services_avatar.gif?ex=6836d866&is=683586e6&hm=c818d597519f4b2e55c77aeae4affbf0397e12591743e1069582f605c125f80c&=")
    embed.add_field(name="👷 Worker", value=f"<@{worker_id}>" if isinstance(worker_id, int) else worker_id, inline=False)
    embed.add_field(name="📌 Customer", value=f"<@{customer_id}>" if isinstance(customer_id, int) else customer_id, inline=False)
    embed.add_field(name="🎟️ Holder", value=f"<@{holder_id}>" if isinstance(holder_id, int) else holder_id, inline=False)
    embed.add_field(name="📕 Description", value=description, inline=False)
    embed.add_field(name="💵 Deposit", value=f"**```{deposit}M```**", inline=True)
    embed.add_field(name="💰 Order Value", value=f"**```{value}M```**", inline=True)
    embed.add_field(name="🆔 Order ID", value=order_id, inline=False)
    embed.set_image(url="https://media.discordapp.net/attachments/985890908027367474/1258798457318019153/Cynx_banner.gif?ex=67bf2b6b&is=67bdd9eb&hm=ac2c065a9b39c3526624f939f4af2b1457abb29bfb8d56a6f2ab3eafdb2bb467&=")
    embed.set_thumbnail(url="https://media.discordapp.net/attachments/1208792947232079955/1376855814735921212/discord_with_services_avatar.gif?ex=6836d866&is=683586e6&hm=c818d597519f4b2e55c77aeae4affbf0397e12591743e1069582f605c125f80c&=")
    await interaction.response.send_message(embed=embed)



# Syncing command tree for slash commands
@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands.")
    except Exception as e:
        print(f"Error syncing commands: {e}")

# Syncing command tree for slash commands
@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands.")
    except Exception as e:
        print(f"Error syncing commands: {e}")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    try:
        synced = await bot.tree.sync()  # Sync all slash commands
        print(f"Synced {len(synced)} commands.")
    except Exception as e:
        print(f"Error syncing commands: {e}")

# Flask setup for keeping the bot alive (Replit hosting)
app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    thread = Thread(target=run)
    thread.start()

import asyncio

@bot.event
async def on_message(message):
    if message.channel.id in CHANNEL_IDS and not message.author.bot:
        for emoji in CUSTOM_EMOJIS:
            try:
                await message.add_reaction(emoji)
                await asyncio.sleep(0.2)  # Add a delay of 0.2 seconds between reactions
            except discord.errors.HTTPException:
                print(f"Failed to react with emoji: {emoji}")
    await bot.process_commands(message)

# Add restart command for the bot (Owner-only)
@bot.command()
@commands.is_owner()
async def restart(ctx):
    await ctx.send("Restarting bot...")
    os.execv(__file__, ['python'] + os.sys.argv)

# Retrieve the token from the environment variable
token = os.getenv('DISCORD_BOT_TOKEN')
if not token:
    print("Error: DISCORD_BOT_TOKEN is not set in the environment variables.")
    exit(1)

# Keep the bot alive for Replit hosting
keep_alive()

@bot.command()
async def test(ctx):
    await ctx.send("Bot is responding!")

@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")
# Run the bot with the token
bot.run(token)
