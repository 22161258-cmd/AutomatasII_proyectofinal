import glob
import random

import notaciones as N
from errores import ERRORES


def pruebas_notaciones():
    casos = [
        ("a + b * c", "a b c * +", "+ a * b c"),
        ("(a + b) * c", "a b + c *", "* + a b c"),
        ("a - b - c", "a b - c -", "- - a b c"),
        ("a - (b - c)", "a b c - -", "- a - b c"),
        ("-a * b", "a neg b *", "* neg a b"),
        ("no a y b", "a no b y", "y no a b"),
        ("no a > b", "a b > no", "no > a b"),
        ("a o b y c", "a b c y o", "o a y b c"),
        ("x * (p + q) / 2", "x p q + * 2 /", "/ * x + p q 2"),
        ('"hola" + "mundo"', '"hola" "mundo" +', '+ "hola" "mundo"'),
        ("c.gastado <= c.limite", "c.gastado c.limite <=", "<= c.gastado c.limite"),
        ("- - 3", "3 neg neg", "neg neg 3"),
    ]
    for infija, post, pre in casos:
        toks = N.tokenizar(infija)
        got_post = " ".join(N.infija_a_postfija(toks))
        got_pre = " ".join(N.infija_a_prefija(toks))
        if got_post != post or got_pre != pre:
            return False, f"'{infija}': postfija={got_post!r} (esperada {post!r}), prefija={got_pre!r} (esperada {pre!r})"
        if " ".join(N.prefija_a_postfija(pre.split())) != post:
            return False, f"prefija->postfija falla en '{infija}'"
        re_toks = N.tokenizar(N.postfija_a_infija(post.split()))
        if N.infija_a_postfija(re_toks) != post.split():
            return False, f"ida y vuelta infija falla en '{infija}'"

    for malo in ["a + ", "(a + b", "a + b)"]:
        try:
            N.infija_a_postfija(N.tokenizar(malo))
            if malo == "a + ":
                N.postfija_a_prefija(N.infija_a_postfija(N.tokenizar