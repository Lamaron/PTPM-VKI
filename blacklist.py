BLACKLIST = {
    "admin",
    "root",
    "user",
    "test",
    "guest",
    "superuser",
    "moderator",
    "administrator",
    "support",
    "manager",
}

BLACKLIST_LOWER = {login.lower() for login in BLACKLIST}