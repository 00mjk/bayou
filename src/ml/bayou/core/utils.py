import argparse
import re
import json
from itertools import chain
import tensorflow as tf

CONFIG_GENERAL = ['latent_size', 'batch_size', 'num_epochs',
                  'learning_rate', 'print_step', 'alpha']
CONFIG_ENCODER = ['name', 'units', 'tile']
CONFIG_DECODER = ['units', 'max_ast_depth']
CONFIG_DECODER_INFER = ['chars', 'vocab', 'vocab_size']

C0 = 'CLASS0'
UNK = '_UNK_'
CHILD_EDGE = 'V'
SIBLING_EDGE = 'H'


def length(tensor):
    elems = tf.sign(tf.reduce_max(tensor, axis=2))
    return tf.reduce_sum(elems, axis=1)


# split s based on camel case and lower everything (uses '#' for split)
def split_camel(s):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1#\2', s)  # UC followed by LC
    s1 = re.sub('([a-z0-9])([A-Z])', r'\1#\2', s1)  # LC followed by UC
    split = s1.split('#')
    return [s.lower() for s in split]


# Do not move these imports to the top, it will introduce a cyclic dependency
import bayou.core.evidence


# convert JSON to config
def read_config(js, save_dir, infer=False):
    config = argparse.Namespace()

    for attr in CONFIG_GENERAL:
        config.__setattr__(attr, js[attr])
    
    config.evidence = bayou.core.evidence.Evidence.read_config(js['evidence'], save_dir)
    config.decoder = argparse.Namespace()
    for attr in CONFIG_DECODER:
        config.decoder.__setattr__(attr, js['decoder'][attr])
    if infer:
        for attr in CONFIG_DECODER_INFER:
            config.decoder.__setattr__(attr, js['decoder'][attr])

    return config


# convert config to JSON
def dump_config(config):
    js = {}

    for attr in CONFIG_GENERAL:
        js[attr] = config.__getattribute__(attr)

    js['evidence'] = [ev.dump_config() for ev in config.evidence]
    js['decoder'] = {attr: config.decoder.__getattribute__(attr) for attr in
                     CONFIG_DECODER + CONFIG_DECODER_INFER}

    return js


HELP = """Use this to extract evidences from a raw data file with sequences generated by driver.
You can also filter programs based on number and length of sequences."""


def extract_evidence(clargs):
    with open(clargs.input_file[0]) as f:
        js = json.load(f)
    programs = []
    for program in js['programs']:
        sequences = program['sequences']
        if len(sequences) > clargs.max_seqs or \
                any([len(sequence['calls']) > clargs.max_seq_length for sequence in sequences]):
            continue

        calls = set(chain.from_iterable([sequence['calls'] for sequence in sequences]))

        keywords = [bayou.core.evidence.Keywords.from_call(call) for call in calls]
        types = [bayou.core.evidence.Types.from_call(call) for call in calls]
        context = [bayou.core.evidence.Context.from_call(call) for call in calls]

        program['keywords'] = list(set(chain.from_iterable(keywords)))
        program['types'] = list(set(chain.from_iterable(types)))
        program['context'] = list(set(chain.from_iterable(context)))

        programs.append(program)

    with open(clargs.output_file[0], 'w') as f:
        json.dump({'programs': programs}, fp=f, indent=2)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description=HELP)
    parser.add_argument('input_file', type=str, nargs=1,
                        help='input data file')
    parser.add_argument('output_file', type=str, nargs=1,
                        help='output data file')
    parser.add_argument('--max_seqs', type=int, default=9999,
                        help='maximum number of sequences in a program')
    parser.add_argument('--max_seq_length', type=int, default=9999,
                        help='maximum length of each sequence in a program')
    clargs = parser.parse_args()
    extract_evidence(clargs)
