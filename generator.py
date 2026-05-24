import anthropic
from dotenv import load_dotenv
import os

load_dotenv()
client = anthropic.Anthropic()


def Dict_To_Context_String_Converter(reranked_function_list):
    context_string = ""
    for idx, function in enumerate(reranked_function_list):
        order = idx + 1
        file_name = os.path.basename(function["function_name"].split("::")[0])
        func_part = function["function_name"].split("::")[-1].lstrip(".")
        clean_name = f"{file_name}::{func_part}"
        context_string += f"""
--- FUNCTION {order} ---
Function Name: {clean_name}
Code:
{function["code"]}
Start Line: {function['start_line']}
End Line: {function["end_line"]}

"""
    return context_string


def Build_User_Prompt(user_query, context_string):
    user_prompt = f"User Query: {user_query}\nContext:\n{context_string}"
    return user_prompt


def Ask_To_LLM(content_messages):
    system_prompt = """ You are helpful legacy code explainer. The user will ask you some question about their codebase.
Related functions about question will be provided to you. You will answer the user question only in the scope of provided function information.
You will not use your prior knowledge. If you cannot find any answer according to given information then say "I do not know".
For each answer also provide citation. When citing, always mention the file name and function name, not just the function number.
Give the user from which function you get this result. Respond in the same language as the user.
"""

    llm_message = client.messages.create(
        model = "claude-haiku-4-5",
        max_tokens = 1000,
        system = system_prompt,
        messages = content_messages
    )

    return llm_message.content[0].text


def Chat(user_prompt, content_messages):
    content_messages.append({"role": "user", "content": user_prompt})

    if len(content_messages) > 10:
        content_messages = content_messages[-10:]  # son 10 mesajı tut

    llm_response = Ask_To_LLM(content_messages)
    content_messages.append({"role": "assistant", "content": llm_response})

    return llm_response, content_messages