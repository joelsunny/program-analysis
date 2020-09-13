import pprint
f = pprint.pprint
star = *range(4)
a = "you"
d = "name"
j = f"{a} is my {d}"
a = ",".join(["hello", "world"])
generatorExp = (x**2 for x in my_list)
myDict = {x: x**2 for x in [1,2,3,4,5]} 
s = {(m, n) for n in range(2) for m in range(3, 5)}
d = {
    "a": 1,
    "b": 2,
    "d": "hello"
}

x = lambda a, b, c : a + b + c
if (a := plusone(1)) > 2:
    print(a)
A = [1]
B = [2]
C = A @ B
k = +1
q = ~10
f = not True
primes: List[int] = [3,5]
a = 1*2
a += 9
l = [i*2 for i in range(10) if i > 3]
j = ["Even" if i%2==0 else "Odd" for i in range(8)]
k = [i for i in range(8) if i%2==0 if i%3==0]
m = l[1]

q,w = (2,5)
a = {1,2,3}

if 1 > 2:
    a = 0
else:
    jk = 23

def plusone(n):
    return n+1

def fun(j,i, k=10):
    def _f(c):
        d = c*6
    c = _f(c)
    return c

import asyncio


async def test():
    return True

async def main():

    # test() returns coroutine:
    coro = test()
    print(coro)  # <coroutine object test at ...>


    # we can await for coroutine to get result:
    res = await coro    
    print(res)  # True