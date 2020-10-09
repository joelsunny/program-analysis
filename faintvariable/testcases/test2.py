a = 235
b = 51
c = 47
d = 55
p = a < b
q = a < c
r = a < d
s = b < c
t = b < d
u = c < d
if p:
    if q:
        if r:
            print(a)
        else:
            print(d)
    elif u:
        print(c)
    else:
        print(d)
else:
    if s:
        if t:
            print(b)
        else:
            print(d)
    elif u:
        print(c)
    else:
        print(d)