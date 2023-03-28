from pyrogram.client import Client
from pyrogram.types import ChatPermissions
from pyrogram.types import ChatPrivileges
from pyrogram.enums import ChatMemberStatus
import hashlib

class TgMember:
    def __init__(self):
        self.username = None
        self.is_admin = None
        self.admin_title = None
        self.permissions = None
        self.privileges = None

class TgGroup:
    def __init__(self):
        self.id = None
        self.title = None
        self.image = None
        self.image_hash = None
        self.description = None
        self.members_list = None
        self.chat_permissions = None
        self.ownership = False
        self.exists = False
        
        def validate(self):
            pass



class TgGroupController:
    def __init__(self, session_string):
        self._conn = Client('Telegram Ansible Module', session_string=session_string, in_memory=True)

        

    def _get_chat_member(self, group, username):
        with self._conn:
            return self._conn.get_chat_member(group, username)

    def _get_default_chat_permissions(self, group):
        with self._conn:
            chat = self._conn.get_chat(group.id)
            return chat.permissions


    def get_member_obj(self, group, username):
        old_user = self._get_chat_member(group.id, username)
        user = TgMember()
        user.username = old_user.user.username
        user.is_admin = old_user.status == ChatMemberStatus.ADMINISTRATOR
        if old_user.permissions == None:
            user.permissions = self._get_default_chat_permissions(group)
        else:
            user.permissions = old_user.permissions
        if user.is_admin:
            user.admin_title = old_user.custom_title
            user.privileges = old_user.privileges
        else:
            user.privileges = ChatPrivileges(can_manage_chat=True)
        return user

    def get_group_obj(self, title, id=None):
        group = TgGroup()
        group.id = id
        group.title = title
        if group.id == None:
            group.exists = self._check_if_group_exists_by_title(group.title)
            group.id = self._get_id_by_title(group.title)
        else:
            group.exists = self._check_if_group_exists_by_id(group.id)
        if group.exists:
            group.ownership = self._check_ownership(group.id)
            if group.ownership:
                raw_group = self._fetch_group_data(group.id)
                if group.title == None or not group.title == raw_group.title:
                    group.title = raw_group.title
                group.description = raw_group.description
                group.image_hash = self._get_last_image_hash(group.id)
        return group

    def create_new_group(self, group): #Получает перечисленные параметры, создает группу.
        with self._conn:
            new_group = self._conn.create_supergroup(group.title)
            group.id = new_group.id
            group.title = new_group.title
            group.ownership = True
            group.exists = True
            self._conn.send_message(chat_id=group.id, text='group_id:' + str(group.id))
            return group

    def _check_if_group_exists_by_title(self, title): #находит в списке чатов группу с таким именем. Возвращает bool
        with self._conn:
            for dialog in self._conn.get_dialogs():
                if (dialog.chat.title == title) and (dialog.chat.type.name == "GROUP" or dialog.chat.type.name == "SUPERGROUP"):
                    return True
            return False

    def _check_if_group_exists_by_id(self, id): #находит в списке чатов группу с таким именем. Возвращает bool
        with self._conn:
            for dialog in self._conn.get_dialogs():
                if (dialog.chat.id == id ) and (dialog.chat.type.name == "GROUP" or dialog.chat.type.name == "SUPERGROUP"):
                    return True
            return False

    def _get_id_by_title(self, title):
        with self._conn:
            for dialog in self._conn.get_dialogs():
                if (dialog.chat.title == title ) and (dialog.chat.type.name == "GROUP" or dialog.chat.type.name == "SUPERGROUP"):
                    return dialog.chat.id
            return None

    def _fetch_group_data(self, id): #Получает по названию группы все данные, и записывает в переменные объекта. Возвращает Null
        with self._conn:
            for dialog in self._conn.get_dialogs():
                if dialog.chat.id == id:
                     return self._conn.get_chat(id)

    def _check_ownership(self, id): #находит в списке чатов группу с таким именем. Возвращает bool
        with self._conn:
            for dialog in self._conn.get_dialogs():
                if (dialog.chat.id == id) and (dialog.chat.type.name == "GROUP" or dialog.chat.type.name == "SUPERGROUP"):
                    members = self._conn.get_chat_members(chat_id=dialog.chat.id)
                    for member in members:
                        if member.user.is_self == True:
                            if member.status == ChatMemberStatus.OWNER:
                               return True
                    return False

    def _get_last_image_hash(self, id):
        with self._conn:
            result = None
            messages = self._conn.search_messages(chat_id=id, query='image_hash:')
            for message in messages:
                try:
                    if message.from_user.is_self:
                        result = message.text.split(':')[1]
                except IndexError as e:
                    pass
                break
            return result


    def remove_group(self, group): #Удаляет группу
        with self._conn:
            return self._conn.delete_supergroup(group.id)

    def set_group_description(self, group): #Задает группе описание. 
        if len(group.description) > 255:
            raise ValueError("Description longer than 255 symbols!")
        with self._conn:
            self._conn.set_chat_description(chat_id=group.id, description=group.description)

    def open_image_file(self, path_to_image:str):
        image = open(path_to_image, "rb")
        return image

    def get_image_hash(self, image):
        image_hash = hashlib.md5(image.read()).hexdigest()
        return image_hash

    def close_image(self, image):
        image.close()

    def check_membership(self, group, username):
        result = False
        with self._conn:
            members = self._conn.get_chat_members(group.id, username)
            for member in members:
                if member.user.username == username:
                    result = True
        return result

    def set_new_group_image(self, group): #Задает группе изображение
        with self._conn:
            self._conn.set_chat_photo(chat_id=group.id, photo=group.image)
            self._conn.send_message(chat_id=group.id, text="image_hash:" + group.image_hash)

    def set_new_title(self, group):
        with self._conn:
            self._conn.set_chat_title(chat_id=group.id, title=group.title)

    def add_new_member(self, group, username):
        with self._conn:
            self._conn.unban_chat_member(group.id, username)
            self._conn.add_chat_members(group.id, username)

    def delete_member(self, group, username):
        with self._conn:
            self._conn.ban_chat_member(group.id, username)

    def list_object_merge(self, array, object):
        for key in array.keys():
            setattr(object, key, array[key])
        return object

    def push_permissions(self, group, username, permissions):
        with self._conn:
            self._conn.restrict_chat_member(group.id, username, permissions)

    def push_privileges(self, group, username, privileges):
        with self._conn:
            self._conn.promote_chat_member(group.id, username, privileges)

    def remove_privileges(self, group, username):
        with self._conn:
            self._conn.promote_chat_member(group.id, username, ChatPrivileges(can_manage_chat=False, can_delete_messages=False, can_change_info=False, can_invite_users=False, can_edit_messages=False, can_manage_video_chats=False, can_post_messages=False, can_promote_members=False, can_restrict_members=False, is_anonymous=False))

    def set_admin_title(self, group, username, title):
        with self._conn:
            self._conn.set_administrator_title(group.id, username, title)

    def push_default_permissions(self, group, permissions):
        with self._conn:
            self._conn.set_chat_permissions(group.id, permissions)




if __name__ == '__main__':
    pass

