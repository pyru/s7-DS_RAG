# Operating Systems: Core Concepts

An operating system (OS) is the software layer that manages hardware resources and provides services to applications. Understanding OS fundamentals is essential for systems programming, performance optimization, and debugging complex software behavior.

## Process Management

A **process** is a running program instance with its own address space, resources, and state.

**Process states**:
- Running: Currently executing on CPU
- Ready: Waiting to be scheduled
- Blocked/Waiting: Waiting for I/O or event

**Process Control Block (PCB)**: OS data structure storing process state, program counter, registers, memory maps, open file descriptors, and scheduling information.

### Context Switching

When the OS switches from one process to another:
1. Save current process state (registers, PC) to its PCB
2. Load next process state from its PCB
3. Switch memory mappings (TLB flush)

Context switches cost 1-100μs depending on hardware. This is why threads within a process switch faster (shared memory map, no TLB flush).

### Process Creation

```c
// UNIX: fork() creates exact copy of parent process
pid_t pid = fork();
if (pid == 0) {
    // Child process
    execv("/usr/bin/ls", args);  // Replace child image with ls
} else {
    // Parent process
    wait(NULL);  // Wait for child to complete
}
```

Python's `subprocess` module wraps these system calls.

## Threads

A **thread** is a lightweight execution unit within a process, sharing the process's memory space.

**Thread advantages**:
- Faster creation than processes (~10μs vs ~1ms)
- Fast context switching (shared memory map)
- Easy communication (shared memory vs IPC)

**Thread challenges**:
- Race conditions require synchronization (mutex, semaphore, condition variable)
- Deadlock risk when multiple locks are held
- GIL in CPython limits thread parallelism for CPU-bound work

## Memory Management

**Virtual memory**: Each process sees a private address space, mapped to physical RAM by the OS via page tables.

**Pages**: 4KB blocks (typically). Virtual-to-physical mapping stored in page tables, hardware-cached in TLB.

**Demand paging**: Pages loaded from disk only when accessed. Page faults trigger the OS to load the missing page.

**Memory hierarchy** (from fastest to largest):
L1 cache (32KB, ~1ns) → L2 (256KB, ~5ns) → L3 (16MB, ~20ns) → RAM (32GB, ~80ns) → SSD (1TB, ~100μs) → HDD (4TB, ~10ms)

## File Systems

**File system components**:
- **Superblock**: Metadata about the filesystem (size, block size, free block count)
- **inode**: Per-file metadata (permissions, timestamps, data block pointers) — NOT the filename
- **Directory**: Maps filenames to inode numbers
- **Data blocks**: Actual file content

**Journaling**: Modern file systems (ext4, NTFS, APFS) keep a journal of pending changes, enabling fast recovery after crashes without full fsck.

**Copy-on-Write (CoW)**: ZFS and Btrfs write new data to new blocks before updating pointers — no in-place modification means atomicity and easy snapshots.

## Scheduling

The **scheduler** decides which ready process runs next:

- **FIFO**: Simple, no starvation, poor for interactive workloads
- **Round Robin**: Each process gets a time quantum (5-20ms); fair but high overhead if quantum is small
- **CFS (Completely Fair Scheduler)**: Linux default; tracks "virtual runtime" per process; always runs the least-run process
- **Priority scheduling**: Higher-priority processes preempt lower-priority; risk of starvation (solved by aging)
- **MLFQ (Multi-Level Feedback Queue)**: New processes start at high priority; if they use full quantum, demoted; favors interactive workloads

## System Calls

System calls are the interface between user space and kernel space:

```python
# Python's os module wraps system calls
import os

pid = os.getpid()           # getpid()
children = os.fork()        # fork()
os.execv("/bin/ls", ["ls"]) # execv()
fd = os.open("file.txt", os.O_RDONLY)  # open()
data = os.read(fd, 1024)    # read()
```

System call overhead: ~100ns for a simple call (user→kernel mode switch, argument validation, return).
