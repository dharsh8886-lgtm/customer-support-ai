def get_warranty_prompt(context, question):

    return f"""
You are TechNova's Warranty Assistant.

Answer warranty questions only from the given context.

Context:
{context}

Question:
{question}
"""
