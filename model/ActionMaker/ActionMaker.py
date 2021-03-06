from model.Enums.ActionsEnum import ActionsEnum
from model.Containers.ActionQueue.Action import Action
import random, hashlib

class ActionMaker:

    TIME_OUT_SEND_POST = 5

    TIME_OUT_GET_GROUPS = 0.001

    TIME_OUT_INTERNAL_OPERATIONS = 0.001

    COUNTRY_ID = 3

    MAX_AMOUNT_OF_GROUPS = 50

    EACH_POST_TO_EACH_GROUP = 1

    MIN_AMOUNT_USERS_IN_GROUP = 200

    def __init__(self,action_queue,t_o_send_post,t_o_get_group,t_o_internal_operations):

        self.__action_queue = action_queue
        self.__scheduled_actions_hashes = []

        ActionMaker.TIME_OUT_SEND_POST = t_o_send_post

        ActionMaker.TIME_OUT_GET_GROUPS = t_o_get_group

        ActionMaker.TIME_OUT_INTERNAL_OPERATIONS  = t_o_internal_operations

    def create_send_posts_to_groups_actions(self, groups, posts, asap = False):
        for pair in self.get_group_and_post_to_send(groups, posts):
            group, post = pair

            post_to_group_string = str(group.gid) + post.text
            post_to_group_hash = hashlib.md5(post_to_group_string.encode('utf-8')).hexdigest()

            if post_to_group_hash not in self.__scheduled_actions_hashes: # to exclude duplicated sendings during one start
                self.__action_queue.add_action_to_leisurely_queue(
                    self.create_send_post_to_group_action(group.gid, post.text, post.list_of_photos), asap)
            self.__scheduled_actions_hashes.append(post_to_group_hash)

    def get_group_and_post_to_send(self, groups, posts):
        pairs_to_send = []
        if ActionMaker.EACH_POST_TO_EACH_GROUP:
            for post in posts:
                for group in groups:
                    pairs_to_send.append([group, post])
        else:
            for group in groups:
                rand_post = random.choice(posts)
                pairs_to_send.append([group, rand_post])

        return  pairs_to_send

    def create_search_groups_action(self,key_word) :
        self.__action_queue.add_action_to_hurriedly_queue(
            Action(ActionsEnum.SEARCH_GROUPS,(key_word,ActionMaker.MAX_AMOUNT_OF_GROUPS,
                                        ActionMaker.COUNTRY_ID,ActionMaker.MIN_AMOUNT_USERS_IN_GROUP),ActionMaker.TIME_OUT_GET_GROUPS))

    def create_send_post_to_group_action(self,group_id,text_for_post,list_of_photos):
        return Action(ActionsEnum.SEND_POSTS_TO_GROUPS,
                      (group_id,text_for_post,list_of_photos),ActionMaker.TIME_OUT_SEND_POST)

    def create_edit_post_to_group_action(self,old_text,new_text,new_list_of_paths):
        self.__action_queue.add_action_to_edit_containers_queue(
            Action(ActionsEnum.EDIT_POST, (old_text, new_text,new_list_of_paths),
                   ActionMaker.TIME_OUT_INTERNAL_OPERATIONS))

    def create_add_post_action(self,new_text,new_list_of_paths):
        self.__action_queue.add_action_to_edit_containers_queue(
            Action(ActionsEnum.ADD_POST, (new_text,new_list_of_paths),
                   ActionMaker.TIME_OUT_INTERNAL_OPERATIONS))

    def create_delete_post_action(self, text):
        self.__action_queue.add_action_to_edit_containers_queue(
            Action(ActionsEnum.REMOVE_POST,text,
                   ActionMaker.TIME_OUT_INTERNAL_OPERATIONS))

    def create_read_all_records_from_db_action(self):
        self.__action_queue.add_action_to_edit_containers_queue(
            Action(ActionsEnum.READ_ALL_RECORDS_FROM_DB, (),
                   ActionMaker.TIME_OUT_INTERNAL_OPERATIONS))

