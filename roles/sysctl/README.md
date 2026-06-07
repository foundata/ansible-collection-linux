# Ansible role: `foundata.linux.sysctl`

Manages Linux kernel parameters via `sysctl`, with optional workload-specific profiles that auto-tune values based on system resources.

Choose one or more profiles for your workload (web server, the database engines, file server, virtualization host, or router) and the role applies performance-tuned parameters. Security hardening lives in separate, stackable profiles (`
`, `hardening-extra`) — stack them with a workload profile, e.g. `["hardening-default", "web"]`. Override any value with `sysctl_linux_parameters`.


## Table of contents<a id="toc"></a>

- [Features](#features)
- [Example playbooks, using this role](#examples)
- [Supported tags](#tags)<!-- ANSIBLE DOCSMITH TOC START -->
- [Role variables](#variables)
  - [`sysctl_linux_state`](#variable-sysctl_linux_state)
  - [`sysctl_linux_autoupgrade`](#variable-sysctl_linux_autoupgrade)
  - [`sysctl_linux_profile`](#variable-sysctl_linux_profile)
  - [`sysctl_linux_parameters`](#variable-sysctl_linux_parameters)
  - [`sysctl_linux_reload`](#variable-sysctl_linux_reload)
  - [`sysctl_linux_verify`](#variable-sysctl_linux_verify)
  - [`sysctl_linux_ignore_unknown_key_errors`](#variable-sysctl_linux_ignore_unknown_key_errors)
  - [`sysctl_linux_config_dropin_file_name`](#variable-sysctl_linux_config_dropin_file_name)
<!-- ANSIBLE DOCSMITH TOC END -->
- [Dependencies](#dependencies)
- [Compatibility](#compatibility)
- [External requirements](#requirements)



## Features

Main features:

* **Simple usage**: Use the [`sysctl_linux_parameters`](#variable-sysctl_linux_parameters) dictionary to maintain custom kernel parameters
* **Optional, stackable profiles** (`sysctl_linux_profile` is a list, applied in order, last wins):
  * Workload (performance) profiles: `web`, `postgresql`, `mysql`, `redis`, `elasticsearch`, `file`, `virtualization`, `router`/`router_v4only`/`router_v6only` (see [`sysctl_linux_profile`](#variable-sysctl_linux_profile) for details).
  * Security profiles to stack on a workload: `hardening-default` (shared network/kernel/filesystem hardening) and `hardening-extra` (stricter kernel hardening), e.g. `["hardening-default", "web", "hardening-extra"]`.
  * Auto-tuning: Profiles automatically calculate optimal values based on system RAM using Ansible facts.
  * Use [`sysctl_linux_parameters`](#variable-sysctl_linux_parameters) to overwrite a profile parameter to customize for edge cases.
* Container-aware: on detected containers the role automatically skips live application (`sysctl -w`) and only writes the drop-in file, and tolerates `sysctl --system` reload failures — no need to set `sysctl_linux_verify: false` yourself.
* Designed for cross-platform compatibility, working seamlessly across major Linux distributions.



## Example playbooks, using this role<a id="examples"></a>

Set custom kernel parameters:

```yaml
---

- name: "Configure sysctl parameters"
  hosts: "webservers"
  tasks:

    - name: "Apply custom sysctl settings"
      ansible.builtin.include_role:
        name: "foundata.linux.sysctl"
      vars:
        sysctl_linux_parameters:
          "net.core.somaxconn": 65535
          "net.ipv4.tcp_max_syn_backlog": 65535
          "vm.swappiness": 10
```

Use a profile for workload-specific tuning:

```yaml
---

- name: "Configure web server with profile"
  hosts: "webservers"
  tasks:

    - name: "Apply web server profile with the shared security baseline"
      ansible.builtin.include_role:
        name: "foundata.linux.sysctl"
      vars:
        sysctl_linux_profile:
          - "hardening-default"
          - "web"
```


Override profile values with custom parameters:

```yaml
---

- name: "Configure PostgreSQL server"
  hosts: "databases"
  tasks:

    - name: "Apply postgresql + hardening-default, override swappiness, unmanage dirty_bytes, allow routing"
      ansible.builtin.include_role:
        name: "foundata.linux.sysctl"
      vars:
        sysctl_linux_profile:
          - "hardening-default"
          - "postgresql"
        sysctl_linux_parameters:
          "vm.swappiness": 1  # override profile default with another value
          "vm.dirty_bytes": null  # override profile default, do not manage and use kernel default
          "net.ipv4.ip_forward": 1 # additional parameter not handled by the profile at all
```




## Supported tags<a id="tags"></a>

It might be useful and faster to only call parts of the role by using tags:

- `sysctl_linux_setup`: Manage basic resources, such as packages or service users.
- `sysctl_linux_config`: Manage sysctl parameters.

There are also tags usually not meant to be called directly but listed for the sake of completeness** and edge cases:

- `sysctl_linux_always`, `always`: Tasks needed by the role itself for internal role setup and the Ansible environment.


<!-- ANSIBLE DOCSMITH MAIN START -->

## Role variables<a id="variables"></a>

The following variables can be configured for this role:

| Variable | Type | Required | Default | Description (abstract) |
|----------|------|----------|---------|------------------------|
| `sysctl_linux_state` | `str` | No | `"present"` | Determines whether the managed resources should be `present` or `absent`.<br><br>`present` ensures that required components, such as software packages, are installed and configured.<br><br>`absent` reverts changes as much as possible, such as […](#variable-sysctl_linux_state) |
| `sysctl_linux_autoupgrade` | `bool` | No | `false` | If set to `true`, all managed packages will be upgraded during each Ansible run (e.g., when the package provider detects a newer version than the currently installed one). |
| `sysctl_linux_profile` | `list` | No | `[]` | Selects one or more predefined sets of kernel parameters ("profiles") optimized for specific workloads.<br><br>Profiles are applied in the given order and, for a parameter set by more than one profile, the later profile wins. The required kernel […](#variable-sysctl_linux_profile) |
| `sysctl_linux_parameters` | `dict` | No | `{}` | Dictionary of kernel parameters to manage via sysctl. Keys are parameter names (e.g., `net.ipv4.ip_forward`), values are the desired settings.<br><br>The drop-in configuration file is fully declarative: any parameter in the file that is not present […](#variable-sysctl_linux_parameters) |
| `sysctl_linux_reload` | `bool` | No | `true` | If set to `true`, triggers `sysctl --system` after configuration changes to reload all sysctl configuration files following the proper precedence order. This ensures all drop-in files and possibly existing other sysctl configuration files not managed […](#variable-sysctl_linux_reload) |
| `sysctl_linux_verify` | `bool` | No | `true` | If set to `true`, verifies the parameter value using the sysctl command and actively sets it in the running kernel using `sysctl -w` if the current value differs from the desired one.<br><br>When `false`, only writes the parameter to the […](#variable-sysctl_linux_verify) |
| `sysctl_linux_ignore_unknown_key_errors` | `bool` | No | `false` | If set to `true`, ignores errors caused by unknown or unsupported kernel parameter keys. This is useful in container environments where certain parameters may not exist or be accessible.<br><br>Generally not recommended for bare-metal or VM […](#variable-sysctl_linux_ignore_unknown_key_errors) |
| `sysctl_linux_config_dropin_file_name` | `str` | No | `"90-managed.conf"` | Filename of the drop-in configuration file to be placed in `/etc/sysctl.d/`. Defaults to `90-managed.conf`. The `90-` prefix ensures late loading and thus higher precedence over files with lower-numbered prefixes.<br><br>If a non-default filename is […](#variable-sysctl_linux_config_dropin_file_name) |

### `sysctl_linux_state`<a id="variable-sysctl_linux_state"></a>

[*⇑ Back to ToC ⇑*](#toc)

Determines whether the managed resources should be `present` or `absent`.

`present` ensures that required components, such as software packages, are
installed and configured.

`absent` reverts changes as much as possible, such as removing packages,
deleting created users, stopping services, restoring modified settings, ...

Note: For this role, the required component and package set is minimal. There
are no users or services to manage and the components needed to set kernel
parameter are preinstalled even on hardened systems. They also cannot be
safely removed due to dependencies, so the role rarely modifies the system
in this regard.

On `absent`, the managed drop-in file(s) are removed and any lines the role
previously commented out in the main config file (`/etc/sysctl.conf`, to make
the drop-in win) are restored — only those lines, identified by an internal
marker, so settings you commented out yourself are left untouched. As with any
sysctl change, already-applied running values are not actively reset; a reload
(or reboot) re-applies the restored main-file values.

- **Type**: `str`
- **Required**: No
- **Default**: `"present"`
- **Choices**: `present`, `absent`



### `sysctl_linux_autoupgrade`<a id="variable-sysctl_linux_autoupgrade"></a>

[*⇑ Back to ToC ⇑*](#toc)

If set to `true`, all managed packages will be upgraded during each Ansible
run (e.g., when the package provider detects a newer version than the
currently installed one).

- **Type**: `bool`
- **Required**: No
- **Default**: `false`



### `sysctl_linux_profile`<a id="variable-sysctl_linux_profile"></a>

[*⇑ Back to ToC ⇑*](#toc)

Selects one or more predefined sets of kernel parameters ("profiles") optimized
for specific workloads.

Profiles are applied in the given order and, for a parameter set by more than
one profile, the later profile wins. The required kernel modules (if any) of
all selected profiles are loaded automatically. An empty list (the default)
applies no profile; and only explicit `sysctl_linux_parameters` are set then.

A single profile is a one-element list, e.g. `["web"]`. Profiles can be
stacked, e.g. `["hardening-default", "web", "hardening-extra"]` to add a workload
profile on to the hardening baseline and kernel hardening on top of the
workload profile.

The workload profiles (`web`, `postgresql`, `mysql`, `redis`, `elasticsearch`,
`file`, `virtualization`, `router`/`router_v4only`/`router_v6only`) tune for
performance and reliability. Security hardening lives in separate, stackable
profiles: `hardening-default` (shared safe network/kernel/filesystem defaults) and
`hardening-extra` (stricter kernel hardening).

Stack them with a workload profile, e.g. `["hardening-default", "web"]` or
`["hardening-default", "web", "hardening-extra"]`. Some values are auto-calculated
from system resources (RAM). Use `sysctl_linux_parameters` to override any
profile value; it takes precedence over every profile.

Available base profiles (alphabetical order):

- `hardening-default`: Shared network/kernel/filesystem security hardening,
  meant to be *stacked first before a workload profile (e.g.
  `["hardening-default", "web"]`). The workload profiles target performance
  and do not include these keys. See
  [`hardening-default.md`](./vars/profiles/hardening-default.md) for details.
- `hardening-extra`: Conservative kernel-level security hardening, meant to be **stacked** on a
  workload profile (e.g. `["hardening-default", "web", "hardening-extra"]`). See
  [`hardening-extra.md`](./vars/profiles/hardening-extra.md) for details.

Available workload profiles (alphabetical order):

- `elasticsearch`: Mandatory `vm.max_map_count`, file limits and memory policy
  for Elasticsearch/OpenSearch. See
  [`elasticsearch.md`](./vars/profiles/elasticsearch.md) for details.
- `file`: Network throughput and storage I/O. Recommended for fileservers
  (NFS, Samba/CIFS, SFTP), backup targets and the like. See
  [`file.md`](./vars/profiles/file.md) for details.
- `mysql`: Like `postgresql`, tuned for MySQL/MariaDB (InnoDB native AIO, file
  limits). See [`mysql.md`](./vars/profiles/mysql.md) for details.
- `postgresql`: Memory policy, byte-based write-back, file limits for
  PostgreSQL. See [`postgresql.md`](./vars/profiles/postgresql.md) for
  details.
- `redis`: Memory overcommit (for fork-based persistence) and a high accept
  backlog for Redis and compatible in-memory stores. See
  [`redis.md`](./vars/profiles/redis.md) for details.
- `router`: Connection tracking, neighbor tables, IP forwarding (IPv4 + IPv6).
  Recommended for firewalls, NAT gateways, VPN concentrators. See
  [`router.md`](./vars/profiles/router.md) for details.
- `router_v4only`: Like `router` but enables IPv4 forwarding only and
  explicitly disables IPv6 forwarding. See
  [`router_v4only.md`](./vars/profiles/router_v4only.md)  for details.
- `router_v6only`: Like `router` but enables IPv6 forwarding only and
  explicitly disables IPv4 forwarding. See
  [`router_v6only.md`](./vars/profiles/router_v6only.md) for details.
- `virtualization`: Memory overcommit, scheduler tuning, storage I/O.
  Recommended for KVM/QEMU hosts, Proxmox VE and the like. See
  [`virtualization.md`](./vars/profiles/virtualization.md) for details.
- `web`: High connection count and throughput. Recommended for web servers,
  API gateways, load balancers, reverse proxies. See
  [`web.md`](./vars/profiles/web.md) for details.

Note: removing a profile (or a key from one) stops the role from managing that
key and the role notifies a `sysctl --system` reload, which re-applies the
remaining configuration files However, `sysctl` cannot reset a key that is no
longer present in any file back to its kernel default, and a persistently
loaded kernel module stays loaded; reverting those to the pre-role state needs
a reboot (or a manual `sysctl -w` / `modprobe -r`).

- **Type**: `list`
- **Required**: No
- **Default**: `[]`
- **Choices**: `web`, `postgresql`, `mysql`, `redis`, `elasticsearch`, `file`, `virtualization`, `router`, `router_v4only`, `router_v6only`, `hardening-default`, `hardening-extra`
- **List Elements**: `str`



### `sysctl_linux_parameters`<a id="variable-sysctl_linux_parameters"></a>

[*⇑ Back to ToC ⇑*](#toc)

Dictionary of kernel parameters to manage via sysctl. Keys are parameter
names (e.g., `net.ipv4.ip_forward`), values are the desired settings.

The drop-in configuration file is fully declarative: any parameter in the
file that is not present in the effective configuration (profile + this
dictionary) will be automatically removed and the kernel default will be used
instead. This ensures the file always reflects exactly what is defined in your
Ansible configuration.

These parameters take precedence over any values set by `sysctl_linux_profile`
(if any). This allows using a profile as a baseline while customizing specific
values.

Example:

```yaml
sysctl_linux_parameters:
  "net.ipv4.ip_forward": 0
  "vm.swappiness": 5
```

Example overriding a profile value:

```yaml
sysctl_linux_profile:
  - "redis"
sysctl_linux_parameters:
  "vm.swappiness": 1  # override profile default with another value
  "vm.overcommit_memory": null  # override profile default, do not manage and use kernel default
  "net.ipv4.ip_forward": 1 # additional parameter not handled by the profile at all
```

Note: removing a key stops the role from managing that key and the role
notifies a `sysctl --system` reload, which re-applies the remaining
configuration files However, `sysctl` cannot reset a key that is no longer
present in any file back to its kernel default, and a persistently loaded
kernel module stays loaded; reverting those to the pre-role state needs a
reboot (or a manual `sysctl -w` / `modprobe -r`).

- **Type**: `dict`
- **Required**: No
- **Default**: `{}`



### `sysctl_linux_reload`<a id="variable-sysctl_linux_reload"></a>

[*⇑ Back to ToC ⇑*](#toc)

If set to `true`, triggers `sysctl --system` after configuration changes to
reload all sysctl configuration files following the proper precedence order.
This ensures all drop-in files and possibly existing other sysctl configuration
files not managed by this role are applied consistently.

You generally do not need to change this for containers: the role tolerates
`sysctl --system` reload failures on detected containers (and skips live
`sysctl -w`, see `sysctl_linux_verify`). Set to `false` only if you want to
skip the reload entirely (e.g. to batch it yourself).

- **Type**: `bool`
- **Required**: No
- **Default**: `true`



### `sysctl_linux_verify`<a id="variable-sysctl_linux_verify"></a>

[*⇑ Back to ToC ⇑*](#toc)

If set to `true`, verifies the parameter value using the sysctl command and
actively sets it in the running kernel using `sysctl -w` if the current value
differs from the desired one.

When `false`, only writes the parameter to the configuration file without
verifying or immediately applying it to the running kernel.

Note: this is automatically treated as `false` on detected containers
(kernel parameters are typically read-only there), so the role only writes
the drop-in file and does not fail. You do not need to set it manually for
containers.

- **Type**: `bool`
- **Required**: No
- **Default**: `true`



### `sysctl_linux_ignore_unknown_key_errors`<a id="variable-sysctl_linux_ignore_unknown_key_errors"></a>

[*⇑ Back to ToC ⇑*](#toc)

If set to `true`, ignores errors caused by unknown or unsupported kernel
parameter keys. This is useful in container environments where certain
parameters may not exist or be accessible.

Generally not recommended for bare-metal or VM deployments where all expected
parameters should be available.

- **Type**: `bool`
- **Required**: No
- **Default**: `false`



### `sysctl_linux_config_dropin_file_name`<a id="variable-sysctl_linux_config_dropin_file_name"></a>

[*⇑ Back to ToC ⇑*](#toc)

Filename of the drop-in configuration file to be placed in `/etc/sysctl.d/`.
Defaults to `90-managed.conf`. The `90-` prefix ensures late loading and thus
higher precedence over files with lower-numbered prefixes.

If a non-default filename is used, any existing `/etc/sysctl.d/90-managed.conf`
from previous Ansible runs will be removed automatically to prevent conflicts.

- **Type**: `str`
- **Required**: No
- **Default**: `"90-managed.conf"`




<!-- ANSIBLE DOCSMITH MAIN END -->

## Dependencies<a id="dependencies"></a>

See `dependencies` in [`meta/main.yml`](./meta/main.yml).



## Compatibility<a id="compatibility"></a>

See `min_ansible_version` in [`meta/main.yml`](./meta/main.yml) and `__reboot_linux_supported_platforms` in [`vars/main.yml`](./vars/main.yml).



## External requirements<a id="requirements"></a>

There are no special requirements not covered by Ansible itself.
