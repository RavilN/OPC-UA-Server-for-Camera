from opcua import Server, ua
import cv2
import numpy as np
import time

def percent_difference(img1, img2):
# Convert to grayscale
    gray1 = cv2.cvtColor(img1,cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(img2,cv2.COLOR_BGR2GRAY)
    
    # Resize to same size (in case of small differences)
    gray2=cv2.resize(gray2, (gray1.shape[1], gray1.shape[0]))
    # Compute absolute difference
    diff = cv2.absdiff(gray1, gray2)
    
    # Normalize and compute percentage of changed pixels
    diff_norm = diff > 30  # pixel intensity threshold (tune if needed)
    change_ratio = np.sum(diff_norm) / diff_norm.size * 100
    return change_ratio

# --- Set up OPC UA Server ---
server = Server()
server.set_endpoint("opc.tcp://0.0.0.0:4840/opcfy/server/")

# Setup namespace
uri = "http://opcfy.io/camera"
idx = server.register_namespace(uri)

# Create a new object to hold camera variables
objects = server.get_objects_node()
camera_obj = objects.add_object(idx, "CameraDevice")

# Add a variable to hold image data (as ByteString)
image_var = camera_obj.add_variable(idx, "CameraImage", b"")
image_var.set_writable()  # Allow server-side updates

# Start the server
server.start()
print("OPC UA server started at opc.tcp://0.0.0.0:4840/opcfy/server/")

# Open camera (use 0 or the index of your camera)
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
if not cap.isOpened():
    print("Failed to open camera")
    exit()

ret, prev_frame = cap.read()
if not ret:
    print("Cannot read initial frame.")
    cap.release()
    exit()

print("Monitoring camera... (press Ctrl+C to stop)")

prev_time=0
interval=0.1  # seconds between camera readings
deadband=3 #If image change is greater than this percent, update the OPC UA image variable.
try:
    while True:        
        # Only process snapshot logic every 'interval' seconds
        current_time=time.time()
        if current_time-prev_time>=interval:
            prev_time=current_time
            ret, frame = cap.read()
            if not ret:
                print("Failed to read frame.")
                break
            diff_percent=percent_difference(prev_frame, frame)
            if diff_percent > deadband:
                
                # For debugging, the image can be displayed in dialog window.:
                # cv2.imshow("Camera Feed", frame)
                
                # Get image in PNG format:
                success, buffer = cv2.imencode('.png', frame)
                if success:
                    img_bytes = buffer.tobytes()  # raw binary data
                    # Update OPC UA variable
                    image_var.set_value(img_bytes, ua.VariantType.ByteString)
                    # For debugging, can be saved in a file from binary data:
                    #with open("snapshot.png", "wb") as f:
                    #    f.write(img_bytes)
        
            prev_frame=frame.copy()

        # Call waitKey with a small delay (1-10 ms) to refresh window and to prevent CPU spinning:
        if cv2.waitKey(1) == 27:
            print("\nExiting, stopped by the user.")
            break
except KeyboardInterrupt:
    print("\nExiting, stopped by the user.")
except:
    print("\nExiting, exception happened.")

cap.release()
cv2.destroyAllWindows()
server.stop()
