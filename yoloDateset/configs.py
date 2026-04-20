"""
YOLO-OBB 数据集公共配置

在此统一管理类别列表，各脚本通过 from configs import CLASSES 引用
"""

# 完整的类别名称列表（顺序对应 class_id）
# CLASSES = [
#     "angelSteelBack",
#     "angelSteelFront",
#     "clamp",
#     "LConnection",
#     "TConnection",
#     "tiltedConnection",
#     "dimension",
#     "arrowhead",
# ]

CLASSES = [
    "angelSteelBack",
    "angelSteelFront",
    "clamp",
    "LConnection",
    "TConnection",
    "dimension",
    "angelSteelNumber",
    "clampNumber",
    "endMark"
]

