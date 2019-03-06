from abstract_net_model import LogicBlock
from module import Module
from wires import Wire
from typing import List, Set

majority_primary_gates = [
            0, 255,
            170, 85, 204, 51, 240, 15,
            136, 119, 160, 95, 192, 63,
            34, 221, 10, 245, 12, 243,
            17, 238, 5, 250, 3, 252,
            68, 187, 80, 175, 48, 207,
            232, 23, 212, 43, 178, 77, 142, 113
]

majority_primary_truth = [
            None, None,
            2, 1, 2, 1, 2, 1,
            8, 7, 8, 7, 8, 7,
            2, 13, 2, 13, 2, 13,
            1, 14, 1, 14, 1, 14,
            4, 11, 4, 11, 4, 11,
            232, 23, 212, 43, 178, 77, 142, 113
        ]

majority_primary_inputs = [
            [], [],
            [1], [1], [2], [2], [3], [3],
            [1, 2], [1, 2], [1, 3], [1, 3], [2, 3], [2, 3],
            [1, 2], [1, 2], [1, 3], [1, 3], [2, 3], [2, 3],
            [1, 2], [1, 2], [1, 3], [1, 3], [2, 3], [2, 3],
            [1, 2], [1, 2], [1, 3], [1, 3], [2, 3], [2, 3],
            [1, 2, 3], [1, 2, 3], [1, 2, 3], [1, 2, 3], [1, 2, 3], [1, 2, 3], [1, 2, 3], [1, 2, 3]
]


def majority_convert(target: int, min_width: int = 3):
    results = set()
    total = len(majority_primary_gates)
    for i in range(total):
        for j in range(i + 1, total):
            for k in range(j + 1, total):
                truths = [majority_primary_gates[j], majority_primary_gates[j], majority_primary_gates[k]]
                mapped = True
                for item in range(8):
                    values = sum(x % 2 for x in truths)
                    if target % 2 == 1 and values <= 1:
                        mapped = False
                        break
                    if target % 2 == 0 and values >= 2:
                        mapped = False
                        break
                    truths = [int(v / 2) for v in truths]
                    target = int(target / 2)
                if mapped:
                    results.add(MajorityMap.create([i, j, k]))
    if len(results) == 0:
        return
    width = min(x.final_width for x in results)
    if width < min_width:
        return
    min_size = min(x.size for x in results)
    return {x for x in results if x.size == min_size}


class MajorityMap:
    def __init__(self):
        self._selection = list()

    @classmethod
    def create(cls, selection: List[int]):
        if len(selection) != 3:
            return
        maj = cls()
        maj._selection = selection
        maj._selection.sort(key=lambda x: x)
        return maj

    def __eq__(self, other):
        if not isinstance(other, MajorityMap):
            return False
        return self.__hash__() == other.__hash__()

    def __hash__(self):
        return hash(';'.join(str(x) for x in self._selection))

    @property
    def selection(self):
        return self._selection

    @property
    def gates(self):
        return [majority_primary_gates[x] for x in self._selection]

    @property
    def reduced(self):
        return [int(x / 2) for x in self._selection]

    @property
    def final_width(self):
        return sum(x > 1 for x in self._selection)

    @property
    def size(self):
        return sum(x > 7 for x in self._selection)


class MajorityBlock(LogicBlock):
    def __init__(self, parent: Module, source: Wire, inputs: List[Wire], combinations: Set[MajorityMap]):
        name = "{}_pre_majority".format(source.name)
        super().__init__(name, parent)
        self._inputs = inputs
        self._output = source
        self._combo = combinations

    @property
    def input_pins(self):
        return self._inputs

    @property
    def output_pins(self):
        return {self._output}

    def get_delay(self, other: str = None):
        return 0

    def gate_count(self):
        return 0

    def to_verilog(self):
        return "\tMajority_block"

    def cell_mapping(self, library):
        pass

