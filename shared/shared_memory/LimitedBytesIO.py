import io
from typing import override


class LimitedBytesIO(io.BytesIO):
    def __init__(self, max_size, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_size = max_size

    @override
    def write(self, b):
        b_len = len(b)
        current_len = self.getbuffer().nbytes
        if b_len > self.max_size:
            # Only keep the last max_size bytes of b
            b = b[-self.max_size:]
            b_len = self.max_size
            self.seek(0)
            self.truncate(0)
            super().write(b)
            return b_len
        if current_len + b_len > self.max_size:
            # Discard oldest data to make room
            overflow = current_len + b_len - self.max_size
            self.seek(overflow)
            remaining = self.read()
            self.seek(0)
            self.truncate(0)
            super().write(remaining)
        self.seek(0, io.SEEK_END)
        return super().write(b)