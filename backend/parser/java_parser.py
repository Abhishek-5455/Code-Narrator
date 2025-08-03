import re
from typing import List, Dict, Any, Optional

def parse_code_to_markdown(code: str) -> str:
    """Parse Java code and generate comprehensive markdown documentation."""
    doc_lines = ["# Java Code Documentation\n"]
    
    # Extract Javadoc comments
    javadoc_comments = _extract_javadoc_comments(code)
    
    # Parse package declaration
    package = _extract_package(code)
    if package:
        doc_lines.append(f"## Package: `{package}`\n")
    
    # Parse imports
    imports = _extract_imports(code)
    if imports:
        doc_lines.append("## Imports")
        for imp in imports:
            doc_lines.append(f"- `{imp}`")
        doc_lines.append("")
    
    # Parse interfaces
    interfaces = _extract_interfaces(code, javadoc_comments)
    if interfaces:
        doc_lines.append("## Interfaces")
        for interface in interfaces:
            doc_lines.extend(_format_interface(interface))
    
    # Parse classes
    classes = _extract_classes(code, javadoc_comments)
    if classes:
        doc_lines.append("## Classes")
        for cls in classes:
            doc_lines.extend(_format_class(cls))
    
    # Parse enums
    enums = _extract_enums(code, javadoc_comments)
    if enums:
        doc_lines.append("## Enums")
        for enum in enums:
            doc_lines.extend(_format_enum(enum))
    
    return "\n".join(doc_lines)

def _extract_javadoc_comments(code: str) -> Dict[int, str]:
    """Extract Javadoc comments and map them to line numbers."""
    javadoc_pattern = r'/\*\*(.*?)\*/'
    javadoc_comments = {}
    
    for match in re.finditer(javadoc_pattern, code, re.DOTALL):
        line_num = code[:match.start()].count('\n')
        # Clean up the javadoc content
        content = match.group(1)
        content = re.sub(r'^\s*\*\s?', '', content, flags=re.MULTILINE)
        javadoc_comments[line_num] = content.strip()
    
    return javadoc_comments

def _extract_package(code: str) -> Optional[str]:
    """Extract package declaration."""
    package_pattern = r'package\s+([\w.]+)\s*;'
    match = re.search(package_pattern, code)
    return match.group(1) if match else None

def _extract_imports(code: str) -> List[str]:
    """Extract import statements."""
    import_pattern = r'import\s+(?:static\s+)?([\w.*]+)\s*;'
    matches = re.finditer(import_pattern, code)
    return [match.group(0).strip() for match in matches]

def _extract_interfaces(code: str, javadoc_comments: Dict[int, str]) -> List[Dict[str, Any]]:
    """Extract interface definitions."""
    interfaces = []
    
    # Interface pattern with optional extends
    interface_pattern = r'(?:(public|private|protected)\s+)?(?:(abstract)\s+)?interface\s+(\w+)(?:\s+extends\s+([\w,\s]+))?\s*\{([^}]*(?:\{[^}]*\}[^}]*)*)\}'
    
    matches = re.finditer(interface_pattern, code, re.DOTALL)
    
    for match in matches:
        access_modifier = match.group(1)
        # abstract_modifier = match.group(2)
        interface_name = match.group(3)
        extends_clause = match.group(4)
        interface_body = match.group(5)
        
        line_num = code[:match.start()].count('\n')
        interface_doc = _find_javadoc_for_line(javadoc_comments, line_num)
        
        interface_info = {
            'name': interface_name,
            'access_modifier': access_modifier,
            'extends': [ext.strip() for ext in extends_clause.split(',')] if extends_clause else [],
            'docstring': interface_doc,
            'methods': _extract_interface_methods(interface_body)
        }
        
        interfaces.append(interface_info)
    
    return interfaces

def _extract_classes(code: str, javadoc_comments: Dict[int, str]) -> List[Dict[str, Any]]:
    """Extract class definitions."""
    classes = []
    
    # Class pattern with optional modifiers, extends, implements
    class_pattern = r'(?:(public|private|protected)\s+)?(?:(static|final|abstract)\s+)*class\s+(\w+)(?:\s+extends\s+(\w+))?(?:\s+implements\s+([\w,\s]+))?\s*\{([^}]*(?:\{[^}]*\}[^}]*)*)\}'
    
    matches = re.finditer(class_pattern, code, re.DOTALL)
    
    for match in matches:
        access_modifier = match.group(1)
        other_modifiers = match.group(2)
        class_name = match.group(3)
        extends_clause = match.group(4)
        implements_clause = match.group(5)
        class_body = match.group(6)
        
        line_num = code[:match.start()].count('\n')
        class_doc = _find_javadoc_for_line(javadoc_comments, line_num)
        
        class_info = {
            'name': class_name,
            'access_modifier': access_modifier,
            'modifiers': other_modifiers.split() if other_modifiers else [],
            'extends': extends_clause,
            'implements': [impl.strip() for impl in implements_clause.split(',')] if implements_clause else [],
            'docstring': class_doc,
            'fields': _extract_fields(class_body),
            'constructors': _extract_constructors(class_body, class_name),
            'methods': _extract_methods(class_body)
        }
        
        classes.append(class_info)
    
    return classes

def _extract_enums(code: str, javadoc_comments: Dict[int, str]) -> List[Dict[str, Any]]:
    """Extract enum definitions."""
    enums = []
    
    enum_pattern = r'(?:(public|private|protected)\s+)?enum\s+(\w+)(?:\s+implements\s+([\w,\s]+))?\s*\{([^}]*)\}'
    
    matches = re.finditer(enum_pattern, code, re.DOTALL)
    
    for match in matches:
        access_modifier = match.group(1)
        enum_name = match.group(2)
        implements_clause = match.group(3)
        enum_body = match.group(4)
        
        line_num = code[:match.start()].count('\n')
        enum_doc = _find_javadoc_for_line(javadoc_comments, line_num)
        
        # Extract enum constants
        constants = []
        # Simple enum constant pattern
        constant_pattern = r'(\w+)(?:\([^)]*\))?(?:\s*\{[^}]*\})?\s*[,;]?'
        for constant_match in re.finditer(constant_pattern, enum_body):
            constant_name = constant_match.group(1)
            if constant_name.isupper() or constant_name[0].isupper():
                constants.append(constant_name)
        
        enum_info = {
            'name': enum_name,
            'access_modifier': access_modifier,
            'implements': [impl.strip() for impl in implements_clause.split(',')] if implements_clause else [],
            'docstring': enum_doc,
            'constants': constants
        }
        
        enums.append(enum_info)
    
    return enums

def _extract_fields(class_body: str) -> List[Dict[str, Any]]:
    """Extract field declarations from class body."""
    fields = []
    
    # Field pattern: modifiers type name = value;
    field_pattern = r'(?:(public|private|protected)\s+)?(?:(static|final)\s+)*(\w+(?:<[^>]+>)?(?:\[\])*)\s+(\w+)(?:\s*=\s*([^;]+))?\s*;'
    
    matches = re.finditer(field_pattern, class_body)
    
    for match in matches:
        access_modifier = match.group(1)
        modifiers = match.group(2)
        field_type = match.group(3)
        field_name = match.group(4)
        initial_value = match.group(5)
        
        # Skip if it looks like a method call or other non-field
        if '(' in field_type or field_type in ['if', 'for', 'while', 'return', 'throw']:
            continue
        
        field_info = {
            'name': field_name,
            'type': field_type,
            'access_modifier': access_modifier,
            'modifiers': modifiers.split() if modifiers else [],
            'initial_value': initial_value.strip() if initial_value else None
        }
        
        fields.append(field_info)
    
    return fields

def _extract_constructors(class_body: str, class_name: str) -> List[Dict[str, Any]]:
    """Extract constructor definitions."""
    constructors = []
    
    # Constructor pattern
    constructor_pattern = rf'(?:(public|private|protected)\s+)?{class_name}\s*\(([^)]*)\)\s*(?:throws\s+[\w,\s]+)?\s*\{{'
    
    matches = re.finditer(constructor_pattern, class_body)
    
    for match in matches:
        access_modifier = match.group(1)
        parameters = match.group(2)
        
        constructor_info = {
            'access_modifier': access_modifier,
            'parameters': _extract_method_parameters(parameters)
        }
        
        constructors.append(constructor_info)
    
    return constructors

def _extract_methods(class_body: str) -> List[Dict[str, Any]]:
    """Extract method definitions."""
    methods = []
    
    # Method pattern
    method_pattern = r'(?:(public|private|protected)\s+)?(?:(static|final|abstract|synchronized)\s+)*(\w+(?:<[^>]+>)?(?:\[\])*)\s+(\w+)\s*\(([^)]*)\)\s*(?:throws\s+[\w,\s]+)?\s*[{;]'
    
    matches = re.finditer(method_pattern, class_body)
    
    for match in matches:
        access_modifier = match.group(1)
        modifiers = match.group(2)
        return_type = match.group(3)
        method_name = match.group(4)
        parameters = match.group(5)
        
        # Skip constructors and common keywords
        if method_name in ['if', 'for', 'while', 'return', 'throw', 'new']:
            continue
        
        method_info = {
            'name': method_name,
            'return_type': return_type,
            'access_modifier': access_modifier,
            'modifiers': modifiers.split() if modifiers else [],
            'parameters': _extract_method_parameters(parameters)
        }
        
        methods.append(method_info)
    
    return methods

def _extract_interface_methods(interface_body: str) -> List[Dict[str, Any]]:
    """Extract method declarations from interface."""
    methods = []
    
    # Interface method pattern (no body, just declaration)
    method_pattern = r'(?:(public|private)\s+)?(?:(static|default)\s+)*(\w+(?:<[^>]+>)?(?:\[\])*)\s+(\w+)\s*\(([^)]*)\)\s*(?:throws\s+[\w,\s]+)?\s*[;{]'
    
    matches = re.finditer(method_pattern, interface_body)
    
    for match in matches:
        access_modifier = match.group(1) or 'public'  # Interface methods are public by default
        modifiers = match.group(2)
        return_type = match.group(3)
        method_name = match.group(4)
        parameters = match.group(5)
        
        method_info = {
            'name': method_name,
            'return_type': return_type,
            'access_modifier': access_modifier,
            'modifiers': modifiers.split() if modifiers else [],
            'parameters': _extract_method_parameters(parameters)
        }
        
        methods.append(method_info)
    
    return methods

def _extract_method_parameters(parameters: str) -> List[Dict[str, Any]]:
    """Extract method parameters."""
    if not parameters.strip():
        return []
    
    param_list = []
    # Split by comma, but be careful of generics
    param_parts = re.split(r',(?![^<]*>)', parameters)
    
    for param in param_parts:
        param = param.strip()
        if not param:
            continue
        
        # Extract parameter type and name
        param_match = re.match(r'(?:(final)\s+)?(\w+(?:<[^>]+>)?(?:\[\])*)\s+(\w+)', param)
        if param_match:
            is_final = param_match.group(1) is not None
            param_type = param_match.group(2)
            param_name = param_match.group(3)
            
            param_info = {
                'name': param_name,
                'type': param_type,
                'is_final': is_final
            }
            
            param_list.append(param_info)
    
    return param_list

def _find_javadoc_for_line(javadoc_comments: Dict[int, str], line_num: int) -> Optional[str]:
    """Find Javadoc comment that precedes the given line."""
    # Look for Javadoc in the few lines before
    for i in range(max(0, line_num - 10), line_num):
        if i in javadoc_comments:
            return javadoc_comments[i]
    return None

def _format_interface(interface: Dict[str, Any]) -> List[str]:
    """Format interface information as markdown."""
    lines = [f"### Interface: `{interface['name']}`"]
    
    if interface['access_modifier']:
        lines.append(f"**Access:** {interface['access_modifier']}")
    
    if interface['extends']:
        lines.append(f"**Extends:** {', '.join(f'`{ext}`' for ext in interface['extends'])}")
    
    if interface['docstring']:
        lines.append(f"**Description:** {interface['docstring']}")
    
    if interface['methods']:
        lines.append("**Methods:**")
        for method in interface['methods']:
            lines.extend(_format_method(method, is_interface=True))
    
    lines.append("")
    return lines

def _format_class(cls: Dict[str, Any]) -> List[str]:
    """Format class information as markdown."""
    lines = [f"### Class: `{cls['name']}`"]
    
    if cls['access_modifier']:
        lines.append(f"**Access:** {cls['access_modifier']}")
    
    if cls['modifiers']:
        lines.append(f"**Modifiers:** {', '.join(cls['modifiers'])}")
    
    if cls['extends']:
        lines.append(f"**Extends:** `{cls['extends']}`")
    
    if cls['implements']:
        lines.append(f"**Implements:** {', '.join(f'`{impl}`' for impl in cls['implements'])}")
    
    if cls['docstring']:
        lines.append(f"**Description:** {cls['docstring']}")
    
    if cls['fields']:
        lines.append("**Fields:**")
        for field in cls['fields']:
            modifiers_str = ' '.join(field['modifiers']) + ' ' if field['modifiers'] else ''
            access_str = field['access_modifier'] + ' ' if field['access_modifier'] else ''
            value_str = f" = `{field['initial_value']}`" if field['initial_value'] else ""
            lines.append(f"- {access_str}{modifiers_str}`{field['name']}`: {field['type']}{value_str}")
    
    if cls['constructors']:
        lines.append("**Constructors:**")
        for i, constructor in enumerate(cls['constructors']):
            access_str = constructor['access_modifier'] + ' ' if constructor['access_modifier'] else ''
            lines.append(f"#### Constructor {i+1}: {access_str}`{cls['name']}`")
            if constructor['parameters']:
                lines.append("**Parameters:**")
                for param in constructor['parameters']:
                    final_str = 'final ' if param.get('is_final', False) else ''
                    lines.append(f"- {final_str}`{param['name']}`: {param['type']}")
            lines.append("")
    
    if cls['methods']:
        lines.append("**Methods:**")
        for method in cls['methods']:
            lines.extend(_format_method(method))
    
    lines.append("")
    return lines

def _format_enum(enum: Dict[str, Any]) -> List[str]:
    """Format enum information as markdown."""
    lines = [f"### Enum: `{enum['name']}`"]
    
    if enum['access_modifier']:
        lines.append(f"**Access:** {enum['access_modifier']}")
    
    if enum['implements']:
        lines.append(f"**Implements:** {', '.join(f'`{impl}`' for impl in enum['implements'])}")
    
    if enum['docstring']:
        lines.append(f"**Description:** {enum['docstring']}")
    
    if enum['constants']:
        lines.append("**Constants:**")
        for constant in enum['constants']:
            lines.append(f"- `{constant}`")
    
    lines.append("")
    return lines

def _format_method(method: Dict[str, Any], is_interface: bool = False) -> List[str]:
    """Format method information as markdown."""
    prefix = "####" 
    modifiers_str = ' '.join(method['modifiers']) + ' ' if method['modifiers'] else ''
    access_str = method['access_modifier'] + ' ' if method['access_modifier'] else ''
    
    lines = [f"{prefix} Method: {access_str}{modifiers_str}`{method['name']}`"]
    
    if not is_interface:
        lines.append(f"**Returns:** `{method['return_type']}`")
    
    if method['parameters']:
        lines.append("**Parameters:**")
        for param in method['parameters']:
            final_str = 'final ' if param.get('is_final', False) else ''
            lines.append(f"- {final_str}`{param['name']}`: {param['type']}")
    
    lines.append("")
    return lines
