from thread_pool import ThreadPool


def foo(x, y):
    print("foo called...\n")

def bar(x, y):
    print("bar called...\n")

def test(x):
    print("test called...\n")

if __name__ == '__main__':
    with ThreadPool(workers=10) as pool:
        f1 = pool.submit(fn=foo, args=(10, 20))
        f2 = pool.submit(fn=bar, args=("Hello", "world"))
        f3 = pool.submit(fn=test, args=(100,))

    #print(f1.get(), f2.get(), f3.get())

    #with ThreadPool(workers=10) as pool:
    #    result = pool.map(fn=square, data=range(100))
    #    print("result =", result)

