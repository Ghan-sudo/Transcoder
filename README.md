# A fault tolerent, Event Driven, distributed video processing pipeline. Implemented ontop of aws

REST API Secured with API key using AWS API Gateway.
Uploads are secured through S3 signed urls with Content-Length size headers and Expiry time of 5 seconds.
Videos are provided through CloudfrontCDN.

Processing videos take a lot of compute resources. If we use the default scale in policy provided by AWS, it might resultin killing an instance that is actively processing a video.
Curently using a scale in protection policy implemented in a lambda. This is very important since it allows us to only kill the instances that do not have
any task. Though, the lambda execution time limit is only 2 seconds. Which is not enough for a cold start, therefore we have and autoinvocation from EventBridge every 4 minutes
to keep the lambda warm.

The Autoscaling group pulls an AMI to start EC2 instances with all the libraries and code included.
The AMI is based on an Ubuntu image with custom startup script to run my python code.

The EC2 instance polls the que for 20s, if no task is received it sends a custom scale down metric to Cloudwatch and registers
itself in the KillMe list in the Elasticache(redis).

Similarly, When a request is received the Upload VideoHandler Service sends a custom metric to CLoudwatch to scale out
the EC2 instances.

We are using FIFO ques for their Exactly-Once-Delivery(EOD) garantee. As said before video processing is expensive using EOD saves us compute resources.

Since we are processing multiple Video resolutions in parallel on multiple machines we need to decide which machine gets to generate the final mpd and sound files.
For this we are using(abusing?) Elasticache's(Redis) atomic and isolation garantees. Each instance after uplaoding the processed files invokes a Redis function/Script
(which are garanteed by Redis to be atomic and run in isolation). which checks if the other files have been processed as well, if they were processed, it returns a true value
which the invoker can go ahead and genearte the final files. If the other files are not processed, it returns and false and the invoker can move on to a new task.

We are basically using redis to implemented a sort of linearizer(In a sense using Redis to provide us with a strict consistency model of a shared memory)
(Kinda how random unique messages in Paxos induce a hirarchy of instanes during an election)






![Archiecture Diagram](Architecture.svg)
