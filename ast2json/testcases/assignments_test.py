s = "hi" + "my" + "name" + "is"

#  dictionary assignment
d = {
    "a": 1,
    "b": 2,
    "d": "hello"
}

# List assignment
A = [1]
B = [2]

# unary operator result assignment
q = ~10
f = not True

# binary operator results
a = 1*2
C = A @ B # matrix multiplication operator

# augmented assignments
a += 9
a *= 2
a ^= 1

# boolean operator results
x = (True or False) and (True and False)

# list indexing, subscripting
l = [1,2,3,4,5]
v1 = l[1]
v2 = l[1:4]
v3 = l[0:4:2]

# assignment within if else chain
if 1 > 2:
    a = 0
else:
    jk = 23

# assignment inside nested functions
def fun(j,i, k=10):
    def _f(c):
        d = c*6
    c = _f(c)
    return c