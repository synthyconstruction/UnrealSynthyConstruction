from .builder import DATASETS
from .custom import CustomDataset


@DATASETS.register_module()
class SynthCon(CustomDataset):
    """Synthy Construction dataset"""

    CLASSES = (
        "background",
        "fixture-sign",
        "fixture-alarm-fire",
        "fixture-alarm-smoke",
        "fixture-fan",
        "fixture-light",
        "beam-concrete",
        "beam-steel",
        "ceiling-compound",
        "ceiling-framing-wood",
        "ceiling-gypsumboard",
        "ceiling-plastered",
        "ceiling-concrete",
        "ceiling-soffit",
        "ceiling-skylight",
        "column-concrete",
        "column-steel",
        "curtainwall-concrete",
        "curtainwall-glass",
        "curtainwall-metal",
        "curtainwall-mullion",
        "curtainwall-panel",
        "curtainwall-panel",
        "drywall-framing:wood",
        "drywall-framing:metal",
        "drywall-insulation",
        "drywall-gypsumboard",
        "drywall-plastered",
        "duct-diffuser",
        "duct-insulated",
        "duct-uninsulated",
        "duct-vent",
        "duct-hanger",
        "electrical-box",
        "electrical-cabletray",
        "electrical-conduit",
        "electrical-coverplate",
        "electrical-junctionbox",
        "electrical-motor",
        "floor",
        "floor-concrete",
        "floor-formwork",
        "floor-metaldeck",
        "floor-tile",
        "floor-rebar",
        "foundation-pile",
        "foundation-slab",
        "framing-plate",
        "framing-truss-metal",
        "framing-joist-metal",
        "guardrails",
        "railing",
        "rebar",
        "pipe-hangers",
        "pipe-hangers",
        "pipe-insulated",
        "pipe-uninsulated",
        "pipe-sprinkler",
        "pipe-fitting",
        "pipe-valve",
        "pipe-valve",
        "roadway-asphalt",
        "roadway-paint",
        "stairs",
        "stairs-concrete",
        "stairs-escalator",
        "wall",
        "wall-brick",
        "wall-cmu",
        "wall-concrete",
        "windows",
        "furniture-chair",
        "furniture-fireextinguisher",
        "furniture-table",
        "furniture-countertop",
        "furniture-cabinet",
        "furniture-cabinet",
        "door",
        "mechanical-equipment",
        "mechanical-pump",
        "mechanical-tank",
        "plumbing-bathtub",
        "plumbing-urinal",
        "plumbing-toilet",
        "plumbing-toiletpartition-panel",
        "plumbing-waterheater",
        "plumbing-stove",
        "plumbing-showerhead",
        "plumbing-sink",
        "vendingmachine",
        "firehydrant",
        "firecabinet")

    PALETTE = [[0, 0, 0], #background
                [255, 31, 0], #fixture-sign
                [194,45,72], #fixture-alarm-fire
                [156,75,124], #fixture-alarm-smoke
                [255, 7, 71], #fixture-fan
                [7, 255, 224], #fixture-light
                [180, 120, 120], #beam-concrete
                [6, 230, 230], #beam-steel
                [255, 71, 0], #ceiling-compound
                [4, 200, 3], #ceiling-framing-wood
                [120, 120, 80], #ceiling-gypsumboard
                [56,65,222], #ceiling-plastered
                [40, 207, 100], #ceiling-concrete
                [255, 224, 0], #ceiling-soffit
                [0, 255, 245], #ceiling-skylight
                [140, 140, 140], #column-concrete
                [204, 5, 255], #column-steel
                [230, 230, 230], #curtainwall-concrete
                [4, 250, 7], #curtainwall-glass
                [224, 5, 255], #curtainwall-metal
                [235, 255, 7], #curtainwall-mullion
                [150, 5, 61], #curtainwall-panel
                [120, 120, 70], #curtainwall-panel
                [255, 6, 82], #drywall-framing-wood
                [143, 255, 140], #drywall-framing-metal
                [204, 255, 4], #drywall-insulation
                [255, 51, 7], #drywall-gypsumboard
                [204, 70, 3], #drywall-plastered
                [235, 12, 255], #duct-diffuser
                [160, 150, 20], #duct-insulated
                [0, 102, 200], #duct-uninsulated
                [0, 255, 20], #duct-vent
                [0, 211, 255], #duct-hanger
                [61, 230, 250], #electrical-box
                [0, 163, 255], #electrical-cabletray
                [255, 6, 51], #electrical-conduit
                [11, 102, 255], #electrical-coverplate
                [140, 140, 140], #electrical-junctionbox
                [250, 10, 15], #electrical-motor
                [255, 9, 224], #floor
                [9, 7, 230], #floor-concrete
                [11, 200, 200], #floor-formwork
                [220, 220, 220], #floor-metaldeck
                [31, 0, 255], #floor-tile
                [255, 163, 0], #floor-rebar
                [255, 9, 92], #foundation-pile
                [20, 255, 0], #foundation-slab
                [207, 10, 20], #framing-plate
                [10, 148, 30], #framing-truss-metal
                [8, 255, 214], #framing-joist-metal
                [112, 9, 255], #guardrails
                [10, 255, 71], #railing
                [255, 41, 10], #rebar
                [255, 82, 0], #pipe-hangers
                [56,26,143], #pipe-hangers
                [31, 255, 0], #pipe-insulated
                [255, 184, 6], #pipe-uninsulated
                [255, 0, 0], #pipe-sprinkler
                [195, 183, 48], #pipe-fitting
                [93, 43, 184], #pipe-valve
                [222,111,43], #pipe-valve
                [7, 255, 255], #roadway-asphalt
                [224, 255, 8], #roadway-paint
                [255, 61, 6], #stairs
                [255, 194, 7], #stairs-concrete
                [237, 207, 0], #stairs-escalator
                [213,43,222], #wall
                [153, 255, 0], #wall-brick
                [0, 0, 255], #wall-cmu
                [255, 5, 153], #wall-concrete
                [6, 51, 255], #windows
                [43, 59, 173], #furniture-chair
                [59, 10, 255], #furniture-fireextinguisher
                [45, 32, 101], #furniture-table
                [0, 235, 255], #furniture-countertop
                [80, 50, 50], #furniture-cabinet
                [80, 50, 50], #furniture-cabinet
                [8, 255, 51], #door
                [72, 63, 157], #mechanical-equipment
                [255, 28, 199], #mechanical-pump
                [56, 253, 193], #mechanical-tank
                [120, 120, 120], #plumbing-bathtub
                [0, 255, 112], #plumbing-urinal
                [255, 122, 8], #plumbing-toilet
                [0, 61, 255], #plumbing-toiletpartition-panel
                [255, 8, 41], #plumbing-waterheater
                [111,222,43], #plumbing-stove
                [67,67,45], #plumbing-showerhead
                [102, 8, 255], #plumbing-sink
                [0, 255, 133], #vendingmachine
                [0, 173, 255], #firehydrant
                [30, 237, 10] #firecabinet
                ]

    def __init__(self, **kwargs):
        super(SynthCon, self).__init__(
            img_suffix='.jpg',
            seg_map_suffix='.png',
            reduce_zero_label=True,
            **kwargs)
