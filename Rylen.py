from discord.ext import tasks, commands
import discord
from datetime import datetime
import openai
import json
import csv
import forecast
import config

# TODO: Add !forecast and !hourly to self.rylen_commands so that only one check is performed in the on_message

class Rylen(commands.Bot):
    def __init__(self):
        # Command_prefix - Bot command trigger, checks for existence at start of message to see if command sent
        # Intents parameters - 'Subscriptions' to specific Discord events
        super().__init__(command_prefix="!", intents=discord.Intents.all())

        # OpenAI parameters - API Key and specified engine
        openai.api_key = config.openai_api_key # Use your own key here
        self.model_engine = "gpt-3.5-turbo"
        self.temperature = 0.5
        self.persona = str(next(iter(config.bot_personalities)))
        self.avail_personas = [persona for persona in config.bot_personalities]
        self.rylen_commands = ("!parameters", "!temperature", "!personality", "!rylen_help", "!role_message", "!information")
        self.rylen_triggers = ("Bad bot", "bad bot")

        # Guild Roles
        self.roles = {
            "💻" : 1107429161611575466, # Computer Science
            "⚡" : 1107439941606199327, # Electrical Engineering
            "♻️" : 1107440608315986050, # Environmental Engineering
            "🏥" : 1107451574315388939, # Civil Engineering
            "⚙️" : 1107451993326358548, # Mechanical Engineering
            "🕵️" : 1107452341910781952, # Cybersecurity
            }
        self.roles_channel_id = 1107453198798696589 # Channel ID for location specific roles message
        self.roles_message_id = 1107460272899235920 # Message ID for specific roles message
        self.current_reactions = {} # For keeping track of reactions on roles message
        # CSV parameters - file name, column names (for data logging)
        self.csv_file_name = "bot_chat_logs.csv"
        self.csv_field_names = ["user_name", "user_id", "query_message", "response_message", 'prompt_tokens', 'completion_tokens', 'total_tokens']

        # Commands for changing bot parameters
        @self.command(name="rylen_help") # Display current commands with '!rylen_help'
        async def rylen_help(ctx):
            embed = discord.Embed(title="Available Commands", colour=0x4f2d7f)
            embed.set_footer(text="Rylen: Tarleton Engineering Discord Bot")
            embed.add_field(name="!information", value="Information about Rylen, libraries, and used APIs", inline=False)
            embed.add_field(name="!parameters", value="Shows current parameters used for OpenAI API calls", inline=False)
            embed.add_field(name="!temperature [temperature]", value="Sets the temperature to the float value passed (0.0 - 2.0)", inline=False)
            embed.add_field(name="!personality [persona]", value="Sets the persona to the string value passed", inline=False)
            embed.add_field(name="Available Peronas: ", value=self.avail_personas, inline=False)
            embed.add_field(name="!forecast [city, state]", value="Displays forecast of desired location - ex. Dallas, TX", inline=False)
            embed.add_field(name="!hourly [city, state]", value="Displays hourly forecast of desired location - ex. Stephenville, TX", inline=False)
            embed.add_field(name="!alerts [city, state]", value="Displays active weather alerts of desired location - ex. Fort Worth, TX", inline=False)
            await ctx.send(embed=embed)

        # Change temperature of engine with '!temperature'
        @self.command(name="temperature")
        async def temperature(ctx):
            message_parts = ctx.message.content.split()
            try:
                temp = float(message_parts[1])
                if len(message_parts) >= 2 and temp > 0.0 and temp < 2.0:
                    self.temperature = temp
                    await ctx.send(f"Temperature has been set to {self.temperature}.")
                else:
                    await ctx.send("Invalid temperature value. Please enter a number between 0.0 and 2.0 after the command, like this: '!temperature 0.7'.")
            except ValueError:
                await ctx.send("Invalid temperature value. Please enter a number after the command, like this: '!temperature 0.7'.")

        # Change personality of engine with '!personality'
        @self.command(name="personality")
        async def personality(ctx):
            message_parts = ctx.message.content.split()
            if len(message_parts) >= 2 and message_parts[1] in self.avail_personas:
                self.persona = message_parts[1]
                embed = discord.Embed(title="Personality Updated", colour=0x4f2d7f)
                embed.add_field(name="Personality changed to", value=self.persona)
            else:
                embed = discord.Embed(title="Invalid persona give", colour=0x4f2d7f)
                embed.add_field(name="Please enter on of the available personas listed below", value=self.avail_personas, inline=False)
            embed.set_footer(text="Rylen: Tarleton Engineering Discord Bot")
            await ctx.send(embed=embed)

        # Display all current parameters with '!parameters'
        @self.command(name="parameters")
        async def parameters(ctx):
            embed = discord.Embed(title="Current OpenAI parameters for API calls", colour=0x4f2d7f)
            embed.set_footer(text="Rylen: Tarleton Engineering Discord Bot")
            embed.add_field(name="Model Engine: ", value=self.model_engine, inline=False)
            embed.add_field(name="Model Persona: ", value=self.persona, inline=False)
            embed.add_field(name="Temperature", value=self.temperature, inline=False)
            await ctx.send(embed=embed)
            #await ctx.send(f"Model Engine: {self.model_engine}\nModel Persona: {self.persona}\nModel Temperature: {self.temperature}")

        @self.command(name="role_message")
        async def role_message(ctx):
            embed = discord.Embed(title="Choose Your Major", colour=0x1e1f22)
            embed.set_footer(text="If you do not see your major listed above, please contact an admin so that it can be added to the list.")
            embed.add_field(name="Electrical Engineering", value="Zap - ⚡", inline=False)
            embed.add_field(name="Computer Science", value="Computer - 💻", inline=False)
            embed.add_field(name="Cybersecurity", value="Detective - 🕵️", inline=False)
            embed.add_field(name="Environmental Engineering", value="Recycle - ♻️", inline=False)
            embed.add_field(name="Civil Engineering", value="Hospital - 🏥", inline=False)
            embed.add_field(name="Mechanical Engineering", value="Gear - ⚙️", inline=False)
            channel = self.get_channel(1107453198798696589)
            message = await channel.send(embed=embed)
            for emoji in self.roles.keys():
                await message.add_reaction(emoji)

        @self.command(name="information")
        async def information(ctx):
           embed = discord.Embed(title="Information", description="Information about Rylen, libraries, and used APIs", colour=0x006400)
           embed.set_footer(text="Tarleton Mayfield College of Engineering")
           embed.add_field(name="Rylen", value="Rylen is an open source Discord bot created for fun by students from the Tarleton Mayfield College of Engineering. You are free to use this bot on your own server, all we ask is that you cite where the bot originated.", inline=False)
           embed.add_field(name="Rylen Bot GitHub", value="https://github.com/Pixer9/Rylen", inline=False)
           embed.add_field(name="OpenAI API", value="https://openai.com/blog/openai-api - Paid Subscription Key Required", inline=False)
           embed.add_field(name="National Weather Service API", value="https://api.weather.gov/ - Public Domain", inline=False)
           embed.add_field(name="Discord.py", value="https://github.com/Rapptz/discord.py", inline=False)
           embed.add_field(name="Geopy.py", value="https://pypi.org/project/geopy/", inline=False)
           await ctx.send(embed=embed)
       # End commands 
    
    # Method for logging interaction data (most importantly keeps track of token usage)
    async def data_logging(self, message, response):
        try:
            with open(self.csv_file_name, mode='a', newline='') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=self.csv_field_names)
                writer.writerow({
                    "user_name" : message.author.name,
                    "user_id" : message.author.id,
                    "query_message" : message.content,
                    "response_message" : response.choices[0]["message"].content[:2000],
                    "prompt_tokens" : response.usage.prompt_tokens,
                    "completion_tokens" : response.usage.completion_tokens,
                    "total_tokens" : response.usage.total_tokens
                    })
        except Exception as e:
            print("Error occurred while writing to CSV: ", e)
    
    # On ready event
    @commands.Cog.listener()
    async def on_ready(self):
        print("Logged in as {0.user}".format(self))
        await self.change_presence(activity=discord.Activity(name="Your Mom's OnlyFans", type=discord.ActivityType.watching))
    
    # On message listener
    @commands.Cog.listener()
    async def on_message(self, message):
        # Channel IDs for where the bot is allowed - (restricted to bot channel for now)
        allowed_channels = [1107119090541285470] # 1105651398110085251 - rylens-house channel id
        # Verify that message is not from bot or is not within disallowed channels
        if message.author == self.user or message.channel.id not in allowed_channels:
            return

        # Command checks
        if message.content.startswith(self.rylen_commands):
            await self.process_commands(message)
            return

        # Message checks
        if message.content.startswith("!forecast"): # Fetching 2-Day forecast using Weather.gov API
            client_location = message.content[len("!forecast") + 1:]
            channel = self.get_channel(message.channel.id)
            wait = await channel.send("Pulling data......")
            daily_forecast = forecast.getForecast(client_location)
            await wait.delete()
            if daily_forecast == None:
                await message.channel.send("Please input a valid location")
            else:
                for data in daily_forecast[:3]:
                    await self.forecastEmbed(channel, client_location, data)

        if message.content.startswith("!hourly"): # Fetching hourly forecast using Weather.gov API
            client_location = message.content[len("!hourly") + 1:]
            channel = self.get_channel(message.channel.id)
            wait = await channel.send("Pulling data......")
            hourly_forecast = forecast.getForecastHourly(client_location)
            await wait.delete()
            if hourly_forecast == None:
                await channel.send("Please input a valid location")
            else:
                await self.forecastHourlyEmbed(channel, client_location, hourly_forecast)

        if message.content.startswith("!alerts"): # Fetching active weather alerts using Weather.gov API
            client_location = message.content[len("!alerts") + 1:]
            channel = self.get_channel(message.channel.id)
            wait = await channel.send("Pulling data......")
            alerts = forecast.getCountyAlerts(client_location)
            await wait.delete()
            if alerts != None:
                await self.weatherAlert(channel, alerts, client_location)
            else:
                await channel.send("Please enter a valid area.")

        if message.content in self.rylen_triggers: # Special phrases to trigger Rylen - ex. 'Bad bot'
            async with message.channel.typing():
                custom_query = {"role" : "user", "content" : message.clean_content}
                prompt_query = config.bot_personalities["chad"]
                try:
                    response = openai.ChatCompletion.create(model = self.model_engine, messages = prompt_query, temperature = 0.5)
                    await message.channel.send(response.choices[0].message.content[:2000], reference=message) # Discord limits messages to 2000 character size
                except Exception as e:
                    print(f"Error: {e}")
            await self.data_logging(message, response) # Log the correspondence with the bot

        # Only @Rylen will trigger the bot (bot and role mentions, if the same) - @everyone is ignored by bot
        if bot.user.mentioned_in(message) or any(role.name == "Rylen" for role in message.role_mentions) and message.mention_everyone is False:
            async with message.channel.typing():
                custom_query = {"role" : "user", "content" : message.clean_content}
                prompt_query = config.bot_personalities[self.persona]
                complete_query = prompt_query.append(custom_query)
                try:
                    response = openai.ChatCompletion.create(model = self.model_engine, messages = prompt_query, temperature = self.temperature)
                    response_message = response.choices[0].message.content
                    # Split the response message into chunks of 2000 characters or less since this is the single message limit for Discord
                    response_chunks = [response_message[i:i+2000] for i in range(0, len(response_message), 2000)]
                    for chunk in response_chunks:
                        await message.channel.send(chunk)
                except Exception as e:
                    print(f"Error: {e}")
            await self.data_logging(message, response) # Log the correspondence with the bot

    # Display 2-Day forecast upon request
    @commands.Cog.listener()
    async def forecastEmbed(self, channel, location, data):
        embed = discord.Embed(title = data['name'], description = "Forecast for " + location, colour = 0x4285F4)
        embed.set_thumbnail(url=data['icon'])
        embed.set_footer(text="Information retrieved from weather.gov using publicly available API")
        embed.add_field(name="Weather", value=data['shortForecast'], inline=False)
        embed.add_field(name="Precipitation", value=str(data['probabilityOfPrecipitation']['value'])+"%", inline=False)
        embed.add_field(name="Temperature", value=str(data['temperature']) + " °F", inline=False)
        embed.add_field(name="Wind", value=data['windSpeed'] + " " + data['windDirection'], inline=False)
        await channel.send(embed=embed)
    
    # Display hourly forecast upon request
    @commands.Cog.listener()
    async def forecastHourlyEmbed(self, channel, location, forecast):
        embed = discord.Embed(title="Hourly Forecast for " + location, color = 0x4285F4)
        embed.set_footer(text="Information retreived from weather.gov using publicly available API")
        for data in forecast[:4]:
            time_str = data['startTime'][len("0000-00-00T") : len("0000-00-00T00:00")]
            time = datetime.strptime(time_str, '%H:%M').strftime('%I:%M %p')
            weather = data['shortForecast']
            temperature = str(data['temperature']) + " °F"
            wind = data['windSpeed'] + " " + data['windDirection']
            precip = data['probabilityOfPrecipitation']['value']
            embed.add_field(name=time, value=f"Weather: {weather}\nPrecipitation: {precip}%\nTemperature: {temperature}\nWind: {wind}", inline=False)
        await channel.send(embed=embed)

    # Display active weather alerts for the area
    @commands.Cog.listener()
    async def weatherAlert(self, channel, alerts, area):
        embed = discord.Embed(title=f"Active weather alerts for {area}", colour=0xFF7F50)
        embed.set_footer(text="Information retrieved from weather.gov using publicly available API")
        if not alerts:
            embed.add_field(name="No Alerts", value=f"There are currently no active weather alerts in {area}. Visit weather.gov for official information")
        else:
            for alert in alerts[:3]:
                if alert['properties']['event'].__contains__("Warning") or alert['properties']['event'].__contains__("Tornado"):
                    embed.add_field(name=alert['properties']['headline'], value=alert['properties']['description'][:1024], inline=False)
        await channel.send(embed=embed)

    # Method for "Declare Your Major" bot functionality of adding unique roles
    # User role is granted based on emoji reaction by user - only one role/reaction per user, all others removed upon new selection
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        print(payload)
        guild = self.get_guild(payload.guild_id)
        member = discord.utils.get(guild.members, id=payload.user_id)
        if member == self.user: # Ignore if bot added reaction - useful if you modify existing message to add new reactions/roles
            return
        # Check that specific message is in specific channel - only one is necessary, two were used for redundancy in case two bot messages exist in channel
        if payload.channel_id == self.roles_channel_id and payload.message_id == self.roles_message_id:
            message = await guild.get_channel(payload.channel_id).fetch_message(payload.message_id)
            roles = [discord.utils.get(guild.roles, id=self.roles[str(r)]) for r in message.reactions if str(r) in self.roles]
            user_roles = [r for r in member.roles if r in roles]
            if str(payload.emoji) in self.roles.keys():
                role_id = self.roles[str(payload.emoji)]
                role = discord.utils.get(payload.member.guild.roles, id=role_id)
                if role is not None:
                    await member.remove_roles(*user_roles)
                    await member.add_roles(role)
                    print(f"Added {role} to {member}")
            else:
                role = discord.utils.get(guild.roles, name=payload.emoji)
                if role is not None and role not in member.roles:
                    for reaction in message.reactions:
                        await member.remove_roles(*user_roles)
                        await member.add_roles(role)
                    print(f"Added {role} to {member}")
        if payload.user_id in self.current_reactions.keys():
            await message.remove_reaction(self.current_reactions[payload.user_id], member)
        self.current_reactions.update({payload.user_id : str(payload.emoji)})

    # Method for "Declare Your Major" bot functionality of removing unique roles
    # User role is removed based on removal of emoji reaction by user - only one role/reaction per user, all others removed upon new selection
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        guild = self.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        if payload.channel_id == self.roles_channel_id and payload.message_id == self.roles_message_id:
            if str(payload.emoji) in self.roles:
                role = guild.get_role(self.roles[str(payload.emoji)])
            else:
                role = discord.utils.get(guild.roles, name=payload.emoji)
            if role is not None:
                await member.remove_roles(role)
                print(f"Removed {role} from {member}")
        if payload.user_id in self.current_reactions.keys():
            del self.current_reactions[payload.user_id]

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = discord.utils.get(member.guild_text_channels, name="general")
        await channel.send(f"{member} has arrived!")

if __name__ == "__main__":
    bot = Rylen()
    bot.run(config.discord_api_key) # Use your own key here
