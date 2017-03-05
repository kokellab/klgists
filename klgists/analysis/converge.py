import warnings
import numpy as np
from typing import Iterable, Mapping, Callable, Any, Tuple
def converge(sampler: Callable[[None], Iterable[float]],
                             statistic:Callable[[np.ndarray], float]=np.mean,
                             ε:float=0.01, min_iters:int=3, max_iters:int=50,
                             noter:Callable[[int, float, float, Iterable[float]], Any]=lambda i, estimate, delta, samples: print('Iteration {}: {:.3f}, δ=={:.3f}'.format(i, estimate, delta))
            ) -> Tuple[float, Iterable[float]]:
    """Repeatedly sample something until the mean (or other statistic) converges to within ε.
    
    Example usage:
        import numpy as np
        x = np.arange(101)
        samples, estimate = converge(lambda: np.random.choice(x, 40))
        print("{:.5f}".format(estimate))
    Example output:
        Iteration 1: 54.225, δ==inf
        Iteration 2: 52.538, δ==0.031
        Iteration 3: 50.883, δ==0.031
        Iteration 4: 50.269, δ==0.012
        Iteration 5: 51.765, δ==0.030
        Iteration 6: 51.880, δ==0.002
        51.879

    Arguments:
        sampler: A function that takes nothing and returns a list of new samples
        statistic: A function that returns an estimate from the list of samples (including those from previous iterations);
            Should probably be either numpy.mean or numpy.median
        ε: The maximal fractional change from the previous estimate at which to halt
        min_iters: Perform at least this many iterations
        max_iters: Halt after this many iterations and warn with a string starting with "Estimatation exceeded"
        noter: Optional function that takes, in order, the iteration index, the current estimate,
            the change in the estimate from the previous, and the samples;
            This is most notably important if the estimates take a long time to compute and should be written to disk

    Returns:
        A 2-tuple containing, in order, the estimate and all of the samples
    """
    prev_estimate = None
    δ = float('+Inf')
    collected_samples = []
    i = 0
    while δ > ε and i <= max_iters or i < min_iters:
        samples = sampler()
        collected_samples.extend(samples)
        current_estimate = statistic(collected_samples)
        if prev_estimate is not None:
            δ = abs(current_estimate - prev_estimate) / prev_estimate
        prev_estimate = current_estimate
        i += 1
        if noter is not None:
            noter(i, current_estimate, δ, samples)
    if i >= max_iters:
        warnings.warn('Estimatation exceeded max_iters=={} without converging'.format(max_iters))
    return collected_samples, statistic(collected_samples)
