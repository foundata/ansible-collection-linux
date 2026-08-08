# sysctl profile `postgresql`

Tuning for PostgreSQL database servers. PostgreSQL keeps a large working set resident and relies on the OS page cache for most caching, so it benefits from a swap-averse memory policy, bounded write-back to avoid checkpoint/fsync stalls, and high file-descriptor limits for many backends and relation files.

This profile targets performance; stack others for security hardening (see "Security hardening" below). All values can be overridden with `sysctl_linux_parameters`; set a value to `null` to stop managing it.


## Auto-calculation

| Parameter | Formula | Rationale |
|-----------|---------|-----------|
| `fs.file-max` | `max(RAM_MiB * 100, 100000)` | Scale the system-wide FD limit with memory, never below 100k. |
| `vm.dirty_background_bytes` | `min(RAM_bytes / 20, 1 GiB)` | Start background flushing at a fixed, bounded amount of dirty data. |
| `vm.dirty_bytes` | `min(RAM_bytes / 10, 4 GiB)` | Hard cap on dirty data, bounded regardless of RAM. |


## Memory & write-back

| Parameter | Value | Why |
|-----------|-------|-----|
| `vm.swappiness` | `10` | Avoid swapping the working set while still allowing swap as a safety valve. |
| `vm.vfs_cache_pressure` | `50` | Retain inode/dentry caches longer: PostgreSQL touches many relation files. |
| `vm.zone_reclaim_mode` | `0` | Disable NUMA zone reclaim, which causes latency spikes on multi-socket hosts. |
| `vm.dirty_background_bytes`, `vm.dirty_bytes` | auto | Byte-based write-back limits replace the RAM-percentage `dirty_ratio`/`dirty_background_ratio`. On large-RAM hosts a 40%/10% ratio means tens of GiB of dirty pages and multi-second stalls when flushed; a fixed ceiling keeps checkpoints smooth. Setting `*_bytes` automatically disables the `*_ratio` knobs (they are mutually exclusive). Tune to your storage. |
| `fs.aio-max-nr` | `1048576` | Headroom for libaio (used by prefetch / `effective_io_concurrency`). Helps libaio, not io_uring. |
| `fs.file-max`, `fs.nr_open` | auto / `2097152` | High open-file limits; `fs.nr_open` raises the ceiling that a service's systemd `LimitNOFILE` can reach (still set the service limit separately). |


## Security hardening

This profile is optimized for performance and does **not** include security hardening. Stack [`hardening-default`](./hardening-default.md) to enable shared safe defaults for networking, kernel, and filesystem settings, for example `["hardening-default", "postgresql"]`. You can also add [`hardening-extra`](./hardening-extra.md) for stricter hardening, but it may break compatibility, so test thoroughly before using it in production.


## Scope limitations

- **System V shared memory** (`kernel.shmmax`/`shmall`) is intentionally **not** set: PostgreSQL ≥ 9.3 uses POSIX/mmap shared memory, so the legacy SysV limits no longer constrain `shared_buffers`, and the modern kernel default is effectively unlimited (setting it would only lower it).
- **HugePages** (`vm.nr_hugepages`) can help large `shared_buffers`, but the right value is deployment-specific and pairs with `huge_pages=try|on` in `postgresql.conf`, so it is out of scope here; manage it explicitly if you use it.


## References

- PostgreSQL: Managing Kernel Resources: <https://www.postgresql.org/docs/current/kernel-resources.html>
