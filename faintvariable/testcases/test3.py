a = 1
b = 2
c = 3
d = 4
p = a < b
q = b < c
r = c < d
while p:
    while q>0:
        while r>0:
            c = c + 1
            r = c < d
        b = b + 1
        q = b < c
    a = a + 1
    p = a < b
print(a)