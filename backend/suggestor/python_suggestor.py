import re
import ast

def suggest_refactor(code: str) -> list:
    suggestions = []
    lines = code.split('\n')
    
    # Code smell and best practice checks
    suggestions.extend(_check_code_smells(code, lines))
    
    # Naming convention checks
    suggestions.extend(_check_naming_conventions(code, lines))
    
    # Security and performance suggestions
    suggestions.extend(_check_security_performance(code, lines))
    
    # Spelling mistakes in comments and strings
    suggestions.extend(_check_spelling_mistakes(code, lines))
    
    # AST-based checks
    try:
        tree = ast.parse(code)
        suggestions.extend(_check_ast_issues(tree))
    except SyntaxError:
        suggestions.append("⚠️ Syntax error detected - code cannot be parsed")
    
    return suggestions

def _check_code_smells(code: str, lines: list) -> list:
    suggestions = []
    
    for line_num, line in enumerate(lines, 1):
        # Basic code smells
        if "==" in line and "None" in line:
            suggestions.append(f"🔧 Line {line_num}: Use 'is None' instead of '== None' for None comparisons")
        
        if "!=" in line and "None" in line:
            suggestions.append(f"🔧 Line {line_num}: Use 'is not None' instead of '!= None' for None comparisons")
        
        if "print(" in line:
            suggestions.append(f"🚫 Line {line_num}: Avoid using print statements in production code - use logging instead")
        
        # Long lines
        if len(line) > 100:
            suggestions.append(f"📏 Line {line_num}: Line is too long ({len(line)} chars) - consider breaking it down")
        
        # Multiple imports on one line
        if re.search(r'import\s+\w+\s*,', line):
            suggestions.append(f"📦 Line {line_num}: Use separate import statements for better readability")
        
        # Bare except clauses
        if re.search(r'except\s*:', line):
            suggestions.append(f"⚠️ Line {line_num}: Avoid bare 'except:' clauses - specify exception types")
        
        # Mutable default arguments
        if re.search(r'def\s+\w+\([^)]*=\s*\[\]', line):
            suggestions.append(f"🐛 Line {line_num}: Avoid mutable default arguments (list) - use None instead")
        
        if re.search(r'def\s+\w+\([^)]*=\s*\{\}', line):
            suggestions.append(f"🐛 Line {line_num}: Avoid mutable default arguments (dict) - use None instead")
        
        # Global variables
        if re.search(r'^global\s+\w+', line):
            suggestions.append(f"🌐 Line {line_num}: Avoid using global variables - consider class attributes or function parameters")
    
    return suggestions

def _check_naming_conventions(code: str, lines: list) -> list:
    suggestions = []
    
    for line_num, line in enumerate(lines, 1):
        # Function names should be snake_case
        func_matches = re.findall(r'def\s+([A-Z]\w*)', line)
        for func in func_matches:
            suggestions.append(f"🐍 Line {line_num}: Function '{func}' should use snake_case naming convention")
        
        # Class names should be PascalCase
        class_matches = re.findall(r'class\s+([a-z]\w*)', line)
        for cls in class_matches:
            suggestions.append(f"🏗️ Line {line_num}: Class '{cls}' should use PascalCase naming convention")
        
        # Constants should be UPPER_CASE
        const_matches = re.findall(r'^([a-z]\w*)\s*=\s*[\'\"]\w+[\'\"]\s*$', line)
        for const in const_matches:
            suggestions.append(f"🔢 Line {line_num}: Constant '{const}' should use UPPER_CASE naming convention")
    
    return suggestions

def _check_security_performance(code: str, lines: list) -> list:
    suggestions = []
    
    for line_num, line in enumerate(lines, 1):
        # Security issues
        if 'eval(' in line:
            suggestions.append(f"🔒 Line {line_num}: Avoid using eval() - it's a security risk")
        
        if 'exec(' in line:
            suggestions.append(f"🔒 Line {line_num}: Avoid using exec() - it's a security risk")
        
        if 'input(' in line and 'int(' in line:
            suggestions.append(f"🔒 Line {line_num}: Validate user input before converting to int")
        
        # Performance suggestions
        if '+=' in line and 'str' in line:
            suggestions.append(f"⚡ Line {line_num}: For string concatenation in loops, consider using join() or f-strings")
        
        if re.search(r'for\s+\w+\s+in\s+range\(len\(', line):
            suggestions.append(f"⚡ Line {line_num}: Consider using enumerate() instead of range(len())")
        
        if '.keys()' in line and 'in ' in line:
            suggestions.append(f"⚡ Line {line_num}: Use 'key in dict' instead of 'key in dict.keys()'")
    
    return suggestions

def _check_spelling_mistakes(code: str, lines: list) -> list:
    suggestions = []
    
    # Common misspellings in variable names and comments
    common_misspellings = {
        'lenght': 'length',
        'widht': 'width',
        'heigh': 'height',
        'recieve': 'receive',
        'occured': 'occurred',
        'seperator': 'separator',
        'definately': 'definitely',
        'succesful': 'successful',
        'proccess': 'process',
        'adress': 'address',
        'sucess': 'success',
        'manger': 'manager',
        'comparsion': 'comparison',
        'compatability': 'compatibility',
        'accesible': 'accessible',
        'colum': 'column',
        'usualy': 'usually',
        'ocasionally': 'occasionally'
    }
    
    for line_num, line in enumerate(lines, 1):
        # Check comments for spelling mistakes
        comment_match = re.search(r'#\s*(.+)', line)
        if comment_match:
            comment_text = comment_match.group(1)
            words = re.findall(r'\b[a-zA-Z]+\b', comment_text.lower())
            for word in words:
                if word in common_misspellings:
                    suggestions.append(f"📝 Line {line_num}: Spelling in comment: '{word}' might be misspelled, did you mean '{common_misspellings[word]}'?")
        
        # Check string literals for spelling mistakes
        string_matches = re.findall(r'["\']([^"\']+)["\']', line)
        for string_content in string_matches:
            words = re.findall(r'\b[a-zA-Z]+\b', string_content.lower())
            for word in words:
                if word in common_misspellings:
                    suggestions.append(f"📝 Line {line_num}: Spelling in string: '{word}' might be misspelled, did you mean '{common_misspellings[word]}'?")
        
        # Check variable and function names for common misspellings
        identifiers = re.findall(r'\b([a-zA-Z_]\w*)\b', line)
        for identifier in set(identifiers):  # Remove duplicates
            lower_id = identifier.lower()
            for misspelling, correction in common_misspellings.items():
                if misspelling in lower_id:
                    suggestions.append(f"📝 Line {line_num}: Variable/function name '{identifier}' contains potential misspelling: '{misspelling}' → '{correction}'")
    
    return suggestions

def _check_ast_issues(tree) -> list:
    suggestions = []
    
    for node in ast.walk(tree):
        # Check for functions without docstrings
        if isinstance(node, ast.FunctionDef) and not ast.get_docstring(node):
            line_num = getattr(node, 'lineno', 'unknown')
            suggestions.append(f"📚 Line {line_num}: Function '{node.name}' is missing a docstring")
        
        # Check for classes without docstrings
        if isinstance(node, ast.ClassDef) and not ast.get_docstring(node):
            line_num = getattr(node, 'lineno', 'unknown')
            suggestions.append(f"📚 Line {line_num}: Class '{node.name}' is missing a docstring")
        
        # Check for functions with too many arguments
        if isinstance(node, ast.FunctionDef) and len(node.args.args) > 5:
            line_num = getattr(node, 'lineno', 'unknown')
            suggestions.append(f"🔧 Line {line_num}: Function '{node.name}' has too many parameters ({len(node.args.args)}) - consider refactoring")
        
        # Check for deeply nested code
        if isinstance(node, (ast.If, ast.For, ast.While, ast.With)):
            depth = _get_nesting_depth(node)
            if depth > 3:
                line_num = getattr(node, 'lineno', 'unknown')
                suggestions.append(f"🔧 Line {line_num}: Code block has deep nesting (depth: {depth}) - consider extracting to separate functions")
    
    return suggestions

def _get_nesting_depth(node, depth=0):
    """Calculate the maximum nesting depth of a node"""
    max_depth = depth
    for child in ast.iter_child_nodes(node):
        if isinstance(child, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
            child_depth = _get_nesting_depth(child, depth + 1)
            max_depth = max(max_depth, child_depth)
    return max_depth
