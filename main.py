import discord
from discord import app_commands

# Your guild ID and bot token
GUILD_ID = 123456789  # Replace with your guild's ID
TOKEN = "your_bot_token"  # Replace with your bot token

intents = discord.Intents.default()
intents.reactions = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

filters = {}
bot_active = True


@tree.command(name="add", description="Add a filter for a role in a channel", guild=discord.Object(id=GUILD_ID))
async def add_filter(interaction: discord.Interaction, role: discord.Role, channel: discord.TextChannel):
    if channel.id not in filters:
        filters[channel.id] = []
    if role.id not in filters[channel.id]:
        filters[channel.id].append(role.id)
        await interaction.response.send_message(f"Filter added for role {role.name} in {channel.name}.")
    else:
        await interaction.response.send_message(f"Filter already exists for role {role.name} in {channel.name}.")


@tree.command(name="remove", description="Remove a filter for a role in a channel", guild=discord.Object(id=GUILD_ID))
async def remove_filter(interaction: discord.Interaction, role: discord.Role, channel: discord.TextChannel):
    if channel.id in filters and role.id in filters[channel.id]:
        filters[channel.id].remove(role.id)
        await interaction.response.send_message(f"Filter removed for role {role.name} in {channel.name}.")
    else:
        await interaction.response.send_message(f"No filter found for role {role.name} in {channel.name}.")


@tree.command(name="list", description="List all filters", guild=discord.Object(id=GUILD_ID))
async def list_filters(interaction: discord.Interaction):
    if filters:
        message = "Current filters:\n"
        for channel_id, roles in filters.items():
            channel = client.get_channel(channel_id)
            role_names = [interaction.guild.get_role(role_id).name for role_id in roles]
            message += f"#{channel.name}: {', '.join(role_names)}\n"
        await interaction.response.send_message(message)
    else:
        await interaction.response.send_message("No filters set.")


@tree.command(name="on", description="Turn on the bot", guild=discord.Object(id=GUILD_ID))
async def turn_on(interaction: discord.Interaction):
    global bot_active
    bot_active = True
    await interaction.response.send_message("Bot is now active.")


@tree.command(name="off", description="Turn off the bot", guild=discord.Object(id=GUILD_ID))
async def turn_off(interaction: discord.Interaction):
    global bot_active
    bot_active = False
    await interaction.response.send_message("Bot is now inactive.")


@tree.command(name="remove_reactions",
              description="Remove all reactions from a message made by users with a specified role",
              guild=discord.Object(id=GUILD_ID))
async def remove_reactions(interaction: discord.Interaction, message_id: str, role: discord.Role):
    try:
        message = await interaction.channel.fetch_message(int(message_id))
    except discord.NotFound:
        await interaction.response.send_message("Message not found.")
        return
    except discord.HTTPException as e:
        await interaction.response.send_message(f"An error occurred: {e}")
        return

    # Iterate over all reactions on the message
    for reaction in message.reactions:
        async for user in reaction.users():
            # Check if the user has the specified role
            if role in user.roles:
                await reaction.remove(user)

    await interaction.response.send_message(f"Reactions removed for users with the {role.name} role.")


@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=GUILD_ID))
    print("Bot is ready!")


@client.event
async def on_reaction_add(reaction, user):
    if not bot_active:
        return

    channel_id = reaction.message.channel.id
    if channel_id in filters and any(role.id in filters[channel_id] for role in user.roles):
        await reaction.remove(user)


client.run(TOKEN)
