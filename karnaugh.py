class KarnaughMinTerm:
    def __init__(self, size: int = 1,  value: int = 2):
        self._pattern = []
        for i in range(size):
            self._pattern.append(value%2 == 1)
            value = int(value / 2)

    @classmethod
    def from_pattern(cls, pattern: list):
        if set(pattern) != {True, False}:
            print("Invalid boolean pattern")
            return None
        value = 0
        for i in pattern:
            value = (value << 1) | int(i)
        return cls(len(pattern), value)

    @property
    def value(self):
        value = 0
        for i in self._pattern:
            value = (value << 1) | int(i)
        return value

    @property
    def pattern(self):
        return self._pattern

    def __eq__(self, other):
        if isinstance(other, KarnaughMinTerm):
            return self._pattern == other._pattern
        return False

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash((len(self._pattern), self.value))

    def __len__(self):
        return len(self._pattern)

    def __getitem__(self, item: int):
        return self._pattern[item]

    def remove(self, to_remove: int):
        if to_remove < len(self):
            del self._pattern[to_remove]

    def reorder(self, new_order:list):
        pattern = [self._pattern[x] for x in new_order]
        self._pattern = pattern


class KarnaughMap:
    def __init__(self, size: int = 1, value: int = 1):
        self._k_map = {KarnaughMinTerm(size, index) for index, x in enumerate(bin(value)[2:]) if int(x) == 1}
        self._size = size

    @classmethod
    def deep_copy(cls, other):
        if not isinstance(other, KarnaughMap):
            return None
        return cls(other.size, other.value)

    @property
    def value(self):
        return sum([x.value for x in self._k_map])

    @property
    def size(self):
        return self._size

    def add_by_value(self, value: int):
        to_add = KarnaughMinTerm(self.size, value)
        self._k_map.add(to_add)

    def add_by_pattern(self, pattern: list):
        to_add = KarnaughMinTerm.from_pattern(pattern)
        if to_add is None:
            return
        if len(to_add) != self.size:
            print("Pattern to add does not match size")
            return
        self._k_map.add(to_add)

    def __getitem__(self, item: int):
        temp = KarnaughMinTerm(self.size, item)
        if temp in self._k_map:
            return True
        return False

    def evaluate(self, item: list):
        temp = KarnaughMinTerm.from_pattern(item)
        if temp is None:
            return None
        return temp in self._k_map

    def __invert__(self):
        c_value = 2 ** self.size - 1 - self.value
        return KarnaughMap(self.size, c_value)

    def __hash__(self):
        return hash((self.size, self.value))

    def __eq__(self, other):
        if not isinstance(other, KarnaughMap):
            return False
        return self._k_map == other._k_map

    def __ne__(self, other):
        return not self == other

    def reorder(self, new_order: list):
        for k in self._k_map:
            k.reorder(new_order)






