import streamlit
import openai
from restaurant import Restaurant
import datetime
import json

def generate_response(client, messages):
    response = client.chat.completions.create(
        model='gpt-4o',
        messages=messages
    )

    return response.choices[0].message.content

with streamlit.sidebar:
    api_key = str(streamlit.text_input('Azure OpenAI API Key', key='chatbot_api_key', type='password')).strip()

streamlit.title('28 Restaurant')

if 'restaurant' not in streamlit.session_state:
    restaurant = Restaurant(
        table_sizes={2: 4, 4: 4, 8: 2},
        hours=[(48, 94), (144, 190), (256, 286), (336, 382), (432, 478), (528, 574), (624, 670)],
        menu={
            # 0: {
            #     'name': 'Cheese and cold meat platter',
            #     'price': 188, 
            #     'description': 'Mixture of smoked cheese, blue cheese, Camembert cheese, Palma ham, and salami Milano. Served with crackers.',
            #     'time': 2,
            # },
            # 1: {
            #     'name': 'Barramundi goujons rice balls platter',
            #     'price': 188,
            #     'description': 'Strips of barramundi and rice balls filled with cheese and peas, deep fried in bread crumbs and sliced fresh vegetables. Served with hummus and tartare dips.',
            #     'time': 2,
            # }
            1: {
                'name': 'fries',
                'price': 20,
                'description': 'fries',
                'time': 1
            },
            2: {
                'name': 'burger',
                'price': 40,
                'description': 'burger',
                'time': 2
            },
            3: {
                'name': 'diet coke',
                'price': 10,
                'description': 'diet coke',
                'time': 0
            }
        }
    )
    streamlit.session_state['restauant'] = restaurant.to_json()
else:
    restaurant = Restaurant.from_json(streamlit.session_state['restaurant'])

t = datetime.datetime.now().strftime('%a %d %b %Y, %H:%M')
prompt = f'The current time is {t}.' + '''You are an assistant for 28 Restaurant, an Asian fusion restaurant on the ground floor of block B,
Man Yee Wan San Tsuen, 28 Yi Chun Street, Sai Kung in Hong Kong.
28 Restaurant supports dine-in, curbside pickup, and no-contact delivery. You will aid in these functions.
If the user's inquiry can directly be answered, respond normally. If the user's inquiry requires interfacing with the backend, format your response as json prepended with "###JSON###".
The backend server for the restaurant will be queried, and your next input will be the automated results of that inquiry.
Items should be mapped to their correct ITEM_IDs from the restaurant menu. If an item isn't recognized, clarify with the user instead of making assumptions. Do not allow orders with ITEM_IDs not on the menu.
Time should be formatted as following: "31 Jan 2022, 23:59". Reservations operate on 15-minute blocks. Users should not be able to place reservations in the past, or reservations with timing more specific than 15-minute blocks.
Here are the options for querying the system:
{"operation": "get_available_times", "party_size": SIZE, "time": TIME} -> returns a list of times with an available times
{"operation": "book", "party_size": SIZE, "time": TIME} -> makes a 1 hour booking for a party size, returning the table number if successful and False if unsuccessful
{"operation": "order", "items": [[ITEM_ID, COUNT], [ITEM_ID, COUNT], ...]} -> returns the cost and estimated wait time to complete the order
Example 1:
USER: I'd like to order three sets of fries and a diet coke.
YOU: ###JSON###{"operation": "order", "items": [[1, 3], [2, 1]]}
SYSTEM: {'time': 12, 'cost': 144}
YOU: Thanks for placing an order with 28 Restaurant! Your total is $144 and your order will be available in around 12 minutes. Please pick it up at the front counter.
Example 2:
USER: Can I book a table on Sunday for 4 at 7 PM?
YOU: ###JSON###{"operation": "get_available_times", "party_size": 4, "time": "16 Mar 2025, 19:00"}
SYSTEM: ["16 Mar 2025, 18:45", "16 Mar 2025, 19:00", "16 Mar 2025, 19:15", "16 Mar 2025, 19:30"]
YOU: We have availability at 6:45 PM, 7:00 PM, 7:15 PM, and 7:30 PM. Which would you like?
USER: 7 PM sounds great.
YOU: ###JSON###{"operation": "book", "party_size": 4, "16 Mar 2025, 19:00"}
SYSTEM: 5
YOU: Your table has been booked for 7 PM! You'll be seated at table 5.
Menu:
Fries: 1
Burger: 2
Diet coke: 3
'''

if 'messages' not in streamlit.session_state:
    streamlit.session_state['messages'] = [{
        'role': 'system',
        'content': prompt
    }]
    streamlit.session_state['messages'].append({'role': 'assistant', 'content': 'How can I help?'})
    print(streamlit.session_state['messages'])

for message in streamlit.session_state.messages:
    if message['role'] == 'system':
        continue
    streamlit.chat_message(message['role']).write(message['content'])

client = None
if prompt := streamlit.chat_input():
    if not api_key:
        streamlit.info('Please enter your api key.')
    else:
        streamlit.session_state.messages.append({'role': 'user', 'content': prompt})
        streamlit.chat_message('user').write(prompt)

        if client is None:
            client = openai.AzureOpenAI(
                api_key=api_key,
                api_version='2023-12-01-preview',
                azure_endpoint='https://hkust.azure-api.net/'
            )
        
        message = generate_response(client, streamlit.session_state.messages)
        if message.startswith('###JSON###'):
            result = restaurant.process_query(json.loads(message[10:].strip()))
            streamlit.session_state.messages.append({'role': 'system', 'content': str(result)})
            user_message = generate_response(client, streamlit.session_state.messages)
            streamlit.session_state.messages.append({'role': 'assistant', 'content': user_message})
            streamlit.chat_message('assistant').write(user_message)
        else:
            streamlit.session_state.messages.append({'role': 'assistant', 'content': message})
            streamlit.chat_message('assistant').write(message)