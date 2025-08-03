import re

def suggest_refactor_javascript(code: str) -> list:
    """
    Analyze JavaScript code and provide refactoring suggestions with line numbers.
    """
    suggestions = []
    lines = code.split('\n')
    
    # JavaScript-specific checks
    suggestions.extend(_check_js_code_smells(code, lines))
    suggestions.extend(_check_js_naming_conventions(code, lines))
    suggestions.extend(_check_js_security_performance(code, lines))
    suggestions.extend(_check_js_spelling_mistakes(code, lines))
    suggestions.extend(_check_js_best_practices(code, lines))
    
    return suggestions

def _check_js_code_smells(code: str, lines: list) -> list:
    suggestions = []
    
    for i, line in enumerate(lines, 1):
        line_content = line.strip()
        
        # == vs === comparison
        if '==' in line_content and '===' not in line_content and '!=' in line_content:
            suggestions.append(f"🔧 Line {i}: Use strict equality (===) instead of loose equality (==)")
        
        if '!=' in line_content and '!==' not in line_content:
            suggestions.append(f"🔧 Line {i}: Use strict inequality (!==) instead of loose inequality (!=)")
        
        # console.log in production
        if 'console.log' in line_content:
            suggestions.append(f"🚫 Line {i}: Remove console.log statements in production code")
        
        # var instead of let/const
        if re.search(r'\bvar\s+\w+', line_content):
            suggestions.append(f"🔧 Line {i}: Use 'let' or 'const' instead of 'var'")
        
        # Global variables
        if line_content.startswith('var ') or line_content.startswith('let ') or line_content.startswith('const '):
            if i == 1 or not any(line.strip().startswith(('function', 'class', '{', '(')) for line in lines[:i-1]):
                suggestions.append(f"🌐 Line {i}: Avoid global variables - use modules or IIFE")
        
        # Long lines
        if len(line) > 100:
            suggestions.append(f"📏 Line {i}: Line too long ({len(line)} chars) - consider breaking it down")
        
        # Empty catch blocks
        if 'catch' in line_content and '{' in line_content:
            next_lines = lines[i:i+3] if i < len(lines) - 2 else []
            if any('}' in next_line.strip() and len(next_line.strip()) <= 1 for next_line in next_lines):
                suggestions.append(f"🚫 Line {i}: Empty catch block - handle errors properly")
        
        # eval() usage
        if 'eval(' in line_content:
            suggestions.append(f"🔒 Line {i}: Avoid eval() - it's a security risk and performance issue")
        
        # Trailing commas in objects/arrays (good practice in modern JS)
        if re.search(r'[\[\{][^[\{\]\}]*[^,\s][\]\}]', line_content):
            suggestions.append(f"📝 Line {i}: Consider adding trailing commas for better diffs")
        
        # Function declarations inside blocks
        if re.search(r'^\s+function\s+\w+', line_content):
            suggestions.append(f"🔧 Line {i}: Avoid function declarations inside blocks - use function expressions")
    
    return suggestions

def _check_js_naming_conventions(code: str, lines: list) -> list:
    suggestions = []
    
    for i, line in enumerate(lines, 1):
        line_content = line.strip()
        
        # Variable names should be camelCase
        var_matches = re.findall(r'(?:var|let|const)\s+([A-Z]\w*)', line_content)
        for var_name in var_matches:
            suggestions.append(f"🐍 Line {i}: Variable '{var_name}' should use camelCase naming")
        
        # Function names should be camelCase
        func_matches = re.findall(r'function\s+([A-Z]\w*)', line_content)
        for func_name in func_matches:
            suggestions.append(f"🔧 Line {i}: Function '{func_name}' should use camelCase naming")
        
        # Constructor functions should be PascalCase
        new_matches = re.findall(r'new\s+([a-z]\w*)', line_content)
        for constructor in new_matches:
            suggestions.append(f"🏗️ Line {i}: Constructor '{constructor}' should use PascalCase naming")
        
        # Constants should be UPPER_CASE
        const_matches = re.findall(r'const\s+([a-z]\w*)\s*=\s*["\'\d]', line_content)
        for const_name in const_matches:
            suggestions.append(f"🔢 Line {i}: Constant '{const_name}' should use UPPER_CASE naming")
        
        # Private methods/properties (convention: underscore prefix)
        if re.search(r'this\.([a-zA-Z]\w*)\s*=', line_content):
            prop_name = re.search(r'this\.([a-zA-Z]\w*)', line_content).group(1)
            if not prop_name.startswith('_') and 'private' in line_content.lower():
                suggestions.append(f"🔒 Line {i}: Private property '{prop_name}' should start with underscore")
    
    return suggestions

def _check_js_security_performance(code: str, lines: list) -> list:
    suggestions = []
    
    for i, line in enumerate(lines, 1):
        line_content = line.strip()
        
        # Security issues
        if 'innerHTML' in line_content and '=' in line_content:
            suggestions.append(f"🔒 Line {i}: Using innerHTML can lead to XSS - consider textContent or sanitization")
        
        if 'document.write' in line_content:
            suggestions.append(f"🔒 Line {i}: Avoid document.write - it can overwrite the entire document")
        
        if 'setTimeout' in line_content and 'string' in str(type(line_content)):
            if re.search(r'setTimeout\s*\(\s*["\']', line_content):
                suggestions.append(f"🔒 Line {i}: Avoid string-based setTimeout - use functions instead")
        
        # Performance issues
        if 'document.getElementById' in line_content and 'for' in code:
            suggestions.append(f"⚡ Line {i}: Cache DOM elements outside loops to improve performance")
        
        if re.search(r'for\s*\(\s*var\s+\w+\s*=\s*0.*\.length', line_content):
            suggestions.append(f"⚡ Line {i}: Cache array length in variable to avoid repeated access")
        
        if '+=' in line_content and re.search(r'["\'`]', line_content):
            suggestions.append(f"⚡ Line {i}: Use template literals or array.join() for string concatenation")
        
        # Synchronous AJAX
        if 'XMLHttpRequest' in line_content and 'false' in line_content:
            suggestions.append(f"⚡ Line {i}: Avoid synchronous AJAX - use async requests")
        
        # Memory leaks
        if 'addEventListener' in line_content:
            suggestions.append(f"💾 Line {i}: Remember to remove event listeners to prevent memory leaks")
    
    return suggestions

def _check_js_spelling_mistakes(code: str, lines: list) -> list:
    suggestions = []
    
    # Common JavaScript-specific misspellings
    js_misspellings = {
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
        'ocasionally': 'occasionally',
        'fucntion': 'function',
        'retrun': 'return',
        'calback': 'callback',
        'asyncronous': 'asynchronous',
        'promiss': 'promise',
        'reponse': 'response',
        'requets': 'request'
    }
    
    for i, line in enumerate(lines, 1):
        # Check comments
        comment_match = re.search(r'//(.*)|/\*([^*]|\*[^/])*\*/', line)
        if comment_match:
            comment_text = comment_match.group(1) or comment_match.group(2) or ""
            words = re.findall(r'\b[a-zA-Z]+\b', comment_text.lower())
            for word in words:
                if word in js_misspellings:
                    suggestions.append(f"📝 Line {i}: Spelling in comment: '{word}' → '{js_misspellings[word]}'")
        
        # Check string literals
        string_matches = re.findall(r'["\']([^"\']+)["\']', line)
        for string_content in string_matches:
            words = re.findall(r'\b[a-zA-Z]+\b', string_content.lower())
            for word in words:
                if word in js_misspellings:
                    suggestions.append(f"📝 Line {i}: Spelling in string: '{word}' → '{js_misspellings[word]}'")
        
        # Check template literals
        template_matches = re.findall(r'`([^`]+)`', line)
        for template_content in template_matches:
            words = re.findall(r'\b[a-zA-Z]+\b', template_content.lower())
            for word in words:
                if word in js_misspellings:
                    suggestions.append(f"📝 Line {i}: Spelling in template: '{word}' → '{js_misspellings[word]}'")
        
        # Check identifiers
        identifiers = re.findall(r'\b([a-zA-Z_$]\w*)\b', line)
        for identifier in set(identifiers):
            lower_id = identifier.lower()
            for misspelling, correction in js_misspellings.items():
                if misspelling in lower_id:
                    suggestions.append(f"📝 Line {i}: Identifier '{identifier}' contains '{misspelling}' → '{correction}'")
    
    return suggestions

def _check_js_best_practices(code: str, lines: list) -> list:
    suggestions = []
    
    for i, line in enumerate(lines, 1):
        line_content = line.strip()
        
        # Missing semicolons
        if line_content and not line_content.endswith((';', '{', '}', ')', ',')):
            if re.search(r'(var|let|const|return|throw)\s+.*[^;{}\(\),]$', line_content):
                suggestions.append(f"📝 Line {i}: Consider adding semicolon at end of statement")
        
        # Using == null instead of === null
        if '== null' in line_content:
            suggestions.append(f"🔧 Line {i}: Use '=== null' instead of '== null'")
        
        # Array/Object method chaining without proper formatting
        if line_content.count('.') > 2 and len(line_content) > 60:
            suggestions.append(f"📝 Line {i}: Consider breaking method chains across multiple lines")
        
        # Missing JSDoc for functions
        if line_content.startswith('function') or 'function' in line_content:
            prev_lines = lines[max(0, i-3):i-1]
            if not any('/**' in prev_line for prev_line in prev_lines):
                suggestions.append(f"📚 Line {i}: Consider adding JSDoc documentation for function")
        
        # Using for...in for arrays
        if 'for' in line_content and 'in' in line_content and '[' in code:
            suggestions.append(f"🔧 Line {i}: Use for...of or forEach for arrays instead of for...in")
        
        # Nested callbacks (callback hell)
        indentation_level = len(line_content) - len(line_content.lstrip())
        if indentation_level > 12 and 'function' in line_content:
            suggestions.append(f"🔧 Line {i}: Deep nesting detected - consider using Promises or async/await")
        
        # Using var in function scope
        if 'function' in line_content and i < len(lines) - 1:
            next_lines = lines[i:i+10]
            for j, next_line in enumerate(next_lines):
                if 'var ' in next_line:
                    suggestions.append(f"🔧 Line {i+j+1}: Use 'let' or 'const' instead of 'var' in function scope")
                    break
        
        # Magical numbers
        if re.search(r'\b(?!0|1)\d{2,}\b', line_content) and not line_content.strip().startswith('//'):
            suggestions.append(f"📏 Line {i}: Consider using named constants instead of magic numbers")
        
        # Promises without error handling
        if '.then(' in line_content and '.catch(' not in code[code.find(line_content):]:
            suggestions.append(f"⚠️ Line {i}: Promise chain missing error handling (.catch)")
        
        # Using deprecated methods
        deprecated_methods = ['escape(', 'unescape(', 'with (']
        for method in deprecated_methods:
            if method in line_content:
                suggestions.append(f"⚠️ Line {i}: '{method.rstrip('(')}' is deprecated - use modern alternatives")
    
    return suggestions 