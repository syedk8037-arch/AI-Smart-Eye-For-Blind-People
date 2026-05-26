import bluetooth
import os
import json

# Directory where known faces are stored
FACE_DIR = "/home/project/projecteye/known_faces"

# Ensure directory exists
os.makedirs(FACE_DIR, exist_ok=True)

def list_faces():
    """List all faces in the known_faces directory."""
    faces = []
    for person in os.listdir(FACE_DIR):
        person_path = os.path.join(FACE_DIR, person)
        if os.path.isdir(person_path):
            images = [f for f in os.listdir(person_path) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
            faces.append({"name": person, "images": images})
    return faces


def save_face(name, image_bytes):
    """Save an image for a given face name."""
    person_dir = os.path.join(FACE_DIR, name)
    os.makedirs(person_dir, exist_ok=True)
    image_path = os.path.join(person_dir, f"{int(time.time())}.jpg")
    with open(image_path, "wb") as f:
        f.write(image_bytes)
    print(f"✅ Saved face image: {image_path}")


def delete_face(name):
    """Delete a person's face folder."""
    person_dir = os.path.join(FACE_DIR, name)
    if os.path.exists(person_dir):
        os.system(f"rm -rf '{person_dir}'")
        print(f"🗑️ Deleted face: {name}")
        return True
    return False


def handle_request(data):
    """Process incoming Bluetooth requests."""
    try:
        request = json.loads(data)
        command = request.get("command")

        if command == "list":
            faces = list_faces()
            return json.dumps({"status": "ok", "faces": faces})

        elif command == "delete":
            name = request.get("name")
            if name and delete_face(name):
                return json.dumps({"status": "ok", "message": f"Deleted {name}"})
            else:
                return json.dumps({"status": "error", "message": "Face not found"})

        elif command == "add":
            name = request.get("name")
            image_data = request.get("image_data")
            if name and image_data:
                import base64
                image_bytes = base64.b64decode(image_data)
                save_face(name, image_bytes)
                return json.dumps({"status": "ok", "message": f"Added {name}"})
            else:
                return json.dumps({"status": "error", "message": "Invalid add request"})

        else:
            return json.dumps({"status": "error", "message": "Unknown command"})

    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


# ---------- BLUETOOTH SERVER ----------
server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
server_sock.bind(("", bluetooth.PORT_ANY))
server_sock.listen(1)

port = server_sock.getsockname()[1]
bluetooth.advertise_service(server_sock, "FaceSyncServer",
                            service_classes=[bluetooth.SERIAL_PORT_CLASS],
                            profiles=[bluetooth.SERIAL_PORT_PROFILE])

print(f"📡 Waiting for Bluetooth connection on RFCOMM channel {port}...")

client_sock, client_info = server_sock.accept()
print(f"✅ Connected to {client_info}")

try:
    while True:
        data = client_sock.recv(4096).decode("utf-8")
        if not data:
            break

        print(f"📩 Received: {data}")
        response = handle_request(data)
        client_sock.send(response.encode("utf-8"))
        print(f"📤 Sent: {response}")

except Exception as e:
    print(f"❌ Error: {e}")

finally:
    client_sock.close()
    server_sock.close()
    print("🔌 Connection closed")
