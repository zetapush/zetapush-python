from zetapush_python import Client
from zetapush_python import Service

import time

# Create the Client to handle the connection with ZetaPush
zpClient = Client(businessId="Rj7PY_1I", apiUrl="http://demo-1.zpush.io/zbo/pub/business/")

# We create the macro service
serviceMacro = Service("macro_0", zpClient)


# Define a function that will be called when the connection is established
def onConnectionSuccessful():
    print("ZetaPush::ConnectionSuccess")

    # We call the macroscript 'send'
    serviceMacro.send('test', {'num1': 3, 'num2': 5})


# We define a function called when the macroscript "test" return us a result
def handleTest(params):
    print("result => ", params['result'])


# Affect a function that will be called when the connection is established
zpClient.onConnectionSuccess = onConnectionSuccessful

# We affect a function to handle the result of the 'test' macroscript
serviceMacro.on('test', handleTest)

# Launch the connection with our credentials
zpClient.connect(login="user", password="password")

# Pause the program during 5 seconds
time.sleep(5)

# Properly close the communication with ZetaPush
zpClient.stopZPConnection()