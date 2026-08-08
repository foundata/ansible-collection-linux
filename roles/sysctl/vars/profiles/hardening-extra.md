# sysctl profile `hardening-extra`

Conservative kernel-level security hardening, meant to be **stacked** on top of a workload profile (and `hardening-default`) rather than used alone:

```yaml
sysctl_linux_profile:
  - "hardening-default"
  - "web"
  - "hardening-extra"
```

This profile adds kernel-information and memory hardening on top of the shared network/kernel/filesystem defaults in [`hardening-default`](./hardening-default.md); the two do not overlap. The workload profiles themselves target performance and carry no hardening, so stack `hardening-default` as well: omitting it means no ASLR, ICMP/source-route hardening or `fs.protected_*`. Stacking composes them (last wins on conflicts, of which there are none here).

All values can be overridden with `sysctl_linux_parameters`; set a value to `null` to stop managing it.


## What this profile sets (safe subset)

| Parameter | Value | Why |
|-----------|-------|-----|
| `kernel.kptr_restrict` | `1` | Hide kernel pointers from unprivileged users (`/proc/kallsyms`, etc.), raising the bar for exploit development. |
| `kernel.dmesg_restrict` | `1` | Restrict the kernel ring buffer (`dmesg`) to privileged users; it can leak addresses and other sensitive info. |
| `vm.mmap_min_addr` | `65536` | Disallow mapping the low address space, mitigating kernel NULL-pointer-dereference exploits. |
| `net.ipv4.tcp_rfc1337` | `1` | Protect against TCP TIME-WAIT assassination (RFC 1337). |

Several of these already match modern distro defaults; they are asserted so the posture is explicit and tamper-evident.

These values are **enforced exactly** (the role writes them with `sysctl -w` when `sysctl_linux_verify` is true), so on a host already hardened *beyond* them the profile would **lower** the setting. This is most relevant for `vm.mmap_min_addr` (some distributions/architectures default higher than `65536`) and `kernel.kptr_restrict` (a host set to `2` would be reduced to `1`). If your platform already uses a stricter value, override it via `sysctl_linux_parameters` (e.g. `"vm.mmap_min_addr": 1048576`) or set it to `null` to stop managing that key.


## Opt-in (NOT set here; enable deliberately, with caveats)

These materially harden the host but **break common workflows, so they are left for you to enable explicitly via `sysctl_linux_parameters`** once you have confirmed they fit your environment:

| Parameter | Suggested | Caveat |
|-----------|-----------|--------|
| `kernel.yama.ptrace_scope` | `1` (or `2`/`3`) | Restricts `ptrace`. Breaks `gdb`/`strace` attach to non-child processes, some debuggers, CRIU and certain APM/profilers. Requires the Yama LSM. |
| `kernel.perf_event_paranoid` | `3` | Disables unprivileged use of `perf`. Breaks profiling tools (`perf`, some eBPF profilers) for non-root users. |
| `kernel.unprivileged_bpf_disabled` | `1` | Blocks unprivileged BPF. Breaks some observability/networking tooling that relies on unprivileged BPF. |

Example:

```yaml
sysctl_linux_profile:
  - "hardening-default"
  - "web"
  - "hardening-extra"
sysctl_linux_parameters:
  "kernel.yama.ptrace_scope": 1
  "kernel.unprivileged_bpf_disabled": 1
```


## Scope

This is a sysctl-only hardening helper, not a complete hardening solution. Full host hardening also covers boot parameters, LSMs (SELinux/AppArmor), module signing, filesystem mount options and more, which are out of scope for a sysctl role.


## References

- Linux kernel admin sysctl documentation: <https://www.kernel.org/doc/Documentation/admin-guide/sysctl/kernel.rst>
- Kernel Self-Protection Project: <https://kernsec.org/wiki/index.php/Kernel_Self_Protection_Project>
