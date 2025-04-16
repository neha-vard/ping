import { useState, useEffect } from "react";
import { io } from "socket.io-client";

// Connect to the WebSocket server
const socket = io("http://localhost:5000");

function App() {
    const [alert, setAlert] = useState(null);
    const [file, setFile] = useState(null);
    const [name, setName] = useState("");
    const [registrationResult, setRegistrationResult] = useState(null);

    // Handle image + name uploads
    const handleFileChange = (e) => {
        const selectedFile = e.target.files[0];
        if (selectedFile) {
            setFile(selectedFile);
        }
    };

    const handleImageSubmit = () => {
        if (!file || !name) {
            alert("Please select a file and enter a name.");
            return;
        }

        const reader = new FileReader();
        reader.onloadend = () => {
            const base64Data = reader.result.split(',')[1];
            socket.emit("upload_image_bytes", {
                name,
                imageData: base64Data
            });
            console.log("Image data sent");
        };
        reader.readAsDataURL(file);
    };


    // Listen for visitor alerts
    useEffect(() => {
        socket.on("alert", (data) => {
            console.log("Received alert:", data);  // Debugging: Check the data received
            setAlert(data.message);
        });

        // Listen for image registration result
        socket.on("image_registration_result", (data) => {
            console.log("Received image registration result:", data);  // Debugging: Check the result received
            setRegistrationResult(data.message);
        });

        return () => {
            socket.off("alert");
            socket.off("image_registration_result");  // Clean up the socket on unmount
        };
    }, []);

    return (
        <div>
            <h1>Ping Security System</h1>
            {alert && <p style={{ color: "red" }}>{alert}</p>}

            {registrationResult && <p style={{ color: "green" }}>{registrationResult}</p>}
            <input
                type="file"
                accept="image/*"
                onChange={handleFileChange}
            />
            <input
                type="text"
                value={name}
                onChange={(e) => {setName(e.target.value)}}
                placeholder="Enter name to associate with image"
            />
            <button onClick={handleImageSubmit}>Submit Image</button>
        </div>
    );
}

export default App;
