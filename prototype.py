import serial
import time

# Setup serial connection (adjust 'COM4' and 115200 to match your setup)
ser = serial.Serial('COM4', 115200, timeout=1)

def main():
    print("Press 'o' to open gate, 'c' to close gate, and 'q' to quit.")
    try:
        while True:
            # Non-blocking wait for user input
            command = input("Enter command: ")

            # Process user input
            if command == 'o':
                print("Sending open gate command...")
                ser.write(b'openGate\n')  # Send command to open the gate
            elif command == 'c':
                print("Sending close gate command...")
                ser.write(b'closeGate\n')  # Send command to close the gate
            elif command == 'q':
                print("Quitting program...")
                break  # Exit the loop to quit
            else:
                print("Invalid command. Please press 'o' to open gate, 'c' to close gate, and 'q' to quit.")
    except KeyboardInterrupt:
        print("Program terminated by user")
    finally:
        ser.close()
        print("Serial connection closed")

if __name__ == '__main__':
    main()
