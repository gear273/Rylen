# .gitignore should include reference to config.py
# This is an example of what the config.py file could look like

openai_api_key = ""

discord_api_key = ""

# Example format of how bot personalities can be formed based on a little bit of prompt engineering
# Full information can be found here https://platform.openai.com/docs/guides/chat/introduction
bot_personalities = {
    "Assistant" : [{"role" : "system", "content" : "You are an assistant named Rylen that does everything I ask."},
                   {"role" : "user", "content" : "What is the purpose of life?"},
                   {"role" : "assistant", "content" : "The purpose of life is a question that has been asked by humans for centuries, \
                   and the answer can vary depending on one's beliefs and values. Some believe that the purpose of life is to seek \
                   happiness, others believe it is to fulfill a certain destiny or mission, and still, others believe that it is to \
                   seek spiritual enlightenment or connect with a higher power."}]
    }

'''
    Example response format:

{
 'id': 'chatcmpl-6p9XYPYSTTRi0xEviKjjilqrWU2Ve',
 'object': 'chat.completion',
 'created': 1677649420,
 'model': 'gpt-3.5-turbo',
 'usage': {'prompt_tokens': 56, 'completion_tokens': 31, 'total_tokens': 87},
 'choices': [
   {
    'message': {
      'role': 'assistant',
      'content': 'The 2020 World Series was played in Arlington, Texas at the Globe Life Field, which was the new home stadium for the Texas Rangers.'},
    'finish_reason': 'stop',
    'index': 0
   }
  ]
}

'''






