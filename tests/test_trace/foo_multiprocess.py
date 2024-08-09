import multiprocessing

from tests.test_trace.foo import foo

if __name__ == '__main__':
    with multiprocessing.Pool(1) as p:
        p.map(foo, [1])
