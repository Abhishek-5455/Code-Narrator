import ast
# import re
from typing import List, Dict, Any  #, Optional

# import markdown2

def parse_code_to_markdown(code: str) -> str:
    """Parse Python code and generate comprehensive markdown documentation."""
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return f"# Syntax Error\n\nFailed to parse Python code: {str(e)}\n"
    
    doc_lines = ["# Python Code Documentation\n"]
    
    # Parse module-level docstring
    module_docstring = ast.get_docstring(tree)
    if module_docstring:
        doc_lines.append("## Module Description")
        doc_lines.append(f"{module_docstring}\n")
    
    # Parse imports
    imports = _extract_imports(tree)
    if imports:
        doc_lines.append("## Imports")
        for imp in imports:
            doc_lines.append(f"- `{imp}`")
        doc_lines.append("")
    
    # Parse global variables and constants
    globals_vars = _extract_global_variables(tree)
    if globals_vars:
        doc_lines.append("## Global Variables")
        for var in globals_vars:
            doc_lines.append(f"- **{var['name']}**: {var['type']} = `{var['value']}`")
        doc_lines.append("")
    
    # Parse classes
    classes = _extract_classes(tree)
    if classes:
        doc_lines.append("## Classes")
        for cls in classes:
            doc_lines.extend(_format_class(cls))
    
    # Parse standalone functions (not in classes)
    functions = _extract_standalone_functions(tree)
    if functions:
        doc_lines.append("## Functions")
        for func in functions:
            doc_lines.extend(_format_function(func))
    
    return "\n".join(doc_lines)

def _extract_imports(tree: ast.AST) -> List[str]:
    """Extract import statements from the AST."""
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.asname:
                    imports.append(f"import {alias.name} as {alias.asname}")
                else:
                    imports.append(f"import {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                if alias.name == "*":
                    imports.append(f"from {module} import *")
                elif alias.asname:
                    imports.append(f"from {module} import {alias.name} as {alias.asname}")
                else:
                    imports.append(f"from {module} import {alias.name}")
    return imports

def _extract_global_variables(tree: ast.AST) -> List[Dict[str, Any]]:
    """Extract global variables and constants."""
    variables = []
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    var_info = {
                        'name': target.id,
                        'type': _get_type_annotation(node),
                        'value': _get_value_repr(node.value)
                    }
                    variables.append(var_info)
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            var_info = {
                'name': node.target.id,
                'type': _get_annotation_string(node.annotation),
                'value': _get_value_repr(node.value) if node.value else "Not assigned"
            }
            variables.append(var_info)
    return variables

def _extract_classes(tree: ast.AST) -> List[Dict[str, Any]]:
    """Extract class definitions with their methods and attributes."""
    classes = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            class_info = {
                'name': node.name,
                'docstring': ast.get_docstring(node),
                'bases': [_get_annotation_string(base) for base in node.bases],
                'decorators': [_get_annotation_string(dec) for dec in node.decorator_list],
                'methods': [],
                'attributes': []
            }
            
            # Extract methods and attributes
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    method_info = _extract_function_info(item)
                    method_info['is_method'] = True
                    class_info['methods'].append(method_info)
                elif isinstance(item, ast.Assign):
                    for target in item.targets:
                        if isinstance(target, ast.Name):
                            attr_info = {
                                'name': target.id,
                                'type': _get_type_annotation(item),
                                'value': _get_value_repr(item.value)
                            }
                            class_info['attributes'].append(attr_info)
            
            classes.append(class_info)
    return classes

def _extract_standalone_functions(tree: ast.AST) -> List[Dict[str, Any]]:
    """Extract standalone functions (not class methods)."""
    functions = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            func_info = _extract_function_info(node)
            func_info['is_method'] = False
            functions.append(func_info)
    return functions

def _extract_function_info(node: ast.FunctionDef | ast.AsyncFunctionDef) -> Dict[str, Any]:
    """Extract detailed information about a function."""
    return {
        'name': node.name,
        'docstring': ast.get_docstring(node),
        'arguments': _extract_function_args(node),
        'return_type': _get_annotation_string(node.returns) if node.returns else None,
        'decorators': [_get_annotation_string(dec) for dec in node.decorator_list],
        'is_async': isinstance(node, ast.AsyncFunctionDef)
    }

def _extract_function_args(node: ast.FunctionDef | ast.AsyncFunctionDef) -> List[Dict[str, Any]]:
    """Extract function arguments with type hints and defaults."""
    args = []
    defaults = node.args.defaults
    defaults_offset = len(node.args.args) - len(defaults)
    
    for i, arg in enumerate(node.args.args):
        arg_info = {
            'name': arg.arg,
            'type': _get_annotation_string(arg.annotation) if arg.annotation else None,
            'default': None
        }
        
        # Check if this argument has a default value
        if i >= defaults_offset:
            default_index = i - defaults_offset
            arg_info['default'] = _get_value_repr(defaults[default_index])
        
        args.append(arg_info)
    
    # Handle *args
    if node.args.vararg:
        args.append({
            'name': f"*{node.args.vararg.arg}",
            'type': _get_annotation_string(node.args.vararg.annotation) if node.args.vararg.annotation else None,
            'default': None
        })
    
    # Handle **kwargs
    if node.args.kwarg:
        args.append({
            'name': f"**{node.args.kwarg.arg}",
            'type': _get_annotation_string(node.args.kwarg.annotation) if node.args.kwarg.annotation else None,
            'default': None
        })
    
    return args

def _get_annotation_string(annotation) -> str:
    """Convert an AST annotation to a string representation."""
    if annotation is None:
        return "Any"
    return ast.unparse(annotation)

def _get_type_annotation(node) -> str:
    """Get type annotation from a node."""
    if hasattr(node, 'annotation') and node.annotation:
        return _get_annotation_string(node.annotation)
    return "Any"

def _get_value_repr(node) -> str:
    """Get string representation of a value node."""
    if node is None:
        return "None"
    try:
        return ast.unparse(node)
    except Exception:
        return str(type(node).__name__)

def _format_class(cls: Dict[str, Any]) -> List[str]:
    """Format class information as markdown."""
    lines = [f"### Class: `{cls['name']}`"]
    
    if cls['bases']:
        lines.append(f"**Inherits from:** {', '.join(f'`{base}`' for base in cls['bases'])}")
    
    if cls['decorators']:
        lines.append(f"**Decorators:** {', '.join(f'`@{dec}`' for dec in cls['decorators'])}")
    
    if cls['docstring']:
        lines.append(f"**Description:** {cls['docstring']}")
    
    if cls['attributes']:
        lines.append("**Attributes:**")
        for attr in cls['attributes']:
            default_text = f" = `{attr['value']}`" if attr['value'] != "None" else ""
            lines.append(f"- `{attr['name']}`: {attr['type']}{default_text}")
    
    if cls['methods']:
        lines.append("**Methods:**")
        for method in cls['methods']:
            lines.extend(_format_function(method, is_method=True))
    
    lines.append("")
    return lines

def _format_function(func: Dict[str, Any], is_method: bool = False) -> List[str]:
    """Format function information as markdown."""
    prefix = "####" if is_method else "###"
    async_prefix = "async " if func.get('is_async', False) else ""
    lines = [f"{prefix} {async_prefix}Function: `{func['name']}`"]
    
    if func['decorators']:
        lines.append(f"**Decorators:** {', '.join(f'`@{dec}`' for dec in func['decorators'])}")
    
    if func['arguments']:
        lines.append("**Arguments:**")
        for arg in func['arguments']:
            arg_str = f"- `{arg['name']}`"
            if arg['type']:
                arg_str += f": {arg['type']}"
            if arg['default']:
                arg_str += f" = `{arg['default']}`"
            lines.append(arg_str)
    
    if func['return_type']:
        lines.append(f"**Returns:** {func['return_type']}")
    
    if func['docstring']:
        lines.append(f"**Description:** {func['docstring']}")
    
    lines.append("")
    return lines
