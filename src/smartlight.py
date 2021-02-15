import smartthings
from pprint import pprint

token = smartthings.get_token(search_path=['..'])

device_named = {
    'On Air Light': '8ec0dd7b-a9b6-4cef-8b1a-f4e1d23fc9af',
    'Bedroom Light': 'b86ffa15-ed17-4ef5-aeb1-356f6057d7cf'
}

# b86ffa15-ed17-4ef5-aeb1-356f6057d7cf => Bedroom Light
response = smartthings.device_switch(token, device_named['On Air Light'], state='off')
pprint(response.json())