import os
from dotenv import load_dotenv  # Add this import
import discord
from discord.ext import commands

load_dotenv()

intents = discord.Intents.default()
intents.reactions = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_ready():
    print(f'Thread Pinster is alive!')


@bot.event
async def on_thread_create(thread):
    """Send welcome message when a thread is created"""
    try:
        # Wait a moment to ensure thread is fully created
        await asyncio.sleep(1)

        # Check if bot has permission to send messages in the thread
        if not thread.permissions_for(thread.guild.me).send_messages:
            return

        # Send welcome message with instructions
        embed = discord.Embed(
            title="📌 Thread Pinster Bot",
            description="I can help you pin and unpin messages in this thread!",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="How to pin a message:",
            value="React with 📌 to any message",
            inline=False
        )
        embed.add_field(
            name="How to unpin a message:",
            value="React with ❌ to any pinned message",
            inline=False
        )
        embed.add_field(
            name="Requirements:",
            value="Only thread owners can manage pins\nReactions are automatically removed",
            inline=False
        )
        embed.set_footer(text="React with ❌ to dismiss this message")

        welcome_msg = await thread.send(embed=embed)
        # Add dismiss reaction
        await welcome_msg.add_reaction('❌')

    except Exception as e:
        print(f"Error sending welcome message: {e}")


@bot.event
async def on_reaction_add(reaction, user):
    # Ignore bot reactions
    if user.bot:
        return

    # Get the channel and message objects
    channel = reaction.message.channel
    message = reaction.message

    # Handle welcome message dismissal
    if (isinstance(channel, discord.Thread) and
            str(reaction.emoji) == '❌' and
            message.author == bot.user and
            message.embeds and
            "Thread Pinster Bot" in message.embeds[0].title):
        try:
            await message.delete()
            return
        except:
            pass

    # Check if the channel is a thread
    if not isinstance(channel, discord.Thread):
        return

    # Check if the user is the thread owner
    if user.id != channel.owner_id:
        # Send temporary message in chat
        notice = await channel.send(f"{user.mention}, only the thread owner can manage pins here.")
        await notice.delete(delay=5)
        # Remove the user's reaction
        try:
            await reaction.remove(user)
        except:
            pass
        return

    try:
        if str(reaction.emoji) == '📌':
            # PIN action
            if message.pinned:
                notice = await channel.send("This message is already pinned.")
                await notice.delete(delay=5)
                # Remove the user's reaction
                try:
                    await reaction.remove(user)
                except:
                    pass
                return

            await message.pin()
            print(f"Pinned message in thread {channel.name} by {user}")
            confirmation = await channel.send(f"📌 Message pinned by {user.mention}!")
            await confirmation.delete(delay=5)
            # Remove the user's reaction after successful pin
            try:
                await reaction.remove(user)
            except:
                pass

        elif str(reaction.emoji) == '❌':
            # UNPIN action
            if not message.pinned:
                notice = await channel.send("This message is not pinned.")
                await notice.delete(delay=5)
                # Remove the user's reaction
                try:
                    await reaction.remove(user)
                except:
                    pass
                return

            await message.unpin()
            print(f"Unpinned message in thread {channel.name} by {user}")
            confirmation = await channel.send(f"❌ Message unpinned by {user.mention}!")
            await confirmation.delete(delay=5)
            # Remove the user's reaction after successful unpin
            try:
                await reaction.remove(user)
            except:
                pass

    except discord.Forbidden:
        error_msg = await channel.send("I don't have permission to manage messages in this thread.")
        await error_msg.delete(delay=10)
        # Try to remove reaction even on error
        try:
            await reaction.remove(user)
        except:
            pass
    except discord.HTTPException as e:
        error_msg = await channel.send(f"Failed to manage message: {e}")
        await error_msg.delete(delay=10)
        # Try to remove reaction even on error
        try:
            await reaction.remove(user)
        except:
            pass


# Help command
@bot.command()
async def pinhelp(ctx):
    """Show how to use the pin bot"""
    embed = discord.Embed(
        title="📌 Thread Pinster Bot Help",
        description="Use reactions to manage pinned messages in your threads",
        color=discord.Color.blue()
    )
    embed.add_field(
        name="How to pin a message:",
        value="React with 📌 to any message in your thread",
        inline=False
    )
    embed.add_field(
        name="How to unpin a message:",
        value="React with ❌ to any pinned message in your thread",
        inline=False
    )
    embed.add_field(
        name="Auto-welcome:",
        value="I automatically introduce myself when threads are created\nReact with ❌ to dismiss my welcome message",
        inline=False
    )
    embed.set_footer(text="Reactions are automatically removed after processing")
    await ctx.send(embed=embed)


# Error handling
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    print(f"Error: {e}")


if __name__ == "__main__":
    import asyncio
    token = os.getenv('DISCORD-TOKEN')
    if not token:
        print("Error: DISCORD_BOT_TOKEN not found in environment variables")
        exit(1)
    bot.run(token)