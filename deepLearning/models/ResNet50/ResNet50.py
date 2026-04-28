import json
import os
import random
import time
from datetime import datetime

import torch
import torch.multiprocessing as mp
import torch.nn as nn
import torch.optim as optim
import torchvision.datasets as datasets
import torchvision.transforms as transforms
from PIL import Image
from matplotlib import pyplot as plt
from sklearn.metrics import precision_score, recall_score, accuracy_score, f1_score
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
    plt.style.use('seaborn')

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
class Bottleneck(nn.Module):
    expansion = 4

    def __init__(self, in_channels, out_channels, stride=1, downsample=None):
        super(Bottleneck, self).__init__()
        self.conv1 = nn.Conv2d(in_channels, out_channels, kernel_size=1, bias=False)
        self.bn1 = nn.BatchNorm2d(out_channels)
        self.conv2 = nn.Conv2d(out_channels, out_channels, kernel_size=3, stride=stride,
                               padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(out_channels)
        self.conv3 = nn.Conv2d(out_channels, out_channels * self.expansion, kernel_size=1, bias=False)
        self.bn3 = nn.BatchNorm2d(out_channels * self.expansion)
        self.relu = nn.ReLU(inplace=True)
        self.downsample = downsample

    def forward(self, x):
        identity = x

        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)

        out = self.conv2(out)
        out = self.bn2(out)
        out = self.relu(out)

        out = self.conv3(out)
        out = self.bn3(out)

        if self.downsample is not None:
            identity = self.downsample(x)

        out += identity
        out = self.relu(out)

        return out


class ResNet50(nn.Module):
    def __init__(self, num_classes=1000):
        super(ResNet50, self).__init__()
        self.in_channels = 64
        self.conv1 = nn.Conv2d(3, 64, kernel_size=7, stride=2, padding=3, bias=False)
        self.bn1 = nn.BatchNorm2d(64)
        self.relu = nn.ReLU(inplace=True)
        self.maxpool = nn.MaxPool2d(kernel_size=3, stride=2, padding=1)

        self.layer1 = self._make_layer(64, 3)
        self.layer2 = self._make_layer(128, 4, stride=2)
        self.layer3 = self._make_layer(256, 6, stride=2)
        self.layer4 = self._make_layer(512, 3, stride=2)

        self.avgpool = nn.AdaptiveAvgPool2d((1, 1))
        self.fc = nn.Linear(512 * Bottleneck.expansion, num_classes)

    def _make_layer(self, out_channels, blocks, stride=1):
        downsample = None
        if stride != 1 or self.in_channels != out_channels * Bottleneck.expansion:
            downsample = nn.Sequential(
                nn.Conv2d(self.in_channels, out_channels * Bottleneck.expansion,
                          kernel_size=1, stride=stride, bias=False),
                nn.BatchNorm2d(out_channels * Bottleneck.expansion)
            )

        layers = []
        layers.append(Bottleneck(self.in_channels, out_channels, stride, downsample))
        self.in_channels = out_channels * Bottleneck.expansion
        for _ in range(1, blocks):
            layers.append(Bottleneck(self.in_channels, out_channels))

        return nn.Sequential(*layers)

    def forward(self, x):
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)
        x = self.maxpool(x)

        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)

        x = self.avgpool(x)
        x = torch.flatten(x, 1)
        x = self.fc(x)

        return x


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

    # 数据转换
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

    # 导入ResNet50模型
    # model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V1)
    # model.fc = nn.Sequential(
    #     nn.Dropout(p=0.5),
    #     nn.Linear(model.fc.in_features, 512),
    #     nn.ReLU(),
    #     nn.Linear(512, num_classes)
    # )
    # model.conv1 = nn.Conv2d(
    #     in_channels=3,
    #     out_channels=64,
    #     kernel_size=7,
    #     stride=2,
    #     padding=3,
    #     bias=False
    # )
    # model = model.to(device)
    model = ResNet50(num_classes=num_classes)

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
    best_f1 = 0.0
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
