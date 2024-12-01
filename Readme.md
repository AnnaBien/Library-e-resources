# Library e-resources

[Provincial Public Library](https://www.rajska.info/) is providing special codes that allow library members to get a free monthly subscription to the Legimi or EmpikGo apps.
To get the code a library member has to fill out an online form and submit it at the beginning of each month. 
When the code is obtained (sent via e-mail) it has to be activated at dedicated website.
More information available on library website: [Legimi](https://www.rajska.info/e-zasoby-legimi) or [EmpikGo](https://www.rajska.info/e-zasoby-empikgo)

---

#### This project automates the process of submitting an online form requesting the codes for a free Legimi or EmpikGo subscription.


Note! Although the process of submitting form is fully automated, you still need to activate the code obtained via e-mail yourself.


## Why was this project developed?

Due to the popularity of e-resources.
Unfortunately the number of available codes is limited and the order of applications decides.

The form is available from the first of each month and must be sent every month to keep your subscription.
In practice, the form should be sent not too long after midnight, otherwise you may forget to receive the code.

This really complicates the ease of the process. Sometimes you may miss the right time to submit a form or just want to get to bed early.
These are enough reasons why it is nice to have such things automated.

## Deployment

Google Cloud is used to deploy this project. 
Each directory ```container_deploy```, ```container_delete``` and ```selenium_app``` contains code of single Cloud Run Function.
File ```main.py``` present in each project is required and contains the entry point for Cloud Run Functions.

Note! These projects are separeted from each other which resulted in repetition of ```logger.py``` file. 

### Cloud Run Function: Container deploy

Implements function responsible for deploying a container [selenium/standalone-chrome](https://hub.docker.com/r/selenium/standalone-chrome), which is needed to handle all
Selenium WebDriver requests. A container is deployed from image previously added into google project's artifact registry.

For this function a custom IAM service account must be created as function needs special permissions to manipulate Cloud Run resources:
- Cloud Run Admin - to grant the run.services.setIamPolicy permission
- Service Account User - to grant the iam.serviceAccounts.actAs permission

### Cloud Run Function: Selenium App

This project implements the functionality of filling out and submitting an online form.
The Selenium library is used in conjunction with the WebDriver interface, which communicates remotely with a previously deployed container.


### Cloud Run Function: Container delete

Removes the standalone-chrome container when the Selenium application finishes its tasks.

### Cloud Scheduler

Scheduler is used to invoke Cloud Run Functions by sending HTTP GET request at certain URLs.
Application is scheduled to deploy a container at 12.00 AM the first day of the month. 
Next at 12.03 AM Cloud Scheduler sends an HTTP request that triggers the application.
At the end the last function is invoked to delete the container.

## Running on localhost

If you do not feel fancy enough to use Google Cloud, run this code on your localhost. 
Only make sure you have the Chrome browser already installed or preferably  run [selenium/standalone-chrome](https://hub.docker.com/r/selenium/standalone-chrome) container on port 4444.

Firstly prepare your environment:
```bash
cd selenium_app
pip install -r requirements.txt
```

Comment out or delete below lines from ```logger.py```:

```python
CLIENT = google.cloud.logging.Client()
CLIENT.setup_logging()
```

Now you can fill out your data and run below code instead of ```main.selenium_client```:

```python
from selenium_app.request_resource_access import RequestResourceAccess
from selenium_app.form_data import EResourceType

user_data = [
    {
        'library_card_no': '213721',
        'email': 'example@gmail.com',
        'resource_type': EResourceType.empikgo.value
    }
]
resource_request_instance = RequestResourceAccess(cmd_exec_url='http://127.0.0.1:4444')
resource_request_instance.wait_until_form_is_available()  # you may want to extend the waiting time
resource_request_instance.fill_form_and_send(user_data)

```

Note! Application will raise a RequestNotSend exception while the online form is not available.
