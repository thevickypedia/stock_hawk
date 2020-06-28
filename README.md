## Note: 
This is the AWS version of [robinhood_monitor](https://github.com/thevickypedia/robinhood_monitor)

This sub folder contains scripts that run on lambda connecting to SSM. Using SSM connector, I got rid of local environment variables which improves secured storage.

## Setup

##### Prerequisites:
* Running a script on AWS without a deployment tool like jenkins, requires all the libraries/packages to be locally maintained. 
* Refer [documentation](https://aws.amazon.com/premiumsupport/knowledge-center/build-python-lambda-deployment-package/) to begin setup.
* Lambda handler or source file should always be in the root.
* Use the following file structure.<br>
——— src or .zip<br>
——— ——— handler.py<br>
——— some-sub-directory

##### Quick tip:
* create a fresh folder eg: lambda_function and drop your code there (DON'T use sub-folders).
* pip install any package in the format (pip3 install 'package' --target=~/lambda_function/)
* wrap everything together as a .zip file and upload it to AWS.
* root file should be directly accessible within the .zip, so don't include any unnecessary additional sub-folders.

##### 1. Below are the parameters that has to be on your AWS SSM.

* Name = user; Value = Robinhood login email address
* Name = pass; Value = Robinhood login password
* Name = qr; Value = Robinhood MFA QR code (Check for steps in original [README.md](https://github.com/thevickypedia/robinhood_monitor/blob/master/README.md))
* Name = ACCESS_KEY; Value = AWS login access key
* Name = SECRET_KEY; Value = AWS secret key
* Name = SENDER; Value = sender email address (verified via AWS SES)
* Name = RECIPIENT; Value = receiver email address (verified via AWS SES)
<br/><br/>Optional (If you'd like to setup whats app notifications else skip these, app will still run):
* Name = SID; Value = S-ID from twilio
* Name = TOKEN; Value = Token from twilio
* Name = SEND; Value = sender whats app number (fromat - +1xxxxxxxxxx)
* Name = RECEIVE; Value = receiver whats app number (fromat - +1xxxxxxxxxx)<br><br>

##### 2. Setup lambda function and attach an IAM policy

* Create a lambda function with the handler as robinhood.send_whatsapp (this will invoke the send_whats app function inside the robinhood.py file)
* Create an IAM policy with read access to GetParameter and attached to the executing lambda function.
* Once that is done, make sure to check your lambda function's permission to SSM.
* Policy update time: ~5-10 minutes.

##### 3. If you like to setup a cron schedule:
* Add trigger to your lambda function (Trigger name: CloudWatch Events/EventBridge)
* Refer [aws docs](https://docs.aws.amazon.com/AmazonCloudWatch/latest/events/ScheduledEvents.html) for scheduling format.

##### 4. If you like to include historical report graphs for your stocks:
* Use files in the repo [Historical_Graphs_Included](https://github.com/thevickypedia/stock_hawk/tree/master/Historical_Graphs_Included)
* This uses the historical data for your stocks and plots the data as a graph.
* Use /tmp/ for it to work on AWS (default writable folder by AWS)
* matplotlib could be a tricky part to implement on lambda so I have added few steps below.
* Go to https://pypi.org/project/matplotlib/#files
* Choose your python version (37 for 3.7 and 38 for 3.8) and download the manylinux1_x86_64.whl file.
* unzip filename.whl && rm filename.whl
* zip all your folders together and upload it to an S3 bucket and run your lambda connecting to S3.

## License & copyright

&copy; Vignesh Sivanandha Rao, Stock Hawk

Licensed under the [MIT License](LICENSE)
