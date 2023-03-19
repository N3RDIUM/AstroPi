import os
import base64
import json
import threading

class Transferrer():
    """
    Transferrer
    This class is used to transfer images from the Pi to the client.
    """
    def __init__(self, conn, transfer_quality=0):
        """
        Initialize the Transferrer object.

        Here, conn is the socket connection to the client.
        Also, transfer_quality is the quality of the image to be transferred,
        where 0 is original quality, and 1 is low quality.
        """
        self.conn = conn
        self.transfer_quality = transfer_quality
        self.running = True
        self.image_queue = []
        self.listen_thread = threading.Thread(target=self.listen)
        self.listen_thread.start()
        
    def start(self) -> None:
        """
        Start listening for images to transfer.
        """
        while self.running:
            # Get the image
            image = self.get_image()
            
            if image is not None:
                # Send the image
                with open(image, "rb") as image_file:
                    image_encoded = base64.b64encode(image_file.read()).decode("utf-8")
                    self.conn.send(json.dumps({
                        "type": "b64",
                        "data": image_encoded,
                        "path": image,
                    }).encode("utf-8"))
                    # Now that we've sent the image, delete it
                    os.remove(image)
    
    def get_image(self) -> str:
        """
        Get the image to transfer.
        """
        if len(self.image_queue) > 0:
            return self.image_queue.pop(0)
        return None
    
    def listen(self,) -> None:
        """
        Listen for images to transfer.
        """
        while True:
            files = os.listdir()
            for file in files:
                if file.startswith("capture_") and file.split(".") in ["jpg", "jpeg", "png", "dng"] and file not in self.image_queue:
                    self.image_queue.append(file)
                
    def stop(self) -> None:
        self.running = False