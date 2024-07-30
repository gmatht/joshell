#!/usr/bin/env python3
"""
Fixes Python scripts

Usage: fixpy.py can be used in place of python. It will automatically (e)dit
any script that ends in .e.py or .e.pyw etc. Before fixing the script, it
will backup the original file to bak/filename.e.py.hashsum
If you want to see how it# would fix a file, use
  fixpy.py ---fix script.py

It can fix simple cases of
 - Missing quotes, braces, colons (eg 'print "hello'  )
 - Missing imports
 - Missing f behind an f-string
 - ++ becomes +=1
"""
import filecmp
import hashlib
import os
import re
import subprocess
import sys

if os.name == 'nt':
    #execl is broken on windows, do not use.
    def execl(*args):
        lists = [item for item in args]
        subprocess.call(lists)
else:
    from os import execl

if len(sys.argv) == 1:
    execl(sys.executable, sys.executable , '-u')
    sys.exit()

def eprint(*args, **kwargs):
    """
    Prints the given arguments to the standard error stream.

    Args:
        *args: The arguments to be printed.
        **kwargs: Additional keyword arguments that are passed to the print function.

    Returns:
        None
    """
    print(*args, file=sys.stderr, **kwargs)

def sha256sum(data):
    """
    Calculate the SHA256 hash of a file and return it as a hexadecimal string.

    Parameters:
        filename (str): The path to the file to be hashed.

    Returns:
        str: The SHA256 hash of the file as a hexadecimal string.
    """
    hasher = hashlib.new('sha256')
    hasher.update(data.encode("utf-8"))
    return hasher.hexdigest()

def add_missing_braces_and_colons(script):
    """
    Adds missing braces to print statements, missing colons to a script.

    Args:
        script (str): The script to be modified.

    Returns:
        str: The modified script with missing braces and colons added.

    This function adds missing braces to print statements by replacing
    occurrences of 'print ' followed by a non-parenthesis character sequence with
    'print(' and the same character sequence.

    It also adds missing colons to loops and conditionals by replacing
    occurrences of a loop or conditional keyword followed by a non-colon
    character sequence at the end of a line with the same keyword, the same
    character sequence, and a colon.

    The function also replaces occurrences of '++' with '+=1' and replaces
    occurrences of a non-whitespace character at the end of a line with 'print('
    and the character.
    """
    # Add missing braces to print statements
    script = re.sub(r'(^\s*)print\s+([^(\n]+)$', r'\1print(\2)', script,0,re.MULTILINE)

    # Add missing colons to loops and conditionals
    needs_colon = r'^(\s*)\b(if|for|while|else|elif|try|except|finally|def)\b([^\:\\\\\n]*)$'
    script = re.sub(needs_colon, r'\1\2\3:', script,0,re.MULTILINE)

    script = re.sub(r'^([^#]*)\+\+$', r'\1 += 1', script,0,re.MULTILINE)
    script = re.sub(r'^(\s*)([a-zA-Z])$', r'\1print(\2)', script,0,re.MULTILINE)

    return script

def swap_quotes(input_string):
    """
    Swaps single quotes with double quotes and vice versa in a given string.

    Args:
        input_string (str): The input string.

    Returns:
        str: The modified string with the quotes swapped.

    This function takes an input string and iterates over each character.
     f the character is a single quote, it is replaced with a double quote.
      If the character is a double quote, it is replaced with a single quote.
       All other characters remain the same. The modified string is then returned.

    Example:
        >>> swap_quotes("\"Hello 'World'\"")
        'Hello "World"'
    """
    swapped_string = ""
    for char in input_string:
        if char == "'":
            swapped_string += '"'
        elif char == '"':
            swapped_string += "'"
        else:
            swapped_string += char
    return swapped_string

def replace (operation,input_str):
    """
    Replaces all occurrences of a pattern in a string with a new string.

    Args:
        operation (str): A string containing the pattern to search for in the input string,
                         followed by an arrow '->' and the new string to replace the pattern with.
        input (str): The string in which to perform the replacements.

    Returns:
        str: The modified string with all occurrences of the pattern replaced by the new string.

    This function splits the operation string into the search pattern and the new string.
    It then uses the re.sub() function to replace all occurrences of the search pattern
    in the input string with the new string. The function returns the modified string.
    """
    (search,new) = operation.split('->')
    return re.sub(search, new, input_str,0,re.MULTILINE)

def re_quote(operation,operand):
    """
    Replaces occurrences of a pattern in a string with a new string.

    Args:
        operation (str): The pattern to search for in the string.
        operand (str): The string in which to perform the replacements.

    Returns:
        str: The modified string with the replacements applied.

    This function takes an operation and an operand as input. It first runs
    the replace 'operation' in the operand using the replace function.
    Then, it swaps the quotes ' with " and visa versa in the operation
    using the swap_quotes function. Finally, it replaces the occurrences
    of the swapped operation in the operand. Finally, it returns the modified operand.
    """
    operand=replace(            operation ,operand)
    operand=replace(swap_quotes(operation),operand)
    return operand

def find_assignments(script):
    """
    Finds all variable assignments in a given script and returns a set of the variable names.

    Args:
        script (str): The script to search for variable assignments.

    Returns:
        set: A set of variable names found in the script.
    """
    pattern = re.compile(r'^\s*(\w+)\s*=\s*.*', re.MULTILINE)
    var_names=dict.fromkeys(pattern.findall(script))
    pattern = re.compile(r'^\s*for\s+(\w+)\s+in', re.MULTILINE)
    for name in pattern.findall(script):
        var_names[name]=None
    pattern = re.compile(r'def\s+\w+[(]((?:[\w, =?]|"[^"]*"|\'[^\']*)+)[)]', re.MULTILINE)
    for pat in pattern.findall(script):
        for arg in pat.split(','):
            var_names[arg.strip().split('=')[0]]=None

    return var_names.keys()

def fix_missing_fstr(script):
    """
    Adds missing "f" character at the beginning of f-strings
    Args:
        script (str): The script to be fixed.

    Returns:
        str: The modified script with the missing f-string formatting fixed.

    This function finds variable assignments in the script using the find_assignments function.
    It then constructs a regular expression matching "...{some_variable}..." missing a prior f.
    The modified script is returned.

    Note:
        The find_assignments and re_quote functions are defined elsewhere in the codebase.
    """
    assignments = find_assignments(script)
    re_assignments='|'.join(assignments)
    #for assignment in assignments:
    #pattern='^([^\'"]*[^f\'"][^f\'"])("[^"]*[{]{(?:'+re_assignments+'))->\\1f\\2'
    operation=r'^([^\'"#]*[^f\'"][^f\'"])("[^"]*{(?:'+re_assignments+')\\b)->\\1f\\2'

    return re_quote(operation,script)

def fix_missing_quotes(input_string):
    """
    Fixes missing quotes in a given input string.

    Args:
        input_string (str): The input string to fix missing quotes in.

    Returns:
        str: The modified input string with missing quotes replaced by appropriate double quotes.

    This function takes an input string and uses the `re_quote` function add missing quotes.
    To do this it uses two operations of the form "find->replace".

    The modified input string is returned.

    Example:
        >>> fix_missing_quotes('print("hello)')
        'print("hello")'
    """
    #Fix ("foo)->("foo") [and ('foo)->('foo']
    result=re_quote(r'^([^\'"#]*[(]["][^"]*)([)])$->\1")',input_string)

    #Fix (foo")->("foo") [and (foo')->('foo')]
    result=re_quote(r'^((?:\w|\s|=|[.])*[(])([^"]*"[)])$->\1"\2',result)
    return result


# Example usage
SAMPLE_SCRIPT = """import sys
x++
for B in [1, 2, 3]:
    print("{x})
    print({x}")
    print('{x})
    print({x[0]}')
    print("{not_a_variable}") # Don't assume everything with {} is an f-string
def f(C,S="hello")
    print 'Hello, world'
    def f(z)
for i in range(10)
    i
if x == 5
    print 'x is 5'
    #Note the following won't be fixed. We don't even try to fix multilines
    for x in \\
    [1,2,3]
        print 'x is ', x
path.isdir() # Submodule Import Missing
sys.exit()   # Module Import NOT Missing
time.sleep(5)# Module Import Missing"""


def fix_imports(script):
    """
    Given a python script, this function adds missing imports of common modules and submodules.

    Args:
        script (str): The script to be fixed.

    Returns:
        str: The modified script with fixed import statements.
    """
    missing={}
    for mat in re.finditer(r'^[^\'"#.]*\b([a-zA-Z]\w*)\b[.]', script,re.MULTILINE):
        #eprint(f'Missing Import "{mat[1]}"')
        missing[mat[1]]=None
    for mat in re.finditer(r'^[^\'"#]*\b([a-zA-Z]\w*)\b.*=[.]', script,re.MULTILINE):
        missing[mat[1]]=None
    for line in re.finditer(r'import (.*)', script,re.MULTILINE):
        for mat in re.finditer(r'\b(\w+)\b',line[1]):
            missing.pop(mat[1], None)

    imports = ''
    alias={
        'path': 'os.path',
        'np': 'numpy as np',
        'tk': 'tkinter as tk',
        'tktp': 'tktimepicker as tktp'
    }

    #I am currently getting lots of false positives. To fix that, only add common modules.
    common_modules=("abc argparse asyncio base64 collections copy csv ctypes "
                    "datetime decimal functools hashlib http importlib "
                    "inspect itertools json logging math multiprocessing os "
                    "pdb pygame pynput random re shutil sys threading time "
                    "tkinter tktimepicker types unittest urllib uuid Xlib")
    common_modules=common_modules.split()
    for key in common_modules:
        #eprint('COMMON:',key)
        if key in missing:
            #eprint(f'Adding Import {mat[1]}')
            imports += 'import ' + key + '\n'
    for key, value in alias.items():
        if key in missing:
            #eprint(f'Adding Alias {mat[1]}')
            imports += 'import ' + value + '\n'
    return imports + script

def fix_all(script):
    """
    Given a script, this function applies all fixed defined in this module to the script.

    Args:
        script (str): The script to be fixed.

    Returns:
        str: The modified script with simple cases of the following issues fixed:
            missing import statements,
            missing "f" before f-string,
            missing quotes, missing braces and colons.
    """
    result = script
    result = []
    for line in script.splitlines():
        result.append(line.rstrip())
    result='\n'.join(result)
    result = add_missing_braces_and_colons(result)
    result = fix_missing_quotes(result)
    result = fix_missing_fstr(result)
    result = fix_imports(result)

    return result


if len(sys.argv) == 2:
    if sys.argv[1] == '---demo':
        commented=[]
        for line in SAMPLE_SCRIPT.splitlines():
            line=' '+line+' '
            commented.append(line.replace(' ','#'))
            commented.append(line)
        fixed=fix_all('\n'.join(commented))
        print(fixed)
        sys.exit()

if len(sys.argv) == 3:
    if sys.argv[1] == '---fix':
        with open(sys.argv[2],encoding="utf8") as x:
            slurped_f = x.read()
        fixed=fix_all(slurped_f)
        print(fixed)
        sys.exit()

for fname in sys.argv:
    splt=os.path.splitext(fname)
    base=splt[0]

    if(splt[1][0:3] == '.py' and os.path.splitext(base)[1]=='.e'):

        with open(fname, encoding="utf8") as x:
            slurped_f = x.read()
            x.close()
        sha=sha256sum(slurped_f)
        bakdir=os.path.join(os.path.dirname(fname),'bak')
        if not os.path.isdir(bakdir):
            os.makedirs(bakdir)
        bakfile=os.path.join(bakdir,fname)+"."+sha
        fixed=fix_all(slurped_f)
        #eprint('###' + fname + '###')
        #eprint(fixed)
        try:
            os.rename(fname,bakfile)
            with open(fname,'w',encoding="utf8") as x:
                x.write(fixed)
                x.close()
        except FileNotFoundError:
            eprint("Failed to Move "+fname+" Not found?")
        except FileExistsError:
            if filecmp.cmp(fname, bakfile, shallow=False):
                os.remove(fname)
                with open(fname,'w',encoding="utf8") as x:
                    x.write(fixed)
                    x.close()

execl(sys.executable, os.path.abspath(sys.argv[1]), *sys.argv[1:])
