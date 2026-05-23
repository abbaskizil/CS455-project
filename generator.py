def Dict_To_Context_String_Converter(reranked_function_list):
    context_string = ""
    for idx, function in enumerate(reranked_function_list):
        order = idx + 1
        context_string += f"""
--- FUNCTION {order} ---
Function Name: {function["function_name"]}
Code:
{function["code"]}
Start Line: {function['start_line']}
End Line: {function["end_line"]}

"""
    return context_string
