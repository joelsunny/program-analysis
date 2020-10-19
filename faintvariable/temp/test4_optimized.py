
num = 900
upper = 1000
p = num <= upper
while p:
	q = num > 1
	if q:
		d = 2
		r = d < num
		while r:
			s = (num%d) == 0
			if s:
				print(num)
				break
			else:
				d = d+1
				r = d < num

	num = num+1
	p = num <= upper