# sysctl profile `redis`

Tuning for **Redis** (and API-compatible in-memory stores like Valkey/KeyDB). Redis is single-threaded with a large in-memory dataset and forks a child for background persistence (RDB snapshots, AOF rewrite), so the two things that matter most at the kernel level are **memory overcommit** (so the fork cannot fail) and a **high accept backlog**.

This profile targets performance; stack others for security hardening (see "Security hardening" below). All values can be overridden with `sysctl_linux_parameters`; set a value to `null` to stop managing it.


## Redis specifics

| Parameter | Value | Why |
|-----------|-------|-----|
| `vm.overcommit_memory` | `1` | **Required by Redis.** Background saves `fork()` and rely on copy-on-write; under heuristic (`0`) or strict (`2`) overcommit the fork can fail under memory pressure, breaking persistence. Redis logs a startup warning if this is not `1`. |
| `net.core.somaxconn` | `65535` | Redis's `tcp-backlog` is silently capped by `somaxconn`; raise it so a high `tcp-backlog` takes effect under connection bursts. |


## Memory & write-back

| Parameter | Value | Why |
|-----------|-------|-----|
| `vm.swappiness` | `10` | Avoid swapping the dataset (swapped keys cause severe latency) while keeping swap as a safety valve. |
| `vm.vfs_cache_pressure` | `50` | Retain inode/dentry caches longer. |
| `vm.zone_reclaim_mode` | `0` | Disable NUMA zone reclaim (latency spikes on multi-socket hosts). |
| `vm.dirty_background_bytes`, `vm.dirty_bytes` | `min(RAM/20, 1 GiB)` / `min(RAM/10, 4 GiB)` | **Byte-based** write-back caps so an AOF rewrite / RDB save does not build a huge dirty-page backlog and stall. Setting `*_bytes` disables the `*_ratio` knobs (mutually exclusive). |
| `fs.aio-max-nr` | `1048576` | Headroom for background persistence I/O. |


## Security hardening

This profile is optimized for performance and does **not** include security hardening. Stack [`hardening-default`](./hardening-default.md) to enable shared safe defaults for networking, kernel, and filesystem settings, for example `["hardening-default", "redis"]`. You can also add [`hardening-extra`](./hardening-extra.md) for stricter hardening, but it may break compatibility, so test thoroughly before using it in production.


## Scope limitations

- **Transparent Huge Pages (THP)**: Redis strongly recommends **disabling** THP, which causes latency and fork-time copy-on-write memory blow-up. THP lives under `/sys/kernel/mm/transparent_hugepage/` (not a sysctl) — **out of scope** here; disable it separately.
- **File-descriptor limit**: Redis caps `maxclients` to the process `RLIMIT_NOFILE`; raise the service's systemd `LimitNOFILE` (not a sysctl) if you need many clients.


## References

- Redis: Administration: <https://redis.io/docs/management/admin/>
