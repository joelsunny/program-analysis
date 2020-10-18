a = 1
b = 2
print(a)

c = 1
if a > 0:
    c = 9
elif a > 1:
    c = 0
    c = 3
    if c < 2:
        print("inner")
else:
    print("else")
    print("somethin else")
print(c)