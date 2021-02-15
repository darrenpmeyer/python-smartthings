import smartthings.api_base
from pprint import pprint, pformat

st = smartthings.SmartThingsClient(tokenfile='access_token.secret', tokenfilepath=['..'])
result = st.list_devices(capability='light')

for device in result['items']:
    print("{id} {name} ({type}):\n{capabilities}".format(
        id=device['deviceId'],
        name=device['label'],
        type=device['name'],
        capabilities=pformat(device['components'][0]['capabilities'], indent=3, compact=True)
    ))

    description = st.describe_device(device['deviceId'])
    # pprint(dict(description))
    print(f"{description['label']}: {description['deviceId']}")
