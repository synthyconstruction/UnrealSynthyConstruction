Experiments are created using [MMSegmentation](https://github.com/open-mmlab/mmsegmentation)

We provide here the different training configuration files for training and testing a Swin Large model, together with the data.py files for the mmseg package.
We suggest to simply build the MMSegmentation repository, and add the files provided in this folder where indicated (same folder structure).
NOTE that 

All code modifications/additions are denoted by a comment "#NOTE: ADDED CODE"


For training the encoder-decoder, we set the learning rate at 0.0006.
For training the decoder only, we set the learning rate at 0.0003.
You may modify the learning rate directly in the configuration files.

