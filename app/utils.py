import os
import time


def group_files_by_base_name(public_dir: str, base_url: str) -> list:
    if not os.path.exists(public_dir):
        return {"error": "The public directory does not exist."}

    file_groups = {}

    for file in os.listdir(public_dir):
        modification_time = os.path.getmtime(os.path.join(public_dir, file))
        base_name, _ = os.path.splitext(file)
        file_url = f"{base_url}/{file}"

        if base_name not in file_groups:
            file_groups[base_name] = {
                "base_name": base_name,
                "files": [],
                "modification_time": modification_time,
            }

        file_groups[base_name]["files"].append({"file_name": file, "url": file_url})

        if modification_time > file_groups[base_name]["modification_time"]:
            file_groups[base_name]["modification_time"] = modification_time

    grouped_files = list(file_groups.values())
    sorted_grouped_files = sorted(grouped_files, key=lambda x: x["modification_time"], reverse=True)

    for group in sorted_grouped_files:
        group["modification_time"] = time.strftime(
            "%Y-%m-%d %H:%M:%S", time.localtime(group["modification_time"])
        )

    return sorted_grouped_files


# Endpoint to check if SamGeo is using GPU
@app.get("/gpu-check")
def check_gpu():
    # Initialize SamGeo model
    sam = SamGeo(
        model_type="vit_h",
        checkpoint="sam_vit_h_4b8939.pth",
        sam_kwargs=None,
    )

    # Check if GPU is available and being used
    if torch.cuda.is_available():
        device = torch.device("cuda")
        sam.model.to(device)  # Ensure the model is moved to GPU
        return {"gpu": True, "device": torch.cuda.get_device_name(0)}
    else:
        return {"gpu": False, "message": "No GPU available, using CPU"}
