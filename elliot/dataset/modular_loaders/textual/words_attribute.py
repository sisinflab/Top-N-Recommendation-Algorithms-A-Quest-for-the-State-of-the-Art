import typing as t
import numpy as np
import json
from types import SimpleNamespace

from elliot.dataset.modular_loaders.abstract_loader import AbstractLoader


class WordsTextualAttributes(AbstractLoader):
    def __init__(self, users: t.Set, items: t.Set, ns: SimpleNamespace, logger: object):
        self.logger = logger
        self.vocabulary_features_path = getattr(ns, "vocabulary_features", None)
        self.users_tokens_path = getattr(ns, "users_tokens", None)
        self.items_tokens_path = getattr(ns, "items_tokens", None)

        self.item_mapping = {}
        self.user_mapping = {}
        self.word_feature_shape = None
        self.word_features = None
        self.users_tokens = None
        self.items_tokens = None

        inner_users, inner_items = self.check_interactions_in_folder()

        self.users = users & inner_users
        self.items = items & inner_items

    def get_mapped(self) -> t.Tuple[t.Set[int], t.Set[int]]:
        return self.users, self.items

    def filter(self, users: t.Set[int], items: t.Set[int]):
        self.users = self.users & users
        self.items = self.items & items

    def create_namespace(self) -> SimpleNamespace:
        ns = SimpleNamespace()
        ns.__name__ = "WordsTextualAttributes"
        ns.object = self
        ns.vocabulary_features_path = self.vocabulary_features_path
        ns.users_tokens_path = self.users_tokens_path
        ns.items_tokens_path = self.items_tokens_path

        ns.user_mapping = self.user_mapping
        ns.item_mapping = self.item_mapping

        ns.word_feature_shape = self.word_feature_shape

        return ns

    def check_interactions_in_folder(self) -> (t.Set[int], t.Set[int]):
        users = set()
        items = set()
        if self.vocabulary_features_path and self.users_tokens_path and self.items_tokens_path:
            with open(self.users_tokens_path, "r") as f:
                self.users_tokens = json.load(f)
                self.users_tokens = {int(k): v for k, v in self.users_tokens.items()}
            with open(self.items_tokens_path, "r") as f:
                self.items_tokens = json.load(f)
                self.items_tokens = {int(k): v for k, v in self.items_tokens.items()}
            users = users.union(list(self.users_tokens.keys()))
            items = items.union(list(self.items_tokens.keys()))
            self.word_features = np.load(self.vocabulary_features_path)
            self.word_feature_shape = self.word_features.shape
        if users:
            self.user_mapping = {user: val for val, user in enumerate(users)}
        if items:
            self.item_mapping = {item: val for val, item in enumerate(items)}

        return users, items
