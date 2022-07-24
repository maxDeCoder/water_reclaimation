a = [1,2,3,4,5,6]
b = "h"
def k():
    global a, b
    t = a
    t.remove(5)
    a = t

k()

print(a)