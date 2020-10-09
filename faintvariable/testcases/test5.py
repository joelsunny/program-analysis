def recur_factorial(n):
   p = n == 1
   if p:
       return n
   else:
       return n*recur_factorial(n-1)

num = 7

if num < 0:
   print("Negative Number")
elif num == 0:
   print("Factorial is 1")
else:
   print("Factorial of", num, "is", recur_factorial(num))