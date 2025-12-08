"""Test file with clean/good code patterns - no issues expected."""


def calculate_total(items):
    """Clean function - proper length and structure."""
    return sum(item.price * item.quantity for item in items)


def validate_email(email):
    """Simple validation with early return."""
    if not email:
        return False
    if "@" not in email:
        return False
    if "." not in email.split("@")[1]:
        return False
    return True


def process_order(order):
    """Well-structured order processing."""
    if not order.is_valid():
        return {"error": "Invalid order"}
    
    total = calculate_total(order.items)
    tax = total * 0.1
    
    return {
        "subtotal": total,
        "tax": tax,
        "total": total + tax,
    }


class UserService:
    """Clean class with proper method sizes."""
    
    def __init__(self, repository):
        self.repository = repository
    
    def get_user(self, user_id):
        """Simple getter."""
        return self.repository.find_by_id(user_id)
    
    def create_user(self, name, email):
        """Simple creator."""
        user = {"name": name, "email": email}
        return self.repository.save(user)
    
    def delete_user(self, user_id):
        """Simple deleter."""
        return self.repository.delete(user_id)


def format_currency(amount, currency="USD"):
    """Clean formatting function."""
    symbols = {"USD": "$", "EUR": "€", "GBP": "£"}
    symbol = symbols.get(currency, currency)
    return f"{symbol}{amount:,.2f}"


def parse_date(date_string):
    """Clean date parsing."""
    from datetime import datetime
    
    formats = ["%Y-%m-%d", "%d/%m/%Y", "%m-%d-%Y"]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_string, fmt)
        except ValueError:
            continue
    
    return None
