a = {'a', 'b'}

c = a
class d:
    def __init__(self, g):
        self.d = g
m = d(a)

c.remove('a')
c.add('g')

print(c)
print(m.d)