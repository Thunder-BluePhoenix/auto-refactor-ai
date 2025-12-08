# Too Many Parameters Example - Before

"""
This function has too many parameters, making it hard to call correctly.
"""


def create_user(
    username,
    email,
    password,
    first_name,
    last_name,
    phone,
    address_line1,
    address_line2,
    city,
    state,
    zip_code,
    country,
    is_admin=False,
    is_verified=False,
    receive_newsletter=True,
):
    """Create a user with all these parameters - hard to use!"""
    user = {
        'username': username,
        'email': email,
        'password': hash_password(password),
        'first_name': first_name,
        'last_name': last_name,
        'phone': phone,
        'address': {
            'line1': address_line1,
            'line2': address_line2,
            'city': city,
            'state': state,
            'zip': zip_code,
            'country': country,
        },
        'is_admin': is_admin,
        'is_verified': is_verified,
        'receive_newsletter': receive_newsletter,
    }
    return save_user(user)
