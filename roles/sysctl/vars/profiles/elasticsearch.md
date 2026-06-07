# sysctl profile `elasticsearch`

Tuning for Elasticsearch / OpenSearch (Lucene-based search engines). Lucene memory-maps a very large number of index segment files, so the defining kernel requirement is a high `vm.max_map_count`; beyond that the profile applies a swap-averse memory policy, bounded write-back and high file-descriptor limits.

This profile targets performance; stack others for security hardening (see "Security hardening" below). All values can be overridden with `sysctl_linux_parameters`; set a value to `null` to stop managing it.


## Elasticsearch specifics

| Parameter | Value | Why |
|-----------|-------|-----|
| `vm.max_map_count` | `262144` | **Mandatory.** Lucene `mmap`s many segment files; the `65530` default is far too low and Elasticsearch fails its bootstrap check (refuses to start) below `262144`. |
| `fs.file-max`, `fs.nr_open` | auto / `2097152` | Many shards/segments and clients keep many files open; `fs.nr_open` raises the ceiling a service's systemd `LimitNOFILE` can reach (still set the service limit, e.g. `65535`+). |


## Memory & write-back

| Parameter | Value | Why |
|-----------|-------|-----|
| `vm.swappiness` | `10` | Avoid swapping the heap and the page cache used for mmap'd segments. |
| `vm.vfs_cache_pressure` | `50` | Retain inode/dentry caches longer. |
| `vm.zone_reclaim_mode` | `0` | Disable NUMA zone reclaim (latency spikes on multi-socket hosts). |
| `vm.dirty_background_bytes`, `vm.dirty_bytes` | `min(RAM/20, 1 GiB)` / `min(RAM/10, 4 GiB)` | **Byte-based** write-back caps for steady merge/refresh I/O instead of RAM-percentage ratios. Setting `*_bytes` disables the `*_ratio` knobs (mutually exclusive). |
| `fs.aio-max-nr` | `1048576` | Headroom for async I/O across many shards. |


## Security hardening

This profile is optimized for performance and does **not** include security hardening. Stack [`hardening-default`](./hardening-default.md) to enable shared safe defaults for networking, kernel, and filesystem settings, for example `["hardening-default", "elasticsearch"]`. You can also add [`hardening-extra`](./hardening-extra.md) for stricter hardening, but it may break compatibility, so test thoroughly before using it in production.


## Scope limitation: swap

Elasticsearch recommends **disabling swap entirely**, or locking the heap into memory (`bootstrap.memory_lock: true` plus the matching service `LimitMEMLOCK`). `vm.swappiness=10` strongly discourages swapping but does not disable it; if you want swap fully off, manage that separately (it is not a sysctl). Memory locking also needs the service-level `MEMLOCK` limit, not a sysctl.


## References

- Elasticsearch: Virtual memory (`vm.max_map_count`): <https://www.elastic.co/guide/en/elasticsearch/reference/current/vm-max-map-count.html>
- Elasticsearch: Disable swapping: <https://www.elastic.co/guide/en/elasticsearch/reference/current/setup-configuration-memory.html>
