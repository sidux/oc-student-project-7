import matplotlib.pyplot as plt
import json
import os
import shutil

import pandas as pd
from matplotlib import pyplot as plt

def save_cell_output(cell: str | int | None = None, **kwargs):
    base_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "result")

    cell_dir = base_dir
    if cell is not None:
        cell_dir = os.path.join(base_dir, f"cell_{cell}")
        if os.path.exists(cell_dir):
            shutil.rmtree(cell_dir)

    os.makedirs(cell_dir, exist_ok=True)

    saved_files = []

    for filename, data in kwargs.items():
        try:
            if isinstance(data, pd.DataFrame):
                # Save DataFrame as CSV
                filepath = os.path.join(cell_dir, f"{filename}.csv")
                data.to_csv(filepath, index=False)
                saved_files.append(filepath)

            elif isinstance(data, plt.Figure) or hasattr(data, 'savefig'):
                # Save matplotlib figure
                filepath = os.path.join(cell_dir, f"{filename}.png")
                data.savefig(filepath, dpi=300, bbox_inches='tight')
                saved_files.append(filepath)

            elif isinstance(data, (dict, list)):
                # Save dictionary or list as JSON
                filepath = os.path.join(cell_dir, f"{filename}.json")
                with open(filepath, 'w') as f:
                    json.dump(data, f, indent=2, default=str)
                saved_files.append(filepath)

            elif isinstance(data, str):
                # Save string as text file
                filepath = os.path.join(cell_dir, f"{filename}.txt")
                with open(filepath, 'w') as f:
                    f.write(data)
                saved_files.append(filepath)

            elif hasattr(data, 'to_dict'):
                # Save objects with to_dict method as JSON
                filepath = os.path.join(cell_dir, f"{filename}.json")
                with open(filepath, 'w') as f:
                    json.dump(data.to_dict(), f, indent=2, default=str)
                saved_files.append(filepath)

            else:
                # Try to save as string representation
                filepath = os.path.join(cell_dir, f"{filename}.txt")
                with open(filepath, 'w') as f:
                    f.write(str(data))
                saved_files.append(filepath)

        except Exception as e:
            print(f"Warning: Could not save {filename}: {str(e)}")

    return saved_files
