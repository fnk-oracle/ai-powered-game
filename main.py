import json
import gradio as gr
from helper import get_together_api_key, load_env, get_game_state, start_game, is_safe
from together import Together

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

    for user_input, model_output in history:  # Loop through history properly
        messages.append({"role": "user", "content": user_input})
        messages.append({"role": "assistant", "content": model_output})

    messages.append({"role": "user", "content": message})
    model_output = client.chat.completions.create(
        model="meta-llama/Llama-3-70b-chat-hf",
        messages=messages
    )
    result = model_output.choices[0].message.content
    return result

# Global game state (preserved across interactions)
game_state = get_game_state(inventory={
    "cloth pants": 1,
    "cloth shirt": 1,
    "goggles": 1,
    "leather bound journal": 1,
    "gold": 5
})
history = []

# Gradio-compatible format for chat history
def gradio_main(user_input, chat_history):
    output = run_action(user_input, history, game_state)
    if not is_safe(output):
        chat_history.append({"role": "user", "content": user_input})
        chat_history.append({"role": "assistant", "content": "Invalid output. Please try a different action."})
        return chat_history

    item_updates = detect_inventory_changes(game_state, output)
    update_msg = update_inventory(game_state['inventory'], item_updates)
    full_output = output + update_msg

    # Append to history with correct order: user_input first, then model output
    history.append((user_input, output))  # Correct order: user_input, model_output

    chat_history.append({"role": "user", "content": user_input})
    chat_history.append({"role": "assistant", "content": full_output})
    return chat_history

# Launch the chat
gr.ChatInterface(gradio_main, title="🧙 Fantasy AI Game", type="messages").launch()
