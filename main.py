import os
import zipfile
import shutil
import re
import requests
from pathlib import Path
from io import BytesIO

PROXIES_URL = "https://raw.githubusercontent.com/Stefanuk12/RoProPatcher/master/proxies.txt"


def get_proxies():
    response = requests.get(PROXIES_URL)
    response.raise_for_status()
    print(response.text.splitlines())
    return response.text.splitlines()

def patch(path, proxy):
    re_pattern = re.compile(r"(https://api\.)ropro\.io/(validateUser\.php|getServerInfo\.php|getServerConnectionScore\.php|getServerAge\.php|getSubscription\.php)")
    rep = f"https://{proxy}/$2///api"

    # Patching the background file
    background_path = path / "background.js"
    with open(background_path, "r") as background_file:
        background_contents = background_file.read()

    new_background_contents = re_pattern.sub(rep, background_contents)
    with open(background_path, "w") as background_file:
        background_file.write(new_background_contents)

    if background_contents == new_background_contents:
        print("warning: nothing changed while patching `background.js` (and possibly others within js/page) - already patched?")

    # Patching each file in js/page
    jspage_path = path / "js/page"
    for file_entry in jspage_path.iterdir():
        file_path = jspage_path / file_entry.name
        with open(file_path, "r") as file:
            file_data = file.read()

        new_file_data = re_pattern.sub(rep, file_data)
        with open(file_path, "w") as file:
            file.write(new_file_data)

def download_extension():
    extension_id = "adbacgifemdbhdkfppmeilbgppmhaobf"
    extension_url = f"https://clients2.google.com/service/update2/crx?response=redirect&x=id%3D{extension_id}%26lang%3Den-US"
    response = requests.get(extension_url)
    response.raise_for_status()
    print(response.content)
    return response.content

def download_extract():
    extension_source = download_extension()

    # Output to file
    with open("RoPro.zip", "wb") as file_out:
        file_out.write(extension_source)

    print("Downloaded RoPro.")

def download_patch(selected_proxy):
    extension_source = download_extension()

    # Extract the extension
    extract_dir = Path("RoPro")
    with zipfile.ZipFile(BytesIO(extension_source), "r") as zip_ref:
        zip_ref.extractall(extract_dir)

    patch(extract_dir, selected_proxy)
    print("Finished patching.")

download_extension()

def main():
    proxies = get_proxies()

    args = os.sys.argv
    if len(args) == 2:
        arg = args[1]
        selected_proxy = proxies[int(arg)] if arg[0].isnumeric() else arg

        download_patch(selected_proxy)

        source_dir = Path("RoPro")
        with zipfile.ZipFile("RoPro-PATCHED.zip", "w") as zip_ref:
            for folder_name, _, filenames in os.walk(source_dir):
                for filename in filenames:
                    file_path = os.path.join(folder_name, filename)
                    zip_ref.write(file_path, os.path.relpath(file_path, source_dir))

        shutil.rmtree(source_dir)
        print("Goodbye!")
        return

    print("-------------------------")
    print("-     RoPro Patcher     -")
    print("- Created by Stefanuk12 -")
    print("-------------------------")

    while True:
        print("1. Download RoPro source as .zip")
        print("2. Download and Patch (uses default proxy)")
        print("3. Exit")

        choice = input("Enter your choice: ")
        if choice == "1":
            download_extract()
        elif choice == "2":
            download_patch(proxies[1])
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
