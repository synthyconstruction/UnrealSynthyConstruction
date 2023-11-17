from .builder import DATASETS
from .custom import CustomDataset


@DATASETS.register_module()
class ThreeDFacilities(CustomDataset):
    """3DFacilities dataset.
    """

    CLASSES = (
        'unlabelled', 'furniture', 'door', 'wall', 'floor',
        'window', 'ceiling', 'column', 'beam', 'stairs',
        'railing', 'light_fixture', 'elevator', 'plumbing', 'duct',
        'diffuser', 'sprinkler', 'cable_tray', 'conduit', 'background'
    )

    PALETTE = [
        [0, 0, 0], [0, 51, 0], [0, 51, 102], [255, 153, 255],
        [102, 0, 102], [0, 0, 102], [51, 51, 0], [153, 51, 102],
        [102, 0, 204], [255, 153, 0], [0, 102, 102], [255, 255, 204],
        [51, 102, 255], [51, 204, 255], [0, 255, 0], [204, 0, 255],
        [255, 0, 0], [255, 255, 0], [255, 153, 102], [128, 128, 128]
    ]


    def __init__(self, **kwargs):
        super(ThreeDFacilities, self).__init__(
            img_suffix='.jpg',
            seg_map_suffix='.png',
            reduce_zero_label=True,
            **kwargs)
