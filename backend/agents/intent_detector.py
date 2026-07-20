def detect_intent(user_message: str) -> str:
    message = user_message.lower().strip()

    if any(word in message for word in [
        "refund",
        "return",
        "money back"
    ]):
        return "Refund"

    elif any(word in message for word in [
        "complaint",
        "angry",
        "bad service",
        "not happy"
    ]):
        return "Complaint"

    elif any(word in message for word in [
        "login",
        "password",
        "error",
        "bug",
        "not working",
        "not turning on",
        "charging issue",
        "battery issue",
        "display issue",
        "screen issue"
    ]):
        return "Technical"

    elif any(word in message for word in [
        "shipping",
        "delivery",
        "track order"
    ]):
        return "Shipping"

    elif any(word in message for word in [
        "warranty",
        "repair",
        "guarantee",
        "replacement"
        "service"
    ]):
        return "Warranty"

    elif any(word in message for word in [
        "billing",
        "payment",
        "invoice"
    ]):
        return "Billing"

    elif any(word in message for word in [
        "compare",
        "comparison",
        "difference between",
        "versus",
        " vs "
    ]):
        return "Comparison"

    elif any(phrase in message for phrase in [
        "suggest",
        "recommend",
        "recommendation",
        "best product",
        "best battery",
        "best laptop",
        "best phone",
        "cheapest",
        "under ₹",
        "under rs",
        "under rupees",
        "below ₹",
        "below rs",
        "within budget"
    ]):
        return "Recommendation"

    elif any(phrase in message for phrase in [
        "compare",
        "comparison",
        "difference between",
        "versus",
        " vs "
    ]):
        return "Comparison"

    elif any(word in message for word in [
        "warranty",
        "guarantee",
        "coverage"
    ]):
        return "Warranty"

    elif any(word in message for word in [
        "price",
        "cost",
        "product",
        "products",
        "laptop",
        "pro laptop",
        "airbook",
        "phone",
        "smartphone",
        "nova x10",
        "x10 pro",
        "x10",
        "headphone",
        "headphones",
        "earbud",
        "earpods",
        "earbuds",
        "buds",
        "novabuds",
        "novasound",
        "watch",
        "smartwatch",
        "novawatch",
        "charger",
        "adapter",
        "fastcharge",
        "cable",
        "usb-c",
        "mouse",
        "keyboard",
        "backpack"
    ]):
        return "Product"

    else:
        return "FAQ"
