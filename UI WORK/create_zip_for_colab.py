"""
=============================================================================
             ZIP ARCHIVER FOR GOOGLE COLAB APK BUILD
 Creates a self-contained ZIP archive containing all app code, assets,
 SQLite database, and the complete fast Android Gradle project.
=============================================================================
"""

import os
import zipfile

UI_WORK_DIR = os.path.dirname(os.path.abspath(__file__))
ZIP_OUTPUT = os.path.join(UI_WORK_DIR, "UI_WORK_FOR_COLAB.zip")

FILES_TO_INCLUDE = [
    "main.py",
    "app.py",
    "database.py",
    "promotion_data.py",
    "buildozer.spec",
    "jainagar_chunav.db"
]

FOLDERS_TO_INCLUDE = [
    "assets",
    "www",
    "android_project"
]


def make_colab_zip():
    print(f"Creating Colab Build Package: {ZIP_OUTPUT} ...")
    with zipfile.ZipFile(ZIP_OUTPUT, "w", zipfile.ZIP_DEFLATED) as zf:
        # Include root files
        for f in FILES_TO_INCLUDE:
            f_path = os.path.join(UI_WORK_DIR, f)
            if os.path.exists(f_path):
                zf.write(f_path, arcname=f)
                print(f"  + Added: {f} ({round(os.path.getsize(f_path)/1024, 1)} KB)")
            else:
                print(f"  - Missing: {f}")

        # Include folders
        for folder in FOLDERS_TO_INCLUDE:
            folder_path = os.path.join(UI_WORK_DIR, folder)
            if os.path.exists(folder_path):
                for root, _, files in os.walk(folder_path):
                    for file in files:
                        full_path = os.path.join(root, file)
                        rel_path = os.path.relpath(full_path, UI_WORK_DIR)
                        zf.write(full_path, arcname=rel_path)
                        print(f"  + Added: {rel_path}")

    size_mb = round(os.path.getsize(ZIP_OUTPUT) / (1024 * 1024), 2)
    print("\n" + "=" * 60)
    print(f"SUCCESS: Package created: {ZIP_OUTPUT}")
    print(f"Package Size: {size_mb} MB")
    print("Ready to upload directly to Google Colab!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    make_colab_zip()
