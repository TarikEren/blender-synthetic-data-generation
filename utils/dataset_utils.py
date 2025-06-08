import random
import shutil
from pathlib import Path

from tqdm import tqdm

from .logger_utils import logger

def split_images(train_ratio: float,
                 test_ratio: float,
                 val_ratio: float,
                 images_path: Path,
                 labels_path: Path,
                 seed: int = 59) -> dict[str, list[Path]]:
    """
    Calculates the size of the train, test and validation splits

    Args:
        train_ratio (float): Ratio of the train split (Between 0 and 1)
        test_ratio (float): Ratio of the train split (Between 0 and 1)
        val_ratio (float): Ratio of the train split (Between 0 and 1)
        images_path (Path): Path to the images
        labels_path (Path): Path to the labels
        seed (int): Seed for the randomiser

    Returns:
        dict[str, list[Path]]: A dictionary with keys 'train', 'test' and 'val' denoting each split's files' list.
    """
    if train_ratio <= 0:
        raise ValueError("Train ratio cannot be less than or equal to 0")
    
    # All image extensions are .png by default
    all_images = list(images_path.glob("*.png"))

    # All label extensions are .txt by default
    all_labels = list(labels_path.glob("*.txt"))

    if len(all_images) != len(all_labels):
        raise ValueError(f"Length of all images ({len(all_images)}) is not equal to the length of all labels ({len(all_labels)}). Please check the dataset for unlabeled images before proceeding.")

    # Initialise randomisation
    random.seed(seed)

    # Shuffle all images
    random.shuffle(all_images)

    # Calculate the count of train, test and validation groups
    n = len(all_images)
    train_count = int(n * train_ratio)
    test_count = int(n * test_ratio)
    val_count = int(n * val_ratio)

    # If the sum of all groups isn't equal to all image count add the difference to the train count
    difference = len(all_images) - (train_count + test_count + val_count)
    if difference != 0:
        train_count += difference
    
    # Get train, test and val images from all images based on their calculated counts
    train_images = all_images[:train_count]                         # Images between 0 and train_count
    val_images   = all_images[train_count:train_count + val_count]  # Images between train_count and train_count + val_count
    test_images  = all_images[train_count + val_count:]             # Images between train_count + val_count and len(all_images) - 1

    logger.info(f"""Split dataset into: [train: {train_count}, val: {val_count}, test: {test_count}]""")

    return {
        "train": train_images,
        "test": test_images,
        "val": val_images 
    }

def create_dataset_paths(sub_paths: list[str] = ["images", "labels"], splits: list[str] = ["train", "test", "val"]) -> None:
    """
    Creates the required dataset paths

    Args:
        sub_paths (list[str]): Sub paths of the dataset. ['images', 'labels'] by default
        splits (list[str]): The names of the splits. ['train', 'test', 'val'] by default

    Returns:
        None
    """
    # Set required paths
    dataset_path = Path("./dataset")

    for path in sub_paths:
        for split in splits:
            new_dir = dataset_path / path / split
            if Path.exists(new_dir):
                logger.info(f"Directory '{new_dir}' already exists, skipping creation")
            else:
                new_dir.mkdir(parents=True, exist_ok=True)
                logger.info(f"Created directory: '{new_dir}'")

def copy_dataset_contents(dataset_path: Path, splits: dict[str, list[Path]], labels_path: Path) -> None:
    """
    Copies the dataset contents to the target

    Args:
        dataset_path (Path): Path to the root dataset folder
        splits (dict[str, list[Path]]): Dictionary containing the dataset splits
        labels_path (Path): Path to the labels

    Returns:
        None
    """
    # Check if the provided dictionary is in the required format
    required_keys = ["train", "test", "val"]
    for key in required_keys:
        if key not in splits:
            raise ValueError(f"Missing key: {key}")
        
    # Copy all files
    for split, img_list in splits.items():
        logger.info(f"Processing {split} split:")
        for img_path in tqdm(img_list, desc=f"{split}", unit="files"):

            # Get the label using the image path name
            lbl_path = labels_path / (img_path.stem + '.txt')
            if not lbl_path.exists():
                raise FileNotFoundError(f"Label file not found: {lbl_path}")

            # Create the destination paths
            dst_img = dataset_path / "images" / split / img_path.name
            dst_lbl = dataset_path / "labels" / split / lbl_path.name

            # Copy the images and labels to the destination paths
            shutil.copy2(img_path, dst_img)
            shutil.copy2(lbl_path, dst_lbl)

def create_yolo_yaml(classes: list[str], dataset_path: Path) -> None:
    """
    Creates the data.yaml file for YOLO to use

    Args:
        classes (list[str]): List of class names in order.

    Returns:
        None
    """

    class_dict = {}
    for i in range(len(classes)):
        class_dict[f"{i}"] = classes[i]

    with open(dataset_path / "data.yaml", "w") as file:
        file.write(f"""path: {dataset_path}     # The dataset root

train: {dataset_path / "train"}     # Path to train
test: {dataset_path / "test"}       # Path to test
val: {dataset_path / "val"}         # Path to val

names:  # Class names
""")
        for item in class_dict:
            file.write(f"\t{item}: {class_dict[item]}\n")