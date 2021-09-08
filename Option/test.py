from contextlib import contextmanager

@contextmanager
def foo(num):
    print("starting...")
    while num<10:
        num=num+1
        yield 
        print('chenshi', num)


with foo(0):
    print('test')



