
import cv2 as cv
from deepface import DeepFace
import os
import shutil
import json
# Define the folder paths
folders_to_create = ["./imageMedia", "./videoMedia", "./media"]

# Function to create folders
def create_folders(folder_paths):
    for folder_path in folder_paths:
        if not os.path.exists(folder_path):
            try:
                os.makedirs(folder_path)
                print(f"Folder '{folder_path}' created successfully.")
            except OSError as e:
                print(f"Error: Failed to create folder '{folder_path}': {e}")
        else:
            print(f"Folder '{folder_path}' already exists.")

# Create the folders
create_folders(folders_to_create)

# Path to the imageMedia folder
imagemedia_folder_path = "./imageMedia/"

# Path to the videoMedia folder
video_media_folder_path = "./videoMedia/"

# Get the list of image files in the imageMedia folder
image_files = os.listdir(imagemedia_folder_path)

# Check if there are any image files
if not image_files:
    print("Error: No image files found in the 'imageMedia' folder.")
    exit(1)

# Select the first image file as the source image
source_image_filename = image_files[0]
source_image_path = os.path.join(imagemedia_folder_path, source_image_filename)

# Load the source image
source_image = cv.imread(source_image_path)

# Get the list of video files in the videoMedia folder
video_files = os.listdir(video_media_folder_path)

# Check if there are any video files
if not video_files:
    print("Error: No video files found in the 'videoMedia' folder.")
    exit(1)

# Select the first video file as the source video
video_filename = video_files[0]
video_path = os.path.join(video_media_folder_path, video_filename)

# Path to the output folder
output_folder_path = "./media/"

# Clear the 'media' folder before starting frame extraction
shutil.rmtree(output_folder_path, ignore_errors=True)
os.makedirs(output_folder_path, exist_ok=True)

# Initialize the video capture
cap = cv.VideoCapture(video_path)

# Get the frames per second (fps) of the video
fps = cap.get(cv.CAP_PROP_FPS)

# Initialize face detector
face_cascade = cv.CascadeClassifier(cv.data.haarcascades + 'haarcascade_frontalface_default.xml')

result_frames = []

frame_count = 0
while cap.isOpened():
    # Read a frame from the video
    ret, frame = cap.read()
    if not ret:
        break
    
    frame_count += 1

    # Calculate the timestamp of the current frame

    # Assuming timestamp is in seconds
    timestamp = frame_count / fps
    # Assuming timestamp is in seconds
    # timestamp_seconds = frame_count / fps

    # # Calculate hours, minutes, and seconds
    # hours = int(timestamp_seconds // 3600)
    # minutes = int((timestamp_seconds % 3600) // 60)
    # seconds = int(timestamp_seconds % 60)

    # # Format the time as hours:minutes:seconds
    # formatted_timestamp = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    # # Formated_timestamp=100
    # print(formatted_timestamp)




    # Check if it's the 60th frame
    if frame_count % 60 != 0:
        continue
    
    # Convert the frame to grayscale for face detection
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

    # Detect faces in the frame
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4)

    # Check if any face is detected
    if len(faces) > 0:
        # Extract face embeddings using DeepFace
        for (x, y, w, h) in faces:
            # Crop the face region
            face = frame[y:y+h, x:x+w]

            try:
                # Perform face recognition using DeepFace with enforce_detection=True
                result = DeepFace.verify(face, source_image, enforce_detection=True)
                
                # Check if the face is verified
                if result['verified']:
                    # Draw a rectangle around the face
                    cv.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    
                    # Label the face as "Face Match"
                    cv.putText(frame, 'Face Match', (x, y-10), cv.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                    
                    # Save the frame with the detected face and timestamp
                    output_filename = f"matched_frame_{frame_count}_timestamp_{timestamp:.2f}.jpg"
                    output_path = os.path.join(output_folder_path, output_filename)
                    cv.imwrite(output_path, frame)
                    
                    # Add filename and timestamp to result_frames list
                    result_frames.append({"filename": output_filename, "timestamp": timestamp})
                else:
                    # Label the face as "No Match"
                    cv.putText(frame, 'No Match', (x, y-10), cv.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
            except ValueError as e:
                # Handle face detection failure gracefully
                print(f"Error: {e}")
                continue

# Release the video capture
cap.release()

# Print completion message
print("The script has completed execution.")

# Output the result frames list as JSON
with open('result_frames.json', 'w') as f:
    json.dump(result_frames, f)
