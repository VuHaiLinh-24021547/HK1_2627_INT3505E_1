USERS = {
    1: {
        "f": "ohne",
        "l": "pixel",
        "first_name": "ohne",
        "last_name": "pixel",
        "email": "ohne.pixel@example.com"
    },
    2: {
        "f": "Lan",
        "l": "Lê",
        "first_name": "Lan",
        "last_name": "Lê",
        "email": "lan.le@example.com"
    }
}

def get_user(uid):
    return USERS.get(uid)