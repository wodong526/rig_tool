class AA:
    def __init__(self, a):
        self.a = a

        self.pA()

    def pA(self):
        print('父级的a{}'.format(self.a))

class BB(AA):
    def __init__(self, A, B):
        self.A = A
        super(BB, self).__init__(B)
        self.B = B

        self.pB()

    def pB(self):
        print('子级的A{}'.format(self.A))
        print('子级的B{}'.format(self.B))

cla = BB(1, 2)

