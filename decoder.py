def _convert_base(d, e, f):
    g = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ+/'
    h, i = g[:e], g[:f]
    j = sum(h.index(b) * e**c for c, b in enumerate(reversed(d)) if h.index(b) != -1)
    k = ''
    while j:
        k = i[j % f] + k
        j //= f
    return k or '0'

def deobfuscator(h, n, t, e):
    r, i, lh = '', 0, len(h)
    while i < lh:
        s = ''
        while i < lh and h[i] != n[e]:
            s, i = s + h[i], i + 1
        s = ''.join(str(n.index(c)) for c in s)
        r += chr(int(_convert_base(s, e, 10)) - t)
        i += 1
    return r
