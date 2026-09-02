# top_ram_processes
This script lists the processes currently running on the system that are consuming the most RAM, sorted from highest to lowest memory usage. It displays the PID, process name, memory usage (in MB) and the percentage of total system RAM each process is using.

Usage:
    python3 4_top_ram_processes.py [--top N]
    Arguments:
        --top N   Number of top processes to display (default: 10).
        
Requirements:
    pip install psutil
