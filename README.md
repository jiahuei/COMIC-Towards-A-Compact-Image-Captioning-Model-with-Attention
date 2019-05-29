COMIC: Towards a Compact Image Captioning Model with Attention
===================

This is the code repo for the TMM 2019 paper "COMIC: Towards a Compact Image Captioning Model with Attention".

**Please NOTE that this code is NOT yet ready.**

```
@article{tan2019comic,
  title={COMIC: Towards A Compact Image Captioning Model with Attention},
  author={Tan, Jia Huei and Chan, Chee Seng and Chuah, Joon Huang},
  journal={IEEE Transactions on Multimedia},
  year={2019},
  publisher={IEEE}
}
```

## Requirements
- tensorflow r1.9.0
- python 2.7
- java 1.8.0
- tqdm >= 4.24.0
- requests >= 2.18.4
- Pillow >= 3.1.2


## Running the code
Assuming you are in the `src` folder:

1. Run `setup.sh`. This will download the required Stanford models 
and run all the dataset pre-processing scripts.

1. Run the training script `python train.py`.

1. Run the inference and evaluation script 
`python infer.py --infer_checkpoints_dir mscoco/logdir`.

Examples are given in `example.sh`.


## Avoid redownloading datasets
Redownloading can be avoided by:
- Editing `setup.sh`
- Providing the path to the directory containing the dataset files

```bash
python coco_prepro.py --dataset_dir /path/to/coco/dataset
python insta_prepro.py --dataset_dir /path/to/insta/dataset
```

In the same way, both `train.py` and `infer.py` accept alternative dataset paths.

```bash
python train.py --dataset_dir /path/to/coco/dataset
python infer.py --dataset_dir /path/to/insta/dataset
```

This code assumes the following dataset directory structures:

### MS-COCO
```
{coco-folder}
+-- captions
|   +-- {folder and files generated by coco_prepro.py}
+-- test2014
|   +-- {image files}
+-- train2014
|   +-- {image files}
+-- val2014
    +-- {image files}
```

### InstaPIC-1.1M
```
{insta-folder}
+-- captions
|   +-- {folder and files generated by insta_prepro.py}
+-- images
|   +-- {image files}
+-- json
    +-- insta-caption-test1.json
    +-- insta-caption-train.json
```


## Differences compared to the paper
- Added attention map dropout
- RNN init method changed to `x_{t=-1} = W_I * I_{embed}`
from `h_{t=-1} = W_I tanh (LN (I_{embed} ))`
- Changed training scheme (learning rate, ADAM epsilon)
- Possible RNN variational dropout
- Possible context layer
- [SCST](https://arxiv.org/abs/1612.00563) (to be added)


## Main arguments

### train.py
- `token_type`: Language model. Choices are `radix`, `word`, `char`.
- `radix_base`: Base value for Radix models.
- `cnn_name`: CNN model name.
- `cnn_input_size`: CNN input size.
- `cnn_fm_attention`: End point name of feature map for attention.
- `cnn_fm_projection`: Feature map projection method. Choices are `none`, `independent`, `tied`.
    
- `rnn_name`: Type of RNN. Choices are `LSTM`, `LN_LSTM`, `GRU`.
- `rnn_size`: Number of RNN units.
- `rnn_word_size`: Size of word embedding.
- `rnn_init_method`: RNN init method. Choices are `project_hidden`, `first_input`.
- `rnn_recurr_dropout`: If True, enable variational recurrent dropout.
    
- `attn_num_heads`: Number of attention heads.
- `attn_context_layer`: If True, add linear projection after multi-head attention.
- `attn_alignment_method`: Alignment / composition method. Choices are `add`, `dot`.
- `attn_probability_fn`: Attention map probability function. Choices are `softmax`, `sigmoid`.

### infer.py
- `infer_set`: The split to perform inference on. Choices are `test`, `valid`, `coco_test`, `coco_valid`.
`coco_test` and `coco_valid` are for inferencing on the whole 
`test2014` and `val2014` sets respectively. 
These are used for MS-COCO online server evaluation.
- `infer_checkpoints_dir`: Directory containing the checkpoint files.
- `infer_checkpoints`: Checkpoint numbers to be evaluated. Comma-separated.
- `annotations_file`: Annotations / reference file for calculating scores.

- `infer_beam_size`: Beam size of beam search. Pass 1 for greedy search.
- `infer_length_penalty_weight`: Length penalty weight used in beam search.
- `infer_max_length`: Maximum caption length allowed during inference.
- `batch_size_infer`: Inference batch size for parallelism.


## Microsoft COCO Caption Evaluation
This code uses the standard `coco-caption` code with *SPICE* metric.

[Link to repo](https://github.com/tylin/coco-caption/tree/3a9afb2682141a03e1cdc02b0df6770d2c884f6f)



