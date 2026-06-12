import React from "react";
import { BrowserRouter as Router } from "react-router-dom";
import { AuthProvider } from "./auth/AuthContext";
import { ThemeProvider } from "./context/ThemeContext";
import AppRoutes from "./routes/AppRoutes";
import Notifier from "./components/common/Notifier";
import "./styles/global.css";
import "react-loading-skeleton/dist/skeleton.css";

function App() {
  return (
    <Router>
      <AuthProvider>
        <ThemeProvider>
          <div>
            <AppRoutes />
            <Notifier />
          </div>
        </ThemeProvider>
      </AuthProvider>
    </Router>
  );
}

export default App;
