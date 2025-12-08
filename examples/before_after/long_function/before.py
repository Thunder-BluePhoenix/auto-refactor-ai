# Long Function Example - Before

# "This function does too much and is hard to test/maintain."

def process_order(order_id, customer_data, items, shipping_info, payment_info,
                  discount_code=None, gift_wrap=False, notify=True):
    # Validate order
    if not order_id:
        raise ValueError("Order ID required")
    if not customer_data:
        raise ValueError("Customer data required")
    if not items:
        raise ValueError("Items required")

    # Calculate totals
    subtotal = 0
    for item in items:
        item_price = item['price'] * item['quantity']
        if item.get('taxable'):
            item_price *= 1.08
        subtotal += item_price

    # Apply discount
    discount = 0
    if discount_code:
        if discount_code == 'SAVE10':
            discount = subtotal * 0.10
        elif discount_code == 'SAVE20':
            discount = subtotal * 0.20
        elif discount_code == 'FREESHIP':
            shipping_info['cost'] = 0

    # Calculate shipping
    shipping_cost = shipping_info.get('cost', 5.99)
    if subtotal > 100:
        shipping_cost = 0

    # Add gift wrap
    if gift_wrap:
        shipping_cost += 3.99

    # Calculate final total
    total = subtotal - discount + shipping_cost

    # Process payment
    if payment_info['type'] == 'credit':
        # credit card processing
        result = charge_credit_card(payment_info['number'], total)
    elif payment_info['type'] == 'paypal':
        # paypal processing
        result = process_paypal(payment_info['email'], total)
    else:
        raise ValueError("Unknown payment type")

    # Create order record
    order = {
        'id': order_id,
        'customer': customer_data,
        'items': items,
        'subtotal': subtotal,
        'discount': discount,
        'shipping': shipping_cost,
        'total': total,
        'status': 'processed'
    }

    # Save to database
    save_order(order)

    # Send notifications
    if notify:
        send_email(customer_data['email'], 'Order Confirmed', f'Order {order_id}')
        if shipping_info.get('tracking'):
            send_sms(customer_data['phone'], f'Tracking: {shipping_info["tracking"]}')

    return order
