# Mr Fusion - An AI-powered web app to facilitate the resolution of any kind of conflict

## Introduction

Mr Fusion is an AI-powered web application designed to facilitate the resolution of any kind of dispute with ease and empathy.

![Mr Fusion](/images/mrfusion.gif)

Supported by the **[Google Gemini API](https://ai.google.dev/)**, it serves as a **digital mediator** to help users navigate conflicts, whether they involve colleagues, family members, or community issues. 

The application listens to and articulates users' concerns while ensuring they understand the perspectives of others. 

It promotes **structured communication** by presenting different scenarios and potential outcomes, acting like an **impartial friend**. 

With a **mobile-friendly** interface, Mr Fusion offers immediate analysis and dynamic guidance, transforming conflict resolution into a more efficient, empathetic, and effective process.

![Mr Fusion is mobile-friendly](/images/mobile_friendly.gif)

## Features
- Mr Fusion is a [Django-based](https://www.djangoproject.com/) web application. The Django web framework is a free, open source framework that can speed up development of a web application being built in the Python programming language.
- It uses [Django-channels](https://channels.readthedocs.io/en/latest/) and [Redis](https://redis.io) for the real-time communication between the users in a chat. Django-channels empowers Django to handle WebSockets and other asynchronous protocols, while Redis acts as a message broker for facilitating communication between different components of the application.
- It also uses the [htmx](https://htmx.org/) library, a lightweight, dependency-free, extendable JavaScript front-end library to access modern browser features directly from HTML. It allows to deal with AJAX requests, WebSockets, and Server Sent Events directly in HTML code.
- The communication with the [Gemini API](https://ai.google.dev/) is done using [LangChain](https://www.langchain.com/) integrations for Gemini through their generative-ai SDK.

## Installation

### Redis installation

You can install Redis locally but it is much easier simply running it from a Docker container. To use Docker on your computer, you need to install [Docker Desktop](https://www.docker.com/products/docker-desktop/)

There is a version for Linux, Mac and Windows. To check if Docker is already installed on your machine use the following command:

```bash
docker -v
```

> Docker version 27.0.3, build 7d4bcd8

If you got a result like above, it means that Docker is already installed on your machine and you can install the Redis server by simply running the following command:

```bash
docker run --name redis1 -p 0.0.0.0:6379:6379 -d redis
```

### Web Application installation

To run this project in your machine, follow these steps:

#### Create and activate a virtual environment

You may need to install it first with pip:
```bash
pip install virtualenv
```

Once installed, you can create a virtual environment with:
```bash
virtualenv mrfusion_env
```

And then activate it
```bash
source mrfusion_env/bin/activate
```

#### Clone this repository

```bash
git clone https://github.com/carlesilla/MrFusion.git
```
#### Enter the folder and install dependencies

```bash
cd MrFusion
pip install -r requirements.txt
```

#### Create an .env file with this variables

```python
GOOGLE_API_KEY=<GEMINI API KEY>
EMAIL_HOST=<SMTP server>
EMAIL_PORT=<SMTP port>
EMAIL_HOST_USER=<USER>
EMAIL_HOST_PASSWORD=<PASSWORD>
```
The configuration of the SMTP server is optional. You can invite users with the code that will appear in the “Invite parties” modal.


#### Create database

```bash
python manage.py migrate
```

#### Create admin user

```bash
python manage.py createsuperuser
```

#### If everything is alright, you should be able to start the Django development server:

```bash
python manage.py runserver
```

#### Open your browser and go to http://127.0.0.1:8000, you will be greeted with the login page

![Sign In](/images/sign_in.png)

### Setup

Once logged in with the credentials you created with the 'createsuperuser' command, you can start by adding a photo of yourself to the profile so that other participants can identify you more easily.

![Add picture](/images/add_picture.gif)

When creating the administrator user with the command "createsuperuser" you will not have entered your name and surname, so you will have to add them manually in settings

![Add name](/images/add_name.gif)

By default, the administrator user is not included as part of the conflict. If you want this user to participate activate the "Party to conflict" option

![Party to conflict](/images/party_to_conflict.png)

As an administrator, from the settings tab you can make a backup, restore data from a previous session, or even delete all data so you can use the same setup to mediate another conflict.

![Backup and Restore](/images/backup_and_restore.png)

The next step as administrator is invite all parties to register. If you have configured the SMTP server, you can insert the email and they will receive a link to register. If not you can send them the code displayed in the form.

![Send invitations](/images/invite_parties.gif)

## Usage by a participant in the conflict

1. **Set Up Your Profile:**
   - After registering and logging in, the first thing you should do is upload a photo to your profile. This helps personalize your presence on the platform.

   ![Add picture](/images/add_picture.gif)

2. **Describe the Conflict:**
   - Share your unique perspective on the conflict. Be as detailed as possible. This detailed description is crucial as it allows Mr. Fusion to ask insightful questions in a private chat, helping him delve deeper into the problem and guide the conversation effectively.

   ![Conflict description](/images/conflict_description.gif)

3. **Engage in One-to-One Chat:**
   - Head over to the one-to-one chat and answer Mr. Fusion's questions. To start the interaction, simply click the 'Run' button. Mr. Fusion will inform you when he has gathered all the necessary information.

   ![One-to-one chat](/images/one-to-one_chat_marty.gif)

4. **Create and Manage Chats:**
   - Now, you can create new chats to interact with other users. Make sure to fill out the description. This helps Mr Fusion understand the specific purpose of the chat and mediate effectively.
   - Feel free to generate as many chats as needed, inviting the appropriate participants to each one.
   - You can add or remove users from the chat at any time.
   - Use the 'RUN' button to request Mr Fusion to mediate the conflict.

   ![All together chat](/images/all_together_chat_marty.gif)


By following these steps, you'll be well on your way to resolving conflicts efficiently and collaboratively. 

Happy mediating!