import discord
from discord.ext import commands
from os import getenv
import openai
import traceback

intents = discord.Intents.default()
intents.message_content = True  # Need this intent to read message content
bot = commands.Bot(command_prefix='/', intents=intents)

# Set up OpenAI key once
openai.api_key = getenv('OPENAI_API_KEY')

messages = [
    {"role": "system", "content": "あなたは言語学者で名前はdictionaryです。"},
    {"role": "user", "content": "プロンプトが英単語や英語の熟語の場合は、【意味】項目にその英単語の意味を日本語で回答し、【例文】項目に英語の例文を３つリスト形式で回答してください。"},
    {"role": "assistant", "content": "私は AI アシスタントの言語学者dictionaryです。なにかお手伝いできることはありますか？"}
]

@bot.event
async def on_command_error(ctx, error):
    orig_error = getattr(error, "original", error)
    error_msg = 'An unexpected error occurred. Please try again.'
    await ctx.send(error_msg)
    # Logging the error
    print('Error occurred:', traceback.format_exception_only(type(orig_error), orig_error))

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    if bot.user in message.mentions:
        user_msg = message.content.replace(f'<@{bot.user.id}>', '').strip()
        print(user_msg)
        messages.append({"role": "user", "content": user_msg})

        try:
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages
            )
            bot_response = completion.choices[0]['message']['content']
            print(bot_response)
            
            if len(bot_response) > 2000:
                for part in [bot_response[i:i+2000] for i in range(0, len(bot_response), 2000)]:
                    await message.channel.send(part)
            else:
                await message.channel.send(bot_response)
            #await message.channel.send(bot_response)
        except Exception as e:
            error_details = f"Error: {str(e)}"  # Capturing error details
            print(error_details)  # Logging error
            await message.channel.send(error_details)
            # Optionally, you could log more detailed errors in a file or external logging service here

bot.run(getenv('DISCORD_BOT_TOKEN'))
