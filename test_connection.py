from together import Together
from helper import get_together_api_key, load_env

load_env()
client = Together(api_key=get_together_api_key())

print("Client initialized successfully ✅")
