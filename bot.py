import asyncio
import discord
from discord.ext import commands
import paho.mqtt.client as mqtt
import json

async def publish_message(topic, message):
    client = mqtt.Client()
    await asyncio.get_event_loop().run_in_executor(None, client.connect, "localhost", 1883)
    await asyncio.get_event_loop().run_in_executor(None, client.publish, topic, message)
    await asyncio.get_event_loop().run_in_executor(None, client.disconnect)

intents = discord.Intents.default()
intents.message_content = True
bot = discord.Bot(debug_guilds=["991499158156496896"], intents=intents)

async def is_majestic(ctx):
    return ctx.author.id == 159459744170508288

with open("relay_bots.json", "r") as file:
    relay_bots = json.load(file)

with open("trigger_words.json", "r") as file:
    trigger_words = json.load(file)

with open("channel_topics.json", "r") as file:
    channel_topics = json.load(file)

channel_topics = {int(k): str(v) for k, v in channel_topics.items()}
relay_bots = {int(k): str(v) for k, v in relay_bots.items()}

print(relay_bots)
print(channel_topics)
print(trigger_words)


@commands.check(is_majestic)
@bot.command(description="This adds a trigger word.")
async def add_trigger(ctx, trigger_word: discord.Option(str)):
    if trigger_word in trigger_words:
        await ctx.respond(f"{trigger_word} is already a trigger word.", ephemeral=True)
    else:
        trigger_words.append(trigger_word)
        with open("trigger_words.json", "w") as file:
            json.dump(trigger_words, file)
            print(trigger_words)
        await ctx.respond(f"Added {trigger_word} to the list of triggers.", ephemeral=True)
@add_trigger.error
async def add_trigger_error(ctx, error):
    await ctx.send(error)

@commands.check(is_majestic)
@bot.command(description="This deletes a trigger word.")
async def delete_trigger(ctx, trigger_word: discord.Option(str)):
    if trigger_word in trigger_words:
        trigger_words.remove(trigger_word)
        with open("trigger_words.json", "w") as file:
            json.dump(trigger_words, file)
            print(trigger_words)
        await ctx.respond(f"Deleted {trigger_word} from the list of triggers.", ephemeral=True)
    else:
        await ctx.respond(f"{trigger_word} is not a trigger word.", ephemeral=True)
@delete_trigger.error
async def delete_trigger_error(ctx, error):
    await ctx.send(error)
    
@commands.check(is_majestic)
@bot.command(description="This adds a channel id and topic.")
async def add_topic(ctx, channel_id: discord.Option(str), topic_name: discord.Option(str)):
    channel_id = int(channel_id)
    channel_topics[channel_id] = topic_name
    with open("channel_topics.json", "w") as file:
        json.dump(channel_topics, file)
    await ctx.respond(f"Added topic {topic_name} for channel with ID {channel_id}.", ephemeral=True)
    print(channel_topics)
@add_topic.error
async def add_topic_error(ctx, error):
    await ctx.send(error)

@commands.check(is_majestic)
@bot.command(description="This deletes a channel id and topic.")
async def delete_topic(ctx, channel_id: discord.Option(str)):
    channel_id = int(channel_id)
    if channel_id in channel_topics:
        del channel_topics[channel_id]
        with open("channel_topics.json", "w") as file:
            json.dump(channel_topics, file)
        await ctx.respond(f"Deleted topic for channel with ID {channel_id}.", ephemeral=True)
        print(channel_topics)
    else:
        await ctx.respond(f"No topic found for channel with ID {channel_id}.")
@delete_topic.error
async def delete_topic_error(ctx, error):
    await ctx.send(error)

@commands.check(is_majestic)
@bot.command(description="This lists the topics for all channels.")
async def list_topics(ctx):
    with open("channel_topics.json", "r") as file:
        channel_topics = json.load(file)
    embed = discord.Embed(title="Channel Topics", description="List of topics for all channels")
    for channel_id, topic_name in channel_topics.items():
        embed.add_field(name=topic_name, value=channel_id, inline=False)
    await ctx.respond(embed=embed, ephemeral=True)

@commands.check(is_majestic)
@bot.command(description="This lists all the trigger words.")
async def list_triggers(ctx):
    with open("trigger_words.json", "r") as file:
        trigger_words = json.load(file)
        triggers = ", ".join(trigger_words)
        embed = discord.Embed(title="Trigger Words", description=triggers)
        await ctx.respond(embed=embed, ephemeral=True)
        
@commands.check(is_majestic)
@bot.command(description="This adds a relay bot id and name.")
async def add_relay_bot(ctx, relay_bot_id: discord.Option(str), relay_bot_name: discord.Option(str)):
    relay_bot_id = int(relay_bot_id)
    relay_bots[relay_bot_id] = relay_bot_name
    with open("relay_bots.json", "w") as file:
        json.dump(relay_bots, file)
    await ctx.respond(f"Added relay bot {relay_bot_name} with ID {relay_bot_id}.", ephemeral=True)
    print(relay_bots)
@add_relay_bot.error
async def add_relay_bot_error(ctx, error):
    await ctx.send(error)

@commands.check(is_majestic)
@bot.command(description="This deletes a relay bot.")
async def delete_relay_bot(ctx, relay_bot_id: discord.Option(str)):
    relay_bot_id = int(relay_bot_id)
    if relay_bot_id in relay_bots:
        del relay_bots[relay_bot_id]
        with open("relay_bots.json", "w") as file:
            json.dump(relay_bots, file)
        await ctx.respond(f"Deleted relay bot with ID {relay_bot_id}.", ephemeral=True)
        print(relay_bots)
    else:
        await ctx.respond(f"No relay bot found with ID {relay_bot_id}.")
@delete_relay_bot.error
async def delete_relay_bot_error(ctx, error):
    await ctx.send(error)

@bot.command(description="This lists the relay bots.")
async def list_relay_bots(ctx):
    with open("relay_bots.json", "r") as file:
        relay_bots = json.load(file)
    embed = discord.Embed(title="Relay Bots", description="List of relay bots.")
    for relay_bot_id, relay_bot_name in relay_bots.items():
        embed.add_field(name=relay_bot_name, value=relay_bot_id, inline=False)
    await ctx.respond(embed=embed, ephemeral=True)


@bot.event
async def on_ready():
    activity = discord.Activity(name="for pings", type=discord.ActivityType.watching)
    await bot.change_presence(activity=activity)


@bot.listen('on_message')
async def message(message):
    thisissoscuffed = str([embed.to_dict() for embed in message.embeds])
    if message.author.id in relay_bots:
        if message.channel.id in channel_topics:
            topic = channel_topics[message.channel.id]
            for word in trigger_words:
                if word in thisissoscuffed:
                    await publish_message(topic, word)
                    print(topic, word)
                    break

async def run_bot():
    await bot.start("MTA1MTg1OTUxNTEzMTMxMDEzMQ.G0wajn.jauIwfzecW_ir_U1l8313pNIAC9e-O5GGDLr38")

asyncio.run(run_bot())
