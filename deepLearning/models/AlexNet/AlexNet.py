import json
import multiprocessing as mp
import os
import time

import matplotlib.pyplot as plt
import torch
import torch.nn as nn
import torch.optim as optim
import torchvision.transforms as transforms
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from torch.utils.data import DataLoader
from torchvision import datasets, models
from tqdm import tqdm

# 设置matplotlib中文字体
plt.rcParams["font.family"] = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC"]
plt.rcParams["axes.unicode_minus"] = False  # 解决负号显示问题


def create_run_dir(base_dir="train"):
    """创建带有时间戳和序号的新训练目录"""
    timestamp = "train_" + time.strftime("%Y%m%d_%H%M")
    run_dir = os.path.join(base_dir, timestamp)

    # 自动处理重复运行
    counter = 2
    while os.path.exists(run_dir):
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
            'title': '训练和验证损失',
            'ylabel': '损失值',
            'train_key': 'train_loss',
            'val_key': 'val_loss',
            'colors': {'train': '#1f77b4', 'val': '#ff7f0e'},
            'formatter': None
        },
        {
            'name': 'accuracy',
            'title': '训练和验证准确率',
            'ylabel': '准确率',
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
            'title': '验证精确率',
            'ylabel': '精确率',
            'key': 'val_precision',
            'color': '#ff7f0e',
            'formatter': plt.FuncFormatter(lambda x, _: f'{x:.0%}')
        },
        {
            'name': 'recall',
            'title': '验证召回率',
            'ylabel': '召回率',
            'key': 'val_recall',
            'color': '#d62728',
            'formatter': plt.FuncFormatter(lambda x, _: f'{x:.0%}')
        },
        {
            'name': 'f1-score',
            'title': '验证F1分数',
            'ylabel': 'F1分数',
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
                label='训练',
                markeredgecolor='white',
                markeredgewidth=1)

        ax.plot(epochs, val_values,
                marker='o',
                markersize=6,
                linewidth=2.5,
                color=config['colors']['val'],
                alpha=0.8,
                label='验证',
                markeredgecolor='white',
                markeredgewidth=1)

        ax.set_title(config['title'], fontsize=14, pad=15, fontweight='bold')
        ax.set_xlabel('轮次', fontsize=12, labelpad=10)
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
        ax.annotate(f'训练: {last_train:.4f}',
                    xy=(epochs[-1], last_train),
                    xytext=(epochs[-1] - num_epochs * 0.15, last_train * 1.05),
                    fontsize=10,
                    arrowprops=dict(arrowstyle="->", color=config['colors']['train'], linewidth=1.5, alpha=0.7))
        ax.annotate(f'验证: {last_val:.4f}',
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
        ax.set_xlabel('轮次', fontsize=12, labelpad=10)
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


def main():
    # 创建训练目录
    run_dir = create_run_dir()
    print(f"训练记录将保存到: {run_dir}")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"使用设备: {device}")
    if device.type == "cuda":
        print(f"GPU名称: {torch.cuda.get_device_name(0)}")
        print(f"GPU内存: {format_memory(torch.cuda.get_device_properties(0).total_memory / 1024 ** 2)}")

    train_dir = "D:/datasets_200/train/images"

    # 数据预处理
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomChoice([
            transforms.ColorJitter(brightness=0.3, contrast=0.3),  # 改变图像亮度和对比度
            transforms.RandomAffine(degrees=0, translate=(0.1, 0.1)),  # 在水平和垂直方向上随机平移最多 10% 的图像尺寸
            transforms.RandomGrayscale(p=0.1)  # 以 10% 的概率将图像转换为灰度图
        ]),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomVerticalFlip(p=0.1),
        transforms.ToTensor(),  # 转换为张量，将像素值从 [0, 255] 缩放到 [0, 1]
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),  # 标准化
        transforms.RandomErasing(p=0.2, scale=(0.02, 0.1))  # 随机擦除模拟遮挡
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

    batch_size = 4
    num_workers = 8
    persistent_workers = True

    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=True,
        persistent_workers=persistent_workers
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=True,
        persistent_workers=persistent_workers
    )

    # 使用预训练的AlexNet模型
    model = models.alexnet(pretrained=True)

    # 简化分类器以减少参数和内存使用
    model.classifier = nn.Sequential(
        nn.Dropout(p=0.5),
        nn.Linear(256 * 6 * 6, 256),
        nn.ReLU(inplace=True),
        nn.Linear(256, num_classes)
    )
    model = model.to(device)

    # 输出模型结构
    print("\033[1;34m" + "=" * 40 + " 模型架构 " + "=" * 40 + "\033[0m")
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

            with tqdm(train_loader, desc=f"第 {epoch + 1} 轮训练", ncols=120) as pbar:
                for images, labels in pbar:
                    # 将数据移至GPU
                    images = images.to(device, non_blocking=True)
                    labels = labels.to(device, non_blocking=True)

                    # 梯度清零
                    optimizer.zero_grad(set_to_none=True)

                    # 前向传播
                    outputs = model(images)
                    loss = criterion(outputs, labels)

                    # 反向传播
                    loss.backward()
                    optimizer.step()

                    running_loss += loss.item()
                    _, preds = torch.max(outputs, 1)

                    # 将预测和标签移至CPU并收集
                    all_train_preds.extend(preds.cpu().numpy())
                    all_train_labels.extend(labels.cpu().numpy())

                    # 手动释放不需要的张量
                    del images, labels, outputs, preds, loss
                    torch.cuda.empty_cache()  # 清空缓存

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

            with torch.no_grad():  # 不计算梯度以节省内存
                with tqdm(val_loader, desc=f"第 {epoch + 1} 轮验证", ncols=120) as pbar:
                    for images, labels in pbar:
                        # 将数据移至GPU
                        images = images.to(device, non_blocking=True)
                        labels = labels.to(device, non_blocking=True)

                        outputs = model(images)
                        loss = criterion(outputs, labels)
                        val_running_loss += loss.item()

                        _, preds = torch.max(outputs, 1)

                        # 将预测和标签移至CPU并收集
                        all_val_preds.extend(preds.cpu().numpy())
                        all_val_labels.extend(labels.cpu().numpy())

                        # 手动释放不需要的张量
                        del images, labels, outputs, preds, loss
                        torch.cuda.empty_cache()  # 清空缓存

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

            # 保存最佳模型
            if val_f1 > best_f1:
                best_f1 = val_f1
                torch.save(model.state_dict(), os.path.join(run_dir, 'best_model.pth'))
                print(f"已保存最佳模型 (F1: {val_f1:.4f})")

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
                f"轮次 {epoch + 1}/{num_epochs}\n"
                f"时间 [总计: {epoch_time:.2f}秒 | 训练: {time.time() - train_start:.2f}秒 | 验证: {time.time() - val_start:.2f}秒]\n"
                f"训练损失: {avg_train_loss:.4f} | 训练准确率: {train_accuracy:.4f}\n"
                f"训练精确率: {train_precision:.4f} | 训练召回率: {train_recall:.4f} | 训练F1: {train_f1:.4f}\n"
                f"验证损失: {avg_val_loss:.4f} | 验证准确率: {val_accuracy:.4f}\n"
                f"验证精确率: {val_precision:.4f} | 验证召回率: {val_recall:.4f} | 验证F1: {val_f1:.4f}\n"
                "-----------------------------------------------------\n"
            )
            print(log)

            # 添加GPU内存监控
            if device.type == "cuda":
                print(f"GPU内存使用: {format_memory(torch.cuda.memory_allocated() / 1024 ** 2)}")
                print(f"GPU缓存使用: {format_memory(torch.cuda.memory_reserved() / 1024 ** 2)}")

        # 将日志数据以JSON格式写入文件
        json.dump(log_data, f, indent=4)

        # 绘制并保存指标曲线
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

    # 清理GPU内存
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    main()
