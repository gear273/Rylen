from discord.ext import tasks, commands
import discord
import openai
import config  # Use your own config.py here
import csv

class Rylen(commands.Bot):
    def __init__(self):
        # Command_prefix - Bot command trigger, checks for existence at start of message to see if command sent
        # Intents parameters - 'Subscriptions' to specific Discord events
        super().__init__(command_prefix="!", intents=discord.Intents.all())

        # OpenAI parameters - API Key and specified engine
        openai.api_key = config.openai_api_key # Use your own key here
        self.model_engine = "gpt-3.5-turbo"
        self.temperature = 0.5
        self.persona = "chad"
        self.avail_personas = [persona for persona in config.bot_personalities]

        # CSV parameters - file name, column names (for data logging)
        self.csv_file_name = "bot_chat_logs.csv"
        self.csv_field_names = ["user_name", "user_id", "query_message", "response_message", 'prompt_tokens', 'completion_tokens', 'total_tokens']

        #Commands for changing bot parameters
        @self.command(name="rylen_help")
        async def rylen_help(ctx):
            await ctx.send("Command '!temperature x.x' changes the randomness of my responses (0.0 - 2.0, high values = more random).")
            await ctx.send(f"Command '!personality x' changes the manner in which I respond to you - Available Personas: {self.avail_personas}.")
            await ctx.send("Command '!parameters' displays the current parameters being used for the API calls.")
            return

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

        @self.command(name="personality")
        async def personality(ctx):
            message_parts = ctx.message.content.split()
            if len(message_parts) >= 2 and message_parts[1] in self.avail_personas:
                self.persona = message_parts[1]
                await ctx.send(f"Persona has been changed to {self.persona}.")
            else:
                ctx.send(f"Invalid persona given. Please enter one of the available personas: {self.avail_personas}.")

        @self.command(name="parameters")
        async def parameters(ctx):
            await ctx.send(f"Model Engine: {self.model_engine}\nModel Persona: {self.persona}\nModel Temperature: {self.temperature}")

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
    
    # On message listener
    @commands.Cog.listener()
    async def on_message(self, message):
        # Channel IDs for where the bot is allowed
        allowed_channels = [1105651398110085251, 1070898555750977597]
        # Verify that message is not from bot or and message is in allowed channel
        if message.author == self.user or message.channel.id not in allowed_channels:
            return

        # Command checks
        if message.content.startswith('!temperature') or message.content.startswith('!personality') or message.content.startswith('!parameters') or message.content.startswith('!rylen_help'):
            await self.process_commands(message)
            return

        # Message checks
        if message.content == 'Bad bot':
            async with message.channel.typing():
                custom_query = {"role" : "user", "content" : message.clean_content}
                prompt_query = config.bot_personalities["chad"]
                response = openai.ChatCompletion.create(model = self.model_engine, messages = prompt_query, temperature = 0.5)
            await message.channel.send(response.choices[0]["message"].content[:2000], reference=message) # Discord limits messages to 2000 character size
            await self.data_logging(message, response) # Log the correspondence with the bot
        # Only @Rylen will trigger the bot (bot and role mentions, if the same) - @everyone is ignored by bot
        if bot.user.mentioned_in(message) or any(role.name == "Rylen" for role in message.role_mentions) and message.mention_everyone is False:
            async with message.channel.typing():
                custom_query = {"role" : "user", "content" : message.clean_content}
                prompt_query = config.bot_personalities[self.persona]
                response = openai.ChatCompletion.create(model = self.model_engine, messages = prompt_query, temperature = self.temperature)
            # Split the response message into chunks of 2000 characters or less since this is the single message limit for Discord
            response_message = response.choices[0]["message"].content
            response_chunks = [response_message[i:i+2000] for i in range(0, len(response_message), 2000)]
            for chunk in response_chunks:
                await message.channel.send(chunk)
            await self.data_logging(message, response) # Log the correspondence with the bot


if __name__ == "__main__":
    bot = Rylen()
    bot.run(config.discord_api_key) # Use your own key here
