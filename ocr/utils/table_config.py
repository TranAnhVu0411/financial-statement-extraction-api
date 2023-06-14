structure_class_names = [
    'table column', 'table column-header', 'table projected row header', 'table row', 'table spanning cell'
]
structure_class_map = {k: v for v, k in enumerate(structure_class_names)}
structure_class_thresholds = {
    "table column": 0,
    "table column header": 0,
    "table projected row header": 0,
    "table row": 0,
    "table spanning cell": 0,
}