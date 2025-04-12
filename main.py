import json

import gradio as gr
from helper import get_together_api_key, load_env, get_game_state, start_game, is_safe
from together import Together

import os

REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")

# Inventory Detector system prompt
system_prompt = """You are an AI Game Assistant. \
Your job is to detect changes to a player's \
inventory based on the most recent story and game state.
If a player picks up, or gains an item add it to the inventory \
with a positive change_amount.
If a player loses an item remove it from their inventory \
with a negative change_amount.
Given a player name, inventory and story, return a list of json update
of the player's inventory in the following form.
Only take items that it's clear the player (you) lost.
Only give items that it's clear the player gained. 
Don't make any other item updates.
If no items were changed return {"itemUpdates": []}
and nothing else.

Response must be in Valid JSON
Don't add items that were already added in the inventory

Inventory Updates:
{
    "itemUpdates": [
        {"name": <ITEM NAME>, 
        "change_amount": <CHANGE AMOUNT>}...
    ]
}
"""

client = Together(api_key=get_together_api_key())

def detect_inventory_changes(game_state, output):
    inventory = game_state['inventory']
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f'Current Inventory: {str(inventory)}'},
        {"role": "user", "content": f'Recent Story: {output}'},
        {"role": "user", "content": 'Inventory Updates'}
    ]
    chat_completion = client.chat.completions.create(
        model="meta-llama/Llama-3-70b-chat-hf",
        temperature=0.0,
        messages=messages
    )
    response = chat_completion.choices[0].message.content
    result = json.loads(response)
    return result['itemUpdates']

def update_inventory(inventory, item_updates):
    update_msg = ''
    for update in item_updates:
        name = update['name']
        change_amount = update['change_amount']

        if change_amount > 0:
            if name not in inventory:
                inventory[name] = change_amount
            else:
                inventory[name] += change_amount
            update_msg += f'\nInventory: {name} +{change_amount}'
        elif name in inventory and change_amount < 0:
            inventory[name] += change_amount
            update_msg += f'\nInventory: {name} {change_amount}'

        if name in inventory and inventory[name] < 0:
            del inventory[name]

    return update_msg

def run_action(message, history, game_state):
    if message == 'start game':
        return game_state['start']

    system_prompt = """You are an AI Game master. Your job is to write what \
happens next in a player's adventure game.\
Instructions: \
You must on only write 1-3 sentences in response. \
Always write in second person present tense. \
Ex. (You look north and see...) \
Don't let the player use items they don't have in their inventory.
"""

    world_info = f"""
World: {game_state['world']}
Kingdom: {game_state['kingdom']}
Town: {game_state['town']}
Your Character:  {game_state['character']}
Inventory: {json.dumps(game_state['inventory'])}"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": world_info}
    ]

    for action in history:
        messages.append({"role": "assistant", "content": action[0]})
        messages.append({"role": "user", "content": action[1]})

    messages.append({"role": "user", "content": message})
    model_output = client.chat.completions.create(
        model="meta-llama/Llama-3-70b-chat-hf",
        messages=messages
    )
    result = model_output.choices[0].message.content
    return result

def generate_avatar(description):
    output = replicate_client.run(
        "stability-ai/stable-diffusion",
        input={"prompt": description}
    )
    return output[0]  # First image URL

game_state = get_game_state(inventory={
    "cloth pants": 1,
    "cloth shirt": 1,
    "goggles": 1,
    "leather bound journal": 1,
    "gold": 5
})

def main_loop(message, history):
    output = run_action(message, history, game_state)
    if not is_safe(output):
        return 'Invalid Output'

    item_updates = detect_inventory_changes(game_state, output)
    update_msg = update_inventory(game_state['inventory'], item_updates)
    output += update_msg
    return output

def game_with_avatar(character_description, message, history):
    avatar_url = generate_avatar(character_description)
    response = main_loop(message, history)
    return avatar_url, response

gr.Interface(
    fn=game_with_avatar,
    inputs=[
        gr.Textbox(label="Describe your character"),
        gr.Textbox(label="Your action"),
        gr.State(label="Game History")
    ],
    outputs=[
        gr.Image(label="Your Avatar"),
        gr.Textbox(label="Game Output")
    ],
    title="🧙 Fantasy RPG with Avatar Generator"
).launch(share=True)