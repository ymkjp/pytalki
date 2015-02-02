# pytalki

## Getting Started
1. Install packages by `pip install -r requirements.txt`
2. Start the web server as below
3. Access to [http://localhost:5000/](http://localhost:5000/)

```sh
# Setup dummy data and run server
$ python app.py --setup --sqla_uri "mysql://username:password@localhost/db_name"

# Run server without setting-up dummy data
$ python app.py --sqla_uri "mysql://username:password@localhost/db_name"
```


## Here is the programming problem:

#### Required Python Libraries to Use:
* Python (of course)
* Tornado web framework
* Jinja2 - template engine (replace the Tornado template engine - need to change some settings)
* Optional Libraries to Use:
* SQLAlchemy - ORM
* Any others you want to use

#### Task:
* Create a page to display a list of users of a system (much like on italki) using Python, with data stored in MySQL.

#### Functional Requirements:
* Display a list of users, using a simple layout (doesn't need to be very complex)
 * The list view should show some simple information about the user, like their nickname, languages, etc.
* Users can be either teacher or student
* Both teachers and students have some shared properties, like:
 * username
 * name
 * email
* languages spoken and proficiency level
* Teachers have additional properties like:
 * Languages taught
 * Course for languages taught
  * * The course does not need to be displayed in the user list, but please design a suitable MySQL schema for course
* The list of users should be filtered by:
 * User type
 * Languages spoken
 * Languages taught (for the case of teachers)
 
#### Other Requirements:
* Design a suitable table schema for the application
* Use jinja2 as the template engine
* Make sure that requests to the database do not block the I/O loop

#### Optional:
* Use a javascript library where applicable; this could include using asynchronous calls for loading data or filtering

#### Output:
* Python code
* If you have data, an SQL dump
* List of required libraries and versions

Please get it back to me as soon as you finish, if possible by Monday evening. If you have any questions, feel free to send me by email, or message me on Skype.
