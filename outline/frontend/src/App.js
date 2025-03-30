import { useState, useEffect } from "react";
import { io } from "socket.io-client";

// Connect to the WebSocket server
const socket = io("http://localhost:5000");

function App() {
    const [alert, setAlert] = useState(null);
    const [imagePath, setImagePath] = useState("");
    const [registrationResult, setRegistrationResult] = useState(null);

    // Handle the text input for the image path
    const handleImagePathChange = (e) => {
        setImagePath(e.target.value);
    };

    // Handle sending the image path to the backend
    const handleImageSubmit = () => {
        if (imagePath) {
            // Send the image path to backend using Socket.IO
            socket.emit("upload_image", { imagePath });
            console.log("Image path sent:", imagePath);
        } else {
            alert("Please enter an image path.");
        }
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
            
            <input
                type="text"
                value={imagePath}
                onChange={handleImagePathChange}
                placeholder="Enter image path"
            />
            <button onClick={handleImageSubmit}>Submit Image Path</button>

            {registrationResult && <p style={{ color: "green" }}>{registrationResult}</p>}
        </div>
    );
}

export default App;
