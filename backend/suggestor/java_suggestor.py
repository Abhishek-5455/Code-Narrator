import re

def suggest_refactor_java(code: str) -> list:
    """
    Analyze Java code and provide refactoring suggestions with line numbers.
    """
    suggestions = []
    lines = code.split('\n')
    
    # Java-specific checks
    suggestions.extend(_check_java_code_smells(code, lines))
    suggestions.extend(_check_java_naming_conventions(code, lines))
    suggestions.extend(_check_java_security_performance(code, lines))
    suggestions.extend(_check_java_spelling_mistakes(code, lines))
    suggestions.extend(_check_java_best_practices(code, lines))
    
    return suggestions

def _check_java_code_smells(code: str, lines: list) -> list:
    suggestions = []
    
    for i, line in enumerate(lines, 1):
        line_content = line.strip()
        
        # Empty catch blocks
        if line_content == "} catch" or (line_content.startswith("catch") and "{" in line_content):
            next_lines = lines[i:i+3] if i < len(lines) - 2 else []
            if any("}" in next_line.strip() and len(next_line.strip()) <= 1 for next_line in next_lines):
                suggestions.append(f"🚫 Line {i}: Empty catch block - handle exceptions properly")
        
        # System.out.println in production
        if "System.out.println" in line_content:
            suggestions.append(f"🚫 Line {i}: Avoid System.out.println in production - use logging framework")
        
        # == for String comparison
        if re.search(r'"[^"]*"\s*==\s*\w+|w+\s*==\s*"[^"]*"', line_content):
            suggestions.append(f"🔧 Line {i}: Use .equals() instead of == for String comparison")
        
        # Magic numbers
        if re.search(r'\b(?!0|1)\d{2,}\b', line_content) and not line_content.strip().startswith("//"):
            suggestions.append(f"📏 Line {i}: Consider using named constants instead of magic numbers")
        
        # Long lines (Java convention: 120 chars)
        if len(line) > 120:
            suggestions.append(f"📏 Line {i}: Line too long ({len(line)} chars) - consider breaking it down")
        
        # Multiple variable declarations
        if re.search(r'(int|String|boolean|double|float|long)\s+\w+\s*,\s*\w+', line_content):
            suggestions.append(f"📦 Line {i}: Declare variables separately for better readability")
        
        # Raw types (generics)
        if re.search(r'\b(List|Map|Set|ArrayList|HashMap|HashSet)\s+\w+\s*=', line_content):
            if not re.search(r'<[^>]+>', line_content):
                suggestions.append(f"⚠️ Line {i}: Use generics instead of raw types")
        
        # Nested if statements (check for multiple 'if' in one line or subsequent lines)
        if line_content.count('if') > 1:
            suggestions.append(f"🔧 Line {i}: Avoid nested if statements - consider using guard clauses")
    
    return suggestions

def _check_java_naming_conventions(code: str, lines: list) -> list:
    suggestions = []
    
    for i, line in enumerate(lines, 1):
        line_content = line.strip()
        
        # Class names should be PascalCase
        class_match = re.search(r'class\s+([a-z]\w*)', line_content)
        if class_match:
            class_name = class_match.group(1)
            suggestions.append(f"🏗️ Line {i}: Class '{class_name}' should use PascalCase naming")
        
        # Method names should be camelCase
        method_match = re.search(r'(public|private|protected).*?\s+([A-Z]\w*)\s*\(', line_content)
        if method_match:
            method_name = method_match.group(2)
            suggestions.append(f"🔧 Line {i}: Method '{method_name}' should use camelCase naming")
        
        # Variable names should be camelCase
        var_matches = re.findall(r'(int|String|boolean|double|float|long)\s+([A-Z]\w*)', line_content)
        for match in var_matches:
            var_name = match[1]
            suggestions.append(f"🐍 Line {i}: Variable '{var_name}' should use camelCase naming")
        
        # Constants should be UPPER_CASE
        const_matches = re.findall(r'final\s+static\s+\w+\s+([a-z]\w*)', line_content)
        for const_name in const_matches:
            suggestions.append(f"🔢 Line {i}: Constant '{const_name}' should use UPPER_CASE naming")
        
        # Package names should be lowercase
        package_match = re.search(r'package\s+([^;]*[A-Z][^;]*)', line_content)
        if package_match:
            package_name = package_match.group(1)
            suggestions.append(f"📦 Line {i}: Package '{package_name}' should be lowercase")
    
    return suggestions

def _check_java_security_performance(code: str, lines: list) -> list:
    suggestions = []
    
    for i, line in enumerate(lines, 1):
        line_content = line.strip()
        
        # Security issues
        if 'Runtime.getRuntime().exec' in line_content:
            suggestions.append(f"🔒 Line {i}: Avoid Runtime.exec() - potential security risk")
        
        if 'Class.forName' in line_content:
            suggestions.append(f"🔒 Line {i}: Be cautious with Class.forName() - validate input")
        
        if re.search(r'new\s+Random\(\)', line_content):
            suggestions.append(f"🔒 Line {i}: Use SecureRandom instead of Random for security-sensitive operations")
        
        # Performance issues
        if '+=' in line_content and 'String' in lines[max(0, i-5):i]:
            suggestions.append(f"⚡ Line {i}: Use StringBuilder instead of String concatenation in loops")
        
        if '.size()' in line_content and 'for' in line_content:
            suggestions.append(f"⚡ Line {i}: Cache collection.size() in variable to avoid repeated calls")
        
        if 'new String(' in line_content:
            suggestions.append(f"⚡ Line {i}: Avoid unnecessary String constructor - use string literals")
        
        # Boxing/Unboxing
        if re.search(r'new\s+(Integer|Double|Boolean|Float|Long)\(', line_content):
            suggestions.append(f"⚡ Line {i}: Use valueOf() instead of constructor for wrapper classes")
    
    return suggestions

def _check_java_spelling_mistakes(code: str, lines: list) -> list:
    suggestions = []
    
    # Common Java-specific misspellings
    java_misspellings = {
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
        'excpetion': 'exception',
        'connexion': 'connection',
        'initalize': 'initialize',
        'implmentation': 'implementation'
    }
    
    for i, line in enumerate(lines, 1):
        # Check comments
        comment_match = re.search(r'//(.*)|/\*([^*]|\*[^/])*\*/', line)
        if comment_match:
            comment_text = comment_match.group(1) or comment_match.group(2) or ""
            words = re.findall(r'\b[a-zA-Z]+\b', comment_text.lower())
            for word in words:
                if word in java_misspellings:
                    suggestions.append(f"📝 Line {i}: Spelling in comment: '{word}' → '{java_misspellings[word]}'")
        
        # Check string literals
        string_matches = re.findall(r'"([^"]+)"', line)
        for string_content in string_matches:
            words = re.findall(r'\b[a-zA-Z]+\b', string_content.lower())
            for word in words:
                if word in java_misspellings:
                    suggestions.append(f"📝 Line {i}: Spelling in string: '{word}' → '{java_misspellings[word]}'")
        
        # Check identifiers
        identifiers = re.findall(r'\b([a-zA-Z_]\w*)\b', line)
        for identifier in set(identifiers):
            lower_id = identifier.lower()
            for misspelling, correction in java_misspellings.items():
                if misspelling in lower_id:
                    suggestions.append(f"📝 Line {i}: Identifier '{identifier}' contains '{misspelling}' → '{correction}'")
    
    return suggestions

def _check_java_best_practices(code: str, lines: list) -> list:
    suggestions = []
    
    for i, line in enumerate(lines, 1):
        line_content = line.strip()
        
        # Missing @Override annotation
        if i > 1 and re.search(r'public\s+\w+\s+\w+\s*\(', line_content):
            prev_line = lines[i-2].strip() if i > 1 else ""
            if not prev_line.startswith('@Override'):
                # Check if it might be overriding (common method names)
                if re.search(r'(toString|equals|hashCode|compareTo)\s*\(', line_content):
                    suggestions.append(f"📚 Line {i}: Consider adding @Override annotation")
        
        # Missing final keyword for parameters
        if re.search(r'\([^)]*\w+\s+\w+[^)]*\)', line_content) and 'final' not in line_content:
            suggestions.append(f"🔧 Line {i}: Consider making parameters final")
        
        # Utility class without private constructor
        if 'class' in line_content and 'static' in line_content:
            suggestions.append(f"🏗️ Line {i}: Utility classes should have private constructor")
        
        # Missing Javadoc for public methods
        if line_content.startswith('public') and '(' in line_content and ')' in line_content:
            prev_line = lines[i-2].strip() if i > 1 else ""
            if not prev_line.startswith('/**'):
                suggestions.append(f"📚 Line {i}: Public method missing Javadoc documentation")
        
        # Using Vector instead of ArrayList
        if 'Vector' in line_content:
            suggestions.append(f"⚡ Line {i}: Use ArrayList instead of Vector (Vector is synchronized and slower)")
        
        # Using Hashtable instead of HashMap
        if 'Hashtable' in line_content:
            suggestions.append(f"⚡ Line {i}: Use HashMap instead of Hashtable (unless synchronization needed)")
        
        # Interface naming
        if line_content.startswith('interface') and not re.search(r'interface\s+I[A-Z]', line_content):
            interface_match = re.search(r'interface\s+(\w+)', line_content)
            if interface_match and interface_match.group(1).startswith('I'):
                suggestions.append(f"🏗️ Line {i}: Avoid 'I' prefix for interfaces in Java")
    
    return suggestions 