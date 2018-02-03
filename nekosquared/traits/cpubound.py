"""
Trait that implements a process pool execution service for CPU-bound work.

This is more costly to run than a thread, as it is essentially spawning a new
process on the operating system each time we start one, however, these are
cancellable. Generally this should only be used if work is very slow and
consists mainly of CPU-based work.
"""

from nekosquared.shared import magic

# Max process pool size.
PROCESS_POOL_SIZE = magic.magic_number(cpu_bound=True)


