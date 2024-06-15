To ran your app simply run the main.py file
SQLALCHEMY_DATABASE_URL variable consist the credentials for your postgress db
As a db I used this conatiner 
docker run --name restapi-postgres -p 5432:5432 -e POSTGRES_PASSWORD=567234 -d postgres

You can access the documentation by this route http://localhost:8000/docs after you start the Uvicorn web sever.

To make any operations with contacts you'll need to authorize 

Here is a screenshot of the response code if the user already exists https://prnt.sc/1NywAjm1b_Si which is 409 Conflict
Here is a screenshot of the response code of a successful registration https://prnt.sc/ZlAqw7cCaDeD which is 201 Created
Here's when the contact is sucessfully added https://prnt.sc/62at413elPY9 which is 201 Created
If there's no user or the email is wrong here's the screenshot of the response code https://prnt.sc/lwnGdf3Fj2Ot which is 401 Unauthorized

The other commands like delete, update, show the contacts with closest birthday, search by name/email - are working as well.
