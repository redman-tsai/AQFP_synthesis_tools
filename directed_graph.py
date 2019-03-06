from abc import ABC, abstractmethod


class Vertex(ABC):
    @abstractmethod
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def get_parents(self) -> set:
        pass

    @abstractmethod
    def get_children(self) -> set:
        pass

    def get_spouse_to(self, other) -> set:
        if not isinstance(other, Vertex):
            return set()
        if other not in self.get_children():
            return set()
        spouse = other.get_parents()
        spouse.remove(self)
        return spouse

    def get_ancestors(self, level) -> set:
        ancestors = self.get_parents()
        if level == 1:
            return ancestors
        if ancestors == set():
            return ancestors
        for parent in self.get_parents():
            ancestors.update(parent.get_ancestors(level - 1))
        return ancestors

    def is_descendent_of(self, other) -> bool:
        if not isinstance(other, Vertex):
            return False
        if other in self.get_parents():
            return True
        for parent in self.get_parents():
            if parent.is_decedent_of(other):
                return True
        return False


