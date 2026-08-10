# sysctl profile `router`

Tuning for routers, firewalls, NAT gateways and VPN concentrators. A forwarding device needs IP forwarding enabled, a connection-tracking table large enough for all flows passing through it, neighbor (ARP/NDP) tables sized for many peers, and reverse-path filtering relaxed to tolerate the asymmetric routing such devices commonly see.

This is the **canonical router profile and forwards both IPv4 and IPv6**. Two variants share everything here and differ only in the forwarding keys:

- [`router_v4only`](./router_v4only.md): IPv4 forwarding enabled, IPv6 forwarding explicitly disabled.
- [`router_v6only`](./router_v6only.md): IPv6 forwarding enabled, IPv4 forwarding explicitly disabled.

This profile targets performance; stack others for security hardening (see "Security hardening" below). All values can be overridden with `sysctl_linux_parameters`; set a value to `null` to stop managing it.


## IP forwarding

| Parameter | Value | Why |
|-----------|-------|-----|
| `net.ipv4.ip_forward` | `1` | Master switch for IPv4 forwarding. |
| `net.ipv4.conf.all.forwarding`, `net.ipv4.conf.default.forwarding` | `1` | Per-interface IPv4 forwarding (all existing and future interfaces). |
| `net.ipv6.conf.all.forwarding`, `net.ipv6.conf.default.forwarding` | `1` | IPv6 forwarding (all existing and future interfaces). |

The `router_v4only` / `router_v6only` variants set the off-direction explicitly to `0` rather than omitting it. Because the role's drop-in is **declarative** (any unmanaged key is removed and falls back to the kernel default), writing `0` actively **enforces** "forwarding off" at high precedence, instead of merely leaving it to the kernel default or to whatever another config file set. On a device that must not route a given protocol, that guarantee matters.


### IPv6 caveat: Router Advertisements

Enabling `net.ipv6.conf.all.forwarding` makes the kernel **stop accepting IPv6 Router Advertisements (RAs)** on interfaces. If this device learns its **upstream** IPv6 address/default route via RA (SLAAC on the WAN), that will break unless you set `net.ipv6.conf.<wan>.accept_ra=2` on that specific interface. This is interface-specific, so the profile does **not** set it globally; configure it for your WAN interface via `sysctl_linux_parameters` if needed.


## Auto-calculation

The connection-tracking table scales with RAM (`ansible_facts['memtotal_mb']`, in MiB) so the device can track all flows passing through it.

| Parameter | Formula | Rationale |
|-----------|---------|-----------|
| `net.netfilter.nf_conntrack_max` | `RAM_MiB * 32` | A forwarding device tracks every flow in both directions; budget ~32 entries per MiB (each entry ~300 bytes). |
| `net.netfilter.nf_conntrack_buckets` | `conntrack_max / 4` | Hash-table bucket count sized to roughly a quarter of the max entries for a good load factor. |


## Connection tracking

| Parameter | Value | Why |
|-----------|-------|-----|
| `net.netfilter.nf_conntrack_max` | auto | Prevents "nf_conntrack: table full, dropping packet" when many flows traverse the device. |
| `net.netfilter.nf_conntrack_buckets` | auto | Keep hash-bucket count proportional to table size for fast lookups. The canonical way to size the table is the `hashsize` module parameter at module load; this sysctl resizes it after load on current kernels. |

These keys only exist when the `nf_conntrack` module is loaded. The role loads it best-effort when this profile is selected (and registers it for boot in the role-owned `/etc/modules-load.d/zz-managed.conf`; the registration is removed again when the profile is dropped). Where the module cannot be loaded (e.g. unprivileged containers), the load is tolerated on every platform and the keys it gates are skipped with a notice; set `sysctl_linux_modules_required: true` for a hard failure instead.

The TCP `established` / `time_wait` conntrack timeouts are **left at their kernel defaults** (5 days / 2 minutes); the previous profile set those exact defaults, which was pure noise. The timeouts that actually matter for **VPN and NAT gateways are the UDP ones**: WireGuard, IPsec and OpenVPN are UDP-based. If idle tunnels are dropped from the table too aggressively, raise `net.netfilter.nf_conntrack_udp_timeout` and especially `net.netfilter.nf_conntrack_udp_timeout_stream` (default 120 s) via `sysctl_linux_parameters` to match your keepalive interval. This profile leaves them at the kernel defaults rather than guessing your VPN's keepalive.


## Neighbor tables (ARP / NDP)

| Parameter | Value | Why |
|-----------|-------|-----|
| `net.ipv4.neigh.default.gc_thresh1` | `1024` | Below this many entries the garbage collector never runs. |
| `net.ipv4.neigh.default.gc_thresh2` | `4096` | Soft maximum; GC becomes aggressive above it. |
| `net.ipv4.neigh.default.gc_thresh3` | `8192` | Hard maximum number of ARP entries. |
| `net.ipv6.neigh.default.gc_thresh1/2/3` | `1024/4096/8192` | Same thresholds for the IPv6 neighbor (NDP) cache. |

Routers on busy segments talk to many peers; the default thresholds (often 128/512/1024) cause "neighbour table overflow" and dropped packets.


## Reverse-path filtering (`rp_filter`)

`rp_filter` is the one security-relevant key this profile sets, because it is **functional** for a router, not a generic hardening default, which is why it lives here and not in `hardening-default`. It is set to **loose mode (`rp_filter=2`)**: forwarding devices frequently have asymmetric routes (a reply leaves via a different interface than the request arrived on), where strict mode (`1`) would wrongly drop valid traffic, while loose mode still rejects packets with an unroutable source. Note the kernel uses `max(conf.all.rp_filter, conf.<iface>.rp_filter)`, so setting `all`/`default` to `2` raises the effective minimum to loose across interfaces.


## Security hardening

Apart from `rp_filter`, this profile targets routing function and applies no security hardening. Stack [`hardening-default`](./hardening-default.md) (ICMP/source-route hardening, no `send_redirects`, martian logging, ASLR, `fs.protected_*`, ...; also sets `send_redirects=0`, which is correct for a router: it should not nudge hosts via ICMP redirects) to enable shared safe defaults for networking, kernel, and filesystem settings, for example `["hardening-default", "router"]`. You can also add [`hardening-extra`](./hardening-extra.md) for stricter hardening, but it may break compatibility, so test thoroughly before using it in production.


## References

- nf_conntrack sysctl documentation: <https://www.kernel.org/doc/Documentation/networking/nf_conntrack-sysctl.txt>
- Linux kernel networking sysctl documentation: <https://www.kernel.org/doc/Documentation/networking/ip-sysctl.txt>
