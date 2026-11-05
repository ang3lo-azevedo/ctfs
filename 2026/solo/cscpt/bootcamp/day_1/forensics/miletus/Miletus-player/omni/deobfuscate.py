tokens = STRING, NUM, '$(' , '@(' , '(' , ')' , ',' , '.' , IDENT (method names), OP (-f/-join/-as/...), VAR ($x), [Type], EOF

while True:
    spans = find_innermost_spans(text)
    for (s,e) in spans sorted right-to-left:
        body = text[s+2 : e-1]
        try: val = eval_pure(body)
        except NotPure: continue
        text = text[:s] + quote(val) + text[e:]
