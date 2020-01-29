from collections import deque

POSITIVE_SLOPE = 1
NEGATIVE_SLOPE = 0


class Indicator:
    def __init__(self, params=None):
        if not params:
            raise

        self._name = params['name']
        self._seed_period = params['seed_period']
        self._id = params['id']
        self._args = params['args']
        self._data_type = params.get('data_type') or '*'
        self._data_key = params.get('data_key') or 'close'
        self._cache_size = params.get('cache_size')
        self.reset()

    def reset(self):
        if self._cache_size:
            self._values = deque(maxlen=self._cache_size)
        else:
            self._values = []

    def l(self):
        return len(self._values)

    def v(self):
        if len(self._values) == 0:
            return None

        return self._values[-1]

    def prev(self, n=1):
        if len(self._values) <= n:
            return None

        return self._values[-1 - n]

    def add(self, v):
        self._values.append(v)
        return v

    def update(self, v):
        if len(self._values) == 0:
            return self.add(v)

        self._values[-1] = v
        return v

    def crossed(self, target):
        if self.l() < 2:
            return False

        v = self.v()
        prev = self.prev()

        return (
            (v >= target and prev <= target) or
            (v <= target and prev >= target)
        )

    def prev_slope(self, n=1):
        prev2 = self.prev(n=n+1)
        prev3 = self.prev(n=n+2)
        if not (prev2 and prev3):
            return None

        return POSITIVE_SLOPE if prev2 > prev3 else NEGATIVE_SLOPE

    def slope(self):
        prev = self.prev()
        if not prev:
            return None

        return POSITIVE_SLOPE if self.v() > prev else NEGATIVE_SLOPE

    def is_prev_positive(self, n=1):
        return self.prev_slope(n=n) == POSITIVE_SLOPE

    def is_prev_negative(self, n=1):
        return not self.is_prev_positive(n=n)

    def is_positive(self):
        return self.slope() == POSITIVE_SLOPE

    def is_negative(self):
        return not self.is_positive()

    def is_valley(self):
        return not self.fast_ma.is_prev_positive() and self.fast_ma.is_positive()

    def is_mountaintop(self):
        return self.fast_ma.is_positive() and not self.fast_ma.is_prev_positive()

    @staticmethod
    def golden_fork(fast, slow):
        return fast.prev() < slow.prev() and fast.v() > slow.v()

    @staticmethod
    def death_fork(fast, slow):
        return fast.prev() > slow.prev() and fast.v() < slow.v()

    def ready(self):
        return len(self._values) > 0

    def get_seed_period(self):
        return self._seed_period

    def get_data_key(self):
        return self._data_key

    def get_data_type(self):
        return self._data_type
