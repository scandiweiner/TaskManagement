# Task 

Enjoy the task, no pun intended

## Setup

```
clone https://github.com/scandiweiner/TaskManagement.git
cd TaskManagement
```

create virtual venv and activate
```
$ python3 -m venv {path}
$ source env/bin/activate
```
Install the dependencies
```
(venv)$ pip install -r requirements.txt
```
Migrate
```
manage.py migrate
```
create superuser
```
manage.py createsuperuser
```

run
```
manage.py runserver
```

yay

## API examples
I'm using postman, use whatever you like though

### Checkin task
* **URL**

    POST /task/checkin/

* **Example request**
```json
{
  "user": "username",
  "checkin_date": "2020-12-31T17:00:00Z",
  "description": "Do something crazy"
}
```

* **Success response**
    code: 200
    content: 
    ```json
    {
      "data": "Checkin: user: Yana task: Create Task Management API",
      "error": null
    }
    ```

* **Error response**
    * code: 400
    * content: 
        ```json
        {
          "data": null,
          "error": "bad_request"
        }
        ```
  **or**
     * content: 
        ```json
        {
            "data": null,
            "error": "user_already_has_an_open_task"
        }
        ```
  
 ### Checkout task
* **URL**

    POST /task/checkout/

* **Example request**
    ```json
    {
      "checkout_date": "2020-12-31T18:00:00Z"
    }
    ```
* **Success response**
    * code: 200
    * content: 
    ```json
    {
        "data": "Checkout: user: Yana",
        "error": null
    }
    ```

* **Error response**
    * code: 400
    * content: 
    ```json
    {
        "data": null,
        "error": "bad_request"
    }
    ```
  **or**
     * content: 
    ```json
    {
        "data": null,
        "error": "task_was_checked_out"
    }
    ```

 ### Task Report
* **URL**

    GET task/report/
    
* **Success response**
    * code: 200
    * content: 
    ```json
    {
    "yana": [
        "Create API for task management: 1 hours",
        "Add README file to project: 1 hours"
    ],
    "other_person": [
        "Do some very interesting task: 2 hours"
    ]
    }
    ```

## Run tests
for all tests:
```
manage.py test
```

## Assumptions
1. Once a user checks in the task is being created
2. If task is checked in but the user name doesn't exist - create new user
3. user cannot checkin to a task that's in progress
