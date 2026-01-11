# Ansible role: `foundata.linux.reboot`

The `foundata.linux.reboot` Ansible role (part of the `foundata.linux` Ansible collection) detects if a system reboot is required and performs it if so.



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

* **Automatic detection of reboot requirements** using multiple methods:
  * Debian/Ubuntu: Checks for `/var/run/reboot-required` indicator file.
  * RHEL/Fedora: Uses `needs-restarting -r` to detect pending reboots.
  * Kernel updates: Compares running kernel against newest installed kernel in `/boot`.
  * SELinux: Detects mode changes that require a reboot to take effect.
* Configurable reboot behavior (timeout, message, post-reboot delay, connection timeout).
* Container-aware: Detects containerized environments to avoid reboot issues.
* Provides result facts (`reboot_linux_result`) for post-reboot verification and reporting.
* Designed for cross-platform compatibility, working seamlessly across Debian, Ubuntu, RHEL, and Fedora.



## Example playbooks, using this role<a id="examples"></a>

Run system upgrades and reboot if needed after everything else was finished (`post_tasks` ensures it runs after all other roles and their handlers have completed):

```yaml
---

- hosts: "all"
  gather_facts: false
  tasks:

    # Upgrades might create reboot need (e.g. new kernel version)
    - name: "Upgrade all packages (Debian/Ubuntu)"
      ansible.builtin.apt:
        upgrade: "dist"
        update_cache: true
      when: ansible_os_family == "Debian"

    - name: "Upgrade all packages (RHEL/Fedora)"
      ansible.builtin.dnf:
        name: "*"
        state: "latest"
      when: ansible_os_family == "RedHat"

  post_tasks:
    - name: "Trigger invocation of the foundata.linux.reboot role (reboot if required)"
      ansible.builtin.include_role:
        name: "foundata.linux.reboot"
```


## Supported tags<a id="tags"></a>

It might be useful and faster to only call parts of the role by using tags:

- `reboot_linux_setup`: Manage basic resources, such as packages or service users.
- `reboot_linux_reboot`: Manage reboots.

There are also tags usually not meant to be called directly but listed for the sake of completeness** and edge cases:

- `reboot_linux_always`, `always`: Tasks needed by the role itself for internal role setup and the Ansible environment.



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
