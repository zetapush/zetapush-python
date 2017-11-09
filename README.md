# ZetaPush SDK #

This module is a SDK to connect to the ZetaPush platform with Python. (Only with Python3)

## Installation

pip3 install zetapush_python

## Usage

### Imports

First, we need to import 2 objets to use the ZetaPush SDK :

 - Client
 - Service

The `Client` is used to handle the connection with the ZetaPush backend and the `Service` is used to call services from the client. In particular, the service to call macroscripts.

To import them we write :

	from zetapush_python import Client
	from zetapush_python import Service
	

### Connection to ZetaPush backend

First, we need the create the `Client` to handle the connection :

	zpClient = Client(businessId="Rj7PY_1I", apiUrl="http://demo-1.zpush.io/zbo/pub/business/")

	
The *businessId* is the identifier of the sandbox in the ZetaPush back-end. For ZetaPush, a sandbox includes the whole application back-end. Then, we have the *apiUrl*. It is optional in production. During the development we send you the apiUrl if necessary.

Now, we need to launch the connection with our credentials. For this example we use this credentials :

 - login : "user"
 - password: "password"

		zpClient.connect(login="user", password="password")

#### Callback connection

It is useful to launch a function when the connection is established.
For this we implement the *onConnectionSuccess()* method :

	
	def onConnectionSuccess():
		print("OnConnectionSuccess")
	
	zpClient.onConnectionSuccess = onConnectionSuccess



### Call a macroscript

In this step, we call a macroscript. For this, we need to configure a service that manage the macroscript calls.

	serviceMacro = Service("macro_0", zpClient)

Here *macro_0* is the *deployment ID* of our macroscript service. By default we use *macro_0*.
*zpClient* is our Client that we previously create.

In our example, we want to call a macroscript named **test** that takes 2 parameters *num1* and *num2*. The macroscript return the sum of *num1* and *num2* in a object named *result*.

To call the macroscript we use :
	
	serviceMacro.send('test', { 'num1': 3, 'num2': 5})

To listen the result we need to define a function and affect it to the result :

	
	def handleTest(params):
		print("result => ", params['result']

	
	serviceMacro.on('test', handleTest)



### Stop the communication with ZetaPush

To disconnect an user to the ZetaPush platform we can use :

	zpClient.disconnect()

Then, it is necessary to properly close the communication with the ZetaPush backend at the end of the program. For this we use :

	zpClient.stopZPConnection()

### Send JSON in macro

We can also send JSON in a macroscript.

In our example we have a macroscript named *testJson(name, data)* that have 2 parameters :

 - name : String
 - data : Map (or JSON)

We can call this macroscript with this syntax :

	
	serviceMacro.send('testJson', { 'name': 'sensor1', 'data': { 'value': 15, 'unit': 'ppm' }} )
	

## Complete example


Here we have a complete example that launch a connection to the ZetaPush platform, call a macroscript named *test*, print his result and close the communication after few seconds :


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
	    serviceMacro.send('test', { 'num1': 3, 'num2': 5})
	
	# We define a function called when the macroscript "test" return us a result
	def handleTest(params):
	    print("result => ", params['result'])
	
	
	# Affect a function that will be called when the connection is established
	zpClient.onConnectionSuccess = onConnectionSuccessful
	
	# We affect a function to handle the result of the 'test' macroscript
	serviceMacro.on('test', handleTest)
	
	# Launch the connection with our credentials
	zpClient.connect(login= "user", password= "password")
	
	# Pause the program during 2 secondes
	time.sleep(2)
	
	# Properly close the communication with ZetaPush
	zpClient.stopZPConnection()