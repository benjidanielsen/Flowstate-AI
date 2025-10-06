import time
import statistics
import json
import os

# Example functions to benchmark
# In real scenario, import actual Flowstate-AI functions/modules

def example_function_1(n=1000000):
    s = 0
    for i in range(n):
        s += i
    return s

def example_function_2(n=100000):
    return [i*i for i in range(n)]

# Benchmark utility
class Benchmark:
    def __init__(self, fn, name, args=None, kwargs=None, runs=5):
        self.fn = fn
        self.name = name
        self.args = args if args else []
        self.kwargs = kwargs if kwargs else {}
        self.runs = runs
        self.results = []

    def run(self):
        self.results.clear()
        for _ in range(self.runs):
            start = time.perf_counter()
            self.fn(*self.args, **self.kwargs)
            end = time.perf_counter()
            self.results.append(end - start)

    def stats(self):
        return {
            'min': min(self.results),
            'max': max(self.results),
            'mean': statistics.mean(self.results),
            'median': statistics.median(self.results),
            'stdev': statistics.stdev(self.results) if len(self.results) > 1 else 0.0
        }


def main():
    benchmarks = [
        Benchmark(example_function_1, 'example_function_1', args=[1000000], runs=7),
        Benchmark(example_function_2, 'example_function_2', args=[100000], runs=7)
    ]

    results = {}

    for bm in benchmarks:
        bm.run()
        results[bm.name] = {
            'runs': bm.runs,
            'timings': bm.results,
            'stats': bm.stats()
        }

    # Save baseline results
    os.makedirs('benchmarks/results', exist_ok=True)
    baseline_path = 'benchmarks/results/performance_baseline.json'
    with open(baseline_path, 'w') as f:
        json.dump(results, f, indent=4)

    print(f'Benchmark completed. Baseline saved to {baseline_path}')


if __name__ == '__main__':
    main()
