# logic_solver.py

import re

OPS = {
    '¬': {'precedence': 4, 'arity': 1, 'func': lambda a: int(not a)},
    '∧': {'precedence': 3, 'arity': 2, 'func': lambda a, b: a & b},
    '∨': {'precedence': 2, 'arity': 2, 'func': lambda a, b: a | b},
    '→': {'precedence': 1, 'arity': 2, 'func': lambda a, b: int((not a) | b)},
    '↔': {'precedence': 0, 'arity': 2, 'func': lambda a, b: int(a == b)},
}

def tokenize(expr):
    expr = expr.replace(' ', '')
    return re.findall(r'[01()]|¬|∧|∨|→|↔', expr)

def to_rpn(tokens):
    output, stack = [], []
    for token in tokens:
        if token in '01':
            output.append(token)
        elif token in OPS:
            while stack and stack[-1] in OPS and OPS[stack[-1]]['precedence'] >= OPS[token]['precedence']:
                output.append(stack.pop())
            stack.append(token)
        elif token == '(':
            stack.append(token)
        elif token == ')':
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            stack.pop()
    while stack:
        output.append(stack.pop())
    return output

def evaluate_rpn(rpn):
    stack = []
    steps = []
    for token in rpn:
        if token in '01':
            stack.append(int(token))
        elif token in OPS:
            if OPS[token]['arity'] == 1:
                a = stack.pop()
                res = OPS[token]['func'](a)
                steps.append(f"{token}{a} = {res}")
                stack.append(res)
            elif OPS[token]['arity'] == 2:
                b = stack.pop()
                a = stack.pop()
                res = OPS[token]['func'](a, b)
                steps.append(f"{a} {token} {b} = {res}")
                stack.append(res)
    return stack[0], steps

def solve_formula(expr):
    tokens = tokenize(expr)
    rpn = to_rpn(tokens)
    result, steps = evaluate_rpn(rpn)
    return steps + [f"Результат: {result}"]
