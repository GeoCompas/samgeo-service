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
                "modification_time": modification_time
            }
        
        file_groups[base_name]["files"].append({
            "file_name": file,
            "url": file_url
        })
        
        if modification_time > file_groups[base_name]["modification_time"]:
            file_groups[base_name]["modification_time"] = modification_time

    grouped_files = list(file_groups.values())
    sorted_grouped_files = sorted(grouped_files, key=lambda x: x["modification_time"], reverse=True)

    for group in sorted_grouped_files:
        group["modification_time"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(group["modification_time"]))

    return sorted_grouped_files