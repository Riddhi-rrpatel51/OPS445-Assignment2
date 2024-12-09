#!/usr/bin/env python3

import subprocess
import argparse
import sys
import os

def call_du_sub(target_directory):
    """
    Calls the 'du -d 1' command on the target directory and returns a list of strings.
    :param target_directory: Path to the directory.
    :return: List of strings representing du output.
    """
    try:
        process = subprocess.Popen(
            ['du', '-d', '1', target_directory],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            raise RuntimeError(f"Error calling du: {stderr.strip()}")
        return stdout.strip().split('\n')
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

def percent_to_graph(percent, total_chars):
    """
    Converts a percentage into a graphical bar.
    :param percent: Percentage (0-100).
    :param total_chars: Total length of the bar.
    :return: Graphical bar as a string.
    """
    if not (0 <= percent <= 100):
        raise ValueError("Percent must be between 0 and 100.")
    filled_length = round((percent / 100) * total_chars)
    return '=' * filled_length + ' ' * (total_chars - filled_length)

def create_dir_dict(du_output):
    """
    Creates a dictionary from the du output.
    :param du_output: List of strings from 'du -d 1'.
    :return: Dictionary with directory names as keys and sizes in bytes as values.
    """
    dir_dict = {}
    for line in du_output:
        try:
            size, directory = line.split(maxsplit=1)
            dir_dict[directory] = int(size)
        except ValueError:
            continue
    return dir_dict

def parse_command_args():
    """
    Parses command-line arguments.
    :return: Parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="DU Improved -- See Disk Usage Report with bar charts"
    )
    parser.add_argument(
        "target", nargs="?", default=".", help="The directory to scan."
    )
    parser.add_argument(
        "-H", "--human-readable", action="store_true",
        help="Print sizes in human-readable format (e.g., 1K, 23M, 2G)."
    )
    parser.add_argument(
        "-l", "--length", type=int, default=20,
        help="Specify the length of the graph. Default is 20."
    )
    return parser.parse_args()

def get_pid_list():
    """
    Returns a list of PIDs as strings for a given program.
    :return: List of strings representing PIDs.
    """
    result = os.popen('pidof <your_program>').read()
    return result.split()  # List of PIDs as strings

def get_rss_total(pid):
    """
    Retrieves the RSS (memory) usage of a given process by reading the smaps file.
    :param pid: Process ID.
    :return: Total RSS usage in KB.
    """
    try:
        with open(f"/proc/{pid}/smaps", "r") as f:
            total_rss = 0
            for line in f:
                if line.startswith("Rss:"):
                    total_rss += int(line.split()[1])
            return total_rss
    except FileNotFoundError:
        return 0  # If smaps file is not found, return 0

def main():
    args = parse_command_args()
    du_output = call_du_sub(args.target)
    dir_dict = create_dir_dict(du_output)
    
    total_size = sum(dir_dict.values())
    if args.human_readable:
        human_readable = lambda x: (
            f"{x / 1e9:.1f} G" if x >= 1e9 else
            f"{x / 1e6:.1f} M" if x >= 1e6 else
            f"{x / 1e3:.1f} K"
        )
    else:
        human_readable = lambda x: f"{x} B"

    print(f"Total: {human_readable(total_size)}   {args.target}")
    for directory, size in dir_dict.items():
        percent = (size / total_size) * 100 if total_size > 0 else 0
        bar = percent_to_graph(percent, args.length)
        print(f"{percent:>3.0f} % [{bar}] {human_readable(size)} {directory}")

if __name__ == "__main__":
    main()
