# sysctl profile `container`

Tuning for **container hosts with rootful/bridged networking** (Docker, rootful Podman/netavark, and single nodes running containerd/CRI-O or Kubernetes). Hosts running only rootless containers with user-mode networking (Podman with pasta or slirp4netns) never bridge or NAT container traffic; use the far smaller [`container-rootless`](./container-rootless.md) profile there instead. To its containers, such a host acts as a NAT router and bridge switch, it needs IP forwarding, bridged traffic traversing the host firewall, a connection-tracking table sized for many masqueraded flows and neighbor tables sized for many veth peers. At the same time it is a dense multi-process host where per-UID kernel quotas (inotify, keyrings) that are generous for one workload are quickly exhausted by hundreds of containers sharing a UID.

This profile targets container host function; stack others for security hardening (see "Security hardening" below). All values can be overridden with `sysctl_linux_parameters`; set a value to `null` to stop managing it.


## Kernel modules

The profile depends on two kernel modules, loaded best-effort (persistently, via `community.general.modprobe`) when it is selected:

- `nf_conntrack` provides the `net.netfilter.nf_conntrack_*` keys.
- `br_netfilter` provides the `net.bridge.bridge-nf-call-*` keys.

Where a module cannot be loaded, the load is tolerated on every platform and the keys it gates are skipped with a notice (set `sysctl_linux_modules_required: true` for a hard failure instead). This happens in unprivileged containers, but also on e.g. Enterprise Linux 10 cloud images, whose running kernel cannot load `br_netfilter` (the module ships in `kernel-modules-extra`, which GenericCloud images do not install).


## IP forwarding

| Parameter | Value | Why |
|-----------|-------|-----|
| `net.ipv4.ip_forward` | `1` | Master switch for IPv4 forwarding. Rootful bridge networking (Docker's `docker0`, Podman/netavark, CNI plugins) routes and NATs container traffic through the host; Kubernetes requires it on every node. |
| `net.ipv4.conf.all.forwarding`, `net.ipv4.conf.default.forwarding` | `1` | Per-interface IPv4 forwarding (all existing and future interfaces, container veth/bridge interfaces appear and disappear at runtime). |
| `net.ipv6.conf.all.forwarding`, `net.ipv6.conf.default.forwarding` | `1` | IPv6 forwarding for dual-stack container networks (Docker with `ipv6` enabled, Podman/netavark IPv6 subnets, dual-stack Kubernetes). |

Container runtimes flip some of these at daemon start, but only at runtime and only for their own needs; setting them declaratively survives runtime changes, satisfies preflight checks (e.g. `kubeadm`) and keeps hosts consistent. If you run IPv4-only container networking, set the two `net.ipv6.*.forwarding` keys to `0` (enforce off) or `null` (unmanage) via `sysctl_linux_parameters`.


### IPv6 caveat: Router Advertisements

Enabling `net.ipv6.conf.all.forwarding` makes the kernel **stop accepting IPv6 Router Advertisements (RAs)**. If the host learns its **uplink** IPv6 address/default route via RA (SLAAC, common in cloud environments), that will break unless you set `net.ipv6.conf.<uplink>.accept_ra=2` on that specific interface via `sysctl_linux_parameters`.

Do **not** set `accept_ra=2` globally (`conf.all`/`conf.default`) on a container host: it would also apply to the container-facing bridge/veth interfaces, allowing a malicious or misbehaving container to install routes on the host by sending rogue RAs. Scope it to the uplink interface only.


## Bridge netfilter

| Parameter | Value | Why |
|-----------|-------|-----|
| `net.bridge.bridge-nf-call-iptables` | `1` | Bridged (same-bridge, L2) container traffic traverses the host's `iptables`/`nftables`. The runtimes' inter-container isolation and published-port rules only apply to such traffic when this is enabled. |
| `net.bridge.bridge-nf-call-ip6tables` | `1` | Same for IPv6. |

The [`virtualization`](./virtualization.md) profile intentionally leaves bridge netfilter "to the firewall layer, Docker, Kubernetes CNIs or your site firewall". This profile *is* that layer's host profile, so it owns the decision and turns filtering on, matching what Docker enables at daemon start and what Kubernetes setups have required on nodes. Persisting it avoids the classic trap of `iptables`-based container firewalling silently not applying to same-bridge traffic after a reboot when nothing (re)loads `br_netfilter`. It imposes a per-packet netfilter hook on bridged traffic; hosts that want raw bridge performance and handle isolation elsewhere can set both keys to `null`. `net.bridge.bridge-nf-call-arptables` is left unmanaged.


## Auto-calculation

The connection-tracking table scales with RAM (`ansible_facts['memtotal_mb']`, in MiB), using the same sizing as the [`router`](./router.md) profile.

| Parameter | Formula | Rationale |
|-----------|---------|-----------|
| `net.netfilter.nf_conntrack_max` | `RAM_MiB * 32` | Every masqueraded container connection occupies a conntrack entry (each ~300 bytes); budget ~32 entries per MiB. |
| `net.netfilter.nf_conntrack_buckets` | `conntrack_max / 4` | Hash-table bucket count sized to roughly a quarter of the max entries for a good load factor. |


## Connection tracking

| Parameter | Value | Why |
|-----------|-------|-----|
| `net.netfilter.nf_conntrack_max` | auto | NAT for container networks tracks every flow of every container in the host namespace; the default table overflows on busy hosts ("nf_conntrack: table full, dropping packet", dropped connections that are hard to attribute). |
| `net.netfilter.nf_conntrack_buckets` | auto | Keep hash-bucket count proportional to table size for fast lookups. The canonical way to size the table is the `hashsize` module parameter at module load; this sysctl resizes it after load on current kernels. |

All conntrack timeouts are left at their kernel defaults; tune them via `sysctl_linux_parameters` only against a measured problem.


## Neighbor tables (ARP / NDP)

| Parameter | Value | Why |
|-----------|-------|-----|
| `net.ipv4.neigh.default.gc_thresh1` | `1024` | Below this many entries the garbage collector never runs. |
| `net.ipv4.neigh.default.gc_thresh2` | `4096` | Soft maximum; GC becomes aggressive above it. |
| `net.ipv4.neigh.default.gc_thresh3` | `8192` | Hard maximum number of ARP entries. |
| `net.ipv6.neigh.default.gc_thresh1/2/3` | `1024/4096/8192` | Same thresholds for the IPv6 neighbor (NDP) cache. |

Every running container adds neighbor entries on the host's bridges (one veth/MAC per container, more with multiple networks). Dense hosts overflow the small kernel defaults (often 128/512/1024), causing "neighbour table overflow" and dropped packets; the Incus/LXD production guide raises the same thresholds for the same reason.


## Reverse-path filtering (`rp_filter`)

`rp_filter` is the one security-relevant key this profile sets, because it is **functional** for a container host, not a generic hardening default, which is why it lives here and not in `hardening-default`. It is set to **loose mode (`rp_filter=2`)**: multiple container bridges, hairpin NAT (a container reaching its own published port) and service proxying create asymmetric paths where strict mode (`1`) silently drops valid packets, a classic source of "connection works from outside but not between containers" reports; Kubernetes networking (kube-proxy, several CNIs) is known to require loose mode. Loose mode still rejects packets with an unroutable source. Note the kernel uses `max(conf.all.rp_filter, conf.<iface>.rp_filter)`, so setting `all`/`default` to `2` raises the effective minimum to loose across interfaces.


## inotify quotas

| Parameter | Value | Why |
|-----------|-------|-----|
| `fs.inotify.max_user_watches` | `524288` | Maximum number of watched filesystem objects per UID. |
| `fs.inotify.max_user_instances` | `1024` | Maximum number of inotify instances per UID (kernel default: 128). |

inotify quotas are accounted per UID, and containers of the same user share that budget: all rootful containers run under UID 0, all containers of a rootless user under that UID. Containerized software uses inotify heavily (config watchers, log tailers, process supervisors), so a modest number of containers exhausts the defaults, typically surfacing as "too many open files" from `inotify_init`/`inotify_add_watch`. Same values as the [`file`](./file.md) profile; the watch quota is a limit, not a reservation (memory is only used per actually created watch, ~1 KiB each).


## Kernel keyring quotas

| Parameter | Value | Why |
|-----------|-------|-----|
| `kernel.keys.maxkeys` | `2000` | Maximum number of keys per non-root UID (kernel default: 200). |
| `kernel.keys.maxbytes` | `2000000` | Maximum key payload bytes per non-root UID (kernel default: 20000). |

Each container gets its own session keyring, counted against the per-UID quota of the owning user, again shared across all containers of that user. The kernel defaults fail around 200 containers with `disk quota exceeded` errors on container start. Values from the Incus/LXD production guide; they are quotas, not allocations, so raising them costs nothing up front.


## Security hardening

Apart from `rp_filter`, this profile targets container host function and applies no security hardening. Stack [`hardening-default`](./hardening-default.md) to enable shared safe defaults for networking, kernel, and filesystem settings, for example `["hardening-default", "container"]`. You can also add [`hardening-extra`](./hardening-extra.md) for stricter hardening; its conservative subset is container-safe, but the aggressive opt-in keys documented there (e.g. `kernel.unprivileged_bpf_disabled`, `kernel.yama.ptrace_scope`) can break container tooling, test before adding them.

Note that neither hardening profile disables **unprivileged user namespaces** (`user.max_user_namespaces=0` or Debian's legacy `kernel.unprivileged_userns_clone=0`), which some hardening guides recommend: rootless Podman/Docker fundamentally depends on them.


## Intentionally NOT set (policy / workload-specific)

- **`net.ipv4.ip_unprivileged_port_start=80`**: lets rootless containers publish privileged ports (80/443) without root. This is a deliberate policy decision (it weakens the privileged-port protection for *every* unprivileged process on the host, not just container runtimes), so it is documented here as opt-in via `sysctl_linux_parameters` rather than forced.
- **Workload tuning** (`net.core.somaxconn`, socket buffers, `vm.swappiness`, write-back, `vm.max_map_count`, `fs.aio-max-nr`, ...): containers share the host kernel, so a containerized workload needs the same host-level knobs as a bare-metal one, but *which* ones depends on what runs in the containers. Stack the matching workload profile, e.g. `["hardening-default", "container", "postgresql"]` for a host whose main payload is a containerized PostgreSQL, or `["hardening-default", "container", "elasticsearch"]` for Elasticsearch/OpenSearch containers (which refuse to start without `vm.max_map_count`).
- **`kernel.pid_max`**: raising it used to be common advice for dense hosts, but `systemd` ≥ 243 already sets `kernel.pid_max=4194304` on 64-bit systems. Per-container process limits belong to the runtime (`--pids-limit`, cgroup `pids` controller), not to a global sysctl.
- **`net.ipv4.ip_local_port_range`**: widening it helps against SNAT port exhaustion when many containers talk to the same destination, but it also collides with locally bound service ports; the [`web`](./web.md) profile widens it (with `ip_local_reserved_ports` guidance), stack it or set the key explicitly if you actually hit port exhaustion.


## Scope limitation: namespaced sysctls, cgroups and ulimits

Many `net.*` keys are **per network namespace**: each container sees its own copy (e.g. `net.core.somaxconn`, `net.ipv4.tcp_*` inside the container's namespace), initialized from kernel defaults, not from the host's values. Setting them for a specific container is the runtime's job (`docker run --sysctl` / `podman run --sysctl` / pod `securityContext.sysctls`). This profile tunes only what genuinely lives on the host side (forwarding, bridge netfilter, conntrack and neighbor tables used by the host-side NAT/bridges, and the per-UID quotas above). Likewise, cgroup limits (memory, CPU, pids) and file-descriptor ulimits (`LimitNOFILE` of the container service) are not sysctls and are managed by the runtime/systemd, not by this role.


## References

- Linux kernel networking sysctl documentation (`ip_forward`, `forwarding`, `accept_ra`, `rp_filter`, neighbor `gc_thresh*`): <https://www.kernel.org/doc/Documentation/networking/ip-sysctl.txt>
- nf_conntrack sysctl documentation: <https://www.kernel.org/doc/Documentation/networking/nf_conntrack-sysctl.txt>
- Docker: Enable IPv6 support (forwarding and `accept_ra` interaction on SLAAC uplinks): <https://docs.docker.com/engine/daemon/ipv6/>
- Docker: Packet filtering and firewalls (how Docker uses iptables for isolation and published ports): <https://docs.docker.com/engine/network/packet-filtering-firewalls/>
- Kubernetes: Container runtime prerequisites (IPv4 forwarding, historically `br_netfilter` + `bridge-nf-call-iptables` on nodes): <https://kubernetes.io/docs/setup/production-environment/container-runtimes/>
- Incus (LXD): Server settings for a production setup (inotify, keyring and neighbor-table values for dense container hosts): <https://linuxcontainers.org/incus/docs/main/reference/server_settings/>
- Linux kernel: Kernel key retention service (keyring quotas): <https://docs.kernel.org/security/keys/core.html>
- `inotify(7)`, `/proc/sys/fs/inotify` limits: <https://man7.org/linux/man-pages/man7/inotify.7.html>
- Podman: rootless mode and unprivileged port binding (`ip_unprivileged_port_start`): <https://github.com/containers/podman/blob/main/rootless.md>
