import wandb
import os
import torch
import torchvision.transforms as transforms
from torch.utils.data import Dataset, DataLoader
from PIL import Image
from typing import Tuple
import glob
import random


class RGBPackedDataset(Dataset):
    def __init__(self, targ_dir: str) -> None:
        self.all_folders = [os.path.join(targ_dir, directory) for directory in os.listdir(targ_dir)]
        self.random_flip = 0
        self.transform = transforms.Compose([
                transforms.Resize((150, 400)),
                transforms.RandomHorizontalFlip(),
                transforms.PILToTensor(),
                transforms.ConvertImageDtype(torch.float),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])])

    def load_image(self, image) -> Image.Image:
        return self.transform(Image.open(image))

    def __len__(self) -> int:
        return len(self.all_folders)

    def __getitem__(self, index: int) -> Tuple[torch.Tensor, int]:
        self.random_flip = random.getrandbits(1)

        folder_path = self.all_folders[index]
        file_list = glob.glob(os.path.join(folder_path, "*.jpg"))
        file_list_sorted = sorted(file_list, key=lambda x: int(os.path.splitext(os.path.basename(x))[0].split("-")[0]))
        images_tensor = torch.cat([self.load_image(image).unsqueeze(0) for image in file_list_sorted])

        label_list = [int(str(image)[-5]) for image in file_list_sorted]
        label_tensor = torch.tensor(label_list).unsqueeze(1)
        name_sample = os.path.basename(folder_path)
        return images_tensor, label_tensor,name_sample


if __name__ == "__main__":

    wandb.init(
        project="Dataset_Overview",
        entity="snn_team"
    )

    dataset = RGBPackedDataset(r"/home/plgkrzysjed1/datasets/dataset_rgb")
    data_loader = DataLoader(dataset, batch_size=1, shuffle=False, num_workers=2)

    for (img, label, name) in data_loader:
        img = img.squeeze()
        label = label.squeeze()

        for i, (ima, l) in enumerate(zip(img, label)):
            mask_image = wandb.Image(ima.float(), caption=f"Frame number: {i} | Label: {str(l.item())}")
            wandb.log({f"{name[0]}": mask_image})
    wandb.finish()


