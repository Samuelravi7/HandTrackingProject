import subprocess

# Paths to the Python scripts
WEBSITE_SCRIPT = "website.py"
MAIN_SCRIPT = "main.py"
HAND_TRACKING_SCRIPT = "handtrackingmodule.py"

def run_scripts():
    # Start all scripts as separate subprocesses
    processes = []
    try:
        print("Starting website.py...")
        website_process = subprocess.Popen(['python', WEBSITE_SCRIPT])
        processes.append(website_process)

        print("Starting main.py...")
        main_process = subprocess.Popen(['python', MAIN_SCRIPT])
        processes.append(main_process)

        print("Starting handtrackingmodule.py...")
        handtracking_process = subprocess.Popen(['python', HAND_TRACKING_SCRIPT])
        processes.append(handtracking_process)

        # Wait for the processes to complete
        for process in processes:
            process.wait()

    except KeyboardInterrupt:
        print("\nTerminating all processes...")
        for process in processes:
            process.terminate()
        print("All processes terminated.")

if __name__ == '__main__':
    run_scripts()
