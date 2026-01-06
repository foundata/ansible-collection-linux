# Ansible role: `foundata.linux.reboot`

The `foundata.linux.reboot` Ansible role (part of the `foundata.linux` Ansible collection).

FIXME Explain, especially what "required" means



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

Install needed helper tools (FIXME explain how minimal, usually existing even in containers?) and reboot:

```yaml
---

- name: "Initialize the foundata.linux.reboot role"
  hosts: localhost
  gather_facts: false
  tasks:

    - name: "Trigger invocation of the foundata.linux.reboot role (reboot if required)"
      ansible.builtin.include_role:
        name: "foundata.linux.reboot"
```




## Supported tags<a id="tags"></a>

It might be useful and faster to only call parts of the role by using tags:

- `reboot_linux_setup`: Manage basic resources, such as packages or service users.
- `reboot_linux_reboot`: Manage reboots

There are also tags usually not meant to be called directly but listed for the sake of completeness** and edge cases:

- `reboot_linux_always`, `always`: Tasks needed by the role itself for internal role setup and the Ansible environment.



## Dependencies<a id="dependencies"></a>

See `dependencies` in [`meta/main.yml`](./meta/main.yml).



## Compatibility<a id="compatibility"></a>

See `min_ansible_version` in [`meta/main.yml`](./meta/main.yml) and `__reboot_linux_supported_platforms` in [`vars/main.yml`](./vars/main.yml).



## External requirements<a id="requirements"></a>

There are no special requirements not covered by Ansible itself.
