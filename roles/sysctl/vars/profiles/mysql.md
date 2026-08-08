# sysctl profile `mysql`

Tuning for **MySQL and MariaDB** servers. The InnoDB engine keeps a large buffer pool, opens many table/tablespace files, and uses native asynchronous I/O (libaio), so this profile favours a swap-averse memory policy, bounded write-back, AIO headroom and high file-descriptor limits.

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
| `vm.swappiness` | `10` | Avoid swapping the buffer pool while still allowing swap as a safety valve. |
| `vm.vfs_cache_pressure` | `50` | Retain inode/dentry caches longer: many table handles. |
| `vm.zone_reclaim_mode` | `0` | Disable NUMA zone reclaim (latency spikes on multi-socket hosts). |
| `vm.dirty_background_bytes`, `vm.dirty_bytes` | auto | **Byte-based** write-back limits replace the RAM-percentage ratios so large-RAM hosts do not accumulate tens of GiB of dirty pages and stall on flush. Setting `*_bytes` disables the `*_ratio` knobs (mutually exclusive). Tune to your storage. |
| `fs.aio-max-nr` | `1048576` | InnoDB native AIO (`innodb_use_native_aio`, libaio) submits many concurrent requests. Not used by io_uring. |
| `fs.file-max`, `fs.nr_open` | auto / `2097152` | High open-file limits for many tables/connections; `fs.nr_open` only raises the ceiling a service's systemd `LimitNOFILE` can reach (still set the service limit). |


## Security hardening

This profile is optimized for performance and does **not** include security hardening. Stack [`hardening-default`](./hardening-default.md) to enable shared safe defaults for networking, kernel, and filesystem settings, for example `["hardening-default", "mysql"]`. You can also add [`hardening-extra`](./hardening-extra.md) for stricter hardening, but it may break compatibility, so test thoroughly before using it in production.


## Scope limitation: Transparent Huge Pages

MySQL/MariaDB and especially InnoDB are sensitive to **Transparent Huge Pages (THP)**, which can cause latency spikes; most guidance recommends disabling THP. THP is controlled via `/sys/kernel/mm/transparent_hugepage/` (not a sysctl) and is therefore **out of scope**; manage it separately (tuned, a `systemd` unit, or a kernel boot parameter).


## References

- MySQL: `innodb_use_native_aio`: <https://dev.mysql.com/doc/refman/en/innodb-parameters.html#sysvar_innodb_use_native_aio>
- MariaDB: Configuring Linux for MariaDB: <https://mariadb.com/kb/en/configuring-linux-for-mariadb/>
