import { useState, useEffect } from "react";
import { io } from "socket.io-client";
import './App.css';

// Connect to the WebSocket server
const socket = io("http://localhost:5000");

function App() {
    const [alert, setAlert] = useState(null);
    const [file, setFile] = useState(null);
    const [name, setName] = useState("");
    const [registrationResult, setRegistrationResult] = useState(null);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [visitorLog, setVisitorLog] = useState([])

    // Handle image + name uploads
    const handleFileChange = (e) => {
        const selectedFile = e.target.files[0];
        if (selectedFile) {
            setFile(selectedFile);
            const imagePreviewElement = document.querySelector("#image");
            imagePreviewElement.src = URL.createObjectURL(selectedFile);
            imagePreviewElement.style.display = "block";
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
            setVisitorLog(prevLog => [...prevLog, { timestamp: new Date().toISOString(), message: data.message }])
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

    useEffect(() => {
        if (alert) {
          const timer = setTimeout(() => {
            setAlert(null);
          }, 10000);
          return () => clearTimeout(timer);
        }
      }, [alert]);
      
      useEffect(() => {
        if (registrationResult) {
          const timer = setTimeout(() => {
            setRegistrationResult(null);
          }, 10000);
          return () => clearTimeout(timer);
        }
      }, [registrationResult]);
      
    return (
        <div class="container">
            <h1 class="header">Ping Security System</h1>
            <h4 style={{fontStyle: "italic", fontWeight: "normal", width: "60%"}}>First, upload an image of the known person you want to add to model. Then, enter the name associated with the person identified in the image and click the "Submit Image and Name button". Any alerts / notifications will show up at the top of the screen.</h4>
            <div className="toast-container">
                {alert && (
                    <div className="toast toast-error">
                    {alert}
                    </div>
                )}
                {registrationResult && (
                    <div className="toast toast-success">
                    {registrationResult}
                    </div>
                )}
            </div>
            <div class="image-container">
            <div class="img-view">
                <img id="image" />
            </div>
            <label for="file-upload">Upload Image</label>
            <input
                id="file-upload"
                type="file"
                accept="image/*"
                onChange={handleFileChange}
            />
            </div>
            <div className="name-input-container">
                <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="Enter Name"
                    className="name-input"
                />
            </div>
            <button className="submit-button" onClick={handleImageSubmit}>Submit Image and Name</button>
            
            <button className="visitor-log-button" onClick={() => setIsModalOpen(true)}>Visitor Log</button>

            {isModalOpen && (
                <div className="modal">
                    <div className="modal-content">
                        <div className="modal-header">
                            <h2>Visitor Log</h2>
                            <button className="close-button" onClick={() => setIsModalOpen(false)}>x</button>
                        </div>
                        <div className="modal-table-wrapper">
                            <table>
                                <thead>
                                    <tr>
                                    <th>Timestamp</th>
                                    <th>Message</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {[...visitorLog].reverse().map((entry, index) => (
                                    <tr key={index}>
                                        <td>{entry.timestamp}</td>
                                        <td>{entry.message}</td>
                                    </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

export default App;
