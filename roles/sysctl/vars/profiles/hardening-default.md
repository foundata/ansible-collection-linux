# sysctl profile `hardening-default`

A shared baseline of network, kernel and filesystem security hardening. The workload/application profiles (`web`, `postgresql`, `mysql`, `redis`, `elasticsearch`, `file`, `virtualization`, `router`) focus on performance and reliability and intentionally do not carry these keys, so this profile is the single, central place for the common safe defaults.

It is meant to be **stacked**, usually first, before an application profile:

```yaml
sysctl_linux_profile:
  - "hardening-default"
  - "web"
```

Order matters only conceptually (there are no conflicting keys between this and the application profiles); putting it first expresses "secure defaults, then workload tuning". `sysctl_linux_parameters` still overrides everything. For stricter, opt-in hardening, also stack [`hardening-extra`](./hardening-extra.md) (e.g. `["hardening-default", "hardening-extra", "web"]`), but it may break compatibility, so test thoroughly before using it in production.


## What it sets

| Group | Parameters | Purpose |
|-------|-----------|---------|
| Network | `net.ipv4.tcp_syncookies=1` | Survive SYN floods (fallback). |
| Network | `net.ipv4.conf.{all,default}.accept_redirects=0`, `net.ipv6.conf.{all,default}.accept_redirects=0` | Ignore ICMP redirects (anti route-tampering). |
| Network | `net.ipv4.conf.{all,default}.send_redirects=0` | A non-router host should not send redirects. |
| Network | `net.ipv4.conf.{all,default}.accept_source_route=0`, `net.ipv6.conf.{all,default}.accept_source_route=0` | Reject source-routed packets. |
| Network | `net.ipv4.conf.{all,default}.log_martians=1` | Log impossible (martian) source addresses. |
| Network | `net.ipv4.icmp_echo_ignore_broadcasts=1`, `net.ipv4.icmp_ignore_bogus_error_responses=1` | ICMP hardening. |
| Kernel | `kernel.randomize_va_space=2` | Full ASLR. |
| Filesystem | `fs.protected_{hardlinks,symlinks,fifos,regular}`, `fs.suid_dumpable=0` | Mitigate symlink/hardlink races and SUID core dumps. |

Several of these already match modern kernel/distro defaults; they are asserted so the host posture is explicit and tamper-evident.


## Intentionally excluded: `rp_filter`

Reverse-path filtering is **not** set here. Strict mode (`1`) breaks multihomed/asymmetric/VRRP/cloud-secondary-IP setups, and the choice belongs to the host's routing policy. Only the `router` profile manages it (loose mode `2`), where it is functionally needed.


## References

- Linux kernel networking sysctl documentation: <https://www.kernel.org/doc/Documentation/networking/ip-sysctl.txt>
