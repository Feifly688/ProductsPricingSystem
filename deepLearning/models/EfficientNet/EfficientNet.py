import copy
import json
import math
import os
import random
import time
from collections import OrderedDict
from datetime import datetime
from functools import partial
from typing import Optional, Callable

import torch
import torch.multiprocessing as mp
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import torchvision.datasets as datasets
import torchvision.transforms as transforms
from PIL import Image
from matplotlib import pyplot as plt
from sklearn.metrics import precision_score, recall_score, accuracy_score, f1_score
from timm.layers import DropPath
from timm.models.nextvit import _make_divisible
from torch import Tensor
from torch.utils.data import DataLoader
from tqdm import tqdm


def create_run_dir(base_dir="train"):
    """创建带有时间戳和序号的新训练目录"""
    timestamp = "train_" + datetime.now().strftime("%Y%m%d_%H%M")
    run_dir = os.path.join(base_dir, timestamp)

    # 自动处理重复运行
    counter = 2
    if os.path.exists(run_dir):
        run_dir = os.path.join(base_dir, f"{timestamp}_{counter}")
        counter += 1

    os.makedirs(run_dir, exist_ok=True)
    return run_dir


def format_memory(mb):
    """将内存转换为易读格式"""
    for unit in ['MB', 'GB']:
        if mb < 1024:
            return f"{mb:.1f}{unit}"
        mb /= 1024
    return f"{mb:.1f}TB"


def plot_metrics(history, save_path):
    """生成训练和验证指标图表"""
    plt.style.use('seaborn-v0_8')

    # 合并指标配置
    combined_metrics = [
        {
            'name': 'loss',
            'title': 'Training and Validation Loss',
            'ylabel': 'Loss Value',
            'train_key': 'train_loss',
            'val_key': 'val_loss',
            'colors': {'train': '#1f77b4', 'val': '#ff7f0e'},
            'formatter': None
        },
        {
            'name': 'accuracy',
            'title': 'Training and Validation Accuracy',
            'ylabel': 'Accuracy',
            'train_key': 'train_accuracy',
            'val_key': 'val_accuracy',
            'colors': {'train': '#2ca02c', 'val': '#d62728'},
            'formatter': plt.FuncFormatter(lambda x, _: f'{x:.0%}')
        }
    ]

    # 单独验证指标配置
    val_metrics = [
        {
            'name': 'precision',
            'title': 'Validation Precision',
            'ylabel': 'Precision',
            'key': 'val_precision',
            'color': '#ff7f0e',
            'formatter': plt.FuncFormatter(lambda x, _: f'{x:.0%}')
        },
        {
            'name': 'recall',
            'title': 'Validation Recall',
            'ylabel': 'Recall',
            'key': 'val_recall',
            'color': '#d62728',
            'formatter': plt.FuncFormatter(lambda x, _: f'{x:.0%}')
        },
        {
            'name': 'f1-score',
            'title': 'Validation F1-score',
            'ylabel': 'F1-score',
            'key': 'val_f1-score',
            'color': '#9467bd',
            'formatter': plt.FuncFormatter(lambda x, _: f'{x:.0%}')
        }
    ]

    epochs = list(range(1, len(history['train_loss']) + 1))
    num_epochs = len(epochs)

    # 绘制合并指标
    for config in combined_metrics:
        fig = plt.figure(figsize=(10, 6), dpi=150)
        ax = fig.add_subplot(111)

        # 绘制训练和验证曲线
        train_values = history[config['train_key']]
        val_values = history[config['val_key']]

        ax.plot(epochs, train_values,
                marker='o',
                markersize=6,
                linewidth=2.5,
                color=config['colors']['train'],
                alpha=0.8,
                label='Training',
                markeredgecolor='white',
                markeredgewidth=1)

        ax.plot(epochs, val_values,
                marker='o',
                markersize=6,
                linewidth=2.5,
                color=config['colors']['val'],
                alpha=0.8,
                label='Validation',
                markeredgecolor='white',
                markeredgewidth=1)

        ax.set_title(config['title'], fontsize=14, pad=15, fontweight='bold')
        ax.set_xlabel('Epoch', fontsize=12, labelpad=10)
        ax.set_ylabel(config['ylabel'], fontsize=12, labelpad=10)

        ax.set_xlim(0.5, num_epochs + 0.5)
        if config['name'] == 'loss':
            min_val = min(min(train_values), min(val_values))
            max_val = max(max(train_values), max(val_values))
            padding = (max_val - min_val) * 0.1
            ax.set_ylim(min_val - padding, max_val + padding)
        else:
            ax.set_ylim(-0.05, 1.05)

        if config['formatter']:
            ax.yaxis.set_major_formatter(config['formatter'])

        # 设置刻度
        if num_epochs <= 15:
            ax.set_xticks(epochs)
            rotation = 0 if num_epochs <= 10 else 45
        else:
            ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True, nbins=min(15, num_epochs)))
            rotation = 30

        ax.tick_params(axis='x', labelsize=10, rotation=rotation, grid_alpha=0.3)
        ax.tick_params(axis='y', labelsize=10, grid_alpha=0.3)

        ax.grid(True, linestyle='--', alpha=0.4)
        ax.legend(loc='best')

        # 标注最终值
        last_train = train_values[-1]
        last_val = val_values[-1]
        ax.annotate(f'Train: {last_train:.4f}',
                    xy=(epochs[-1], last_train),
                    xytext=(epochs[-1] - num_epochs * 0.15, last_train * 1.05),
                    fontsize=10,
                    arrowprops=dict(arrowstyle="->", color=config['colors']['train'], linewidth=1.5, alpha=0.7))
        ax.annotate(f'Val: {last_val:.4f}',
                    xy=(epochs[-1], last_val),
                    xytext=(epochs[-1] - num_epochs * 0.15, last_val * 0.85),
                    fontsize=10,
                    arrowprops=dict(arrowstyle="->", color=config['colors']['val'], linewidth=1.5, alpha=0.7))

        plt.tight_layout(pad=2.5)
        plt.savefig(os.path.join(save_path, f"{config['name']}_curve.png"), bbox_inches='tight', facecolor='white')
        plt.close(fig)

    # 绘制单独验证指标
    for config in val_metrics:
        fig = plt.figure(figsize=(10, 6), dpi=150)
        ax = fig.add_subplot(111)

        values = history[config['key']]

        ax.plot(epochs, values,
                marker='o',
                markersize=6,
                linewidth=2.5,
                color=config['color'],
                alpha=0.8,
                markeredgecolor='white',
                markeredgewidth=1)

        ax.set_title(config['title'], fontsize=14, pad=15, fontweight='bold')
        ax.set_xlabel('Epoch', fontsize=12, labelpad=10)
        ax.set_ylabel(config['ylabel'], fontsize=12, labelpad=10)

        ax.set_xlim(0.5, num_epochs + 0.5)
        ax.set_ylim(-0.05, 1.05)

        if config['formatter']:
            ax.yaxis.set_major_formatter(config['formatter'])

        # 设置刻度
        if num_epochs <= 15:
            ax.set_xticks(epochs)
            rotation = 0 if num_epochs <= 10 else 45
        else:
            ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True, nbins=min(15, num_epochs)))
            rotation = 30

        ax.tick_params(axis='x', labelsize=10, rotation=rotation, grid_alpha=0.3)
        ax.tick_params(axis='y', labelsize=10, grid_alpha=0.3)

        ax.grid(True, linestyle='--', alpha=0.4)

        # 标注最终值
        last_val = values[-1]
        ax.annotate(f'{last_val:.4f}',
                    xy=(epochs[-1], last_val),
                    xytext=(epochs[-1] - num_epochs * 0.15, last_val * 1.05),
                    fontsize=10,
                    arrowprops=dict(arrowstyle="->", color=config['color'], linewidth=1.5, alpha=0.7))

        plt.tight_layout(pad=2.5)
        plt.savefig(os.path.join(save_path, f"{config['name']}_curve.png"), bbox_inches='tight', facecolor='white')
        plt.close(fig)

class ConvBNActivation(nn.Sequential):  # 卷积+BN+激活函数
    def __init__(self,
                 in_planes: int,  # 输入特征矩阵channel
                 out_planes: int,  # 输出特征矩阵channel
                 kernel_size: int = 3,  # 卷积核大小
                 stride: int = 1,  # 步距
                 groups: int = 1,  # g=1使用dw卷积,g=2使用普通卷积
                 norm_layer: Optional[Callable[..., nn.Module]] = None,  # BN结构
                 activation_layer: Optional[Callable[..., nn.Module]] = None):  # BN结构后的激活函数
        padding = (kernel_size - 1) // 2  # 根据kernel_size计算padding
        if norm_layer is None:  # 如果没有传入norm_layer则使用BN
            norm_layer = nn.BatchNorm2d
        if activation_layer is None:  # 如果没有传入activation_layer则使用SiLU激活函数(和swish激活函数一样)
            activation_layer = nn.SiLU  # alias Swish  (torch>=1.7)
        # 传入所需要构建的一系列层结构
        super(ConvBNActivation, self).__init__(nn.Conv2d(in_channels=in_planes,  # 传入卷积层所需要参数
                                                         out_channels=out_planes,
                                                         kernel_size=kernel_size,
                                                         stride=stride,
                                                         padding=padding,
                                                         groups=groups,
                                                         bias=False),  # 使用BN结构则不使用bias
                                               norm_layer(out_planes),  # BN结构，传入的参数为上一层的输出channel
                                               activation_layer())  # 不传入参数默认使用SiLU激活函数


class SqueezeExcitation(nn.Module):  # SE模块
    def __init__(self,
                 input_c: int,  # block input channel   对应MBConv输入特征矩阵的channel
                 expand_c: int,  # block expand channel  对应第一个1x1卷积层升维后的channel(dw卷积不改变channel)
                 squeeze_factor: int = 4):  # 对应第一个全连接层的节点个数，论文中默认等于4
        super(SqueezeExcitation, self).__init__()
        squeeze_c = input_c // squeeze_factor  # squeeze_c的计算公式
        self.fc1 = nn.Conv2d(expand_c, squeeze_c, 1)  # 构建第一个全连接层
        self.ac1 = nn.SiLU()  # alias Swish
        self.fc2 = nn.Conv2d(squeeze_c, expand_c, 1)  # 构建第二个全连接层
        self.ac2 = nn.Sigmoid()

    def forward(self, x: Tensor) -> Tensor:  # 前向传播过程
        scale = F.adaptive_avg_pool2d(x, output_size=(1, 1))  # 对输入进行平均池化
        scale = self.fc1(scale)
        scale = self.ac1(scale)
        scale = self.fc2(scale)
        scale = self.ac2(scale)
        return scale * x


class InvertedResidualConfig:  # 残差结构配置
    # kernel_size, in_channel, out_channel, exp_ratio, strides, use_SE, drop_connect_rate
    def __init__(self,
                 kernel: int,  # 3 or 5
                 input_c: int,
                 out_c: int,
                 expanded_ratio: int,  # 1 or 6
                 stride: int,  # 1 or 2
                 use_se: bool,  # True
                 drop_rate: float,
                 index: str,  # 1a, 2a, 2b, ...
                 width_coefficient: float):
        self.input_c = self.adjust_channels(input_c, width_coefficient)
        self.kernel = kernel
        self.expanded_c = self.input_c * expanded_ratio
        self.out_c = self.adjust_channels(out_c, width_coefficient)
        self.use_se = use_se
        self.stride = stride
        self.drop_rate = drop_rate
        self.index = index

    @staticmethod
    def adjust_channels(channels: int, width_coefficient: float):
        return _make_divisible(channels * width_coefficient, 8)


class InvertedResidual(nn.Module):  # MBConv模块
    def __init__(self,
                 cnf: InvertedResidualConfig,  # 残差结构配置
                 norm_layer: Callable[..., nn.Module]):  # BN结构
        super(InvertedResidual, self).__init__()

        if cnf.stride not in [1, 2]:  # 判断dw卷积的步长是否在1和2中
            raise ValueError("illegal stride value.")

        self.use_res_connect = (cnf.stride == 1 and cnf.input_c == cnf.out_c)  # 根据步长判断是否使用shortcut连接

        layers = OrderedDict()  # 定义有序字典来搭建MBConv结构
        activation_layer = nn.SiLU  # alias Swish

        # expand               搭建第一个1x1卷积层   注意当n=1时不需要第一个1x1卷积层
        if cnf.expanded_c != cnf.input_c:  # 当expanded_c = input_c时n=1，跳过
            layers.update({"expand_conv": ConvBNActivation(cnf.input_c,  # 调用ConvBNActivation并传入相关参数
                                                           cnf.expanded_c,
                                                           kernel_size=1,
                                                           norm_layer=norm_layer,
                                                           activation_layer=activation_layer)})

        # depthwise       搭建DW卷积
        layers.update({"dwconv": ConvBNActivation(cnf.expanded_c,  # dw卷积输入和输出特征矩阵的channel不发生变化
                                                  cnf.expanded_c,
                                                  kernel_size=cnf.kernel,
                                                  stride=cnf.stride,
                                                  groups=cnf.expanded_c,
                                                  norm_layer=norm_layer,
                                                  activation_layer=activation_layer)})

        if cnf.use_se:  # 判断是否使用SE模块
            layers.update({"se": SqueezeExcitation(cnf.input_c,  # 这里注意，输入特征矩阵为输入MBConv模块的特征矩阵的channel
                                                   cnf.expanded_c)})

        # project     搭建最后的1x1卷积层
        layers.update({"project_conv": ConvBNActivation(cnf.expanded_c,
                                                        cnf.out_c,
                                                        kernel_size=1,
                                                        norm_layer=norm_layer,
                                                        activation_layer=nn.Identity)})  # 在最后1x1卷积层后没有激活函数，因此不做任何处理，传入nn.Identity

        self.block = nn.Sequential(layers)
        self.out_channels = cnf.out_c
        self.is_strided = cnf.stride > 1

        # 只有在使用shortcut连接时才使用dropout层
        if self.use_res_connect and cnf.drop_rate > 0:
            self.dropout = DropPath(cnf.drop_rate)
        else:
            self.dropout = nn.Identity()

    def forward(self, x: Tensor) -> Tensor:
        result = self.block(x)
        result = self.dropout(result)
        if self.use_res_connect:
            result += x

        return result


class EfficientNet(nn.Module):  # 实现EfficientNet
    def __init__(self,
                 width_coefficient: float,  # 网络宽度的倍率因子
                 depth_coefficient: float,  # 网络深度的倍率因子
                 num_classes: int = 200,  # 分类的类别个数
                 dropout_rate: float = 0.2,  # MB模块中的dropout的随机失活比例
                 drop_connect_rate: float = 0.2,  # 最后一个全连接层的dropout的随机失活比例
                 block: Optional[Callable[..., nn.Module]] = None,  # MBConv模块
                 norm_layer: Optional[Callable[..., nn.Module]] = None  # BN结构
                 ):
        super(EfficientNet, self).__init__()

        # kernel_size, in_channel, out_channel, exp_ratio, strides, use_SE, drop_connect_rate, repeats
        default_cnf = [[3, 32, 16, 1, 1, True, drop_connect_rate, 1],  # 以B0构建的默认配置表,stage2~stage8
                       [3, 16, 24, 6, 2, True, drop_connect_rate, 2],
                       [5, 24, 40, 6, 2, True, drop_connect_rate, 2],
                       [3, 40, 80, 6, 2, True, drop_connect_rate, 3],
                       [5, 80, 112, 6, 1, True, drop_connect_rate, 3],
                       [5, 112, 192, 6, 2, True, drop_connect_rate, 4],
                       [3, 192, 320, 6, 1, True, drop_connect_rate, 1]]

        def round_repeats(repeats):  # depth_coefficient * repeats向上取整
            """Round number of repeats based on depth multiplier."""
            return int(math.ceil(depth_coefficient * repeats))

        if block is None:  # 如果block为空就默认等于MBConv
            block = InvertedResidual

        if norm_layer is None:  # 如果norm_layer为空就默认为BN结构
            norm_layer = partial(nn.BatchNorm2d, eps=1e-3, momentum=0.1)

        adjust_channels = partial(InvertedResidualConfig.adjust_channels,  # 对传入的channel乘倍率因子再调整到离它最近的8的整数倍
                                  width_coefficient=width_coefficient)

        # build inverted_residual_setting
        bneck_conf = partial(InvertedResidualConfig,
                             width_coefficient=width_coefficient)

        b = 0  # 统计搭建MBblock的次数
        num_blocks = float(sum(round_repeats(i[-1]) for i in default_cnf))  # 遍历default_cnf列表获取重复次数
        inverted_residual_setting = []  # 定义空列表存储MBConv的配置文件
        for stage, args in enumerate(default_cnf):  # 遍历default_cnf列表
            cnf = copy.copy(args)  # 后面会对数据进行修改，为了不影响原数据
            for i in range(round_repeats(cnf.pop(-1))):  # 遍历每个stage中的MBConv模块
                if i > 0:
                    # strides equal 1 except first cnf
                    cnf[-3] = 1  # strides
                    cnf[1] = cnf[2]  # input_channel equal output_channel

                cnf[-1] = args[-2] * b / num_blocks  # update dropout ratio
                index = str(stage + 1) + chr(i + 97)  # 1a, 2a, 2b, ...
                inverted_residual_setting.append(bneck_conf(*cnf, index))
                b += 1

        # create layers
        layers = OrderedDict()

        # first conv
        layers.update({"stem_conv": ConvBNActivation(in_planes=3,
                                                     out_planes=adjust_channels(32),
                                                     kernel_size=3,
                                                     stride=2,
                                                     norm_layer=norm_layer)})

        # building inverted residual blocks
        for cnf in inverted_residual_setting:
            layers.update({cnf.index: block(cnf, norm_layer)})

        # build top
        last_conv_input_c = inverted_residual_setting[-1].out_c
        last_conv_output_c = adjust_channels(1280)
        layers.update({"top": ConvBNActivation(in_planes=last_conv_input_c,
                                               out_planes=last_conv_output_c,
                                               kernel_size=1,
                                               norm_layer=norm_layer)})

        self.features = nn.Sequential(layers)
        self.avgpool = nn.AdaptiveAvgPool2d(1)

        classifier = []
        if dropout_rate > 0:
            classifier.append(nn.Dropout(p=dropout_rate, inplace=True))
        classifier.append(nn.Linear(last_conv_output_c, num_classes))
        self.classifier = nn.Sequential(*classifier)
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, mode="fan_out")
                if m.bias is not None:
                    nn.init.zeros_(m.bias)
            elif isinstance(m, nn.BatchNorm2d):
                nn.init.ones_(m.weight)
                nn.init.zeros_(m.bias)
            elif isinstance(m, nn.Linear):
                nn.init.normal_(m.weight, 0, 0.01)
                nn.init.zeros_(m.bias)

    def _forward_impl(self, x: Tensor) -> Tensor:
        x = self.features(x)
        x = self.avgpool(x)
        x = torch.flatten(x, 1)
        x = self.classifier(x)

        return x

    def forward(self, x: Tensor) -> Tensor:
        return self._forward_impl(x)


def main():
    # 创建训练目录
    # run_dir = create_run_dir()
    run_dir = "train"
    print(f"训练记录将保存到: {run_dir}")
    # 设备设置
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    # 数据集路径
    train_dir = "../../datasets/train/images"

    # 数据预处理 
    transform = transforms.Compose([
        transforms.RandomChoice([
            transforms.ColorJitter(brightness=0.3, contrast=0.3),
            transforms.RandomAffine(degrees=0, translate=(0.1, 0.1)),
            transforms.RandomGrayscale(p=0.1)
        ]),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomVerticalFlip(p=0.1),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        transforms.RandomErasing(p=0.2, scale=(0.02, 0.1))
    ])

    # 加载数据集
    dataset = datasets.ImageFolder(root=train_dir, transform=transform)
    num_classes = len(dataset.classes)
    print(f"检测到 {num_classes} 个类别: {dataset.classes}")

    # 划分数据集
    train_size = int(0.8 * len(dataset))
    val_size = len(dataset) - train_size
    train_dataset, val_dataset = torch.utils.data.random_split(
        dataset, [train_size, val_size],
        generator=torch.Generator().manual_seed(42)  # 保证可重复性
    )

    # 优化数据加载参数
    num_workers = 8
    persistent_workers = True

    train_loader = DataLoader(
        train_dataset,
        batch_size=32,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=True,
        persistent_workers=persistent_workers
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size=32,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=True,
        persistent_workers=persistent_workers
    )

    # 导入Efficient模型
    model = EfficientNet(width_coefficient=1.0, depth_coefficient=1.0, num_classes=num_classes)
    model = model.to(device)

    # 输出模型结构
    print("\033[1;34m" + "=" * 40 + " Model Architecture " + "=" * 40 + "\033[0m")
    print(model)
    print("\033[1;34m" + "=" * 100 + "\033[0m")

    # 训练参数
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.AdamW(model.parameters(), lr=0.001, weight_decay=1e-4)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, 'max', patience=2)

    # 训练循环
    num_epochs = 10
    log_path = os.path.join(run_dir, "training_log.json")

    # 初始化历史记录
    history = {
        'train_loss': [],
        'train_accuracy': [],
        'train_precision': [],
        'train_recall': [],
        'train_f1-score': [],
        'val_loss': [],
        'val_accuracy': [],
        'val_precision': [],
        'val_recall': [],
        'val_f1-score': []
    }

    log_data = []  # 用于存储JSON格式的日志数据

    with open(log_path, 'w') as f:
        for epoch in range(num_epochs):
            epoch_start = time.time()

            # 训练阶段
            model.train()
            running_loss = 0.0
            all_train_preds = []
            all_train_labels = []
            train_start = time.time()

            with tqdm(train_loader, desc=f"Epoch Training {epoch + 1}", ncols=120) as pbar:
                for images, labels in pbar:
                    images = images.to(device, non_blocking=True)
                    labels = labels.to(device, non_blocking=True)

                    optimizer.zero_grad(set_to_none=True)
                    outputs = model(images)
                    loss = criterion(outputs, labels)
                    loss.backward()
                    optimizer.step()

                    running_loss += loss.item()
                    _, preds = torch.max(outputs, 1)
                    all_train_preds.extend(preds.cpu().numpy())
                    all_train_labels.extend(labels.cpu().numpy())

                avg_train_loss = running_loss / len(train_loader)
                train_accuracy = accuracy_score(all_train_labels, all_train_preds)
                train_precision = precision_score(all_train_labels, all_train_preds, average='weighted',
                                                  zero_division=0)
                train_recall = recall_score(all_train_labels, all_train_preds, average='weighted')
                train_f1 = f1_score(all_train_labels, all_train_preds, average='weighted')

                history['train_loss'].append(avg_train_loss)
                history['train_accuracy'].append(train_accuracy)
                history['train_precision'].append(train_precision)
                history['train_recall'].append(train_recall)
                history['train_f1-score'].append(train_f1)

            # 验证阶段
            model.eval()
            val_running_loss = 0.0
            all_val_preds = []
            all_val_labels = []
            val_start = time.time()

            with torch.no_grad():
                with tqdm(val_loader, desc=f"Epoch Validation {epoch + 1}", ncols=120) as pbar:
                    for images, labels in pbar:
                        images = images.to(device, non_blocking=True)
                        labels = labels.to(device, non_blocking=True)

                        outputs = model(images)
                        loss = criterion(outputs, labels)
                        val_running_loss += loss.item()

                        _, preds = torch.max(outputs, 1)
                        all_val_preds.extend(preds.cpu().numpy())
                        all_val_labels.extend(labels.cpu().numpy())

                    avg_val_loss = val_running_loss / len(val_loader)
                    val_accuracy = accuracy_score(all_val_labels, all_val_preds)
                    val_precision = precision_score(all_val_labels, all_val_preds, average='weighted', zero_division=0)
                    val_recall = recall_score(all_val_labels, all_val_preds, average='weighted')
                    val_f1 = f1_score(all_val_labels, all_val_preds, average='weighted')

                    history['val_loss'].append(avg_val_loss)
                    history['val_accuracy'].append(val_accuracy)
                    history['val_precision'].append(val_precision)
                    history['val_recall'].append(val_recall)
                    history['val_f1-score'].append(val_f1)

            scheduler.step(val_f1)
            epoch_time = time.time() - epoch_start

            # 保存模型
            torch.save(model.state_dict(), 'train/best_model.pth')

            # 记录日志
            epoch_log = {
                "epoch": epoch + 1,
                "time": {
                    "total": epoch_time,
                    "train": time.time() - train_start,
                    "val": time.time() - val_start
                },
                "train": {
                    "loss": avg_train_loss,
                    "acc": train_accuracy,
                    "precision": train_precision,
                    "recall": train_recall,
                    "f1": train_f1
                },
                "val": {
                    "loss": avg_val_loss,
                    "acc": val_accuracy,
                    "precision": val_precision,
                    "recall": val_recall,
                    "f1": val_f1
                }
            }
            log_data.append(epoch_log)

            log = (
                f"Epoch {epoch + 1}/{num_epochs}\n"
                f"Time [Total: {epoch_time:.2f}s | Train: {time.time() - train_start:.2f}s | Val: {time.time() - val_start:.2f}s]\n"
                f"Train Loss: {avg_train_loss:.4f} | Train Acc: {train_accuracy:.4f}\n"
                f"Train Precision: {train_precision:.4f} | Train Recall: {train_recall:.4f} | Train F1: {train_f1:.4f}\n"
                f"Val Loss: {avg_val_loss:.4f} | Val Acc: {val_accuracy:.4f}\n"
                f"Val Precision: {val_precision:.4f} | Val Recall: {val_recall:.4f} | Val F1: {val_f1:.4f}\n"
                "-----------------------------------------------------\n"
            )
            print(log)
            # 添加GPU内存监控
            print(f"GPU Memory Allocated: {torch.cuda.memory_allocated() / 1024 ** 2:.2f} MB")
            print(f"GPU Memory Cached: {torch.cuda.memory_reserved() / 1024 ** 2:.2f} MB")

        # 将日志数据以JSON格式写入文件
        json.dump(log_data, f, indent=4)

        plot_metrics(history, run_dir)
        print("训练指标曲线已保存至以下文件：")
        for metric in ['loss', 'accuracy', 'precision', 'recall', 'f1-score']:
            print(f" * {os.path.join(run_dir, f'{metric}_curve.png')}")


if __name__ == '__main__':
    # Windows多进程必须设置
    mp.freeze_support()

    # 设置多进程启动方法
    try:
        mp.set_start_method('spawn')
    except RuntimeError:
        pass

    # # 限制OpenBLAS线程数
    # torch.set_num_threads(4)
    main()
