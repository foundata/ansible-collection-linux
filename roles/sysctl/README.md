# Ansible role: `foundata.linux.sysctl`

Manages Linux kernel parameters via `sysctl`, with optional workload-specific profiles that auto-tune values based on system resources.

Choose a profile for your workload (web server, database, file server, virtualization host, or router) and the role applies optimized parameters including security hardening. Override any value with `sysctl_linux_parameters`.


## Table of contents<a id="toc"></a>

- [Features](#features)
- [Example playbooks, using this role](#examples)
- [Supported tags](#tags)
- [Role variables](#variables)
- [Dependencies](#dependencies)
- [Compatibility](#compatibility)
- [External requirements](#requirements)



## Features

Main features:

* **Simple usage**: Use the [`sysctl_linux_parameters`](#variable-sysctl_linux_parameters) dictionary to maintain custom kernel parameters
* **Optional workload profiles**:
  * Pre-configured parameter sets for common workloads (e.g. `web`, `database`, ,`virtualization`, `router`; see [`sysctl_linux_profile`](#variable-sysctl_linux_profile) for details).
  * Auto-tuning: Profiles automatically calculate optimal values based on system resources (RAM, CPU cores) using Ansible facts.
  * Security hardening: All profiles include security best practices (source validation, ICMP hardening, filesystem protections).
  * Use [`sysctl_linux_parameters`](#variable-sysctl_linux_parameters) to overwrite a profile parameter to customize for edge cases.
* Container-aware: Handles read-only kernel parameters in containerized environments gracefully.
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


Remove a parameter (and use kernel defaults afterwards)

```yaml
---

- name: "Remove specific sysctl parameter"
  hosts: "all"
  tasks:

    - name: "Remove vm.swappiness from managed configuration"
      ansible.builtin.include_role:
        name: "foundata.linux.sysctl"
      vars:
        sysctl_linux_parameters:
          "vm.swappiness": null
```


Use a profile for workload-specific tuning:

```yaml
---

- name: "Configure web server with profile"
  hosts: "webservers"
  tasks:

    - name: "Apply web server profile"
      ansible.builtin.include_role:
        name: "foundata.linux.sysctl"
      vars:
        sysctl_linux_profile: "web"
```


Override profile values with custom parameters:

```yaml
---

- name: "Configure database server"
  hosts: "databases"
  tasks:

    - name: "Apply database profile with custom swappiness"
      ansible.builtin.include_role:
        name: "foundata.linux.sysctl"
      vars:
        sysctl_linux_profile: "database"
        sysctl_linux_parameters:
          "vm.swappiness": 1  # override profile default
```




## Supported tags<a id="tags"></a>

It might be useful and faster to only call parts of the role by using tags:

- `sysctl_linux_setup`: Manage basic resources, such as packages or service users.
- `sysctl_linux_config`: Manage sysctl parameters.

There are also tags usually not meant to be called directly but listed for the sake of completeness** and edge cases:

- `sysctl_linux_always`, `always`: Tasks needed by the role itself for internal role setup and the Ansible environment.



## Role variables<a id="variables"></a>

See [`defaults/main.yml`](./defaults/main.yml) for all available role parameters and their description. [`vars/main.yml`](./vars/main.yml) contains internal variables you should not override (but their description might be interesting).

Additionally, there are variables read from other roles and/or the global scope (for example, host or group vars) as follows:

- None right now.



## Dependencies<a id="dependencies"></a>

See `dependencies` in [`meta/main.yml`](./meta/main.yml).



## Compatibility<a id="compatibility"></a>

See `min_ansible_version` in [`meta/main.yml`](./meta/main.yml) and `__reboot_linux_supported_platforms` in [`vars/main.yml`](./vars/main.yml).



## External requirements<a id="requirements"></a>

There are no special requirements not covered by Ansible itself.
