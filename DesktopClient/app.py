import threading
import time

import py_cui
import sys

sys.path.append('../')
from MixnetClient import MixnetClient
from utils.coding import unpack_pub_k


class MixerMessenger:
    def __init__(self, master: py_cui.PyCUI):
        self.master = master
        self.app = MixnetClient()
        self.ask_nickname()
        self.chats_list_cell = self.master.add_scroll_menu('Chats', 0, 0, row_span=5, column_span=1)
        self.chats_list_cell.add_text_color_rule("", py_cui.WHITE_ON_BLACK, 'startswith',
                                                 selected_color=py_cui.MAGENTA_ON_BLACK)
        self.chat_cell = self.master.add_scroll_menu("Messages", 0, 1, 5, 5)
        self.add_chat = self.master.add_button(" + Chat", 5, 0, command=self.show_add_pub_k_text_box)
        self.show_keys_btn = self.master.add_button("Show keys", 6, 0, command=self.show_keys)
        self.input = self.master.add_text_box("Your input", 5, 1, 1, 5)
        self.show_chat_list()
        self.chats_list_cell.add_key_command(py_cui.keys.KEY_ENTER, self.show_chat)
        self.input.add_key_command(py_cui.keys.KEY_ENTER, self.send_message)
        self.start_background_updating()
        self.master.move_focus(self.chats_list_cell)
        # self.fill_chats_cell()

    def ask_nickname(self):
        if not self.app.key_manager.nickname_is_saved:
            self.master.show_text_box_popup('Please enter your name', self.save_nickname)

    def save_nickname(self, nickname):
        self.app.key_manager.save_nickname(nickname)

    def show_chat(self, silent=False):
        cur_receiver = self.chats_list_cell.get()
        if not cur_receiver:
            if not silent:
                self.master.show_warning_popup("Warning", "No chat is selected")
            return
        self.show_chat_spec(cur_receiver)

    def show_chat_spec(self, cur_receiver):
        self.chat_cell.clear()
        self.chat_cell.set_title(f"Chat with: {cur_receiver.name}")
        self.fill_chat(cur_receiver)
        self.scroll_chat_to_bottom()
        # self.master.move_focus(self.input)

    #
    def fill_chat(self, user):
        messages = self.app.get_chat(user)
        for m in messages:
            if m.direction == "outgoing":
                self.chat_cell.add_item(f"                                               {m.text}")
            else:
                self.chat_cell.add_item(m.text)

    def scroll_chat_to_bottom(self):
        self.chat_cell._jump_to_bottom(self.chat_cell.get_viewport_height())

    def send_message(self):
        message = self.input.get()
        cur_receiver = self.chats_list_cell.get()
        if not cur_receiver:
            self.master.show_warning_popup("Warning", "Select receiver from 'Chats' menu")
            return
        self.app.send(receiver_pub_k=cur_receiver.pub_k, message=message)
        self.show_chat()
        # self.chat_cell.add_item(message)
        self.input.clear()

    def show_name_text_box(self):
        self.master.show_text_box_popup('Please enter your name', self.register_and_generate_keys)

    def show_keys(self):
        text = "!!!"
        self.master.show_message_popup("PUBLIC KEY", text)

    def show_add_pub_k_text_box(self):
        self.master.show_text_box_popup('Please enter receiver pub k', self.show_add_username_text_box)

    def show_add_username_text_box(self, receiver_pub_k):
        self.tmp_recv_pub_k = receiver_pub_k
        self.master.show_text_box_popup('Please enter nickname', self.add_user)

    def add_user(self, nickname):
        success = self.app.add_user(nickname, self.tmp_recv_pub_k)
        if success:
            self.master.show_message_popup('', 'DONE')
        else:
            self.master.show_warning_popup("Warning", "User with this public key already exist")
        self.show_chat_list()

    def show_chat_list(self):
        """returns bool [is list updated]"""
        self.show_chat(silent=True)
        all_chats = self.app.get_chat_list()
        all_chats_names = set(x.name for x in all_chats)
        existed_names = set(x.name for x in self.chats_list_cell.get_item_list())
        if all_chats_names == existed_names:
            return False
        cur_chat = self.chats_list_cell.get()
        self.chats_list_cell.clear()
        for chat in all_chats:
            self.chats_list_cell.add_item(chat)
        self.chats_list_cell.set_selected(cur_chat)
        return True
        # self.chats_scroll_cell.set_selected(cur_chat)

    #
    # def reset_title(self, new_title):
    #     self.master.set_title(new_title)
    #
    def start_background_updating(self):
        # return
        operation_thread = threading.Thread(target=self.background_update, daemon=True)
        operation_thread.start()

    #
    # def add_new_chats_from_updates(self, updated_chats):
    #     self.chats = list(set(self.chats).union(updated_chats))
    #     self.chats_scroll_cell._view_items = self.chats
    #
    def background_update(self):
        while True:
            cur_chat = self.chats_list_cell.get()
            chat_list_updated = self.show_chat_list()
            # self.show_chat(silent=True)
            # updated_chats, _ = get_updates()
            # self.add_new_chats_from_updates(updated_chats)
            # cur_chat = self.chats_scroll_cell.get()
            # if cur_chat in updated_chats:
            #     self.show_chat()
            time.sleep(1)

    # self.show_chat()


# Create the CUI, pass it to the wrapper object, and start it
root = py_cui.PyCUI(8, 6)
root.set_refresh_timeout(1)
root.set_title('MixerNet')
# root.enable_logging(logging_level=logging.DEBUG)
s = MixerMessenger(root)
root.start()
