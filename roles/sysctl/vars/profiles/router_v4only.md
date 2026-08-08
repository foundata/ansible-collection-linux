# sysctl profile `router_v4only`

Same as the [`router`](./router.md) profile in every respect (connection tracking, neighbor tables, loose reverse-path filtering) **except IP forwarding**. See [`router.md`](./router.md) for the full reasoning behind all shared settings.

Like `router`, this profile targets performance; stack others for security hardening (see "Security hardening" below). All values can be overridden with `sysctl_linux_parameters`; set a value to `null` to stop managing it.


## Difference from `router`

This profile **enables IPv4 forwarding** and **explicitly disables IPv6 forwarding**:

| Parameter | `router` | `router_v4only` |
|-----------|----------|-----------------|
| `net.ipv4.ip_forward` | `1` | `1` |
| `net.ipv4.conf.all.forwarding` / `default.forwarding` | `1` | `1` |
| `net.ipv6.conf.all.forwarding` / `default.forwarding` | `1` | **`0`** |

IPv6 forwarding is set to `0` rather than left out so the declarative drop-in actively enforces it off (see the "IP forwarding" section in [`router.md`](./router.md) for why explicit `0` matters). Use this profile for an IPv4-only router/gateway where IPv6 routing must be guaranteed off.
