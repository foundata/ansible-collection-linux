# sysctl profile `virtualization`

Tuning for **KVM/QEMU hypervisor hosts** (libvirt, Proxmox VE, ...). These hosts pack many guests onto shared hardware and back guest disks with host storage, so they benefit from memory overcommit, an emergency memory reserve, bounded write-back and generous async-I/O limits.

This profile targets performance; stack others for security hardening (see "Security hardening" below). All values can be overridden with `sysctl_linux_parameters`; set a value to `null` to stop managing it.


## Auto-calculation

| Parameter | Formula | Rationale |
|-----------|---------|-----------|
| `vm.min_free_kbytes` | `min(RAM_KiB * 0.01, 2 GiB)` | Emergency free-memory reserve (1% of RAM) so the host can always make progress under pressure, capped at 2 GiB. |
| `vm.dirty_background_bytes` / `vm.dirty_bytes` | `min(RAM/20, 1 GiB)` / `min(RAM/10, 4 GiB)` | Byte-based, bounded write-back. |


## Memory & write-back

| Parameter | Value | Why |
|-----------|-------|-----|
| `vm.overcommit_memory` | `1` | Always overcommit. Hypervisors routinely assign more guest RAM than is physically present (ballooning/KSM, not all guests busy), and mode 1 avoids spurious QEMU allocation failures. |
| `vm.swappiness` | `10` | Avoid swapping host/guest working sets while keeping swap as a safety valve. |
| `vm.dirty_background_bytes`, `vm.dirty_bytes` | auto | Byte-based write-back replaces the RAM-percentage `dirty_ratio`/`dirty_background_ratio`: on a big-RAM hypervisor a 40% ratio is tens of GiB of dirty pages and stalls *all* guests when flushed. Setting `*_bytes` disables the `*_ratio` knobs (mutually exclusive). Tune to your storage. |
| `fs.aio-max-nr` | `1048576` | Headroom for the many outstanding async I/O requests across guest disk backends. |


## Security hardening

This profile is optimized for performance and does **not** include security hardening. Stack [`hardening-default`](./hardening-default.md) to enable shared safe defaults for networking, kernel, and filesystem settings, for example `["hardening-default", "virtualization"]`. You can also add [`hardening-extra`](./hardening-extra.md) for stricter hardening, but it may break compatibility, so test thoroughly before using it in production. Note that `rp_filter` is managed by neither: strict reverse-path filtering frequently breaks bridged/routed guest traffic on a hypervisor.


## Intentionally NOT set (policy / ineffective)

- **Bridge netfilter** (`net.bridge.bridge-nf-call-iptables`/`-ip6tables`/`-arptables`) and the `br_netfilter` module: **left to the firewall layer**. Whether bridged guest traffic traverses the host's `iptables`/`nftables` is a firewall-policy decision owned by Proxmox VE's firewall, Docker, Kubernetes CNIs or your site firewall, not a generic tuning knob. Forcing it off would silently break those stacks; forcing it on imposes per-packet hook overhead. The kernel default (module not loaded → no bridge filtering) is left untouched; load and configure `br_netfilter` from whatever stack actually needs it.
- **`kernel.sched_migration_cost_ns`**: removed. It is a CFS-era knob, largely ineffective under the EEVDF scheduler (Linux ≥ 6.6) and mostly cargo-culted for KVM.


## Optional, deployment-specific (document, not forced)

- **`net.ipv4.ip_forward=1`**: **needed for routed/NAT guest networks (e.g. libvirt's default NAT network)**; bridged setups do not need it. Stack the `router` profile or set it via `sysctl_linux_parameters` if your host routes guest traffic.
- **`kernel.numa_balancing=0`**: common on **hosts with pinned vCPUs / NUMA-aligned guests** (let the VM placement, not autonuma, decide). Left to explicit opt-in because it hurts non-pinned, NUMA-spanning workloads.


## Scope limitation: KSM and HugePages

KSM (`/sys/kernel/mm/ksm/`) and HugePages (`/sys/kernel/mm/hugepages/`, or `vm.nr_hugepages`/boot parameters + `hugetlbfs`) are commonly tuned on hypervisors but are not part of this profile (KSM is not a sysctl at all; HugePages sizing is deployment-specific). Manage them with a dedicated mechanism (tuned, a `systemd` unit, or kernel boot parameters).


## References

- Linux kernel: `/proc/sys/vm/` (`overcommit_memory`, `swappiness`, `dirty_bytes`/`dirty_background_bytes`, `min_free_kbytes`): <https://docs.kernel.org/admin-guide/sysctl/vm.html>
- Linux kernel: `/proc/sys/fs/` (`aio-max-nr`): <https://docs.kernel.org/admin-guide/sysctl/fs.html>
- Red Hat: Optimizing virtual machine performance in RHEL 9 (the `tuned` `virtual-host` profile enables aggressive dirty-page writeback and `virtual-guest` lowers swappiness; the basis for the write-back and `swappiness` choices here): <https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/9/html/configuring_and_managing_virtualization/optimizing-virtual-machine-performance-in-rhel_configuring-and-managing-virtualization>
- Proxmox VE: Dynamic Memory Management (KSM and ballooning; context for memory overcommit and the KSM scope note above): <https://pve.proxmox.com/wiki/Dynamic_Memory_Management>
- Linux kernel: Kernel Samepage Merging (KSM), out of scope for this profile: <https://docs.kernel.org/admin-guide/mm/ksm.html>
- Linux kernel: HugeTLB Pages (`vm.nr_hugepages` / `/sys/kernel/mm/hugepages`), out of scope for this profile: <https://docs.kernel.org/admin-guide/mm/hugetlbpage.html>
