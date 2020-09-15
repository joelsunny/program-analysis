a = 10

if (a > 20) and (a < 20):
    a += 1
elif a < 12:
    a -= 1
elif a < 4:
    a -= 2
else:
    if a == 1:
        print("done")
    elif a < 0:
        print("negative")
    a *= 2