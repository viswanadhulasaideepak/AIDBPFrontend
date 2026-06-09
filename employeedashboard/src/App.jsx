import AppRoutes from "./routes/AppRoutes";
import Notifier from "./components/common/Notifier";
import "./styles/global.css";
import "react-loading-skeleton/dist/skeleton.css";
import { ThemeProvider } from "./context/ThemeContext";
import { AuthProvider } from "./auth/AuthContext";

function App() {
  return (
    // Wrap everything in providers
    <AuthProvider>
      <ThemeProvider>
        <div>
          <AppRoutes />
          <Notifier />
        </div>
      </ThemeProvider>
    </AuthProvider>
  );
}

export default App;
