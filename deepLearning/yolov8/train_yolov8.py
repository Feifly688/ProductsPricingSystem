from ultralytics import YOLO
import torch

def train():

    # 1️⃣ 检查设备
    device = '0' if torch.cuda.is_available() else 'cpu'
    print(f"使用设备: {device}")

    # 2️⃣ 加载模型
    model = YOLO('yolov8l.pt')

    # 3️⃣ 训练配置
    config = {
        'data': 'data.yaml',
        'epochs': 5,
        'batch': 12,
        'imgsz': 640,
        'mosaic': 0.5,
        'mixup': 0.2,
        'copy_paste': 0.3,
        'degrees': 5.0,
        'translate': 0.1,
        'scale': 0.5,
        'shear': 1.0,
        'perspective': 0.0001,
        'flipud': 0.0,
        'fliplr': 0.5,
        'optimizer': 'SGD',
        'lr0': 0.01,
        'lrf': 0.01,
        'momentum': 0.937,
        'weight_decay': 0.0005,
        'box': 7.5,
        'cls': 1.0,
        'dfl': 1.5,
        'patience': 20,
        'save_period': 10,
        'workers': 8,
        'device': device,
        'project': 'runs',
        'name': 'train',
        'exist_ok': True,
        'close_mosaic': 10,
        'warmup_epochs': 3,
        'warmup_momentum': 0.8,
        'warmup_bias_lr': 0.1,
        'val': True,
        'plots': True,
    }

    # 4️⃣ 开始训练
    print("开始训练...")
    print(f"配置: {config}")
    model.train(**config)

    # 5️⃣ 评估最佳模型
    best_model = YOLO('runs/train/weights/best.pt')
    val_results = best_model.val(
        data='data.yaml',
        imgsz=640,
        conf=0.25,
        iou=0.45,
        batch=16,
        plots=True
    )
    print(f"\n✅ 验证集结果:")
    print(f"mAP@0.5: {val_results.box.map50:.4f}")
    print(f"mAP@0.5:0.95: {val_results.box.map:.4f}")
    print(f"Precision: {val_results.box.p:.4f}")
    print(f"Recall: {val_results.box.r:.4f}")

    # 6️⃣ 导出模型
    best_model.export(format='onnx', imgsz=640, half=True)
    print("✅ 模型导出完成")

    return val_results

if __name__ == '__main__':
    train()