#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 28 17:53:58 2017

@author: jiahuei
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os, sys, argparse
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))
import infer_fn as infer
import configuration as conf
import ops
from natural_sort import natural_keys as nat_key
pjoin = os.path.join
_DEBUG = False


def _dprint(string):
    return ops.dprint(string, _DEBUG)


def create_parser():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='lol')
    
    parser.add_argument(
        '--infer_set', type=str,
        choices=['test', 'valid', 'coco_test', 'coco_valid'],
        help='The split to perform inference on.')
    parser.add_argument(
        '--dataset_dir', type=str, required=True,
        help='Dataset directory.')
    parser.add_argument(
        '--run_inference', type=bool, default=True,
        help='Whether to perform inference.')
    parser.add_argument(
        '--get_metric_score', type=bool, default=True,
        help='Whether to perform metric score calculations.')
    parser.add_argument(
        '--save_attention_maps', type=bool, default=True,
        help='Whether to save attention maps to disk as pickle file.')
    parser.add_argument(
        '--gpu', type=str, required=True,
        help='The gpu number.')
    
    parser.add_argument(
        '--infer_beam_size', type=int, default=3,
        help='The beam size.')
    parser.add_argument(
        '--infer_length_penalty_weight', type=float, default=0.0,
        help='The length penalty weight used in beam search.')
    parser.add_argument(
        '--infer_max_length', type=int, default=30,
        help='The maximum caption length allowed during inference.')
    
    parser.add_argument(
        '--batch_size_infer', type=int, required=True,
        help='The batch size.')
    parser.add_argument(
        '--infer_checkpoints_dir', type=str, required=True,
        help='The directory containing the checkpoint files.')
    parser.add_argument(
        '--infer_checkpoints', type=str, required=True,
        help='The checkpoint numbers to be evaluated. Comma-separated.')
    parser.add_argument(
        '--annotations_file', type=str, default='annotations/captions_val2014.json',
        help='The annotations file. Example: `annotations/captions_val2014.json`')
    
    return parser


if __name__ == '__main__':
    ckpt_prefix = 'model_compact-'
    tboard_fname = 'run_{}-tag-{}_perplexity.json'

    parser = create_parser()
    args = parser.parse_args()
    os.environ['CUDA_DEVICE_ORDER'] = 'PCI_BUS_ID'
    os.environ['CUDA_VISIBLE_DEVICES'] = args.gpu
    if args.infer_checkpoints == 'all':
        files = sorted(os.listdir(args.infer_checkpoints_dir), key=nat_key)
        files = [f for f in files if ckpt_prefix in f]
        files = [f.replace('.index', '') for f in files if '.index' in f]
        files = [f.replace(ckpt_prefix, '') for f in files]
        if len(files) > 20:
            files = files[-12:]
        args.infer_checkpoints = files
    else:
        args.infer_checkpoints = args.infer_checkpoints.split(',')
        if len(args.infer_checkpoints) < 1:
            raise ValueError('`infer_checkpoints` must be either `all` or '
                             'a list of comma-separated checkpoint numbers.')
    overwrite = True
    per_process_gpu_memory_fraction = 0.88
    
    ###
    
    c = conf.load_config(pjoin(args.infer_checkpoints_dir, 'config.pkl'))
    c.__dict__.update(args.__dict__)
    c.per_process_gpu_memory_fraction = per_process_gpu_memory_fraction
    ckpt_dir = c.infer_checkpoints_dir
    
    save_name = 'beam_{}_lpen_{}'.format(
                        c.infer_beam_size, c.infer_length_penalty_weight)
    if c.infer_set == 'test':
        save_name = 'infer_test_' + save_name
    elif c.infer_set == 'valid':
        save_name = 'infer_valid_' + save_name
    elif c.infer_set == 'coco_test':
        save_name = 'infer_cocoTest_' + save_name
    elif c.infer_set == 'coco_valid':
        save_name = 'infer_cocoValid_' + save_name
    
    c.infer_save_path = pjoin(ckpt_dir, save_name)
    
    ###############################################################################
    
    if os.path.exists(c.infer_save_path): 
        print('\nINFO: `eval_log_path` already exists.')
    else: 
        print('\nINFO: `eval_log_path` will be created.')
        os.mkdir(c.infer_save_path)
    
    # Loop through the checkpoint files
    scores_combined = {}
    for ckpt_num in c.infer_checkpoints:
        curr_ckpt_path = pjoin(ckpt_dir, ckpt_prefix + ckpt_num)
        infer.evaluate_model(
                    config=c,
                    curr_ckpt_path=curr_ckpt_path,
                    scores_combined=scores_combined)
        print('\n')

    
