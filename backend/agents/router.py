def route_to_agent(intent: str) -> str:
    if intent == "Refund":
        return "Refund Agent"

    elif intent == "Shipping":
        return "Shipping Agent"

    elif intent == "Warranty":
        return "Warranty Agent"

    elif intent == "Comparison":
        return "Comparison Agent"

    elif intent == "Warranty":
        return "Warranty Agent"

    elif intent == "Recommendation":
        return "Recommendation Agent"
    
    elif intent == "Product":
        return "Product Agent"

    elif intent == "Complaint":
        return "Complaint Agent"

    elif intent == "Technical":
        return "Technical Support Agent"

    else:
        return "FAQ Agent"
