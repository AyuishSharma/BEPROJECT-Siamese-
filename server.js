const express = require('express');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const { exec } = require('child_process');

const app = express();

// Set storage engine for multer for images
const imageStorage = multer.diskStorage({
    destination: function (req, file, cb) {
        cb(null, 'imageMedia/');
    },
    filename: function (req, file, cb) {
        cb(null, file.originalname);
    }
});

// Set storage engine for multer for videos
const videoStorage = multer.diskStorage({
    destination: function (req, file, cb) {
        cb(null, 'videoMedia/');
    },
    filename: function (req, file, cb) {
        cb(null, file.originalname);
    }
});

// Initialize multer upload for images
const uploadImage = multer({
    storage: imageStorage
}).single('image');

// Initialize multer upload for videos
const uploadVideo = multer({
    storage: videoStorage
}).single('video');

// Serve index.html for the root URL ("/")
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

// Handle POST request to /upload-image for uploading an image
app.post('/upload-image', (req, res) => {
    deleteFiles('imageMedia', () => {
        uploadImage(req, res, (err) => {
            if (err) {
                console.error('Error uploading image:', err);
                return res.status(500).send('Error uploading image');
            }
            console.log('Image uploaded successfully');
            res.send('Image uploaded successfully');
        });
    });
});

// Handle POST request to /upload-video for uploading a video
app.post('/upload-video', (req, res) => {
    deleteFiles('videoMedia', () => {
        uploadVideo(req, res, (err) => {
            if (err) {
                console.error('Error uploading video:', err);
                return res.status(500).send('Error uploading video');
            }
            console.log('Video uploaded successfully');
            res.send('Video uploaded successfully');
        });
    });
});

// Route to start Python script
app.get('/start-python', (req, res) => {
    const pythonScript = 'app.py';
    exec(`python ${pythonScript}`, (error, stdout, stderr) => {
        if (error) {
            console.error('Error executing Python script:', error);
            return res.status(500).send('Error starting Python script');
        }
        console.log('Python script executed successfully');

        // Read JSON file containing filenames and timestamps
        fs.readFile('result_frames.json', (err, data) => {
            if (err) {
                console.error('Error reading result_frames.json:', err);
                return res.status(500).send('Error reading result_frames.json');
            }
            const resultFrames = JSON.parse(data);
            res.json(resultFrames);
        });
    });
});

// Serve result images
app.get('/result-images/:filename', (req, res) => {
    const filename = req.params.filename;
    const imagePath = path.join(__dirname, 'media', filename);
    res.sendFile(imagePath);
});

// Function to delete files in a directory
function deleteFiles(directory, callback) {
    const mediaDir = path.join(__dirname, directory);
    fs.readdir(mediaDir, (err, files) => {
        if (err) {
            console.error(`Error reading ${directory} folder:`, err);
            return;
        }
        files.forEach((file) => {
            fs.unlink(path.join(mediaDir, file), (err) => {
                if (err) {
                    console.error(`Error deleting file ${file}:`, err);
                }
            });
        });
        callback();
    });
}

// Start server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
