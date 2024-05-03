# Team Polecat Small Group project

## Team members
The members of the team are:
- Kaushik Chinta - k20029311
- Ahmed Banko - k20071320
- Linda Melichercikova - k20074634
- Marsha Lau - k20036179
- Szabolocs Nagy - k20073246

## Project structure
The project is called `system`.  It currently consists of a single app `clubs`.

## Deployed version of the application
The deployed version of the application can be found at [URL](https://morning-fortress-23494.herokuapp.com/).

The link to the administrative interface of the application can be found at [ADMIN URL](https://morning-fortress-23494.herokuapp.com/admin).

The log in details are:

- email: polecat@example.org
- password: Password123

## Installation instructions
To install the software and use it in your local development environment, you must first set up and activate a local development environment.  From the root of the project:

```
$ virtualenv venv
$ source venv/bin/activate
```

Install all required packages:

```
$ pip3 install -r requirements.txt
```

Migrate the database:

```
$ python3 manage.py migrate
```

Seed the development database with:

```
$ python3 manage.py seed
```

**Collect static files (deviation):**

```
$ python3 manage.py collectstatic
```

Run all tests with:

```
$ python3 manage.py test
```

## Other notes

**Please note that you cannot use your King's email when doing a password reset, this is because our email server is not verified and hence blocked. Furthermore, even for other email providers the emails will be sent to the users spam inbox.**

**Officers cannot add an ouctome to a match which has not taken place, only cancel them. Furthermore if it is a match where the officer is a player then the match can only be forfeited.**


## Sources
The packages used by this application are specified in `requirements.txt`

A lot of our code was inspired from clucker from the 5CCS2SEG module lectures.

The inspiration for the custom user manager class was taken from below:

https://www.fomfus.com/articles/how-to-use-email-as-username-for-django-authentication-removing-the-username/

Our css file is themed version of bootstrap which we can find here:

https://bootswatch.com/flatly/

Our icons are from the font awesome cdn:

https://fontawesome.com/

Our email server was inspired by:

https://docs.djangoproject.com/en/4.0/topics/email/
