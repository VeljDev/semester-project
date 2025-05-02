import json
import platform
import subprocess
import sys

# Recupera le applicazioni installate su Windows
def get_installed_apps_windows():
    print("Starting Windows application scan using PowerShell (JSON mode)...")

    apps = []

    try:
        # Comando PowerShell per leggere app installate e convertirle in JSON
        cmd = [
            "powershell",
            "-Command",
            "Get-ItemProperty HKLM:\\Software\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*,"
            "HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\* | "
            "Select-Object DisplayName, DisplayVersion, Publisher, InstallLocation | "
            "ConvertTo-Json -Compress"
        ]

        # Esegue il comando e decodifica l'output in UTF-8, ignorando errori strani
        output = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode('utf-8', errors='ignore')
        data = json.loads(output)  # Converte l'output JSON in oggetti Python

        # Se c'è un solo elemento, lo mettiamo comunque in lista
        if isinstance(data, dict):
            data = [data]

        # Cicla ogni applicazione trovata
        for app in data:
            name = app.get('DisplayName', '') or ''
            version = app.get('DisplayVersion', '') or ''
            vendor = app.get('Publisher', '') or ''
            install_path = app.get('InstallLocation', '') or ''

            # Salva solo le app che hanno un nome valido
            if name:
                apps.append({
                    "name": name,
                    "version": version,
                    "vendor": vendor,
                    "install_path": install_path
                })

        print(f"Found {len(apps)} applications on Windows.")

    except Exception as e:
        # In caso di errori stampa il messaggio
        print(f"Error scanning Windows applications: {e}")

    return apps

# Recupera le applicazioni installate su Linux
def get_installed_apps_linux():
    print("Starting Linux application scan...")
    apps = []
    try:
        # Prima prova: sistemi basati su Debian/Ubuntu usano dpkg
        output = subprocess.check_output(['dpkg', '-l'], stderr=subprocess.DEVNULL)
        lines = output.decode('utf-8', errors='ignore').split('\n')[5:]  # Salta le prime righe di intestazione
        for line in lines:
            parts = line.split()
            if len(parts) >= 3:
                name = parts[1]
                version = parts[2]
                apps.append({
                    "name": name,
                    "version": version,
                    "vendor": "",
                    "install_path": ""
                })
        print(f"Found {len(apps)} applications on Linux (dpkg).")
    except Exception:
        try:
            # Se dpkg fallisce, prova con rpm (Fedora, RedHat, CentOS)
            output = subprocess.check_output(['rpm', '-qa', '--qf', '%{NAME} %{VERSION}\n'], stderr=subprocess.DEVNULL)
            lines = output.decode('utf-8', errors='ignore').split('\n')
            for line in lines:
                parts = line.strip().split()
                if len(parts) >= 2:
                    name = parts[0]
                    version = parts[1]
                    apps.append({
                        "name": name,
                        "version": version,
                        "vendor": "",
                        "install_path": ""
                    })
            print(f"Found {len(apps)} applications on Linux (rpm).")
        except Exception as e:
            # Se fallisce anche rpm, stampa errore
            print(f"Error scanning Linux applications: {e}")
    return apps

# Recupera le applicazioni installate su macOS
def get_installed_apps_mac():
    print("Starting macOS application scan...")
    apps = []
    try:
        # Usa system_profiler per ottenere dati applicazioni e li converte da JSON
        output = subprocess.check_output(['system_profiler', 'SPApplicationsDataType', '-json'], stderr=subprocess.DEVNULL)
        data = json.loads(output)
        applications = data.get('SPApplicationsDataType', [])

        for app in applications:
            name = app.get('_name', '')
            version = app.get('version', '')
            path = app.get('path', '')
            apps.append({
                "name": name,
                "version": version,
                "vendor": "",
                "install_path": path
            })
        print(f"Found {len(apps)} applications on macOS.")
    except Exception as e:
        print(f"Error scanning macOS applications: {e}")
    return apps

# Recupera informazioni sul sistema operativo
def get_os_info():
    return {
        "os_name": platform.system(),
        "os_version": platform.version()
    }

# Salva i dati raccolti in un file JSON
def save_to_json(apps, filename='installed_apps.json'):
    print("Saving scan results to JSON file...")
    data = {
        "system_info": get_os_info(),
        "applications": apps
    }
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"File '{filename}' successfully created!")

# Decide quale metodo usare in base al sistema operativo
def main():
    system_platform = platform.system()
    installed_apps = []

    if system_platform == "Windows":
        installed_apps = get_installed_apps_windows()
    elif system_platform == "Linux":
        installed_apps = get_installed_apps_linux()
    elif system_platform == "Darwin":
        installed_apps = get_installed_apps_mac()
    else:
        print("Unsupported operating system for application scan.")
        sys.exit(1)

    save_to_json(installed_apps)
    print("Scan completed. JSON file is ready.")

if __name__ == "__main__":
    main()
