import argparse
from typing import List, NamedTuple

import psutil


class ProcessMemoryInfo(NamedTuple):
    """Represents memory usage information for a single process."""
    pid: int
    name: str
    memory_mb: float
    memory_percent: float


def bytes_to_megabytes(value_in_bytes: float) -> float:
    """
    Convert a value in bytes to megabytes, rounded to two decimals.

    Args:
        value_in_bytes: Memory size expressed in bytes.

    Returns:
        The equivalent memory size expressed in megabytes.
    """
    return round(value_in_bytes / (1024 ** 2), 2)


def collect_process_memory_usage() -> List[ProcessMemoryInfo]:
    """
    Iterate over all running processes and collect their memory
    usage information.

    Returns:
        A list of ProcessMemoryInfo entries, one per process that
        could be successfully inspected.
    """
    processes: List[ProcessMemoryInfo] = []

    for process in psutil.process_iter(["pid", "name", "memory_info", "memory_percent"]):
        try:
            info = process.info
            memory_info = info.get("memory_info")

            if memory_info is None:
                continue

            processes.append(
                ProcessMemoryInfo(
                    pid=info["pid"],
                    name=info["name"] or "Unknown",
                    memory_mb=bytes_to_megabytes(memory_info.rss),
                    memory_percent=round(info.get("memory_percent") or 0.0, 2),
                )
            )
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            # Process may have terminated or be inaccessible; skip it.
            continue

    return processes


def get_top_ram_processes(
    processes: List[ProcessMemoryInfo], top_n: int
) -> List[ProcessMemoryInfo]:
    """
    Return the top N processes sorted by RAM usage (descending).

    Args:
        processes: List of process memory information to sort.
        top_n: Number of top processes to return.

    Returns:
        A list containing the top N processes by memory usage.
    """
    sorted_processes = sorted(processes, key=lambda p: p.memory_mb, reverse=True)
    return sorted_processes[:top_n]


def print_report(processes: List[ProcessMemoryInfo]) -> None:
    """
    Print a formatted table showing the given processes and their
    memory usage.

    Args:
        processes: List of processes to display, expected to already
                   be sorted by memory usage.
    """
    if not processes:
        print("No process information could be retrieved.")
        return

    header = f"{'PID':<10}{'PROCESS NAME':<30}{'MEMORY (MB)':<15}{'MEMORY (%)':<12}"
    print(header)
    print("-" * len(header))

    for process in processes:
        print(
            f"{process.pid:<10}"
            f"{process.name:<30}"
            f"{process.memory_mb:<15}"
            f"{process.memory_percent:<12}"
        )


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.

    Returns:
        The parsed arguments namespace.
    """
    parser = argparse.ArgumentParser(
        description="Display the top RAM-consuming processes on the system."
    )
    parser.add_argument(
        "--top",
        type=int,
        default=10,
        help="Number of top processes to display (default: 10).",
    )
    return parser.parse_args()


def main() -> None:
    """Main entry point of the script."""
    args = parse_arguments()

    print(f"Collecting memory usage for all running processes...\n")
    all_processes = collect_process_memory_usage()
    top_processes = get_top_ram_processes(all_processes, args.top)

    print(f"Top {args.top} processes by RAM usage:\n")
    print_report(top_processes)


if __name__ == "__main__":
    main()
