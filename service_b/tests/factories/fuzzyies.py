import random
import string

from factory.fuzzy import BaseFuzzyAttribute

SERIAL_ID_REGEX = r"^[a-zA-Z0-9]{6,}$"


class FuzzySerialID(BaseFuzzyAttribute):
    """Генерирует строку 6-10 символов в формате [a-zA-Z0-9]"""

    def __init__(self, min_len: int = 6, max_len: int = 10, **kw):
        super().__init__(**kw)
        self.min_len, self.max_len = min_len, max_len

    def fuzz(self) -> str:
        length = random.randint(self.min_len, self.max_len)
        alphabet = string.ascii_letters + string.digits
        return "".join(random.choices(alphabet, k=length))


class FuzzyCred(BaseFuzzyAttribute):

    def fuzz(self):
        return "".join(
            random.choices(
                string.ascii_lowercase,
                k=random.randint(6, 12),
            )
        )
