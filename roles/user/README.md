# Ansible role: `foundata.linux.user`

The `foundata.linux.user` Ansible role (part of the `foundata.linux` Ansible collection).



## Table of contents<a id="toc"></a>

- [Example playbooks, using this role](#examples)
- [Supported tags](#tags)<!-- ANSIBLE DOCSMITH TOC START -->
- [Role variables](#variables)<!-- ANSIBLE DOCSMITH TOC END -->
- [Dependencies](#dependencies)
- [Compatibility](#compatibility)
- [External requirements](#requirements)



## Example playbooks, using this role<a id="examples"></a>

Installation with automatic upgrade:

```yaml
---

- name: "Initialize the foundata.linux.user role"
  hosts: localhost
  gather_facts: false
  tasks:

    - name: "Trigger invocation of the foundata.linux.user role"
      ansible.builtin.include_role:
        name: "foundata.linux.user"
      vars:
        user_linux_autoupgrade: true
```

Uninstall:

```yaml
---

- name: "Initialize the foundata.linux.user role"
  hosts: localhost
  gather_facts: false
  tasks:

    - name: "Trigger invocation of the foundata.linux.user role"
      ansible.builtin.include_role:
        name: "foundata.linux.user"
      vars:
        user_linux_state: "absent"
```



## Supported tags<a id="tags"></a>

It might be useful and faster to only call parts of the role by using tags:

- `user_linux_setup`: Manage basic resources, such as packages or service users.
- `user_linux_config`: Manage settings, such as adapting or creating configuration files.
- `user_linux_service`: Manage services and daemons, such as running states and service boot configurations.

There are also tags usually not meant to be called directly but listed for the sake of completeness** and edge cases:

- `user_linux_always`, `always`: Tasks needed by the role itself for internal role setup and the Ansible environment.


<!-- ANSIBLE DOCSMITH MAIN START -->

## Role variables<a id="variables"></a>

See [`defaults/main.yml`](./defaults/main.yml) for all available role parameters and their description. [`vars/main.yml`](./vars/main.yml) contains internal variables you should not override (but their description might be interesting).

Additionally, there are variables read from other roles and/or the global scope (for example, host or group vars) as follows:

- None right now.

<!-- ANSIBLE DOCSMITH MAIN END -->

## Dependencies<a id="dependencies"></a>

See `dependencies` in [`meta/main.yml`](./meta/main.yml).



## Compatibility<a id="compatibility"></a>

See `min_ansible_version` in [`meta/main.yml`](./meta/main.yml) and `__user_linux_supported_platforms` in [`vars/main.yml`](./vars/main.yml).



## External requirements<a id="requirements"></a>

There are no special requirements not covered by Ansible itself.
