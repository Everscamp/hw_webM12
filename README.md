To ran your app simply run the main.py file.

Put all your environment variables to ".evn" file. You can use the .envexample file as a base. Do not forget to rename it.
Docker Compose is used to run all services and databases in the application;

You can access the documentation by this route http://localhost:8000/docs after you start the Uvicorn web sever.

To make any operations with contacts you'll need to authorize.

Here is a screenshot of the response code if the user already exists https://prnt.sc/1NywAjm1b_Si which is 409 Conflict
Here is a screenshot of the response code of a successful registration https://prnt.sc/ZlAqw7cCaDeD which is 201 Created
Here's when the contact is sucessfully added https://prnt.sc/62at413elPY9 which is 201 Created
If there's no user or the email is wrong here's the screenshot of the response code https://prnt.sc/lwnGdf3Fj2Ot which is 401 Unauthorized

The other commands like delete, update, show the contacts with closest birthday, search by name/email - are working as well.

******

The number of requests per minute to your contact routes is limited to a certain number specified in the route description
A mechanism for verifying the registered user's e-mail was implemented;
Limit the number of requests . Be sure to limit the speed - creating contacts for the user;
CORS is enabled for the REST API;
Implemented the ability to update the user's avatar using the Cloudinary service;