Store users in the format

{
    "id": "USER ID",
    "username": "USERNAME",
    "email": "EMAIL ADDRESS",
    "admin": WHETHER IS ADMIN,
    "login": {
        "password": hashed password,
        "salt": salt for pas
    },
    "problems": {
        "attempted": {
            key-value of "problem name" -> submission
        },
        "solved": {
            key-value of "problem name" -> submission
        }
    },
    "contests": {
        "joined": [
            unused -- will be list of joined contests
        ]
    },
    "meta": {
        "date-created": "04-28-2025-22-54-47"
    }
}