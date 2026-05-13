import os
import plistlib
import threading


DEFAULT_READ_CHUNK_SIZE = 1024 * 1024
DEFAULT_MAX_BUFFER_SIZE = 32 * 1024 * 1024


class PowermetricsReader:
    def __init__(self, process, parse_plist, read_chunk_size=DEFAULT_READ_CHUNK_SIZE,
                 max_buffer_size=DEFAULT_MAX_BUFFER_SIZE):
        self.process = process
        self.parse_plist = parse_plist
        self.read_chunk_size = max(1, int(read_chunk_size))
        self.max_buffer_size = max(1, int(max_buffer_size))
        self._buffer = b''
        self._latest = False
        self._lock = threading.Lock()
        self._thread = threading.Thread(target=self._read_stdout, daemon=True)
        self._thread.start()

    def latest(self):
        with self._lock:
            return self._latest

    def terminate(self):
        if self.process.poll() is None:
            self.process.terminate()
        if self.process.stdout is not None:
            try:
                self.process.stdout.close()
            except Exception:
                pass
        self._thread.join(timeout=1)

    def _set_latest(self, reading):
        with self._lock:
            self._latest = reading

    def _parse_record(self, record):
        if not record.strip() or len(record) > self.max_buffer_size:
            return
        try:
            self._set_latest(self.parse_plist(plistlib.loads(record)))
        except Exception:
            pass

    def _read_stdout(self):
        if self.process.stdout is None:
            return

        while True:
            try:
                chunk = os.read(self.process.stdout.fileno(), self.read_chunk_size)
            except Exception:
                break
            if not chunk:
                break

            self._buffer += chunk
            records = self._buffer.split(b'\x00')
            self._buffer = records.pop()

            for record in records:
                self._parse_record(record)

            if len(self._buffer) > self.max_buffer_size:
                self._buffer = b''

        self._parse_record(self._buffer)
