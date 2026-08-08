# sysctl profile `container-rootless`

Tuning for hosts that run **only rootless OCI containers with user-mode networking** (Podman with pasta or slirp4netns). Such a host never bridges or NATs container traffic: outbound traffic and published ports are handled by a userspace proxy running as the container user. The kernel therefore needs none of the routing machinery a rootful/bridged container host needs. What actually runs out are the per-UID kernel quotas that all containers of one rootless user share.

For hosts with rootful or bridged container networking (Docker, rootful Podman/netavark, containerd/CRI-O, Kubernetes nodes), use the [`container`](./container.md) profile instead. All values can be overridden with `sysctl_linux_parameters`; set a value to `null` to stop managing it.


## Kernel modules

None. All keys below are provided by the core kernel. Unlike the `container` profile there is nothing to modprobe, which also makes this profile safe on kernels that cannot load optional modules (unprivileged containers, cloud images without `kernel-modules-extra`).


## Why so small compared to `container`

| `container` area | Why it is not needed here |
|------------------|---------------------------|
| IP forwarding (`net.ipv4/ipv6 … forwarding`) | pasta/slirp4netns forward in userspace; the host kernel never routes container traffic. |
| Bridge netfilter (`net.bridge.bridge-nf-call-*`) | No bridges exist; the `br_netfilter` module has nothing to filter. |
| Connection tracking (`net.netfilter.nf_conntrack_*`) | No masquerading in the host namespace; container connections appear as ordinary sockets of the rootless user. |
| Neighbor tables (`net.*.neigh.default.gc_thresh*`) | No veth/bridge peers on the host side. |
| Loose reverse-path filtering (`rp_filter = 2`) | No asymmetric bridge/NAT paths; the hardening/kernel default is fine. |


## inotify (per-UID quotas)

| Parameter | Value | Why |
|-----------|-------|-----|
| `fs.inotify.max_user_watches` | `524288` | Config watchers, log tailers and supervisors in many containers add up, and the quota is shared by every container of the same rootless user. Same value as the `container` and `file` profiles. |
| `fs.inotify.max_user_instances` | `1024` | Kernel default is 128 instances per UID; a handful of containers with a few watchers each exhausts it. |


## Kernel keyring (per-UID quotas)

| Parameter | Value | Why |
|-----------|-------|-----|
| `kernel.keys.maxkeys` | `2000` | Each container gets a session keyring counted against the owning rootless user's quota; the default of 200 keys fails around 200 containers. Values from the Incus/LXD production guide. |
| `kernel.keys.maxbytes` | `2000000` | Byte quota matching `maxkeys` (default 20000 bytes). |


## Privileged ports (deliberately not included)

Publishing ports below 1024 rootlessly (e.g. 80/443) needs `net.ipv4.ip_unprivileged_port_start` lowered, because the userspace proxy binds the port as the unprivileged container user. This is a host-wide relaxation: every local user may then bind those ports, so this profile does not apply it. Opt in explicitly where needed:

```yaml
sysctl_linux_parameters:
  "net.ipv4.ip_unprivileged_port_start": 80
```


## Security hardening

This profile targets container host function only. Stack the shared hardening first, e.g. `sysctl_linux_profile: ["hardening-default", "container-rootless"]`.
