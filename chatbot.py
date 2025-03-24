import streamlit
from streamlit_extras.stylable_container import stylable_container
import openai
from restaurant import Restaurant
import datetime
import json
import pandas as pd
import speech_recognition as sr
import pyttsx3
from streamlit_javascript import st_javascript

#additional installs
#pip install streamlit streamlit_extras
#pip install streamlit-javascript


streamlit.markdown("<h1 style='text-align: center; color: black; margin: 0px; font-family: \"Brush Script MT\"'>28</h1>", unsafe_allow_html=True)
streamlit.markdown("<h3 style='text-align: center; color: black; margin: 0px; font-family: \"Verdana\"'>RESTAURANT</h3>", unsafe_allow_html=True)

# STT
def speech_to_text():
    recognizer = sr.Recognizer()                                    # Initialize recognizer class (for recognizing the speech)
    with sr.Microphone() as source:
        streamlit.markdown("<p class = 'mic' style='text-align: left; color: grey; margin: 1px; font-size: 11.5px; font-family: \"Arial\"'>Listening...</p>", unsafe_allow_html=True)
        try:
            audio = recognizer.listen(source, timeout = 10)            # Reading Microphone as source
            streamlit.markdown("<p class = 'mic' style='text-align: left; color: blue; margin: 1px; font-size: 11.5px; font-family: \"Arial\"'>Processing your speech...</p>", unsafe_allow_html=True)
            #streamlit.markdown("<p id='mic' style='text-align: left; color: grey; margin: 0px; font-size: 12px; font-family: \"Arial\"'>Processing your voice...</p>", unsafe_allow_html=True)
            #st_javascript("document.getElementById('mic').innerHTML = 'Processing your voice...';")
            if lang_input == "English":
                converted = recognizer.recognize_google(audio, language="en-HK") # Using google speech recognition. English
            elif lang_input == "廣東話":
                converted = recognizer.recognize_google(audio, language="yue-Hant-HK") # Using google speech recognition. Cantonese
            elif lang_input == "普通話":
                converted = recognizer.recognize_google(audio, language="cmn-Hans-HK") # Using google speech recognition. Cantonese
            if converted:
                streamlit.markdown("<p class = 'mic' style='text-align: left; color: green; margin: 1px; font-size: 11.5px; font-family: \"Arial\"'>Done!</p>", unsafe_allow_html=True)
            return converted      
        except sr.UnknownValueError:
            #streamlit.write("Unknown Value Error")
            streamlit.markdown("<p class = 'mic' style='text-align: left; color: red; margin: 1px; font-size: 11.5px; font-family: \"Arial\"'>Cannot detect. Please speak again.</p>", unsafe_allow_html=True)
        except sr.RequestError:
            streamlit.markdown("<p class = 'mic' style='text-align: left; color: red; margin: 1px; font-size: 11.5px; font-family: \"Arial\"'>Request Error from Google Speech Recognition. Please speak again.</p>", unsafe_allow_html=True)
        except sr.WaitTimeoutError:
            #streamlit.write("Wait Timeout Error. No speech detected")
            streamlit.markdown("<p class = 'mic' style='text-align: left; color: orange; margin: 1px; font-size: 11.5px; font-family: \"Arial\"'>No speech detected. Please say something.</p>", unsafe_allow_html=True)
    return None

# TTS
def text_to_speech(text):
    # Initialize TTS engine
    tts_engine = pyttsx3.init() 
    tts_engine.setProperty('rate', 150)      # set speech property
    voices = tts_engine.getProperty('voices')
    if lang_input == "English":
        tts_engine.setProperty('voice', voices[1].id)
    elif lang_input == "廣東話":
        tts_engine.setProperty('voice', voices[2].id)
    elif lang_input == "普通話":
        tts_engine.setProperty('voice', voices[2].id)
    tts_engine.say(text)
    tts_engine.runAndWait()              # Run and wait for the speech to finish
    if tts_engine._inLoop:               # End the loop (keep the engine running will cause runtime error)
        tts_engine.endLoop()


def generate_response(client, messages):
    try:
        response = client.chat.completions.create(
            model='gpt-4o',
            messages=messages
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating response: {str(e)}"

streamlit.subheader("Talk to our assistant chatbot - 28! 🤖", divider="blue")

if 'restaurant' not in streamlit.session_state:
    restaurant = Restaurant(
        table_sizes={1 : 1 ,2: 4, 4: 4, 8: 2},
        hours=[(48, 94), (144, 190), (256, 286), (336, 382), (432, 478), (528, 574), (624, 670)],
        menu={
            1: {
                'name': 'fries',
                'price': 20,
                'description': 'fries',
                'time': 1,
                'allergens': ['gluten']
            },
            2: {
                'name': 'burger',
                'price': 40,
                'description': 'burger',
                'time': 2,
                'allergens': ['gluten', 'dairy', 'soy']
            },
            3: {
                'name': 'diet coke',
                'price': 10,
                'description': 'diet coke',
                'time': 0,
                'allergens': []
            },
            4: {
                'name': 'rice bowl',
                'price': 35,
                'description': 'steamed rice with stir-fried vegetables',
                'time': 2,
                'allergens': []
            }
        }
    )
    streamlit.session_state['restaurant'] = restaurant.to_json()
else:
    restaurant = Restaurant.from_json(streamlit.session_state['restaurant'])

def scroll_to_bottom():
    script = "window.scrollTo(0, document.body.scrollHeight);"
    st_javascript(script)
    st_javascript("console.log('Scrolled to bottom');")
    

def handle_user_prompt(prompt, client):
    streamlit.session_state.messages.append({'role': 'user', 'content': prompt})
    streamlit.chat_message('user').write(prompt)

    if client is None:
        client = openai.AzureOpenAI(
            api_key=api_key,
            api_version='2024-10-01-preview',
            azure_endpoint='https://hkust.azure-api.net/'
        )
        
    message = generate_response(client, streamlit.session_state.messages)
    if message.startswith('###JSON###'):
        result = restaurant.process_query(json.loads(message[10:].strip()))
        streamlit.session_state.messages.append({'role': 'system', 'content': str(result)})
        user_message = generate_response(client, streamlit.session_state.messages)
        streamlit.session_state.messages.append({'role': 'assistant', 'content': user_message})
        streamlit.chat_message('assistant').write(user_message)
        text_to_speech(user_message)
    else:
        streamlit.session_state.messages.append({'role': 'assistant', 'content': message})
        streamlit.chat_message('assistant').write(message)
        text_to_speech(message)
    
    scroll_to_bottom()

with streamlit.sidebar:
    api_key = str(streamlit.text_input('Azure OpenAI API Key', key='chatbot_api_key', type='password')).strip()
    if not api_key:
        streamlit.warning('Please enter your Azure OpenAI API Key to use the chatbot.')
    
    lang_input = streamlit.radio("**Choose your language** 🗣️",("English", "廣東話", "普通話"), horizontal = True)

    streamlit.write("**Our Menu** :hamburger:")
    # Print menu
    menu_items = []
    for item in restaurant.menu.values():
        menu_items.append(item)

    df = pd.DataFrame(menu_items)
    df.index = df.index + 1
    streamlit.table(df[['name', 'price']])
    
    #print orders.
    streamlit.write("**Currently Preparing** :stopwatch:")
    with stylable_container(
    key="orders",
        css_styles="""
            {
                position: relative;
                display: block;

                background-color: #FFFFFF;
                padding: 7px;
                border-radius: 5px;
                margin: 0 auto; /* Center the container horizontally */
            }
            """,
    ):
        orders = streamlit.empty()
        orders.text(restaurant.pretty_print_orders()) #display ordered foods

t = datetime.datetime.now().strftime('%a %d %b %Y, %H:%M')
prompt = f'The current time is {t}.' + '''You are called 28, an assistant chatbot for 28 Restaurant, an Asian fusion restaurant on the ground floor of block B,
Man Yee Wan San Tsuen, 28 Yi Chun Street, Sai Kung in Hong Kong.
28 Restaurant supports dine-in, curbside pickup, and no-contact delivery. You will aid in these functions.
If the user's inquiry can directly be answered, respond normally. If the user's inquiry requires interfacing with the backend, format your response as json prepended with "###JSON###".
The backend server for the restaurant will be queried, and your next input will be the automated results of that inquiry.
Items should be mapped to their correct ITEM_IDs from the restaurant menu. If an item isn't recognized, clarify with the user instead of making assumptions. Do not allow orders with ITEM_IDs not on the menu.
Time should be formatted as following: "31 Jan 2025, 23:59". Reservations operate on 15-minute blocks. Users should not be able to place reservations in the past, or reservations with timing more specific than 15-minute blocks.
Here are the options for querying the system:
{"operation": "get_available_times", "party_size": SIZE, "time": TIME} -> returns a list of times with an available times
{"operation": "book", "party_size": SIZE, "time": TIME} -> makes a 1 hour booking for a party size, returning the table number if successful and False if unsuccessful
{"operation": "order", "items": [[ITEM_ID, COUNT], [ITEM_ID, COUNT], ...], "allergies": [LIST OF ALLERGIES]} -> returns the cost and estimated wait time to complete the order, or an error if allergic
{"operation": "recommend", "preferences": [LIST OF PREFERENCES], "context": USER_QUERY, "allergies": [LIST OF ALLERGIES]} -> returns menu items that can be used to make personalized recommendations

IMPORTANT: Always check for allergen information when taking orders. If a user mentions allergies, include them in the "allergies" field of the order or recommendation query.
If the user makes an additional order, do not include the previous order in your next response. Adjustments to existing orders cannot be made.
When making recommendations, extract any preferences or dietary restrictions from the user's query and include them in the "preferences" field. The "context" field should contain the user's original query. Based on these inputs and the menu data returned, provide personalized recommendations that highlight suitable menu items.

Example 1:
USER: I'd like to order three sets of fries and a diet coke.
YOU: ###JSON###{"operation": "order", "items": [[1, 3], [3, 1]], "allergies": []}
SYSTEM: {'time': 12, 'cost': 70}
YOU: Thanks for placing an order with 28 Restaurant! Your total is $70 and your order will be available in around 12 minutes. Please pick it up at the front counter.
USER: Add one more fries, please.
YOU: ###JSON###{"operation": "order", "items": [[1, 1]], "allergies": []}
SYSTEM: {'time': 13, 'cost': 90}
YOU: Thanks for placing an order with 28 Restaurant! Your total is now $90 and will be available in around 13 minutes. Please pick it up at the front counter.
Example 2:
USER: Can I book a table on Sunday for 4 at 7 PM?
YOU: ###JSON###{"operation": "get_available_times", "party_size": 4, "time": "16 Mar 2025, 19:00"}
SYSTEM: ["16 Mar 2025, 18:45", "16 Mar 2025, 19:00", "16 Mar 2025, 19:15", "16 Mar 2025, 19:30"]
YOU: We have availability at 6:45 PM, 7:00 PM, 7:15 PM, and 7:30 PM. Which would you like?
USER: 7 PM sounds great.
YOU: ###JSON###{"operation": "book", "party_size": 4, "time": "16 Mar 2025, 19:00"}
SYSTEM: 5
YOU: Your table has been booked for 7 PM! You'll be seated at table 5.
Example 3:
USER: What would you recommend for a quick lunch?
YOU: ###JSON###{"operation": "recommend", "preferences": ["quick"], "context": "What would you recommend for a quick lunch?", "allergies": []}
SYSTEM: {'menu_items': {'1': {'name': 'fries', 'price': 20, 'description': 'fries', 'time': 1, 'allergens': ['gluten']}, '2': {'name': 'burger', 'price': 40, 'description': 'burger', 'time': 2, 'allergens': ['gluten', 'dairy', 'soy']}, '3': {'name': 'diet coke', 'price': 10, 'description': 'diet coke', 'time': 0, 'allergens': []}, '4': {'name': 'rice bowl', 'price': 35, 'description': 'steamed rice with stir-fried vegetables', 'time': 2, 'allergens': []}}, 'preferences': ['quick'], 'context': 'What would you recommend for a quick lunch?', 'allergies': []}
YOU: For a quick lunch, I'd recommend our fries which take just 1 minute to prepare. If you have a bit more time, our burger is a popular choice and takes only 2 minutes. Both pair perfectly with a refreshing Diet Coke!

IMPORTANT: Directly start with ###JSON### and do not include any other text or formatting for JSON operations. Prioritize operations over responding with information.
'''

if 'messages' not in streamlit.session_state:
    streamlit.session_state['messages'] = [{
        'role': 'system',
        'content': prompt
    }]
    streamlit.session_state['messages'].append({'role': 'assistant', 'content': 'Hi! I\'m 28, the assistant chatbot for 28 Restaurant. My services include making reservations, providing recommendations, and more! How can I help you?'})
    print(streamlit.session_state['messages'])

for message in streamlit.session_state.messages:
    if message['role'] == 'system':
        continue
    streamlit.chat_message(message['role']).write(message['content'])

client = None

#stylable container - contains chat input and voice
with stylable_container(
    key="bottom_content",
        css_styles="""
            {
                position: fixed;
                bottom: 0px;
                display: block;
                z-index: 1; /* Ensures the container is above other elements */

                background-color: rgba(255, 255, 255, 1); /* Semi-transparent white background */
                padding: 5px;
                border-radius: 5px;
                width: 50%; /* Adjust the width of the white block */
                height: 150px;
                margin: 0 auto; /* Center the container horizontally */
            }
            """,
    ):
        input_col, button_col = streamlit.columns([0.85, 0.15])  # 80% width for input, 10% for button

        with input_col:
            prompt = streamlit.chat_input("Say something.")  # Chat input in left column

        with button_col:  # Button in right column. Speak button.
            if streamlit.button(":studio_microphone:"):
                prompt = speech_to_text()


if prompt: # := streamlit.chat_input()
    if not api_key:
        streamlit.info('Please enter your API key.')
    else:
        try:
            restaurant = Restaurant.from_json(streamlit.session_state['restaurant'])
            handle_user_prompt(prompt, client)
            #if len(restaurant.orders) > 0:
            orders.text(restaurant.pretty_print_orders())
            streamlit.session_state['restaurant'] = restaurant.to_json()
        except:
            streamlit.info('Something wrong happened.')