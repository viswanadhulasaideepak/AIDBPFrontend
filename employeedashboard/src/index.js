import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App.jsx";        // extension added
import "./styles/global.css";       // corrected filename

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<App />);
