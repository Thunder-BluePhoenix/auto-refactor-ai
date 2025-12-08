# Too Many Parameters Example - After

"""
Use dataclasses to group related parameters.
"""

from dataclasses import dataclass, field


@dataclass
class Address:
    line1: str
    city: str
    state: str
    zip_code: str
    country: str
    line2: str = ""


@dataclass
class UserSettings:
    is_admin: bool = False
    is_verified: bool = False
    receive_newsletter: bool = True


@dataclass
class CreateUserRequest:
    username: str
    email: str
    password: str
    first_name: str
    last_name: str
    phone: str
    address: Address
    settings: UserSettings = field(default_factory=UserSettings)


def create_user(request: CreateUserRequest) -> dict:
    """Create a user from a structured request object."""
    user = {
        'username': request.username,
        'email': request.email,
        'password': hash_password(request.password),
        'first_name': request.first_name,
        'last_name': request.last_name,
        'phone': request.phone,
        'address': {
            'line1': request.address.line1,
            'line2': request.address.line2,
            'city': request.address.city,
            'state': request.address.state,
            'zip': request.address.zip_code,
            'country': request.address.country,
        },
        'is_admin': request.settings.is_admin,
        'is_verified': request.settings.is_verified,
        'receive_newsletter': request.settings.receive_newsletter,
    }
    return save_user(user)


# Usage is now cleaner:
# address = Address(line1="123 Main St", city="NYC", state="NY", zip_code="10001", country="USA")
# request = CreateUserRequest(username="john", email="j@example.com", ...)
# create_user(request)
