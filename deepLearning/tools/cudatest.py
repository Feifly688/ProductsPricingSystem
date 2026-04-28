import torch

print("PyTorch版本:", torch.__version__)
print("CUDA可用:", torch.cuda.is_available())
print("GPU数量:", torch.cuda.device_count())
print("当前设备:", torch.cuda.current_device())
print("设备名称:", torch.cuda.get_device_name(0))