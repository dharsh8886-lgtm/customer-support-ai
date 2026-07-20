import os

from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException
from groq import Groq
from pydantic import BaseModel

from agents.billing_agent import get_billing_prompt
from agents.complaint_agent import get_complaint_prompt
from agents.faq_agent import get_faq_prompt
from agents.intent_detector import detect_intent
from agents.comparison_agent import get_comparison_prompt
from agents.warranty_agent import get_warranty_prompt
from routes.ticket_routes import router as ticket_router
from agents.recommendation_agent import get_recommendation_prompt
from agents.product_agent import get_product_prompt
from agents.router import route_to_agent
from agents.technical_agent import get_technical_prompt
from auth.auth import login_user, register_user
from auth.jwt_handler import verify_access_token
from database.mongodb import chat_collection
from rag.rag_engine import retrieve_context

# ---------------- CONFIGURATION ----------------

load_dotenv()

app = FastAPI(title="Customer Support AI")

app.include_router(ticket_router)

groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:
    raise RuntimeError(
        "GROQ_API_KEY is missing from the .env file."
    )

client = Groq(api_key=groq_api_key)


# ---------------- REQUEST MODELS ----------------

class ChatRequest(BaseModel):
    message: str


class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


# ---------------- BASIC ROUTES ----------------

@app.get("/")
def home():
    return {
        "message": "Customer Support AI Backend is Running!"
    }


@app.post("/register")
def register(request: RegisterRequest):
    return register_user(
        request.name,
        request.email,
        request.password
    )


@app.post("/login")
def login(request: LoginRequest):
    return login_user(
        request.email,
        request.password
    )

@app.post("/forgot-password")
def forgot_password(data: dict):
    email = data["email"]

    return {
        "message":
        "If an account exists, reset instructions have been sent."
    }

# ---------------- PRODUCT HELPERS ----------------

PRODUCT_KEYWORDS = [
    "technova pro laptop",
    "technova pro",
    "pro laptop",
    "technova airbook",
    "airbook",
    "nova x10 pro",
    "x10 pro",
    "nova x10",
    "x10",
    "novabuds wireless earbuds",
    "novabuds",
    "nova buds",
    "earbuds",
    "earbud",
    "earpods",
    "ear pods",
    "earphones",
    "buds",
    "novasound headphones",
    "novasound",
    "headphones",
    "headphone",
    "novawatch smart",
    "novawatch",
    "smartwatch",
    "smart watch",
    "watch",
    "fastcharge 65w adapter",
    "fastcharge",
    "charger",
    "adapter",
    "usb-c cable",
    "usb c cable",
    "type c cable",
    "cable",
    "laptop backpack",
    "backpack",
    "wireless mouse",
    "mouse",
    "wireless keyboard",
    "keyboard"
]


FEATURE_ALIASES = {
    "price": [
        "price",
        "cost",
        "how much",
        "rate"
    ],
    "processor": [
        "processor",
        "cpu"
    ],
    "ram": [
        "ram",
        "memory"
    ],
    "storage": [
        "storage",
        "ssd",
        "capacity"
    ],
    "display": [
        "display",
        "screen"
    ],
    "battery life": [
        "battery life",
        "backup",
        "how long battery"
    ],
    "battery": [
        "battery",
        "battery capacity"
    ],
    "bluetooth": [
        "bluetooth"
    ],
    "connectivity": [
        "connectivity",
        "connection"
    ],
    "camera": [
        "camera"
    ],
    "charging": [
        "charging",
        "fast charging",
        "charge"
    ],
    "noise cancellation": [
        "noise cancellation",
        "anc"
    ],
    "water resistance": [
        "water resistance",
        "waterproof"
    ],
    "features": [
        "features",
        "specifications",
        "specs",
        "details"
    ]
}


def detect_requested_features(user_text: str) -> list[str]:
    """
    Detect every product specification requested by the user.

    Example:
    "earpods price battery life bluetooth"
    returns:
    ["price", "battery life", "bluetooth"]
    """
    normalized_text = user_text.lower().strip()
    requested_features = []

    # Check longer feature phrases first.
    sorted_features = sorted(
        FEATURE_ALIASES.items(),
        key=lambda item: max(
            len(alias) for alias in item[1]
        ),
        reverse=True
    )

    for feature_name, aliases in sorted_features:
        if any(
            alias in normalized_text
            for alias in aliases
        ):
            requested_features.append(feature_name)

    return requested_features


def find_last_selected_product(recent_chats):
    """
    Find the latest product selected by the user.

    selected_product is preferred because it contains the exact
    product name saved after a product response.
    """
    for chat in recent_chats:
        selected_product = chat.get("selected_product")

        if selected_product:
            return selected_product

    # Fallback for older database entries that do not contain
    # selected_product.
    for chat in recent_chats:
        message = chat.get("user_message", "").lower()

        for keyword in PRODUCT_KEYWORDS:
            if keyword in message:
                return message

    return None


def format_product_details(context: str):
    """
    Convert a single product block into Markdown.

    Input:
    - NovaBuds Wireless Earbuds
      Price: ₹2,999
      Bluetooth: 5.3
    """
    lines = [
        line.strip()
        for line in context.strip().splitlines()
        if line.strip()
    ]

    if not lines:
        return None, None

    first_line = lines[0]

    if not first_line.startswith("- "):
        return None, None

    product_name = first_line.replace("- ", "", 1).strip()

    details = []

    for line in lines[1:]:
        # Ignore separator lines and category titles.
        if line.startswith("---"):
            break

        if line.startswith("- "):
            break

        details.append(f"- {line}")

    reply = (
        "## 📦 Product Details\n\n"
        f"**{product_name}**\n\n"
        + "\n".join(details)
    )

    return product_name, reply


def get_feature_reply(
    context: str,
    requested_features: list[str],
    product_name: str
) -> str:
    """
    Return all requested specifications from one product block.
    """
    if "features" in requested_features:
        _, complete_reply = format_product_details(context)

        if complete_reply:
            return complete_reply

    fields = []

    for line in context.splitlines():
        clean_line = line.strip()

        if not clean_line:
            continue

        lower_line = clean_line.lower()

        if (
            "price" in requested_features
            and lower_line.startswith("price:")
        ):
            fields.append(clean_line)

        if (
            "processor" in requested_features
            and lower_line.startswith("processor:")
        ):
            fields.append(clean_line)

        if (
            "ram" in requested_features
            and lower_line.startswith("ram:")
        ):
            fields.append(clean_line)

        if (
            "storage" in requested_features
            and lower_line.startswith("storage:")
        ):
            fields.append(clean_line)

        if (
            "display" in requested_features
            and (
                lower_line.startswith("display:")
                or lower_line.startswith("resolution:")
            )
        ):
            fields.append(clean_line)

        if (
            "battery life" in requested_features
            and lower_line.startswith("battery life:")
        ):
            fields.append(clean_line)

        if (
            "battery" in requested_features
            and "battery life" not in requested_features
            and (
                lower_line.startswith("battery:")
                or lower_line.startswith("battery life:")
            )
        ):
            fields.append(clean_line)

        if (
            "bluetooth" in requested_features
            and lower_line.startswith("bluetooth:")
        ):
            fields.append(clean_line)

        if (
            "connectivity" in requested_features
            and lower_line.startswith("connectivity:")
        ):
            fields.append(clean_line)

        if (
            "camera" in requested_features
            and "camera:" in lower_line
        ):
            fields.append(clean_line)

        if (
            "charging" in requested_features
            and (
                "charging:" in lower_line
                or lower_line.startswith("port:")
            )
        ):
            fields.append(clean_line)

        if (
            "noise cancellation" in requested_features
            and lower_line.startswith("noise cancellation:")
        ):
            fields.append(clean_line)

        if (
            "water resistance" in requested_features
            and lower_line.startswith("water resistance:")
        ):
            fields.append(clean_line)

    # Remove duplicate lines while keeping order.
    unique_fields = list(dict.fromkeys(fields))

    if not unique_fields:
        feature_names = ", ".join(requested_features)

        return (
            f"I'm sorry, {feature_names} information is not "
            f"available for **{product_name}**."
        )

    formatted_fields = "\n".join(
        f"- {field}"
        for field in unique_fields
    )

    return (
        f"## 📦 {product_name}\n\n"
        f"{formatted_fields}\n\n"
        f"_Showing details for your last selected product._"
    )

def save_chat(
    email: str,
    user_message: str,
    intent: str,
    agent,
    reply_text: str,
    selected_product=None
):
    document = {
        "email": email,
        "user_message": user_message,
        "detected_intent": intent,
        "routed_agent": agent,
        "ai_response": reply_text
    }

    if selected_product:
        document["selected_product"] = selected_product

    chat_collection.insert_one(document)

# ---------------- CHAT HISTORY ----------------

@app.get("/chat-history")
def get_chat_history(
    authorization: str = Header(None)
):
    token = authorization.replace("Bearer ", "")
    email = verify_access_token(token)

    chats = list(
        chat_collection.find(
            {"email": email},
            {"_id": 0}
        ).sort("_id", -1)
    )

    return {
        "history": chats
    }


@app.delete("/chat-history")
def clear_chat_history(
    authorization: str = Header(None)
):
    token = authorization.replace("Bearer ", "")
    email = verify_access_token(token)

    chat_collection.delete_many(
        {"email": email}
    )

    return {
        "message": "Chat history cleared successfully."
    }


# ---------------- CHAT ROUTE ----------------

@app.post("/chat")
def chat(
    request: ChatRequest,
    authorization: str = Header(None)
):
    try:
        # ---------------- VALIDATION ----------------

        if not request.message or not request.message.strip():
            raise HTTPException(
                status_code=400,
                detail="Message cannot be empty."
            )

        if authorization is None:
            raise HTTPException(
                status_code=401,
                detail="Authorization token missing."
            )

        if not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=401,
                detail="Invalid authorization format."
            )

        token = authorization.replace(
            "Bearer ",
            "",
            1
        ).strip()

        email = verify_access_token(token)

        if email is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired token."
            )

        # ---------------- CURRENT MESSAGE ----------------

        user_message = request.message.strip()
        user_text = user_message.lower().strip()

        new_intent = detect_intent(user_message)

        # ---------------- PREVIOUS CHATS ----------------

        recent_chats = list(
            chat_collection
            .find({"email": email})
            .sort("_id", -1)
            .limit(5)
        )

        last_product = find_last_selected_product(
            recent_chats
        )

        memory_text = ""

        for item in reversed(recent_chats):
            previous_user_message = item.get(
                "user_message",
                ""
            )

            previous_ai_response = item.get(
                "ai_response",
                ""
            )

            memory_text += (
                f"User: {previous_user_message}\n"
                f"Assistant: {previous_ai_response}\n\n"
            )

        recent_intent = None

        if recent_chats:
            recent_intent = recent_chats[0].get(
                "detected_intent"
            )

        # ---------------- FOLLOW-UP WORDS ----------------

        follow_up_words = [
            "yes",
            "yeah",
            "yep",
            "ok",
            "okay",
            "more",
            "tell me more",
            "continue"
        ]

        technical_start_phrases = [
            "i need technical support",
            "technical support",
            "technical help",
            "login issue",
            "password issue",
            "forgot password"
        ]

        complaint_start_phrases = [
            "i want to register a complaint",
            "register complaint",
            "raise complaint",
            "new complaint",
            "i have a complaint"
        ]

        product_start_phrases = [
            "show me your products",
            "show products",
            "list products",
            "list all products",
            "available products",
            "what products are available",
            "what are your products",
            "product info",
            "product information"
        ]

        billing_start_phrases = [
            "billing",
            "billing information",
            "payment information",
            "payment issue"
        ]

        refund_start_phrases = [
            "refund",
            "refund policy",
            "return policy",
            "money back"
        ]

        explicit_new_topic = False

        # ---------------- EXPLICIT NEW TOPIC ----------------

        if any(
            phrase in user_text
            for phrase in technical_start_phrases
        ):
            intent = "Technical"
            explicit_new_topic = True

        elif any(
            phrase in user_text
            for phrase in complaint_start_phrases
        ):
            intent = "Complaint"
            explicit_new_topic = True

        elif any(
            phrase in user_text
            for phrase in product_start_phrases
        ):
            intent = "Product"
            explicit_new_topic = True

        elif any(
            phrase in user_text
            for phrase in billing_start_phrases
        ):
            intent = "Billing"
            explicit_new_topic = True

        elif any(
            phrase in user_text
            for phrase in refund_start_phrases
        ):
            intent = "Refund"
            explicit_new_topic = True

        else:
            intent = new_intent

        # A product-feature follow-up should remain in Product flow.
        requested_features = detect_requested_features(
            user_text
        )

        if (
            requested_features
            and last_product
            and recent_intent == "Product"
            and new_intent not in ["Recommendation", "Comparison"]
            and not explicit_new_topic
        ):
            intent = "Product"

        # ---------------- INTENT FLOW ----------------

        if explicit_new_topic:
            search_query = user_message
            memory_text = ""

            if intent == "Complaint":
                current_question = (
                    "The user wants to start a NEW complaint. "
                    "Do not use details from an old complaint. "
                    "Ask for the product name, a brief description "
                    "of the issue and the Order ID if available."
                )
            else:
                current_question = user_message

        elif recent_intent == "Complaint":
            intent = "Complaint"
            search_query = user_message

            current_question = f"""
Current complaint conversation:

{memory_text}

Latest user reply:

{user_message}

Instructions:
- Continue the SAME complaint flow.
- Do not switch to the Product Agent when the user gives a product name.
- If the user gives only a product name, ask what issue they are facing.
- If product and issue are known, register the complaint.
- If the latest reply contains only a number, treat it as the Order ID.
- If the Order ID is given, finalize the complaint.
- Do not show product specifications.
- Do not repeat questions already answered.
"""

        elif recent_intent == "Technical":
            intent = "Technical"
            search_query = user_message

            current_question = f"""
Current technical conversation:

{memory_text}

Latest user reply:

{user_message}

Instructions:
- Continue the SAME technical support conversation.
- Do not switch to the Product Agent when the user gives a product name.
- If the user gives only a product name, ask what technical issue they have.
- If the user gives an issue, provide troubleshooting steps.
- Ask only one question at a time.
- Do not show product specifications.
"""

        elif (
            user_text in follow_up_words
            and recent_chats
            and recent_intent
        ):
            intent = recent_intent
            search_query = user_message

            current_question = f"""
Previous conversation:

{memory_text}

Latest user reply:

{user_message}

Continue the previous conversation naturally.
Do not restart the conversation.
"""

        else:
            intent = new_intent
            search_query = user_message
            current_question = user_message

            if (
                requested_features
                and last_product
                and recent_intent == "Product"
                and new_intent not in ["Recommendation", "Comparison"]
            ):
                intent = "Product"

        # ---------------- DEBUG ----------------

        print("\n========== INTENT DEBUG ==========")
        print("User:", user_message)
        print("Detected Intent:", new_intent)
        print("Recent Intent:", recent_intent)
        print("Final Intent:", intent)
        print("Last Product:", last_product)
        print("Requested Features:", requested_features)
        print("Search Query:", search_query)
        print("==================================\n")

        # ---------------- AGENT ROUTING ----------------

        agent = route_to_agent(intent)

        # ---------------- BUILD PROMPT ----------------

        if intent in ["Refund", "Billing"]:
            context = retrieve_context(search_query)

            prompt = get_billing_prompt(
                context,
                current_question
            )

        elif intent == "Comparison":
            context = retrieve_context(user_message)

            prompt = get_comparison_prompt(
                context,
                user_message
            )

        elif intent == "Warranty":

            context = retrieve_context(user_message)

            prompt = get_warranty_prompt(
                context,
                user_message
            )
    
        elif intent == "Recommendation":

            context = retrieve_context(
                "all products"
            )

            prompt = get_recommendation_prompt(
                context,
                user_message
            )

        elif intent == "Product":

            # Follow-up such as "price" or "battery life"
            if requested_features and last_product:
                search_query = last_product
            else:
                search_query = user_message

            context = retrieve_context(search_query)

            print("\n===== PRODUCT CONTEXT =====")
            print(context)
            print("===========================\n")

            # Feature-specific follow-up.
            if requested_features and last_product:
                reply_text = get_feature_reply(
                    context=context,
                    requested_features=requested_features,
                    product_name=last_product
                )

                save_chat(
                    email=email,
                    user_message=user_message,
                    intent=intent,
                    agent=agent,
                    reply_text=reply_text,
                    selected_product=last_product
                )

                return {
                    "reply": reply_text
                }

            # A single product was found.
            product_name, direct_reply = format_product_details(
                context
            )

            if direct_reply:
                save_chat(
                    email=email,
                    user_message=user_message,
                    intent=intent,
                    agent=agent,
                    reply_text=direct_reply,
                    selected_product=product_name
                )

                return {
                    "reply": direct_reply
                }

            # Product list or general product request.
            prompt = get_product_prompt(
                context,
                user_message
            )

        elif intent == "Technical":
            context = ""

            prompt = get_technical_prompt(
                context,
                current_question
            )

        elif intent == "Complaint":
            context = ""

            prompt = get_complaint_prompt(
                context,
                current_question
            )

        else:
            context = retrieve_context(search_query)

            prompt = get_faq_prompt(
                context,
                current_question
            )

        # ---------------- CONTEXT DEBUG ----------------

        print("\n========== CONTEXT DEBUG ==========")
        print("Intent:", intent)
        print("Search Query:", search_query)
        print("Current Question:", current_question)
        print("Context:")
        print(context)
        print("===================================\n")

        # Product-list responses should not receive old product memory.
        if intent == "Product":
            final_prompt = prompt
        else:
            final_prompt = f"""
        Current Conversation Context:

        {memory_text}

        Current Question:

        {prompt}
        """

        # ---------------- LLM RESPONSE ----------------

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            temperature=0.0,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful customer support assistant "
                        "for TechNova Electronics. "
                        "Always follow the selected agent's instructions. "
                        "Use only information provided in the prompt. "
                        "Do not invent product information. "
                        "Do not show product specifications during "
                        "complaint or technical support flows. "
                        "If a complaint contains the product and issue, "
                        "register it. "
                        "If an Order ID is given after complaint "
                        "registration, finalize the complaint."
                    )
                },
                {
                    "role": "user",
                    "content": final_prompt
                }
            ]
        )

        reply_text = response.choices[0].message.content

        if not reply_text:
            reply_text = (
                "I'm sorry, I couldn't generate a response. "
                "Please try again."
            )

        # ---------------- SAVE CHAT ----------------

        save_chat(
            email=email,
            user_message=user_message,
            intent=intent,
            agent=agent,
            reply_text=reply_text
        )

        return {
            "reply": reply_text
        }

    except HTTPException:
        raise

    except Exception as error:
        print("Chat error:", str(error))

        return {
            "reply": (
                "I'm sorry, something went wrong while processing "
                "your request. Please try again."
            )
        }
