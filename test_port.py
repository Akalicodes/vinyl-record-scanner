import socket
import sys

def test_port(port=5000):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = False
    try:
        sock.bind(("0.0.0.0", port))
        result = True
    except:
        result = False
    finally:
        sock.close()
    return result

if __name__ == "__main__":
    port = 5000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except:
            print(f"Invalid port number: {sys.argv[1]}")
            sys.exit(1)
    
    if test_port(port):
        print(f"Port {port} is available and can be used.")
    else:
        print(f"Port {port} is already in use or blocked by firewall.")
        print("Try using a different port by running: python app.py --port 8080") 