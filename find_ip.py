import socket

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # This doesn't actually connect to the internet
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

if __name__ == "__main__":
    ip = get_ip()
    print(f"\nYour computer's IP address is: {ip}")
    print(f"To access the Vinyl Record Scanner from other devices, use: http://{ip}:5000\n") 