# sysctl profile `web`

Tuning for web servers, API gateways, load balancers and reverse proxies (NGINX, Apache HTTPD, HAProxy, Envoy, Traefik, ..). These workloads are characterised by a high number of concurrent and short-lived connections, large accept/SYN bursts, and a lot of outbound connections when acting as a proxy.

This profile targets performance; stack others for security hardening (see "Security hardening" below). All values can be overridden with `sysctl_linux_parameters`; set a value to `null` to stop managing it.


## Auto-calculation

Some values are derived from the system's RAM (`ansible_facts['memtotal_mb']`, in MiB) so the profile fits small and large machines alike:

| Parameter | Formula | Rationale |
|-----------|---------|-----------|
| `fs.file-max` | `max(RAM_MiB * 100, 100000)` | Scale the system-wide FD limit with memory, never below 100k. |
| `net.core.rmem_max`, `net.core.wmem_max` | `min(RAM_bytes / 128, 16 MiB)` | Allow large socket buffers without letting them dominate RAM; 16 MiB is plenty for LAN/WAN web traffic. |


## Connection handling

| Parameter | Value | Why |
|-----------|-------|-----|
| `net.core.somaxconn` | `65535` | Upper bound for an app's `listen()` backlog (completed-handshake queue). The default (4096 on recent kernels) silently caps high-traffic servers. The application must also pass a large backlog to `listen()` to benefit. |
| `net.ipv4.tcp_max_syn_backlog` | `65535` | Half-open (SYN_RECV) queue size; absorbs connection bursts and SYN spikes. |
| `net.core.netdev_max_backlog` | `65535` | Packets queued per CPU when the NIC ingests faster than the stack drains. |
| `fs.file-max` | auto | Each socket consumes a file descriptor; busy proxies need millions. |
| `fs.nr_open` | `2097152` | Per-process FD ceiling, raised above the `1048576` default so a service's systemd `LimitNOFILE` / PAM `nofile` can be set higher. Note: this only raises the ceiling; the service's own limit still has to be raised separately. |


## TCP

| Parameter | Value | Why |
|-----------|-------|-----|
| `net.ipv4.tcp_fin_timeout` | `15` | Shorter FIN-WAIT-2 frees resources from half-closed connections faster. |
| `net.ipv4.tcp_tw_reuse` | `2` | Loopback-only TIME-WAIT reuse; see below. |
| `net.ipv4.tcp_max_tw_buckets` | `262144` | Bound the number of TIME_WAIT sockets to avoid memory exhaustion. |
| `net.ipv4.ip_local_port_range` | `16384 65535` | Widen the ephemeral port pool for outbound/upstream connections, while keeping the floor clear of most registered service ports. Use `net.ipv4.ip_local_reserved_ports` to carve out specific ports. |
| `net.ipv4.tcp_slow_start_after_idle` | `0` | Keep the congestion window after idle periods, better for keep-alive/HTTP-2 connections. |
| `net.ipv4.tcp_syncookies` | `1` | Survive SYN-flood conditions without dropping legitimate clients (a fallback, not a load-scaling mechanism). |


### TIME-WAIT reuse (`tcp_tw_reuse`)

The knob is an integer: `0` = off, `1` = global reuse, `2` = reuse for **loopback traffic only**. It only ever affects **outbound** connections, and is protected by TCP timestamps (RFC 1323). The kernel changed the default from `0` to `2` ([commit 79e9fed46038](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=79e9fed460385a3d8ba0b5782e9e74405cb199b1)).

We set `2` deliberately rather than `1`: global reuse is discouraged as a blanket setting. As [Bernat](https://vincent.bernat.ch/en/blog/2014-tcp-time-wait-state-linux) explains, the robust fix for ephemeral-port/TIME-WAIT exhaustion is **more quadruplets** (ephemeral ports, client/server IPs), not aggressive TIME-WAIT reuse. Value `2` safely covers the common reverse-proxy→`127.0.0.1` backend case; if you proxy to many *remote* upstreams and have measured a need, raise it to `1` via `sysctl_linux_parameters`. (The genuinely dangerous, NAT-breaking knob was `tcp_tw_recycle`, removed in Linux 4.12; this profile never sets it.)


## Security hardening

This profile is optimized for performance and does **not** include security hardening. Stack [`hardening-default`](./hardening-default.md) to enable shared safe defaults for networking, kernel, and filesystem settings, for example `["hardening-default", "web"]`. You can also add [`hardening-extra`](./hardening-extra.md) for stricter hardening, but it may break compatibility, so test thoroughly before using it in production.


## Connection tracking is out of scope

Sizing `net.netfilter.nf_conntrack_*` is intentionally **not** part of this profile, and it loads no kernel modules. Connection tracking only matters when a stateful firewall/NAT is in the packet path; coupling a plain web server to it would force per-flow tracking it may not otherwise have. If this host is also a stateful firewall or NAT/LB, stack the `router` profile (`["web", "router"]`) or set `nf_conntrack_*` via `sysctl_linux_parameters`.


## References

- Linux kernel networking sysctl documentation: <https://www.kernel.org/doc/Documentation/networking/ip-sysctl.txt>
- Vincent Bernat, Coping with the TCP TIME-WAIT state on busy Linux servers: <https://vincent.bernat.ch/en/blog/2014-tcp-time-wait-state-linux>
- Kernel commit 79e9fed46038 (tcp_tw_reuse loopback default): <https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=79e9fed460385a3d8ba0b5782e9e74405cb199b1>
