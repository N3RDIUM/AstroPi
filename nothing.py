import cv2
from picamera2 import Picamera2, Preview

# Initialize the camera
picam2 = Picamera2()

# Create a preview configuration. Adjust resolution as needed.
preview_config = picam2.create_preview_configuration()
picam2.configure(preview_config)
picam2.start()

# Determine frame dimensions from configuration
# (Alternatively, you can specify your intended resolution)
width = preview_config['size'][0]
height = preview_config['size'][1]

# Define the codec and create VideoWriter object.
# 'XVID' is a common codec for .avi files.
fourcc = cv2.VideoWriter_fourcc(*'XVID')
fps = 30  # frames per second; adjust as desired
video_writer = cv2.VideoWriter('output.avi', fourcc, fps, (width, height))

print("Recording... Press 'q' to stop.")

while True:
    # Capture a frame as a numpy array in BGR format
    frame = picam2.capture_array()
    
    # Write the frame to the video file
    video_writer.write(frame)
    
    # Optionally, show the frame in a window
    cv2.imshow('Recording', frame)
    
    # Stop recording if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Clean up
video_writer.release()
picam2.stop()
cv2.destroyAllWindows()
print("Recording stopped and saved to output.avi")

