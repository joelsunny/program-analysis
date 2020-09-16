import asyncio

# 1. assign result of an awaited value 
async def test():
    return True
async def main():
    coro = test()
    res = await coro
    print(res)

# 2. annotated assignment
primes: List[int] = [3,5]

# 3. Named expression (walrus operator)
if (a := plusone(1)) > 2:
    print(a)
def plusone(n):
    return n+1

# 4. lambda expression
x = lambda a, b, c : a + b + c

# 5. FormattedValue
v1 = "my"
v2 = "X"
j = f"{v1} name is {v2}"

# 6. starred value (dereferencing)
star = *range(4)

# 7. list comprehensions of various type
l = [i*2 for i in range(10) if i > 3]
j = ["Even" if i%2==0 else "Odd" for i in range(8)]
k = [i for i in range(8) if i%2==0 if i%3==0]

# 8. dictionary comprehension
myDict = {x: x**2 for x in [1,2,3,4,5]}

# 9. set comprehension
s = {(m, n) for n in range(2) for m in range(3, 5)}

# 10. Joined string
a = ",".join(["hello", "world"])

# 11. generator expression
generatorExp = (x**2 for x in my_list)
