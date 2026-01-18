from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    OWNER = "owner-event"
    CLIENT = "client"
    SERVICE_CLIENTI = "serviciu_clienti"