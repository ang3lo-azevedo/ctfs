import subprocess

# Define the command to start peepdf in interactive mode
peepdf_command = ["peepdf", "-i", "chall.pdf"]

# Open the output file containing commands
with open("output.txt", "r") as file:
    commands = file.readlines()

# Start the peepdf process in interactive mode
process = subprocess.Popen(peepdf_command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

try:
    # Send each command from the file to the interactive session
    for command in commands:
        command = command.strip()  # Remove any extra whitespace or newline characters
        print(f"Running: {command}")
        process.stdin.write(command + "\n")  # Send the command to the interactive shell
        process.stdin.flush()  # Ensure the command is sent immediately
        # Optionally, capture and display output
        output = process.stdout.readline()
        print(output.strip())  # Print the response from the interactive shell
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    # Close the interactive session
    process.stdin.write("exit\n")  # Ensure you exit peepdf cleanly
    process.stdin.flush()
    process.terminate()