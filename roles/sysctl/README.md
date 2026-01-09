# Ansible role: `foundata.linux.sysctl`

Manages Linux kernel parameters via `sysctl`  and optionally applied immediately.

Planned features:

- opt-in presets (like "webserver", "database", "virtualization_host", "router" including security hardening, still overwritable with singel parameters)
  3. Calculated Values Based on System Resources

  sysctl_linux_auto_tune: true
  Auto-calculate parameters like net.core.rmem_max, vm.min_free_kbytes based on ansible_memtotal_mb. Avoids hardcoding values that don't fit all systems.
  5. Runtime-Only Mode

  sysctl_linux_persist: false  # Apply now but don't write to sysctl.d
  Useful for temporary tuning or testing before committing.


## Table of contents<a id="toc"></a>

- [Role variables](#variables)
- [Example playbooks, using this role](#examples)
- [Supported tags](#tags)
- [Dependencies](#dependencies)
- [Compatibility](#compatibility)
- [External requirements](#requirements)



## Role variables<a id="variables"></a>

See [`defaults/main.yml`](./defaults/main.yml) for all available role parameters and their description. [`vars/main.yml`](./vars/main.yml) contains internal variables you should not override (but their description might be interesting).

Additionally, there are variables read from other roles and/or the global scope (for example, host or group vars) as follows:

- None right now.



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


Enable security hardening with custom overrides (FIXME not implemented yet):

```yaml
---

- name: "Harden kernel parameters"
  hosts: "all"
  tasks:

    - name: "Apply security hardening with custom overrides"
      ansible.builtin.include_role:
        name: "foundata.linux.sysctl"
      vars:
        sysctl_linux_security_hardening: true
        sysctl_linux_parameters:
          # Override a security default
          "net.ipv4.conf.all.log_martians": 0
          # Add additional parameters
          "kernel.randomize_va_space": 2
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



## Supported tags<a id="tags"></a>

It might be useful and faster to only call parts of the role by using tags:

- `sysctl_linux_setup`: Manage basic resources, such as packages or service users.
- `sysctl_linux_config`: Manage sysctl parameters.

There are also tags usually not meant to be called directly but listed for the sake of completeness** and edge cases:

- `sysctl_linux_always`, `always`: Tasks needed by the role itself for internal role setup and the Ansible environment.



## Dependencies<a id="dependencies"></a>

See `dependencies` in [`meta/main.yml`](./meta/main.yml).



## Compatibility<a id="compatibility"></a>

See `min_ansible_version` in [`meta/main.yml`](./meta/main.yml) and `__reboot_linux_supported_platforms` in [`vars/main.yml`](./vars/main.yml).



## External requirements<a id="requirements"></a>

There are no special requirements not covered by Ansible itself.
