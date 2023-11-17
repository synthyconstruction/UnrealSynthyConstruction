# dataset settings
dataset_type = 'ThreeDFacilities'
data_root = '/your/path/here/before/images-gt/folder
img_norm_cfg = dict(
    mean=[108.150, 106.586, 104.614], std=[57.4877, 57.4082, 60.4956], to_rgb=True) 
crop_size = (224, 224)
train_pipeline = [
    dict(type='LoadImageFromFile'),
    dict(type='LoadAnnotations', reduce_zero_label=True),
    dict(type='Resize', img_scale=(224, 224), ratio_range=(0.5, 2.0)),
    dict(type='RandomCrop', crop_size=crop_size, cat_max_ratio=0.75),
    dict(type='RandomFlip', prob=0.5),
    dict(type='PhotoMetricDistortion'),
    dict(type='Normalize', **img_norm_cfg),
    dict(type='Pad', size=crop_size, pad_val=0, seg_pad_val=255),
    dict(type='DefaultFormatBundle'),
    dict(type='Collect', keys=['img', 'gt_semantic_seg']),
]
test_pipeline = [
    dict(type='LoadImageFromFile'),
    dict(
        type='MultiScaleFlipAug',
        img_scale=(224, 224),
        flip=False,
        transforms=[
            dict(type='Resize', keep_ratio=True),
            dict(type='RandomFlip'),
            dict(type='Normalize', **img_norm_cfg),
            dict(type='ImageToTensor', keys=['img']),
            dict(type='Collect', keys=['img']),
        ])
]
data = dict(
    samples_per_gpu=6,
    workers_per_gpu=6,
    train=dict(
        type=dataset_type,
        data_root=data_root,
        img_dir='/your/path/here/images/train',
        ann_dir='/your/path/here/ground_truth/train',
        pipeline=train_pipeline),
    val=dict(
        type=dataset_type,
        data_root=data_root,
        img_dir='/your/path/here/images/val',
        ann_dir='/your/path/here/ground_truth/val',
        pipeline=test_pipeline),
    test=dict(
        type=dataset_type,
        data_root=data_root,        
        img_dir='/your/path/here/images/test',
        ann_dir='/your/path/here/ground_truth/test',
        pipeline=test_pipeline))
