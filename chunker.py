# Import all supported languages tree sitter
import tree_sitter_python as tspython
import tree_sitter_cpp as tscpp
import tree_sitter_javascript as tsjavascript

from tree_sitter import Parser, Language

LANGUAGE_MAP = {
    ".py": tspython,
    ".cpp": tscpp,
    ".js": tsjavascript,
}

def Python_Parser(source_code, file_extension):
    language_grammer = LANGUAGE_MAP[file_extension]
    lang = Language(language_grammer.language())
    parser = Parser(lang)
    tree = parser.parse(bytes(source_code, "utf8"))
    root_node = tree.root_node
    function_lst = []
    Find_Functions(root_node, function_lst)
    for function in function_lst:
        print(function)

def Find_Functions(root_node, function_lst):
    for child in root_node.children:
        if child.type == "function_definition":
            function_name = child.child_by_field_name("name").text.decode("utf-8")
            class_name = None
            if child.parent.parent and child.parent.parent.type == "class_definition":
                class_name = child.parent.parent.child_by_field_name("name").text.decode("utf-8")
            full_name = f"{class_name}.{function_name}" if class_name else function_name
            function_lst.append((child, full_name))
        Find_Functions(child, function_lst)