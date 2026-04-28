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
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
from matplotlib import pyplot as plt
from sklearn.metrics import precision_score, recall_score, accuracy_score, f1_score
from torch.utils.data import DataLoader
from torchvision.models.googlenet import InceptionAux
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

class BasicConv2d(nn.Module):
    def __init__(self, in_channels, out_channels, **kwargs):
        super(BasicConv2d, self).__init__()
        self.conv = nn.Conv2d(in_channels, out_channels, **kwargs)
        self.relu = nn.ReLU(inplace=True)

    def forward(self, x):
        x = self.conv(x)
        x = self.relu(x)
        return x


class Inception(nn.Module):
    def __init__(self, in_channels, ch1x1, ch3x3red, ch3x3, ch5x5red, ch5x5, pool_proj):
        super(Inception, self).__init__()
        self.branch1 = BasicConv2d(in_channels, ch1x1, kernel_size=1)
        self.branch2 = nn.Sequential(
            BasicConv2d(in_channels, ch3x3red, kernel_size=1),
            BasicConv2d(ch3x3red, ch3x3, kernel_size=3, padding=1)
        )

        self.branch3 = nn.Sequential(
            BasicConv2d(in_channels, ch5x5red, kernel_size=1),
            BasicConv2d(ch5x5red, ch5x5, kernel_size=5, padding=2)
        )
        self.branch4 = nn.Sequential(
            nn.MaxPool2d(kernel_size=3, stride=1, padding=1),
            BasicConv2d(in_channels, pool_proj, kernel_size=1)
        )

    def forward(self, x):
        branch1 = self.branch1(x)
        branch2 = self.branch2(x)
        branch3 = self.branch3(x)
        branch4 = self.branch4(x)
        outputs = [branch1, branch2, branch3, branch4]
        return torch.cat(outputs, 1)


class GoogLeNet(nn.Module):
    def __init__(self, num_classes, aux_logits=True, init_weights=False):
        super(GoogLeNet, self).__init__()
        self.aux_logits = aux_logits
        self.conv1 = BasicConv2d(3, 64, kernel_size=7, stride=2, padding=3)
        self.maxpool1 = nn.MaxPool2d(3, stride=2, ceil_mode=True)
        self.conv2 = BasicConv2d(64, 64, kernel_size=1)
        self.conv3 = BasicConv2d(64, 192, kernel_size=3, padding=1)
        self.maxpool2 = nn.MaxPool2d(3, stride=2, ceil_mode=True)
        self.inception3a = Inception(192, 64, 96, 128, 16, 32, 32)
        self.inception3b = Inception(256, 128, 128, 192, 32, 96, 64)
        self.maxpool3 = nn.MaxPool2d(3, stride=2, ceil_mode=True)
        self.inception4a = Inception(480, 192, 96, 208, 16, 48, 64)
        self.inception4b = Inception(512, 160, 112, 224, 24, 64, 64)
        self.inception4c = Inception(512, 128, 128, 256, 24, 64, 64)
        self.inception4d = Inception(512, 112, 144, 288, 32, 64, 64)
        self.inception4e = Inception(528, 256, 160, 320, 32, 128, 128)
        self.maxpool4 = nn.MaxPool2d(3, stride=2, ceil_mode=True)
        self.inception5a = Inception(832, 256, 160, 320, 32, 128, 128)
        self.inception5b = Inception(832, 384, 192, 384, 48, 128, 128)
        if self.aux_logits:
            self.aux1 = InceptionAux(512, num_classes)
            self.aux2 = InceptionAux(528, num_classes)
        self.avgpool = nn.AdaptiveAvgPool2d((1, 1))
        self.dropout = nn.Dropout(0.4)
        self.fc = nn.Linear(1024, num_classes)
        if init_weights:
            self._initialize_weights()

    def forward(self, x):
        x = self.conv1(x)
        x = self.maxpool1(x)
        x = self.conv2(x)
        x = self.conv3(x)
        x = self.maxpool2(x)
        x = self.inception3a(x)
        x = self.inception3b(x)
        x = self.maxpool3(x)
        x = self.inception4a(x)
        if self.training and self.aux_logits:
            aux1 = self.aux1(x)
        x = self.inception4b(x)
        x = self.inception4c(x)
        x = self.inception4d(x)
        if self.training and self.aux_logits:
            aux2 = self.aux2(x)
        x = self.inception4e(x)
        x = self.maxpool4(x)
        x = self.inception5a(x)
        x = self.inception5b(x)
        x = self.avgpool(x)
        x = torch.flatten(x, 1)
        x = self.dropout(x)
        x = self.fc(x)
        if self.training and self.aux_logits:
            return x, aux2, aux1
        return x


def _initialize_weights(self):
    for m in self.modules():
        if isinstance(m, nn.Conv2d):
            nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
        if m.bias is not None:
            nn.init.constant_(m.bias, 0)
        elif isinstance(m, nn.Linear):
            nn.init.normal_(m.weight, 0, 0.01)
            nn.init.constant_(m.bias, 0)


def main():
    # 创建训练目录
    # run_dir = create_run_dir()
    run_dir = "train"
    print(f"训练记录将保存到: {run_dir}")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

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

    dataset = datasets.ImageFolder(root=train_dir, transform=transform)
    num_classes = len(dataset.classes)
    print(f"检测到 {num_classes} 个类别: {dataset.classes}")

    train_size = int(0.8 * len(dataset))
    val_size = len(dataset) - train_size
    train_dataset, val_dataset = torch.utils.data.random_split(
        dataset, [train_size, val_size],
        generator=torch.Generator().manual_seed(42)
    )

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
    # 导入GoogleNet模型
    # model = GoogLeNet(num_classes=num_classes)
    model = models.googlenet(weights=models.GoogLeNet_Weights.DEFAULT, aux_logits=True)
    model.fc = nn.Sequential(
        nn.Dropout(p=0.5),
        nn.Linear(model.fc.in_features, 512),
        nn.ReLU(),
        nn.Linear(512, num_classes)
    )
    model.conv1 = nn.Conv2d(
        in_channels=3,
        out_channels=64,
        kernel_size=7,
        stride=2,
        padding=3,
        bias=False
    )
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

    # 限制OpenBLAS线程数
    torch.set_num_threads(4)
    main()
