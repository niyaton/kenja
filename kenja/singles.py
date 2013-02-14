# tinyawk
# an interpreter of a extremely small subset of AWK programming language.
# supported reserved words are:
#   BEGIN END NF NR if else next print while
#   ( ) [ ] { } ; , < <= > >= == != && || ! - + * / % $
# note that: 
# - escape sequences in string are not supported.
# - regular expression is Python's one.
# - all numbers are integers, no floating points.
# - assignment to NF, NR or $* is undefined behavior.

from pyrem_torq import *
from pyrem_torq.expression import *
from pyrem_torq.treeseq import seq_split_nodes_of_label

def split_to_str(text):
    p = re.compile("|".join([
        r"/[^/\r\n]*/", r'"[^"\r\n]*"', r"\d+", # literals (regex, string, integer)
        r"#[^\r\n]*", # comment
        r"[ \t]+", r"\r\n|\r|\n", # white spaces, newline
        r"[a-zA-Z_](\w|_)*", # identifier
        r"[<>!=]=|&&|[|][|]", r"[-+*/%<>!=()${},;]|\[|\]", # operators
        r"." # invalid chars
    ]))
    return [ 'code' ] + utility.split_to_strings(text, pattern=p)

def tokenizing_expr():
    # identify reserved words, literals, identifiers
    e = Search(script.compile(r"""
    (r_BEGIN <- "BEGIN") | (r_END <- "END")
    | (r_assert <- "assert")
    | (r_boolean <- "boolean") | (r_byte <- "byte") | (r_char <- "char") | (r_int <- "int" )
    | (r_double <- "double")
    | (r_float <- "float")
    | (r_false <- "false")
    | (r_next <- "next") | (r_if <- "if") | (r_else <- "else") | (r_for <- "for") | (r_while <- "while") | (r_do <- "do")
    | (r_break <- "break") | (r_continue <- "continue" ) | (r_case <- "case") | (r_catch <- "catch") | (r_default <- "default")
    | (r_finally <- "finally")
    | (r_instanceof <- "instanceof")
    | (r_long <- "long")
    | (r_new <- "new")
    | (r_null <- "null")
    | (r_return <- "return")
    | (r_short <- "short")
    | (r_switch <- "switch")
    | (r_synchronized <- "synchronized")
    | (r_this <- "this")
    | (r_throw <- "throw")
    | (r_true <- "true")
    | (r_try <- "try")
    | (r_volatile <- "volatile")
    | (id <- r"^[a-zA-Z_]") 
    | (l_integer <- r"^[0-9]") | (l_string <- r"^\"") | (l_string <- r"^'")
    | (op_xor <- "^")
    | (op_xor_eq <- "^=")
    | (op_gt <- ">") | (op_ge <- ">=") | (op_lt <- "<") | (op_le <- "<=") | (op_ne <- "!=") | (op_eq <- "==")
    | (op_and <- "&&") | (op_or <- "||")
    | (op_plusplus <- "++") | (op_minusminus <- "--")
    | (op_plus <- "+") | (op_minus <- "-") | (op_mul <- "*") | (op_div <- "/") | (op_mod <- "%")
    | (op_assign <- "=") | (op_not <- "!") | (op_dollar <- "$") | (op_or2 <- "|")
    | (LP <- "(") | (RP <- ")") | (LB <- "{") | (RB <- "}") | (LK <- "[") | (RK <- "]")
    | (dot <- ".") | (comma <- ",") | (semicolon <- ";") | (colon <- ":")
    | (ques <- "?") | (bslash <- "\\")
    | (newline <- "\r\n" | "\r" | "\n")
    | (null <- r"^[ \t#]")
    | any, error("unexpected character")
    ;"""))
    #yield "identify reserved words, literals, identifiers", e
    #print e
    return e
    
#< ABSTRACT: "abstract" >
#| < CLASS: "class" >
#| < CONST: "const" >
#| < ENUM: "enum" >
#| < EXTENDS: "extends" >
#| < FINAL: "final" >
#| < GOTO: "goto" >
#| < IMPLEMENTS: "implements" >
#| < IMPORT: "import" >
#| < INTERFACE: "interface" >
#| < NATIVE: "native" >
#| < PACKAGE: "package">
#| < PRIVATE: "private" >
#| < PROTECTED: "protected" >
#| < PUBLIC: "public" >
#| < STATIC: "static" >
#| < STRICTFP: "strictfp" >
#| < SUPER: "super" >
#| < THROWS: "throws" >
#| < TRANSIENT: "transient" >
#| < VOID: "void" >
#| < WHILE: "while" >
#}

    # identify statement-terminating new-line chars
    #e = Search(script.compile(r"""
    #(comma | LB | op_or | op_and | r_else), (null <- newline)
    #;"""))
    #yield "remove neglected new-line characters", e


def create_two_singles(seq):
    singles = set()
    prev = seq.pop(0)
    for tok in seq:
        singles.add((prev[0], prev[2], tok[0], tok[2]))
        prev = tok
    #print "\n\n"
    #print singles

    return singles

def tokenize(tokenizer, script):
    seq = split_to_str(script)
    seq = tokenizer.parse(seq)
    return seq_split_nodes_of_label(seq, "null")[0]

def calculate_simirarity(script1, script2):
    tokenizer = tokenizing_expr()
    seq = tokenize(tokenizer, script1)
    seq2 = tokenize(tokenizer, script2)

    singles1 = create_two_singles(seq)
    singles2 = create_two_singles(seq2)

    #print "\n".join(treeseq.seq_pretty(treeseq.seq_remove_strattrs(seq)))

    return len( singles1 & singles2) / float(len(singles1 | singles2))


def main(debugTrace=False):
    import sys
    
    if len(sys.argv) == 1:
        print "usage: tinyawk -f <script> [ <input> ]\nAn interpreter of a awk-like small language."
        return
    
    assert len(sys.argv) in (3, 4)
    assert sys.argv[1] == "-f"
    scriptFile = sys.argv[2]
    scriptFile2 = sys.argv[3]
    #inputFile = sys.argv[3] if len(sys.argv) == 4 else None
    debugWrite = sys.stderr.write if debugTrace else None
    
    f = open(scriptFile, "r")
    try:
        script = f.read()
    finally: f.close()
    script = script + "\n" # prepare for missing new-line char at the last line
    
    f = open(scriptFile2, "r")
    try:
        script2 = f.read()
    finally: f.close()
    script2 = script2 + "\n"

    # parsing
    #seq = split_to_str(script)
    #des = []
    #des.extend(tokenizing_expr_iter())

    #des.extend(stmt_parsing_expr_iter()) 
    #des.extend(expr_parsing_expr_iter())
    #for desc, expr in des:
    #    if debugWrite:
    #        #debugWrite("\n".join(treeseq.seq_pretty(treeseq.seq_remove_strattrs(seq))) + "\n") # prints a seq
    #        debugWrite("step: %s\n" % desc)
    #        newSeq = expr.parse(seq)

    #        #print seq

    #    if newSeq is None: sys.exit("parse error")
    #    seq = newSeq
    #    seq = seq_split_nodes_of_label(seq, "null")[0]
    #print seq

    #tokenizer = tokenizing_expr()
    #seq = tokenize(tokenizer, script)
    #seq2 = tokenize(tokenizer, script2)

    #singles1 = create_two_singles(seq)
    #singles2 = create_two_singles(seq2)

    #print len( singles1 & singles2) / float(len(singles1 | singles2))
    print calculate_simirarity(script, script2)

if __name__ == '__main__':
    main(debugTrace=True)
