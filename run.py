"""Execute the research notebook in a fresh Python kernel."""

import argparse
import os
import sys
from pathlib import Path

import nbformat
from jupyter_client import KernelManager
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("notebook", nargs="?", default="baseline.ipynb", type=Path)
    args = parser.parse_args()
    destination = ROOT / args.notebook
    notebook = nbformat.read(destination, as_version=4)
    for cell in notebook.cells:
        if cell.cell_type == "code":
            cell.outputs = []
            cell.execution_count = None
    for variable, relative in [
        ("MPLCONFIGDIR", ".cache/matplotlib"),
        ("XDG_CACHE_HOME", ".cache"),
        ("IPYTHONDIR", ".cache/ipython"),
        ("JUPYTER_RUNTIME_DIR", ".cache/jupyter-runtime"),
    ]:
        path = ROOT / relative
        path.mkdir(parents=True, exist_ok=True)
        os.environ.setdefault(variable, str(path))

    # Explicitly use the interpreter that starts this script; no global kernelspec installation.
    manager = KernelManager(kernel_name="python3")
    manager.kernel_spec.argv = [sys.executable, "-m", "ipykernel_launcher", "-f", "{connection_file}"]
    client = NotebookClient(
        notebook, km=manager, timeout=1800, record_timing=False,
        resources={"metadata": {"path": str(ROOT)}},
    )
    print(f"Running {destination.name}, Python {sys.version.split()[0]}", flush=True)
    client.execute(cleanup_kc=True)
    nbformat.write(notebook, destination)
    print(f"Saved: {destination.relative_to(ROOT)}", flush=True)


if __name__ == "__main__":
    main()
