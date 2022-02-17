"""
Module description:

"""

__version__ = '0.3.1'
__author__ = 'Antonio Ferrara'
__email__ = 'antonio.ferrara@poliba.it'

import numpy as np
import scipy.sparse as sp
from tqdm import tqdm
import networkx as nx
from collections import defaultdict

from elliot.dataset.samplers import custom_sampler as cs
from elliot.recommender import BaseRecommenderModel
from elliot.recommender.base_recommender_model import init_charger
from elliot.recommender.knowledge_aware.kaHFM_batch.tfidf_utils import TFIDF
from elliot.recommender.knowledge_aware.kahfm_embeddings.kahfm_embeddings_model import KaHFMEmbeddingsModel
from elliot.recommender.recommender_utils_mixin import RecMixin
from elliot.utils.write import store_recommendation


class KGIN(RecMixin, BaseRecommenderModel):
    """
    """
    @init_charger
    def __init__(self, data, config, params, *args, **kwargs):
        ######################################

        self._params_list = [
            ("_learning_rate", "lr", "lr", 0.0001, None, None),
            ("_l_w", "l_w", "l_w", 0.005, None, None),
            ("_l_b", "l_b", "l_b", 0, None, None),
            ("_loader", "loader", "load", "ChainedKG", None, None),
        ]
        self.autoset_params()

        self._ratings = self._data.train_dict

        self._side = getattr(self._data.side_information, self._loader, None)

        self._sampler = cs.Sampler(self._data.i_train_dict)

        ckg_graph = nx.MultiDiGraph()

        self.public_entities = {**self._data.public_items, **self._side.public_objects}
        self.private_entities = {**self._data.private_items, **self._side.private_objects}

        print("Building the graph")
        rd = defaultdict(list)
        rd[0] = list(zip(*self._data.sp_i_train.nonzero()))

        for h_id, r_id, t_id in tqdm(self._side.map_, ascii=True):
            ckg_graph.add_edge(self.public_entities[h_id], self.public_entities[t_id], key=self._side.public_relations[r_id])
            rd[self._side.public_relations[r_id]].append([self.public_entities[h_id], self.public_entities[t_id]])

        print("Building adjacency matrix")

        def _bi_norm_lap(adj):
            # D^{-1/2}AD^{-1/2}
            rowsum = np.array(adj.sum(1))

            d_inv_sqrt = np.power(rowsum, -0.5).flatten()
            d_inv_sqrt[np.isinf(d_inv_sqrt)] = 0.
            d_mat_inv_sqrt = sp.diags(d_inv_sqrt)

            # bi_lap = adj.dot(d_mat_inv_sqrt).transpose().dot(d_mat_inv_sqrt)
            bi_lap = d_mat_inv_sqrt.dot(adj).dot(d_mat_inv_sqrt)
            return bi_lap.tocoo()

        def _si_norm_lap(adj):
            # D^{-1}A
            rowsum = np.array(adj.sum(1))

            d_inv = np.power(rowsum, -1).flatten()
            d_inv[np.isinf(d_inv)] = 0.
            d_mat_inv = sp.diags(d_inv)

            norm_adj = d_mat_inv.dot(adj)
            return norm_adj.tocoo()

        adj_mat_list = []
        print("Begin to build sparse relation matrix ...")
        for r_id in tqdm(rd.keys()):
            np_mat = np.array(rd[r_id])
            if r_id == 0:
                cf = np_mat.copy()
                cf[:, 1] = cf[:, 1] + len(self._data.users)  # [0, n_items) -> [n_users, n_users+n_items)
                vals = [1.] * len(cf)
                adj = sp.coo_matrix((vals, (cf[:, 0], cf[:, 1])), shape=(len(self.public_entities), len(self.public_entities)))
            else:
                vals = [1.] * len(np_mat)
                adj = sp.coo_matrix((vals, (np_mat[:, 0], np_mat[:, 1])), shape=(len(self.public_entities), len(self.public_entities)))
            adj_mat_list.append(adj)

        norm_mat_list = [_bi_norm_lap(mat) for mat in adj_mat_list]
        mean_mat_list = [_si_norm_lap(mat) for mat in adj_mat_list]
        # interaction: user->item, [n_users, n_entities]
        norm_mat_list[0] = norm_mat_list[0].tocsr()[:len(self._data.users), len(self._data.users):].tocoo()
        mean_mat_list[0] = mean_mat_list[0].tocsr()[:len(self._data.users), len(self._data.users):].tocoo()

        self._model = KaHFMEmbeddingsModel(self._user_factors,
                                           self._item_factors,
                                           self._params.lr,
                                           self._params.l_w,
                                           self._params.l_b,
                                           self._seed)

    @property
    def name(self):
        return "KaHFMEmbeddings" \
               + f"_{self.get_base_params_shortcut()}" \
               + f"_{self.get_params_shortcut()}"

    def train(self):
        if self._restore:
            return self.restore_weights()

        for it in self.iterate(self._epochs):
            loss = 0
            steps = 0
            with tqdm(total=int(self._transactions_per_epoch // self._batch_size), disable=not self._verbose) as t:
                for batch in self._sampler.step(self._transactions_per_epoch, self._batch_size):
                    steps += 1
                    loss += self._model.train_step(batch)
                    t.set_postfix({'loss': f'{loss.numpy() / steps:.5f}'})
                    t.update()

            self.evaluate(it, loss.numpy()/(it + 1))

    def get_recommendations(self, k: int = 100):
        predictions_top_k_test = {}
        predictions_top_k_val = {}
        for index, offset in enumerate(range(0, self._num_users, self._batch_size)):
            offset_stop = min(offset + self._batch_size, self._num_users)
            predictions = self._model.predict_batch(offset, offset_stop)
            recs_val, recs_test = self.process_protocol(k, predictions, offset, offset_stop)
            predictions_top_k_val.update(recs_val)
            predictions_top_k_test.update(recs_test)
        return predictions_top_k_val, predictions_top_k_test
