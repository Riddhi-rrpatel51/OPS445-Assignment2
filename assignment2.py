import os
import argparse


# Milestone 1: Functions to Implement
def percent_to_graph(percent: float, length: int = 20) -> str:
    """Convert a percentage into a graphical bar."""
    num_hashes = int(percent * length)
    num_spaces = length - num_hashes
    return f"[{'#' * num_hashes}{' ' * num_spaces} | {int(percent * 100)}%]"


def get_sys_mem() -> int:
    """Get the total system memory from /proc/meminfo."""
    with open("/proc/meminfo", "r") as meminfo:
        for line in meminfo:
            if line.startswith("MemTotal"):
                return int(line.split()[1])
    return 0


def get_avail_mem() -> int:
    """Get the available system memory from /proc/meminfo."""
    with open("/proc/meminfo", "r") as meminfo:
        mem_free = 0
        mem_available = 0
        for line in meminfo:
            if line.startswith("MemAvailable"):
                mem_available = int(line.split()[1])
            elif line.startswith("MemFree"):
                mem_free = int(line.split()[1])
        return mem_available or (mem_free * 2)  # Fallback for WSL
    return 0


# Milestone 2: Argument Parsing and Process Memory Functions
def parse_command_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Memory Visualiser -- See Memory Usage Report with bar charts")
    parser.add_argument("-H", "--human-readable", action="store_true", help="Prints sizes in human readable format")
    parser.add_argument("-l", "--length", type=int, default=20, help="Specify the length of the graph. Default is 20.")
    parser.add_argument("program", nargs="?", help="Program name to show memory usage of its processes")
    return parser.parse_args()


def pids_of_prog(program: str) -> list:
    """Get the PIDs of all processes matching a program name using pidof."""
    try:
        pids = os.popen(f"pidof {program}").read().strip()
        return [int(pid) for pid in pids.split()] if pids else []
    except Exception:
        return []


def rss_mem_of_pid(pid: int) -> int:
    """Get the RSS memory of a process from /proc/[pid]/smaps."""
    try:
        rss = 0
        with open(f"/proc/{pid}/smaps", "r") as smaps:
            for line in smaps:
                if line.startswith("Rss:"):
                    rss += int(line.split()[1])
        return rss
    except FileNotFoundError:
        return 0


# Final Submission: Main Integration
def main():
    args = parse_command_args()

    total_mem = get_sys_mem()
    avail_mem = get_avail_mem()
    used_mem = total_mem - avail_mem

    if args.human_readable:
        total_mem_h = f"{total_mem / 1024:.2f} MiB"
        used_mem_h = f"{used_mem / 1024:.2f} MiB"
        print(f"Memory         {percent_to_graph(used_mem / total_mem, args.length)} {used_mem_h}/{total_mem_h}")
    else:
        print(f"Memory         {percent_to_graph(used_mem / total_mem, args.length)} {used_mem}/{total_mem}")

    if args.program:
        pids = pids_of_prog(args.program)
        if not pids:
            print(f"{args.program} not found.")
            return

        for pid in pids:
            rss_mem = rss_mem_of_pid(pid)
            if args.human_readable:
                rss_mem_h = f"{rss_mem / 1024:.2f} MiB"
                print(f"{pid:<15}{percent_to_graph(rss_mem / total_mem, args.length)} {rss_mem_h}/{total_mem_h}")
            else:
                print(f"{pid:<15}{percent_to_graph(rss_mem / total_mem, args.length)} {rss_mem}/{total_mem}")
        
        # Total for program
        total_rss = sum(rss_mem_of_pid(pid) for pid in pids)
        if args.human_readable:
            total_rss_h = f"{total_rss / 1024:.2f} MiB"
            print(f"{args.program:<15}{percent_to_graph(total_rss / total_mem, args.length)} {total_rss_h}/{total_mem_h}")
        else:
            print(f"{args.program:<15}{percent_to_graph(total_rss / total_mem, args.length)} {total_rss}/{total_mem}")


if __name__ == "__main__":
    main()
