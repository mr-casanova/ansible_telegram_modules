#/usr/bin/python

# Copyright: (c) 2018, Terry Jones <terry.jones@example.org>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


DOCUMENTATION = r'''
---
module: group_keeper

short_description: Module for managing Telegram Groups 

# If this is part of a collection, you need to use semantic versioning,
# i.e. the version is of the form "2.5.0" and not "2.4".
version_added: "1.0.0"

description: This module allows you to manage Telegram Groups, adding descriptions, group picture, users, give users some permission, etc.


# Specify this value according to your collection
# in format of namespace.collection.doc_fragment_name
extends_documentation_fragment:
    - my_namespace.my_collection.my_doc_fragment_name

author:
    - Erik Mosinyan (github.com/mr-casanova)
'''

EXAMPLES = r'''
# create group with description and group picture
- name: Test group
  avant_it.telegram.group_keeper:
      session_string: < session string>      
      group_title: Test group
      group_image: img/example.png
      group_description: Test group for documentation
      state: present
 

# create group with user
  - name: create group with users
    avant_it.telegram.group_keeper:
      session_string: <session_string>
      group_title: Test group
      group_image: img/example.ong
      group_description: Test group with users for documetation
      state: present
      users:
      - name: telegram_username_of_user
        state: present

# create group with users and permissions
  - name: create group with users and permissions
    avant_it.telegram.group_keeper:
      session_string: <session_string>
      group_title: Test group
      group_image: img/example.ong
      group_description: Test group with users for documetation
      state: present
      users:
      - name: telegram_username_of_user
        state: present
        permissions:
          can_pin_messages: True

# create group with administrator
  - name: create group with administrator
    avant_it.telegram.group_keeper:
      session_string: <session_string>
      group_title: Test group
      group_image: img/example.ong
      group_description: Test group with users for documetation
      state: present
      users:
      - name: telegram_username_of_user
        is_admin: True
        admin_title: SomeTitle
        state: present
        privileges:
            can_manage_video_chats: True

# create group and add user with all permissions and privileges
  - name: all permissions and privileges
    avant_it.telegram.group_keeper:
      session_string: <session_string>
      group_title: Test group
      group_image: img/example.ong
      group_description: Test group with users for documetation
      state: present
      users:
      - name: telegram_username_of_user
        is_admin: True
        admin_title: SomeTitle
        state: present
        permissions:
            can_send_messages: True
            can_send_media_messages: True
            can_send_other_messages: True
            can_send_polls: True
            can_add_webpage_preview: True
            can_change_info: True
            can_invite_users: True
            can_pin_messages: True
        privileges:
            can_manage_chat: True
            can_delete_messages: True
            can_manage_video_chats: True
            can_restrict_members: True
            can_promote_members: True
            can_change_info: True
            can_invite_users: True
            can_pin_messages: True
            is_anonymous: True
'''

RETURN = r'''
# These are examples of possible return values, and in general should use other names for return values.
original_message:
    description: The original name param that was passed in.
    type: str
    returned: always
    sample: 'hello world'
message:
    description: The output message that the test module generates.
    type: str
    returned: always
    sample: 'goodbye'
'''
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.avant_it.telegram.plugins.module_utils.tggroupcontroller import TgGroupController

def run_module():
    module_args = dict(
        group_title=dict(type='str', required=True),
        session_string=dict(type='str', required=True),
        group_id=dict(type=int, required=False, default=None),
        group_image=dict(type='str', required=False, default=None),
        group_description=dict(type='str', required=False),
        state=dict(type='str', default='present', required=False, choices=['absent', 'present']),
        default_group_permissions=dict(type='list', required=False, default=None, options=dict(
            can_send_messages=dict(type='bool', required=False, default=None),
            can_send_media_messages=dict(type='bool', required=False, default=None),
            can_send_other_messages=dict(type='bool', required=False, default=None),
            can_send_polls=dict(type='bool', required=False, default=None),
            can_add_webpage_preview=dict(type='bool', required=False, default=None),
            can_change_info=dict(type='bool', required=False, default=None),
            can_invite_users=dict(type='bool', required=False, default=None),
            can_pin_messages=dict(type='bool', required=False, default=None)
            )
          ),
        users=dict(type='list', required=True, options=dict(
            name=dict(type='str', required=True),
            is_admin=dict(type='bool', required=False, default=False),
            admin_title=dict(type='str', required=False),
            state=dict(type='str', required=False, default='present', choices=['absent', 'present']),
            permissions=dict(type='list', required=False, default={}, options=dict(
                can_send_messages=dict(type='bool', required=False, default=None),
                can_send_media_messages=dict(type='bool', required=False, default=None),
                can_send_other_messages=dict(type='bool', required=False, default=None),
                can_send_polls=dict(type='bool', required=False, default=None),
                can_add_webpage_preview=dict(type='bool', required=False, default=None),
                can_change_info=dict(type='bool', required=False, default=None),
                can_invite_users=dict(type='bool', required=False, default=None),
                can_pin_messages=dict(type='bool', required=False, default=None)
                )
            ),
            privileges=dict(type='list', required=False, default=None, options=dict(
                can_manage_chat=dict(type='bool', reqired=False, default=None),
                can_delete_messages=dict(type='bool', required=False, default=None),
                can_manage_video_chats=dict(type='bool', required=False, default=None),
                can_restrict_members=dict(type='bool', required=False, default=None),
                can_promote_members=dict(type='bool', required=False, default=None),
                can_change_info=dict(type='bool', required=False, default=None),
                can_invite_users=dict(type='bool', required=False, default=None),
                can_pin_messages=dict(type='bool', required=False, default=None),
                is_anonymous=dict(type='bool', required=False, default=None)
                )
                )
            )
        )
    )

    result = dict(
        changed=False,
        original_message='',
        message=''
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    changes = {"changed" : False,
               "count" : 0,
               "change list" : []
               }


    def exit_module_error(msg):
        module.fail_json(msg=msg, **result)

    def exit_module():
        if len(changes['change list']) > 0:
            changes['count'] = len(changes['change list'])
            changes['changed'] = True
        result['message'] = changes
        module.exit_json(**result)

    def process_members(members_list, group, controller):
        for member in members_list:
            if member['state'].lower() == 'absent':
                if controller.check_membership(group, member['name']):
                    controller.delete_member(group, member['name'])
                    continue
            if member['state'].lower() == 'present':
                if not controller.check_membership(group, member['name']):
                    controller.add_new_member(group, member['name'])

                cur_user = controller.get_member_obj(group, member['name'])
                if 'permissions' in member and len(member['permissions']) > 0:
                    cur_user.permissions = controller.list_object_merge(member['permissions'], cur_user.permissions)
                    controller.push_permissions(group, cur_user.username, cur_user.permissions)

                if member['is_admin'] == True:
                    if 'privileges' in member and len(member['privileges']) > 0:
                        cur_user.privileges = controller.list_object_merge(member['privileges'], cur_user.privileges)
                        controller.push_privileges(group, cur_user.username, cur_user.privileges)
                    elif not cur_user.is_admin and (not 'privileges' in member or len(member['privileges']) == 0):
                        controller.push_privileges(group, cur_user.username, None)
                elif member['is_admin'] == False:
                    if cur_user.is_admin:
                        controller.remove_privileges(group, cur_user.username)

                if 'admin_title' in member and (member['is_admin'] or cur_user.is_admin):
                    controller.set_admin_title(group, cur_user.username, member['admin_title'])


    def process_group(controller, params, group):
        if not params['group_title'] == group.title:
            group.title = params['group_title']
            controller.set_new_title(group)
            changes['change list'].append({'Group Title' : group.title})

        if not params['group_description'] == group.description:
            group.description = params['group_description']
            changes['change list'].append({'Group Description' : group.description})
            try:
                controller.set_group_description(group)
            except ValueError:
                exit_module_error('Description length must be less than 255 symbols')
            
        if not params['group_image'] == None:
            try:
                image = controller.open_image_file(params['group_image'])
            except Exception as e:
                print(e)
                exit_module_error('Image ' + params['group_image'] + ' doesn\'t exist.')
            image_hash = controller.get_image_hash(image)
            print(image_hash)
            if not group.image_hash == image_hash:
                print(group.image_hash)
                group.image = image
                group.image_hash = image_hash
                controller.set_new_group_image(group)
                changes['change list'].append({'Group Image': group.image_hash})
                controller.close_image(group.image)
    
    try:
        tg_controller = TgGroupController(module.params['session_string'])
    except Exception as e:
        exit_module_error(e)

    group = tg_controller.get_group_obj(title=module.params['group_title'],id = module.params['group_id'])

    if module.params['state'].lower() == 'absent':
        if group.exists:
            tg_controller.remove_group(group)
            changes['change list'].append({'Group removed' : True})
            exit_module()
        else:
            exit_module()
    elif module.params['state'].lower() == 'present':
        if not group.exists:
            new_group = tg_controller.create_new_group(group)
            process_group(tg_controller, module.params, new_group)
            changes['change list'].append({'Group Created' : True})
        else:
            process_group(tg_controller, module.params, group)

    if len(module.params['users']) > 0:
        process_members(module.params['users'], group, tg_controller)

    

    exit_module()

def main():
    run_module()

if __name__ == '__main__':
    main()


