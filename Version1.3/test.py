import random

num = 12
password = []
for char in range(abs(num)):
    result = random.randrange(65, 117, 1)
    result += 6 if result > 90 else 0
    password.append(chr(result))
print(
    ''.join(password)
) 