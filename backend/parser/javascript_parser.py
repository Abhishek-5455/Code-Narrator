import re
from typing import List, Dict, Any, Optional

def parse_code_to_markdown(code: str) -> str:
    """Parse JavaScript code and generate comprehensive markdown documentation."""
    doc_lines = ["# JavaScript Code Documentation\n"]
    
    # Remove comments for parsing (but keep JSDoc)
    cleaned_code, jsdoc_comments = _extract_jsdoc_comments(code)
    
    # Parse imports
    imports = _extract_imports(code)
    if imports:
        doc_lines.append("## Imports")
        for imp in imports:
            doc_lines.append(f"- `{imp}`")
        doc_lines.append("")
    
    # Parse exports
    exports = _extract_exports(code)
    if exports:
        doc_lines.append("## Exports")
        for exp in exports:
            doc_lines.append(f"- `{exp}`")
        doc_lines.append("")
    
    # Parse variables
    variables = _extract_variables(code)
    if variables:
        doc_lines.append("## Variables")
        for var in variables:
            doc_lines.append(f"- **{var['name']}** ({var['type']}): `{var['value']}`")
        doc_lines.append("")
    
    # Parse classes
    classes = _extract_classes(code, jsdoc_comments)
    if classes:
        doc_lines.append("## Classes")
        for cls in classes:
            doc_lines.extend(_format_class(cls))
    
    # Parse standalone functions
    functions = _extract_functions(code, jsdoc_comments)
    if functions:
        doc_lines.append("## Functions")
        for func in functions:
            doc_lines.extend(_format_function(func))
    
    return "\n".join(doc_lines)

def _extract_jsdoc_comments(code: str) -> tuple[str, Dict[int, str]]:
    """Extract JSDoc comments and return cleaned code with JSDoc mapping."""
    jsdoc_pattern = r'/\*\*(.*?)\*/'
    jsdoc_comments = {}
    
    def replace_jsdoc(match):
        line_num = code[:match.start()].count('\n')
        jsdoc_comments[line_num] = match.group(1).strip()
        return ''
    
    cleaned_code = re.sub(jsdoc_pattern, replace_jsdoc, code, flags=re.DOTALL)
    return cleaned_code, jsdoc_comments

def _extract_imports(code: str) -> List[str]:
    """Extract import statements."""
    imports = []
    
    # ES6 imports
    import_patterns = [
        r'import\s+\{([^}]+)\}\s+from\s+[\'"]([^\'"]+)[\'"]',  # Named imports
        r'import\s+([^,\s]+)\s+from\s+[\'"]([^\'"]+)[\'"]',     # Default imports
        r'import\s+\*\s+as\s+(\w+)\s+from\s+[\'"]([^\'"]+)[\'"]',  # Namespace imports
        r'import\s+[\'"]([^\'"]+)[\'"]',                        # Side effect imports
        r'const\s+\{([^}]+)\}\s*=\s*require\([\'"]([^\'"]+)[\'"]\)',  # CommonJS destructuring
        r'const\s+(\w+)\s*=\s*require\([\'"]([^\'"]+)[\'"]\)',  # CommonJS require
    ]
    
    for pattern in import_patterns:
        matches = re.finditer(pattern, code)
        for match in matches:
            if len(match.groups()) == 2:
                if 'require' in match.group(0):
                    imports.append(f"const {match.group(1)} = require('{match.group(2)}')")
                else:
                    imports.append(match.group(0).strip())
            else:
                imports.append(match.group(0).strip())
    
    return imports

def _extract_exports(code: str) -> List[str]:
    """Extract export statements."""
    exports = []
    
    export_patterns = [
        r'export\s+default\s+\w+',
        r'export\s+\{([^}]+)\}',
        r'export\s+(?:const|let|var|function|class)\s+(\w+)',
        r'module\.exports\s*=\s*([^;]+)',
    ]
    
    for pattern in export_patterns:
        matches = re.finditer(pattern, code)
        for match in matches:
            exports.append(match.group(0).strip())
    
    return exports

def _extract_variables(code: str) -> List[Dict[str, Any]]:
    """Extract variable declarations."""
    variables = []
    
    # Match const, let, var declarations
    var_pattern = r'(const|let|var)\s+(\w+)\s*=\s*([^;,\n]+)'
    matches = re.finditer(var_pattern, code)
    
    for match in matches:
        var_type, name, value = match.groups()
        variables.append({
            'name': name,
            'type': var_type,
            'value': value.strip()
        })
    
    return variables

def _extract_classes(code: str, jsdoc_comments: Dict[int, str]) -> List[Dict[str, Any]]:
    """Extract class definitions."""
    classes = []
    
    # Class pattern
    class_pattern = r'class\s+(\w+)(?:\s+extends\s+(\w+))?\s*\{([^}]*(?:\{[^}]*\}[^}]*)*)\}'
    matches = re.finditer(class_pattern, code, re.DOTALL)
    
    for match in matches:
        class_name = match.group(1)
        parent_class = match.group(2)
        class_body = match.group(3)
        
        # Find JSDoc for this class
        line_num = code[:match.start()].count('\n')
        class_doc = _find_jsdoc_for_line(jsdoc_comments, line_num)
        
        class_info = {
            'name': class_name,
            'parent': parent_class,
            'docstring': class_doc,
            'methods': [],
            'properties': []
        }
        
        # Extract methods from class body
        method_pattern = r'(?:(static)\s+)?(\w+)\s*\([^)]*\)\s*\{[^}]*(?:\{[^}]*\}[^}]*)*\}'
        method_matches = re.finditer(method_pattern, class_body, re.DOTALL)
        
        for method_match in method_matches:
            is_static = method_match.group(1) is not None
            method_name = method_match.group(2)
            
            # Skip constructor in methods list, handle separately
            if method_name == 'constructor':
                continue
                
            method_info = {
                'name': method_name,
                'is_static': is_static,
                'docstring': None,  # Could be enhanced to find method JSDoc
                'parameters': _extract_function_params(method_match.group(0))
            }
            class_info['methods'].append(method_info)
        
        # Extract constructor
        constructor_pattern = r'constructor\s*\(([^)]*)\)\s*\{'
        constructor_match = re.search(constructor_pattern, class_body)
        if constructor_match:
            class_info['constructor'] = {
                'parameters': _extract_function_params(constructor_match.group(0))
            }
        
        classes.append(class_info)
    
    return classes

def _extract_functions(code: str, jsdoc_comments: Dict[int, str]) -> List[Dict[str, Any]]:
    """Extract function definitions."""
    functions = []
    
    # Function patterns
    patterns = [
        r'function\s+(\w+)\s*\(([^)]*)\)\s*\{',  # Regular functions
        r'const\s+(\w+)\s*=\s*(?:async\s+)?\([^)]*\)\s*=>\s*[{(]',  # Arrow functions assigned to const
        r'(?:let|var)\s+(\w+)\s*=\s*(?:async\s+)?function[^{]*\{',  # Function expressions
    ]
    
    for pattern in patterns:
        matches = re.finditer(pattern, code)
        for match in matches:
            func_name = match.group(1)
            line_num = code[:match.start()].count('\n')
            func_doc = _find_jsdoc_for_line(jsdoc_comments, line_num)
            
            # Extract full function for parameter analysis
            full_func = _extract_full_function(code, match.start())
            
            func_info = {
                'name': func_name,
                'docstring': func_doc,
                'parameters': _extract_function_params(full_func),
                'is_async': 'async' in match.group(0),
                'is_arrow': '=>' in match.group(0)
            }
            functions.append(func_info)
    
    return functions

def _extract_full_function(code: str, start_pos: int) -> str:
    """Extract the full function definition starting from start_pos."""
    brace_count = 0
    paren_count = 0
    in_function = False
    
    for i, char in enumerate(code[start_pos:], start_pos):
        if char == '{':
            brace_count += 1
            in_function = True
        elif char == '}':
            brace_count -= 1
            if in_function and brace_count == 0:
                return code[start_pos:i+1]
    
    # For arrow functions without braces
    if '=>' in code[start_pos:start_pos+100]:
        # Find the end of the arrow function
        for i, char in enumerate(code[start_pos:], start_pos):
            if char in [';', '\n'] and paren_count == 0:
                return code[start_pos:i]
    
    return code[start_pos:start_pos+200]  # Fallback

def _extract_function_params(func_def: str) -> List[Dict[str, Any]]:
    """Extract function parameters."""
    param_pattern = r'\(([^)]*)\)'
    match = re.search(param_pattern, func_def)
    if not match:
        return []
    
    params_str = match.group(1).strip()
    if not params_str:
        return []
    
    parameters = []
    # Split by comma, but be careful of destructuring
    param_parts = re.split(r',(?![^{[]*[}\]])', params_str)
    
    for param in param_parts:
        param = param.strip()
        if not param:
            continue
        
        # Check for default values
        if '=' in param:
            name, default = param.split('=', 1)
            name = name.strip()
            default = default.strip()
        else:
            name = param
            default = None
        
        # Extract parameter name (handle destructuring)
        if name.startswith('{') or name.startswith('['):
            param_name = name  # Keep destructuring syntax
        else:
            param_name = re.match(r'(\w+)', name)
            param_name = param_name.group(1) if param_name else name
        
        parameters.append({
            'name': param_name,
            'default': default,
            'is_destructured': name.startswith(('{', '['))
        })
    
    return parameters

def _find_jsdoc_for_line(jsdoc_comments: Dict[int, str], line_num: int) -> Optional[str]:
    """Find JSDoc comment that precedes the given line."""
    # Look for JSDoc in the few lines before
    for i in range(max(0, line_num - 5), line_num):
        if i in jsdoc_comments:
            return jsdoc_comments[i]
    return None

def _format_class(cls: Dict[str, Any]) -> List[str]:
    """Format class information as markdown."""
    lines = [f"### Class: `{cls['name']}`"]
    
    if cls['parent']:
        lines.append(f"**Extends:** `{cls['parent']}`")
    
    if cls['docstring']:
        lines.append(f"**Description:** {cls['docstring']}")
    
    if 'constructor' in cls:
        lines.append("**Constructor:**")
        if cls['constructor']['parameters']:
            for param in cls['constructor']['parameters']:
                param_str = f"- `{param['name']}`"
                if param['default']:
                    param_str += f" = `{param['default']}`"
                lines.append(param_str)
        else:
            lines.append("- No parameters")
    
    if cls['methods']:
        lines.append("**Methods:**")
        for method in cls['methods']:
            static_prefix = "static " if method['is_static'] else ""
            lines.append(f"#### {static_prefix}Method: `{method['name']}`")
            if method['parameters']:
                lines.append("**Parameters:**")
                for param in method['parameters']:
                    param_str = f"- `{param['name']}`"
                    if param['default']:
                        param_str += f" = `{param['default']}`"
                    lines.append(param_str)
            if method['docstring']:
                lines.append(f"**Description:** {method['docstring']}")
            lines.append("")
    
    lines.append("")
    return lines

def _format_function(func: Dict[str, Any]) -> List[str]:
    """Format function information as markdown."""
    async_prefix = "async " if func.get('is_async', False) else ""
    arrow_suffix = " (arrow function)" if func.get('is_arrow', False) else ""
    lines = [f"### {async_prefix}Function: `{func['name']}`{arrow_suffix}"]
    
    if func['parameters']:
        lines.append("**Parameters:**")
        for param in func['parameters']:
            param_str = f"- `{param['name']}`"
            if param['default']:
                param_str += f" = `{param['default']}`"
            if param.get('is_destructured', False):
                param_str += " (destructured)"
            lines.append(param_str)
    
    if func['docstring']:
        lines.append(f"**Description:** {func['docstring']}")
    
    lines.append("")
    return lines 