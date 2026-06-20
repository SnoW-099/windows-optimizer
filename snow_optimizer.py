from __future__ import annotations

import ctypes
import datetime as dt
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path


APP_NAME = "Snow Windows Flow"
AUTHOR = "By snow"
APP_DIR = Path(__file__).resolve().parent
LOG_DIR = APP_DIR / "logs"


class C:
    RESET = "\033[0m"
    DIM = "\033[2m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    WHITE = "\033[97m"
    GRAY = "\033[90m"


@dataclass
class MenuItem:
    key: str
    label: str
    action: callable


@dataclass
class Recommendation:
    title: str
    status: str
    detail: str
    action: str
    priority: str = "INFO"


def enable_ansi() -> None:
    if os.name != "nt":
        return
    kernel32 = ctypes.windll.kernel32
    handle = kernel32.GetStdHandle(-11)
    mode = ctypes.c_uint32()
    if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
        kernel32.SetConsoleMode(handle, mode.value | 0x0004)


def is_admin() -> bool:
    if os.name != "nt":
        return False
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def clear() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def line(text: str = "", color: str = C.WHITE) -> None:
    print(f"{color}{text}{C.RESET}")


def pause() -> None:
    input(f"\n{C.GRAY}Press Enter to continue...{C.RESET}")


def confirm(message: str) -> bool:
    answer = input(f"{C.YELLOW}{message} (S/N): {C.RESET}").strip().lower()
    return answer == "s"


def run(command: list[str] | str, shell: bool = False) -> subprocess.CompletedProcess:
    return subprocess.run(command, shell=shell, text=True, capture_output=True)


def log_event(message: str) -> None:
    LOG_DIR.mkdir(exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_file = LOG_DIR / f"snow-{dt.datetime.now():%Y-%m-%d}.log"
    with log_file.open("a", encoding="utf-8") as file:
        file.write(f"[{stamp}] {message}\n")


def powershell(command: str) -> subprocess.CompletedProcess:
    return run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command])


def open_process(target: str) -> None:
    if os.name == "nt":
        os.startfile(target)  # type: ignore[attr-defined]
    else:
        subprocess.Popen(["xdg-open", target])


def format_bytes(value: int | float) -> str:
    value = float(value)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if value < 1024 or unit == "TB":
            return f"{value:.2f} {unit}" if unit != "B" else f"{value:.0f} B"
        value /= 1024
    return f"{value:.2f} TB"


def folder_size(path: Path) -> int:
    total = 0
    if not path.exists():
        return total
    for root, _, files in os.walk(path, topdown=True, onerror=lambda _: None):
        for file_name in files:
            try:
                total += (Path(root) / file_name).stat().st_size
            except OSError:
                pass
    return total


def remove_folder_contents(path: Path) -> int:
    removed = 0
    if not path.exists():
        return removed
    for item in path.iterdir():
        try:
            if item.is_dir():
                shutil.rmtree(item, ignore_errors=False)
            else:
                item.unlink()
            removed += 1
        except OSError:
            pass
    return removed


def get_startup_count() -> int:
    ps = (
        "$paths='HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Run',"
        "'HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Run';"
        "$count=0; foreach($p in $paths){ if(Test-Path $p){"
        "$props=(Get-ItemProperty $p).PSObject.Properties | Where-Object {$_.Name -notmatch '^PS'};"
        "$count += @($props).Count }}; Write-Output $count"
    )
    result = powershell(ps)
    try:
        return int((result.stdout or "0").strip())
    except ValueError:
        return 0


def get_ram_usage() -> tuple[int, int, float] | None:
    ps = (
        "$os=Get-CimInstance Win32_OperatingSystem;"
        "$total=[int64]$os.TotalVisibleMemorySize*1KB;"
        "$free=[int64]$os.FreePhysicalMemory*1KB;"
        "$used=$total-$free;"
        "$pct=[math]::Round(($used/$total)*100,1);"
        "Write-Output \"$used|$total|$pct\""
    )
    result = powershell(ps)
    parts = (result.stdout or "").strip().split("|")
    if len(parts) != 3:
        return None
    try:
        return int(parts[0]), int(parts[1]), float(parts[2])
    except ValueError:
        return None


def get_active_power_plan() -> str:
    result = run(["powercfg", "/getactivescheme"])
    text = (result.stdout or result.stderr or "").strip()
    match = re.search(r"\((.*?)\)", text)
    return match.group(1) if match else text or "Unknown"


def is_game_mode_enabled() -> bool | None:
    ps = (
        "$path='HKCU:\\Software\\Microsoft\\GameBar';"
        "if(Test-Path $path){"
        "$value=(Get-ItemProperty -Path $path -Name AllowAutoGameMode -ErrorAction SilentlyContinue).AllowAutoGameMode;"
        "if($null -eq $value){ 'unknown' } else { $value }"
        "} else { 'unknown' }"
    )
    result = powershell(ps)
    value = (result.stdout or "").strip().lower()
    if value in {"1", "true"}:
        return True
    if value in {"0", "false"}:
        return False
    return None


def collect_recommendations() -> list[Recommendation]:
    recommendations: list[Recommendation] = []

    temp_targets = [
        Path(tempfile.gettempdir()),
        Path(os.environ.get("SystemRoot", "C:\\Windows")) / "Temp",
    ]
    temp_size = sum(folder_size(path) for path in temp_targets)
    if temp_size >= 1 * 1024**3:
        recommendations.append(Recommendation("Temporary files", "Worth optimizing", f"{format_bytes(temp_size)} detected.", "Run Clean temporary files or Quick optimize.", "HIGH"))
    elif temp_size >= 250 * 1024**2:
        recommendations.append(Recommendation("Temporary files", "Optional", f"{format_bytes(temp_size)} detected.", "Clean them if you want quick space back.", "MED"))
    else:
        recommendations.append(Recommendation("Temporary files", "Looks good", f"Only {format_bytes(temp_size)} detected.", "No cleanup needed right now.", "OK"))

    for drive in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        root = Path(f"{drive}:\\")
        if root.exists():
            usage = shutil.disk_usage(root)
            free_pct = round((usage.free / usage.total) * 100, 1)
            if free_pct < 10:
                recommendations.append(Recommendation(f"Disk {drive}:", "Needs attention", f"{format_bytes(usage.free)} free ({free_pct}%).", "Free space soon; Windows can slow down with low disk space.", "HIGH"))
            elif free_pct < 20:
                recommendations.append(Recommendation(f"Disk {drive}:", "Watch it", f"{format_bytes(usage.free)} free ({free_pct}%).", "Run cleanup and review large files.", "MED"))
            else:
                recommendations.append(Recommendation(f"Disk {drive}:", "Looks good", f"{format_bytes(usage.free)} free ({free_pct}%).", "No disk action needed.", "OK"))

    ram = get_ram_usage()
    if ram:
        used, total, pct = ram
        if pct >= 85:
            recommendations.append(Recommendation("Memory", "Heavy usage", f"{format_bytes(used)} / {format_bytes(total)} used ({pct}%).", "Check Top processes and close heavy apps.", "HIGH"))
        elif pct >= 70:
            recommendations.append(Recommendation("Memory", "Moderate usage", f"{format_bytes(used)} / {format_bytes(total)} used ({pct}%).", "Top processes can show what is eating RAM.", "MED"))
        else:
            recommendations.append(Recommendation("Memory", "Looks good", f"{format_bytes(used)} / {format_bytes(total)} used ({pct}%).", "No RAM action needed.", "OK"))

    startup_count = get_startup_count()
    if startup_count >= 10:
        recommendations.append(Recommendation("Startup apps", "Worth reviewing", f"{startup_count} startup entries detected.", "Open Startup items and disable what you do not use.", "HIGH"))
    elif startup_count >= 5:
        recommendations.append(Recommendation("Startup apps", "Could improve boot", f"{startup_count} startup entries detected.", "Review startup apps if boot feels slow.", "MED"))
    else:
        recommendations.append(Recommendation("Startup apps", "Looks clean", f"{startup_count} startup entries detected.", "No startup action needed.", "OK"))

    power_plan = get_active_power_plan()
    if "high performance" in power_plan.lower() or "alto rendimiento" in power_plan.lower():
        recommendations.append(Recommendation("Power plan", "Performance ready", power_plan, "Gaming Boost is mostly already covered.", "OK"))
    else:
        recommendations.append(Recommendation("Power plan", "Can optimize for gaming", power_plan, "Use Gaming Boost when you want max performance.", "MED"))

    game_mode = is_game_mode_enabled()
    if game_mode is True:
        recommendations.append(Recommendation("Game Mode", "Enabled", "Windows Game Mode appears active.", "No action needed.", "OK"))
    elif game_mode is False:
        recommendations.append(Recommendation("Game Mode", "Disabled", "Windows Game Mode appears disabled.", "Open Gaming Boost or Windows gaming settings.", "MED"))
    else:
        recommendations.append(Recommendation("Game Mode", "Unknown", "Could not read Game Mode state.", "Open Windows gaming settings to verify.", "INFO"))

    if is_admin():
        recommendations.append(Recommendation("Admin mode", "Enabled", "Advanced operations are available.", "You can create restore points and run deeper cleanup.", "OK"))
    else:
        recommendations.append(Recommendation("Admin mode", "Standard user", "Some optimizations are limited.", "Use the Admin launcher for restore points and protected cleanup.", "INFO"))

    return recommendations


def show_recommendation(item: Recommendation) -> None:
    colors = {
        "HIGH": C.RED,
        "MED": C.YELLOW,
        "OK": C.GREEN,
        "INFO": C.CYAN,
    }
    color = colors.get(item.priority, C.WHITE)
    line(f"[{item.priority}] {item.title}: {item.status}", color)
    line(f"      {item.detail}", C.GRAY)
    line(f"      -> {item.action}", C.WHITE)


def analyze_pc() -> None:
    header()
    line("PC Analyzer\n", C.WHITE)
    line("Scanning current settings and looking for optimizations that make sense...\n", C.GRAY)

    recommendations = collect_recommendations()
    for item in recommendations:
        show_recommendation(item)
        line()

    high = sum(1 for item in recommendations if item.priority == "HIGH")
    med = sum(1 for item in recommendations if item.priority == "MED")
    ok = sum(1 for item in recommendations if item.priority == "OK")
    log_event(f"Analyze PC completed: {high} high, {med} medium, {ok} ok recommendations")

    line("Summary", C.WHITE)
    if high:
        line(f"{high} important optimization(s) found. Start with the HIGH items.", C.RED)
    elif med:
        line(f"{med} optional optimization(s) found. Your PC is mostly fine.", C.YELLOW)
    else:
        line("Everything important looks good right now.", C.GREEN)
    line(f"Log saved in: {LOG_DIR}", C.GRAY)
    pause()


def header() -> None:
    clear()
    art = [
        "   _________                         ________",
        "  /   _____/ ____   ______  _  __   \\_____  \\",
        "  \\_____  \\ /    \\ /  _ \\ \\/ \\/ /    /  / \\  \\",
        "  /        \\   |  (  <_> )     /    /   \\_/.  \\",
        " /_______  /___|  /\\____/ \\/\\_/     \\_____\\ \\_/",
        "         \\/     \\/                         \\__>",
    ]
    for row in art:
        line(row, C.CYAN)
    line(f"\n  {APP_NAME} - {AUTHOR}", C.WHITE)
    line("  Python terminal optimizer for Windows", C.GRAY)
    line("  codex-code / claude-code terminal flow", C.GRAY)
    line("  " + "-" * 52, C.GRAY)
    line(f"  Mode: {'Administrator' if is_admin() else 'Standard user'}", C.GREEN if is_admin() else C.YELLOW)
    line()


def system_snapshot() -> None:
    header()
    line("System Snapshot\n", C.WHITE)
    line(f"OS      : {platform.platform()}", C.GRAY)
    line(f"Machine : {platform.machine()}", C.GRAY)
    line(f"CPU     : {platform.processor() or 'Unknown'}", C.GRAY)

    if os.name == "nt":
        ps = (
            "Get-CimInstance Win32_OperatingSystem | "
            "Select-Object Caption,Version,TotalVisibleMemorySize,FreePhysicalMemory,LastBootUpTime | "
            "Format-List"
        )
        result = run(["powershell", "-NoProfile", "-Command", ps])
        if result.stdout:
            line("\nWindows details", C.CYAN)
            print(result.stdout.strip())

        line("\nDisk usage", C.CYAN)
        for drive in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            root = Path(f"{drive}:\\")
            if root.exists():
                usage = shutil.disk_usage(root)
                used_pct = round((usage.used / usage.total) * 100, 1)
                line(
                    f"{drive}:  {format_bytes(usage.free)} free / {format_bytes(usage.total)} total ({used_pct}% used)",
                    C.GRAY,
                )

    pause()


def clean_temporary_files() -> None:
    header()
    line("Temporary File Cleaner\n", C.WHITE)
    targets = [
        ("User temp", Path(tempfile.gettempdir())),
        ("Windows temp", Path(os.environ.get("SystemRoot", "C:\\Windows")) / "Temp"),
    ]
    total = 0
    for name, path in targets:
        size = folder_size(path)
        total += size
        line(f"{name}: {path} -> {format_bytes(size)}", C.GRAY)

    line(f"\nEstimated cleanup: {format_bytes(total)}", C.YELLOW)
    if not confirm("Delete unlocked temporary files now?"):
        line("Cancelled.", C.YELLOW)
        pause()
        return

    for name, path in targets:
        count = remove_folder_contents(path)
        line(f"Cleaned {name}: {count} top-level items removed", C.GREEN)
        log_event(f"Cleaned {name}: {count} top-level items removed from {path}")
    pause()


def empty_recycle_bin() -> None:
    header()
    line("Recycle Bin Cleaner\n", C.WHITE)
    if not confirm("Empty recycle bin?"):
        line("Cancelled.", C.YELLOW)
        pause()
        return

    result = run(["powershell", "-NoProfile", "-Command", "Clear-RecycleBin -Force"])
    if result.returncode == 0:
        line("Recycle bin emptied.", C.GREEN)
        log_event("Recycle bin emptied")
    else:
        line("Could not empty recycle bin. Try running as administrator.", C.RED)
        log_event("Recycle bin cleanup failed")
    pause()


def network_refresh() -> None:
    header()
    line("Network Refresh\n", C.WHITE)
    line("Flushes DNS cache and renews local network settings.", C.GRAY)
    if not confirm("Run network refresh?"):
        line("Cancelled.", C.YELLOW)
        pause()
        return

    for command in (["ipconfig", "/flushdns"], ["ipconfig", "/release"], ["ipconfig", "/renew"]):
        completed = run(command)
        print(completed.stdout)
        if completed.stderr:
            line(completed.stderr.strip(), C.YELLOW)
    line("Network refresh finished.", C.GREEN)
    log_event("Network refresh completed")
    pause()


def top_processes() -> None:
    header()
    line("Top Processes\n", C.WHITE)
    ps = (
        "Get-Process | Sort-Object WorkingSet64 -Descending | "
        "Select-Object -First 10 Name,Id,@{Name='RAM_MB';Expression={[math]::Round($_.WorkingSet64/1MB,1)}} | "
        "Format-Table -AutoSize"
    )
    result = run(["powershell", "-NoProfile", "-Command", ps])
    print(result.stdout or "No process data available.")
    pause()


def startup_items() -> None:
    header()
    line("Startup Items\n", C.WHITE)
    ps = (
        "$paths='HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Run',"
        "'HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Run';"
        "foreach($p in $paths){Write-Host $p; if(Test-Path $p){"
        "Get-ItemProperty $p | Select-Object * -ExcludeProperty PS* | Format-List}else{Write-Host 'No entries.'}; Write-Host ''}"
    )
    result = run(["powershell", "-NoProfile", "-Command", ps])
    print(result.stdout or "No startup data available.")
    pause()


def create_restore_point() -> None:
    header()
    line("Restore Point\n", C.WHITE)
    if not is_admin():
        line("Run as administrator to create restore points.", C.YELLOW)
        pause()
        return

    if not confirm("Create restore point named SnowOptimizer?"):
        line("Cancelled.", C.YELLOW)
        pause()
        return

    command = "Checkpoint-Computer -Description 'SnowOptimizer' -RestorePointType 'MODIFY_SETTINGS'"
    result = run(["powershell", "-NoProfile", "-Command", command])
    if result.returncode == 0:
        line("Restore point created.", C.GREEN)
        log_event("Restore point created: SnowOptimizer")
    else:
        line("Could not create restore point. System Protection may be disabled.", C.RED)
        log_event("Restore point creation failed")
        if result.stderr:
            line(result.stderr.strip(), C.GRAY)
    pause()


def windows_tools() -> None:
    while True:
        header()
        line("Windows Tools\n", C.WHITE)
        line("[1] Task Manager", C.CYAN)
        line("[2] Startup Apps", C.CYAN)
        line("[3] Disk Cleanup", C.CYAN)
        line("[4] Storage Settings", C.CYAN)
        line("[5] System Protection", C.CYAN)
        line("[0] Back", C.GRAY)
        choice = input(f"\n{C.CYAN}snow tools>{C.RESET} ").strip()
        tools = {
            "1": "taskmgr",
            "2": "ms-settings:startupapps",
            "3": "cleanmgr",
            "4": "ms-settings:storagesense",
            "5": "SystemPropertiesProtection.exe",
        }
        if choice == "0":
            return
        target = tools.get(choice)
        if target:
            try:
                open_process(target)
            except OSError:
                run(["cmd", "/c", "start", "", target])


def quick_optimize() -> None:
    header()
    line("Quick Optimize\n", C.WHITE)
    line("Flow: temp cleanup, recycle bin, DNS cache, optional restore point.", C.GRAY)
    if not confirm("Start quick optimize?"):
        line("Cancelled.", C.YELLOW)
        pause()
        return

    if is_admin():
        run(["powershell", "-NoProfile", "-Command", "Checkpoint-Computer -Description 'SnowOptimizer Quick Optimize' -RestorePointType 'MODIFY_SETTINGS'"])

    remove_folder_contents(Path(tempfile.gettempdir()))
    remove_folder_contents(Path(os.environ.get("SystemRoot", "C:\\Windows")) / "Temp")
    run(["powershell", "-NoProfile", "-Command", "Clear-RecycleBin -Force"])
    run(["ipconfig", "/flushdns"])
    line("Quick optimize finished.", C.GREEN)
    log_event("Quick optimize completed")
    pause()


def gaming_boost() -> None:
    header()
    line("Gaming Boost\n", C.WHITE)
    line("Sets High Performance power plan and opens Game Mode settings.", C.GRAY)
    if not confirm("Activate Gaming Boost?"):
        line("Cancelled.", C.YELLOW)
        pause()
        return

    run(["powercfg", "/setactive", "SCHEME_MIN"])
    try:
        open_process("ms-settings:gaming-gamemode")
    except OSError:
        pass
    line("Gaming Boost applied. Check Game Mode settings window.", C.GREEN)
    log_event("Gaming Boost applied")
    pause()


def main_menu() -> None:
    items = [
        MenuItem("1", "Analyze PC recommendations", analyze_pc),
        MenuItem("2", "System snapshot", system_snapshot),
        MenuItem("3", "Quick optimize", quick_optimize),
        MenuItem("4", "Clean temporary files", clean_temporary_files),
        MenuItem("5", "Empty recycle bin", empty_recycle_bin),
        MenuItem("6", "Network refresh", network_refresh),
        MenuItem("7", "Top processes", top_processes),
        MenuItem("8", "Startup items", startup_items),
        MenuItem("9", "Create restore point", create_restore_point),
        MenuItem("10", "Open Windows tools", windows_tools),
        MenuItem("11", "Gaming Boost", gaming_boost),
    ]
    while True:
        header()
        line("Command palette", C.WHITE)
        line("Pick an action. Nothing risky runs without confirmation.\n", C.GRAY)
        for item in items:
            line(f"[{item.key}] {item.label}", C.CYAN)
        line("[0] Exit", C.GRAY)
        choice = input(f"\n{C.CYAN}snow>{C.RESET} ").strip()
        if choice == "0":
            line("Bye. Stay clean.", C.GRAY)
            time.sleep(0.5)
            return
        match = next((item for item in items if item.key == choice), None)
        if match:
            match.action()
        else:
            line("Invalid option.", C.YELLOW)
            time.sleep(0.7)


if __name__ == "__main__":
    enable_ansi()
    if os.name != "nt":
        line("Snow Windows Flow is designed for Windows.", C.YELLOW)
    main_menu()
