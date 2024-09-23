from dataclasses import dataclass


@dataclass
class Setting:
    name: str
    type: type
    description: str

    def __iter__(self):
        self.iterator = [self.description, self.type, self.name]
        return self

    def __next__(self):
        if self.iterator:
            x = self.iterator.pop()
            return x
        else:
            raise StopIteration
