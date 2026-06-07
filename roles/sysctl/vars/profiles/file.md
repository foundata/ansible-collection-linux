# sysctl profile `file`

Tuning for file servers and backup targets (NFS, Samba/CIFS, SFTP, rsync, borg/restic, ..). These workloads move large amounts of data over the network and to/from storage and serve many client connections, so they benefit from large *maximum* socket buffers, throughput-oriented TCP options, larger accept/ingress queues and bounded write-back.

This profile targets performance; stack others for security hardening (see "Security hardening" below). All values can be overridden with `sysctl_linux_parameters`; set a value to `null` to stop managing it.


## Auto-calculation

| Parameter | Formula | Rationale |
|-----------|---------|-----------|
| `net.core.rmem_max`, `net.core.wmem_max` | `min(RAM_bytes / 128, 16 MiB)` | Allow large socket buffers for high bandwidth-delay-product transfers without dominating RAM. |
| `net.ipv4.tcp_rmem`, `net.ipv4.tcp_wmem` | `4096 <default> <rmem_max>` | TCP autotuning `min default max`; **only the max is raised** (kept in sync with `*_max`). |
| `fs.file-max` | `max(RAM_MiB * 100, 100000)` | Scale the system-wide FD limit with memory for many open client files. |
| `vm.dirty_background_bytes` / `vm.dirty_bytes` | `min(RAM/20, 1 GiB)` / `min(RAM/10, 4 GiB)` | Byte-based, bounded write-back. |

A deliberate change from a naive throughput profile: the per-socket **default** buffers (`net.core.rmem_default`/`wmem_default` and the middle value of `tcp_rmem`/`tcp_wmem`) are **left at the kernel defaults**. Raising the *default* reserves memory on *every* socket, which bloats memory on a server with thousands of SMB/NFS clients; only the autotuning *maximum* is raised, so connections that actually need large windows can grow into them. Note also that the 16 MiB cap is conservative for very high-BDP WAN transfers (e.g. 10 GbE across continents) — raise `*_max` via `sysctl_linux_parameters` there.


## TCP throughput

| Parameter | Value | Why |
|-----------|-------|-----|
| `net.ipv4.tcp_mtu_probing` | `1` | Enable Packetization-Layer Path MTU Discovery **after an ICMP black hole is detected**. This does **not** proactively use jumbo frames; it prevents PMTU black-hole stalls. |
| `net.ipv4.tcp_slow_start_after_idle` | `0` | Keep the congestion window between bursts/transfers. |
| `net.ipv4.tcp_syncookies` | `1` | Survive SYN-flood conditions (a fallback, not a load-scaling mechanism). |

`tcp_window_scaling`, `tcp_timestamps` and `tcp_sack` are **not managed**: they are default-on on every modern kernel, so asserting them would be noise rather than tuning.


## Connection handling & I/O

| Parameter | Value | Why |
|-----------|-------|-----|
| `net.core.somaxconn` | `65535` | Larger accept queue for many concurrent clients. |
| `net.core.netdev_max_backlog` | `65535` | Ingress queue for high-throughput NICs (matters more here than on a typical web server). |
| `fs.aio-max-nr` | `1048576` | Headroom for outstanding async I/O (libaio). |
| `fs.inotify.max_user_watches` | `524288` | Large trees watched by sync/backup tools (Syncthing, lsyncd). |
| `fs.inotify.max_user_instances` | `1024` | Many concurrent inotify instances across users/services. |
| `vm.vfs_cache_pressure` | `50` | Retain inode/dentry caches longer — fileservers walk huge directory trees (the kernel default `100` is a no-op for this workload). |


## Security hardening

This profile targets performance and does **not** apply security hardening. Stack [`hardening-default`](./hardening-default.md) (shared network/kernel/filesystem safe defaults) before it — e.g. `["hardening-default", "file"]` — and optionally [`hardening-extra`](./hardening-extra.md) for stricter kernel hardening.


## References

- ESnet Fasterdata — Linux Host Tuning: <https://fasterdata.es.net/host-tuning/linux/>
