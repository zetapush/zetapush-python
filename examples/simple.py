from zetapush_python import Client
from zetapush_python import Service

import time

# Create the Client to handle the connection with ZetaPush
zpClient = Client(businessId="zXkUtj0b", apiUrl="http://demo-1.zpush.io/zbo/pub/business/")

# We create the macro service
serviceMacro = Service("macro_0", zpClient)

# We define a function called when the macroscript "test" return us a result
def handleTest(params):
    print("result => ", params['result'])

def handleError(code, message):
    print("Got error {0} with message {1}".format(code, message))

def handleCompleted():
    print("Got completion message")

# We set functions to handle the result of the 'test' macroscript + errors and completion events
serviceMacro.onError(handleError)
serviceMacro.onCompleted(handleCompleted)
serviceMacro.on('test', handleTest)

# Define a function that will be called when the connection is established
def onConnectionSuccessful():
    print("ZetaPush::ConnectionSuccess")

    # We call the macroscript 'send'
    serviceMacro.send('test', {'num1': 3, 'num2': 5})


# Affect a function that will be called when the connection is established
zpClient.onConnectionSuccess = onConnectionSuccessful

# Launch the connection with our credentials
zpClient.connect(login="user", password="password")

# Pause the program during 2 seconds
time.sleep(2)

# Properly close the communication with ZetaPush
zpClient.stopZPConnection()
