version=0.2
import os
import json
import shutil
from datetime import datetime
import subprocess

# === Dynamic Root Path ===
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

data_dir = os.path.join(base_dir, "Data")
servers_dir = os.path.join(base_dir, "Servers")
backups_dir = os.path.join(base_dir, "Backups")
config_path = os.path.join(data_dir, "defaults.json")
updater_dir = os.path.join(data_dir, "updater.py")

subprocess.Popen(["python", updater_dir])

# === Ensure Config Exists ===
default_config = {
    "default_ram": "",
    "gui_enabled": True,
    "default_port": 25565
}

if not os.path.exists(config_path):
    with open(config_path, 'w') as f:
        json.dump(default_config, f, indent=4)

# === Utility Function ===
def update_config(key, value, validator=None, label="Setting"):
    if validator and not validator(value):
        print(f"Invalid input for {label}.")
        return

    try:
        with open(config_path, 'r') as f:
            config = json.load(f)

        config[key] = value

        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)

        print(f"{label} updated to: {value}")

    except Exception as e:
        print(f"Error updating config: {e}")

import requests
import subprocess
import shutil

server_root = servers_dir

def load_defaults():
    if not os.path.exists(config_path):
        return {}
    with open(config_path, 'r') as f:
        return json.load(f)

def prompt_or_default(label, key, defaults):
    value = defaults.get(key)
    if value:
        print(f"{label} (default: {value})")
        return value
    return input(f"{label}: ").strip()

def get_jar_url(server_type, variant, version):
    return f"https://mcjarfiles.com/api/get-jar/{server_type}/{variant}/{version}"

def create_server():
    options = {
        "1": ("vanilla", "release"),
        "2": ("servers", "paper"),
        "3": ("modded", "fabric"),
        "4": ("modded", "forge"),
        "5": ("modded", "neoforge")
    }

    print("Choose server software:")
    print(" 1. Vanilla\n 2. Paper\n 3. Fabric\n 4. Forge\n 5. NeoForge")
    choice = input("> ").strip()

    if choice not in options:
        print("Invalid choice.")
        return

    server_type, variant = options[choice]
    is_paper = server_type == "servers" and variant == "paper"
    version = input("Enter Minecraft version (e.g., 1.20.1): ").strip()
    server_name = input("Enter server name: ").strip()
    server_path = os.path.join(server_root, server_name)

    if os.path.exists(server_path):
        print("Server name already exists.")
        return

    os.makedirs(server_path, exist_ok=True)
    jar_url = get_jar_url(server_type, variant, version)
    jar_path = os.path.join(server_path, "server.jar")

    try:
        print("Downloading server JAR...")
        response = requests.get(jar_url)
        response.raise_for_status()
        with open(jar_path, 'wb') as f:
            f.write(response.content)
        print("Download complete.")
    except Exception as e:
        print(f"Failed to download JAR: {e}")
        shutil.rmtree(server_path)
        return

    defaults = load_defaults()
    ram = prompt_or_default("Enter RAM amount (e.g., 2G)", "default_ram", defaults)
    port = prompt_or_default("Enter port", "default_port", defaults)
    gui_enabled = defaults.get("gui_enabled", True)
    nogui_flag = "" if gui_enabled else "--nogui"

    eula_path = os.path.join(server_path, "eula.txt")

    if is_paper:
        # Paper doesn't auto-generate eula.txt, so we handle it manually
        with open(eula_path, 'w') as f:
            f.write("eula=false\n")

        accept = input("Do you accept the EULA? (yes/no): ").strip().lower()
        if accept != "yes":
            print("EULA not accepted. Deleting server.")
            shutil.rmtree(server_path)
            return

        with open(eula_path, 'w') as f:
            f.write("eula=true\n")


        print("Starting server...")
        subprocess.run(
            ["java", f"-Xmx{ram}", f"-Xms{ram}", "-jar", "server.jar", nogui_flag, f"--port={port}"],
            cwd=server_path,
            shell=True
        )

    else:
        print("Running server to generate eula.txt...")
        subprocess.run(
            ["java", f"-Xmx{ram}", f"-Xms{ram}", "-jar", "server.jar", nogui_flag],
            cwd=server_path,
            shell=True
        )

        if not os.path.exists(eula_path):
            print("eula.txt not found. Server may have failed to start.")
            shutil.rmtree(server_path)
            return

        accept = input("Do you accept the EULA? (yes/no): ").strip().lower()
        if accept != "yes":
            print("EULA not accepted. Deleting server.")
            shutil.rmtree(server_path)
            return

        with open(eula_path, 'w') as f:
            f.write("eula=true\n")


        print("Starting server...")
        subprocess.run(
            ["java", f"-Xmx{ram}", f"-Xms{ram}", "-jar", "server.jar", nogui_flag, f"--port={port}"],
            cwd=server_path,
            shell=True
        )
def delete_server():
    server_name = input("Enter the name of the server to delete: ").strip()
    server_path = os.path.join(server_root, server_name)

    if not os.path.exists(server_path):
        print(f"No server found with the name '{server_name}'.")
        return

    confirm = input(f"Are you sure you want to delete '{server_name}'? This cannot be undone. (yes/no): ").strip().lower()
    if confirm == "yes":
        try:
            shutil.rmtree(server_path)
            print(f"Server '{server_name}' deleted successfully.")
        except Exception as e:
            print(f"Failed to delete server: {e}")
    else:
        print("Deletion cancelled.")
def start_server():
    server_name = input("Enter the name of the server to start: ").strip()
    server_path = os.path.join(server_root, server_name)
    jar_path = os.path.join(server_path, "server.jar")

    if not os.path.exists(server_path):
        print(f"No server found with the name '{server_name}'.")
        return

    if not os.path.exists(jar_path):
        print(f"No server.jar found in '{server_name}'.")
        return

    defaults = load_defaults()
    ram = prompt_or_default("Enter RAM amount (e.g., 2G)", "default_ram", defaults)
    port = prompt_or_default("Enter port", "default_port", defaults)
    gui_enabled = defaults.get("gui_enabled", True)
    nogui_flag = "" if gui_enabled else "--nogui"

    print(f"Starting server '{server_name}'...")
    subprocess.run(
        ["java", f"-Xmx{ram}", f"-Xms{ram}", "-jar", "server.jar", nogui_flag, f"--port={port}"],
        cwd=server_path,
        shell=True
    )


def copy_server(src_folder, dest_folder):
    timestamp = datetime.now().strftime('%d%m%Y')  # DayMonthYear format
    new_name = f"{os.path.basename(src_folder)}_{timestamp}"
    target_path = os.path.join(dest_folder, new_name)
    shutil.copytree(src_folder, target_path)
    return target_path


def move_server(src_folder, dest_folder):
    target_path = os.path.join(dest_folder, os.path.basename(src_folder))
    if os.path.exists(target_path):
        raise FileExistsError(f"Destination already exists: {target_path}")
    shutil.move(src_folder, target_path)
    return target_path



# === Main Loop ===
while True:
    os.system("cls")
    print("Options:\n 1. Create a server\n 2. Delete a server\n 3. Start a server\n 4. Open Settings\n 5. Manage Server Backups\n 6. Exit")
    print("Input the number corresponding to your choice.")
    mode = input("> ").strip()

    if mode == "6":
        exit()

    if mode == "1":
        create_server()

    if mode == "2":
        delete_server()

    if mode == "3":
        start_server()
    
    if mode == "5":
        print("Options:\n 1. Create a Server Backup\n 2. Load a server backup")
        backupmode = input("> ")
        if backupmode == "1":
            print("Please input the name of the server you want to back-up")
            serverbackupname = input("> ")
            copy_server(f"{servers_dir}/{serverbackupname}",backups_dir)
        elif backupmode == "2":
            print("Enter the name of the server to restore:")
            server_name = input("> ").strip()
            backup_dir = backups_dir
            server_dir = servers_dir

            # Find matching backups
            matching_backups = [
                name for name in os.listdir(backup_dir)
                if name.startswith(f"{server_name}_") and os.path.isdir(os.path.join(backup_dir, name))
            ]

            if not matching_backups:
                print(f"No backups found for server '{server_name}'.")
            else:
                print(f"Available backups for '{server_name}':")
                for i, backup in enumerate(matching_backups):
                    date_str = backup.replace(f"{server_name}_", "")
                    print(date_str)
                    # Interpret YYYYMMDD format
                    formatted_date = f"{date_str[6:8]}-{date_str[4:6]}-{date_str[0:4]}"

                    print(f" {i+1}. {backup} (Date: {formatted_date})")

                print("Enter the number of the backup to restore:")
                choice = input("> ").strip()

                if not choice.isdigit() or not (1 <= int(choice) <= len(matching_backups)):
                    print("Invalid selection.")
                else:
                    selected_backup = matching_backups[int(choice) - 1]
                    backup_path = os.path.join(backup_dir, selected_backup)
                    restore_path = os.path.join(server_dir, server_name)

                    if os.path.exists(restore_path):
                        confirm = input(f"Server '{server_name}' already exists. Overwrite? (yes/no): ").strip().lower()
                        if confirm != "yes":
                            print("Restore cancelled.")
                        else:
                            shutil.rmtree(restore_path)

                    shutil.copytree(backup_path, restore_path)
                    print(f"Backup '{selected_backup}' restored to '{restore_path}'.")

        else:
            print("Please choose a valid option.")

    if mode == "4":
        print("Settings:\n 1. Exit Settings\n 2. Set a default RAM amount\n 3. Disable the default server GUI\n 4. Change default port")
        print("Input the number corresponding to your choice.")
        settingsmode = input("> ").strip()

        if settingsmode == "1":
            pass

        elif settingsmode == "2":
            print("Input the amount of RAM to default to. Or 0 to clear it:")
            new_value = input("RAM (in MB or GB): ").strip()
            update_config("default_ram", new_value, label="Default RAM")

        elif settingsmode == "3":
            print("To enable GUI type True, to disable it type False.")
            new_value = input("> ").strip().capitalize()
            update_config(
                "gui_enabled",
                new_value == "True",
                validator=lambda x: x in [True, False],
                label="GUI setting"
            )

        elif settingsmode == "4":
            print("Enter the new default port number (e.g., 25565):")
            new_value = input("Port: ").strip()
            update_config(
                "default_port",
                int(new_value),
                validator=lambda x: isinstance(x, int) and 1 <= x <= 65535,
                label="Default Port"
            )

        else:
            print("Invalid option. Please enter a number from 1 to 4.")
