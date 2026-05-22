# Import all supported languages tree sitter
import tree_sitter_python as tspy
import tree_sitter_cpp as tscpp
import tree_sitter_c as tsc
import tree_sitter_javascript as tsjs
import tree_sitter_typescript as tsts
import tree_sitter_java as tsjava
import tree_sitter_go as tsgo

from tree_sitter import Parser, Language

LANGUAGE_MAP = {
    ".py": {"grammar": tspy, "function_node": "function_definition", "class_node": "class_definition"},
    ".cpp": {"grammar": tscpp, "function_node": "function_definition", "class_node": "class_specifier"},
    ".hpp": {"grammar": tscpp, "function_node": "function_definition", "class_node": "class_specifier"},
    ".c": {"grammar": tsc, "function_node": "function_definition", "class_node": None},
    ".js": {"grammar": tsjs, "function_node": ["function_declaration", "method_definition"], "class_node": "class_declaration"},
    ".ts": {"grammar": tsts, "function_node": ["function_declaration", "method_definition"], "class_node": "class_declaration"},
    ".java": {"grammar": tsjava, "function_node": "method_declaration", "class_node": "class_declaration"},
    ".go": {"grammar": tsgo, "function_node": "function_declaration", "class_node": None},
    ".ipynb": {"grammar": None, "function_node": None, "class_node": None}
}

def Python_Parser(file_path, source_code, file_extension):
    if file_extension == ".ipynb":
    # handle notebook separately
        return
    language_grammar = LANGUAGE_MAP[file_extension]["grammar"]
    # Handle .ts specially - no .language() methode for its grammar
    if file_extension == ".ts":
        lang = Language(language_grammar.language_typescript())
    else:
        lang = Language(language_grammar.language())

    parser = Parser(lang)
    tree = parser.parse(bytes(source_code, "utf8"))
    root_node = tree.root_node
    function_lst = []
    Find_Functions(file_path, root_node, function_lst, file_extension)
    for function in function_lst:
        function_metadata = Function_Metadata_Creator(function[0], function[1])
        for k,v in function_metadata.items():
            print(f"{k}: {v}")


def Find_Functions(file_path, root_node, function_lst, file_extension):
    if file_extension == ".py":
        return
    for child in root_node.children:
        function_node = LANGUAGE_MAP[file_extension]["function_node"]
        # Check whether function_node value a list or string (list for .ts and .js)
        if isinstance(function_node, list):
            is_function = child.type in function_node
        else:
            is_function = child.type == function_node

        if is_function:
            function_name = Get_Function_Name(child)
            class_name = None
            if child.parent.parent and child.parent.parent.type == LANGUAGE_MAP[file_extension]["class_node"]:
                class_name = child.parent.parent.child_by_field_name("name").text.decode("utf-8")
            full_name = f"{file_path}::{class_name}.{function_name}" if class_name else f"{file_path}::.{function_name}"
            function_lst.append((child, full_name))
        Find_Functions(file_path, child, function_lst, file_extension)


def Function_Metadata_Creator(function_node, function_header):
    startLine = function_node.start_point[0]
    endLine = function_node.end_point[0]
    bodyText = function_node.text.decode("utf-8")
    
    return {
        "function_name": function_header,
        "start_line": startLine,
        "end_line": endLine,
        "function_content": bodyText
    }


def Get_Function_Name(node):
    # Name handling for most languages
    name_node = node.child_by_field_name("name")
    if name_node:
        return name_node.text.decode("utf-8")

    # Name handling for C++
    declarator = node.child_by_field_name("declarator")
    if declarator:
        cpp_function_name = declarator.child_by_field_name("declarator").text.decode("utf-8")
        return cpp_function_name
