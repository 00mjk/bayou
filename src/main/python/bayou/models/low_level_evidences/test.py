# Copyright 2017 Rice University
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import print_function
import numpy as np
import tensorflow as tf

import argparse
import os
import sys
import simplejson as json
import textwrap

import time

from bayou.models.low_level_evidences.infer import BayesianPredictor
from bayou.models.low_level_evidences.utils import read_config
from bayou.models.low_level_evidences.data_reader import Reader


evidence = {
    "apicalls": [
        "add",
        "exists"
      ],
      "types": [
        "ArrayList",
      ]
    }



def test(clargs):
    clargs.continue_from = True

    with open(os.path.join(clargs.save, 'config.json')) as f:
        config = read_config(json.load(f), chars_vocab=True)

    reader = Reader(clargs, config, infer=True)

	# Placeholders for tf data

    nodes_placeholder = tf.placeholder(reader.nodes.dtype, reader.nodes.shape)
    parents_placeholder = tf.placeholder(reader.parents.dtype, reader.nodes.shape)
    edges_placeholder = tf.placeholder(reader.edges.dtype, reader.edges.shape)
    targets_placeholder = tf.placeholder(reader.targets.dtype, reader.targets.shape)
    evidence_placeholder = [tf.placeholder(input.dtype, input.shape) for input in reader.inputs]

    # reset batches

    feed_dict={fp: f for fp, f in zip(evidence_placeholder, reader.inputs)}
    feed_dict.update({nodes_placeholder: reader.nodes})
    feed_dict.update({parents_placeholder: reader.nodes})
    feed_dict.update({edges_placeholder: reader.edges})
    feed_dict.update({targets_placeholder: reader.targets})

    dataset = tf.data.Dataset.from_tensor_slices((nodes_placeholder, parents_placeholder, edges_placeholder, targets_placeholder, *evidence_placeholder))
    batched_dataset = dataset.batch(config.batch_size)
    iterator = batched_dataset.make_initializable_iterator()

    sess = tf.InteractiveSession()
    predictor = BayesianPredictor(clargs.save, sess, config, iterator) # goes to infer.BayesianPredictor
    # testing
    # sess.run(iterator.initializer, feed_dict=feed_dict)

    # allEvSigmas = predictor.get_ev_sigma()
    # print(allEvSigmas)

    path_head = predictor.beam_search(evidence)
    path = path_head.dfs()
    print(path)



    return path



#%%
if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--python_recursion_limit', type=int, default=10000,
                        help='set recursion limit for the Python interpreter')
    parser.add_argument('--save', type=str, required=True,
                        help='checkpoint model during training here')
    parser.add_argument('--evidence', type=str, default='all',
                        choices=['apicalls', 'types', 'keywords', 'all'],
                        help='use only this evidence for inference queries')
    parser.add_argument('--output_file', type=str, default=None,
                        help='output file to print probabilities')

    #clargs = parser.parse_args()
    clargs = parser.parse_args()

    sys.setrecursionlimit(clargs.python_recursion_limit)
    test(clargs)