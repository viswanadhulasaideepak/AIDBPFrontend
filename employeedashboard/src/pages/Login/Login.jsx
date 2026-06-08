import { useState, useContext } from "react";
import { FaEnvelope, FaLock } from "react-icons/fa";
import { loginUser, signupUser, resetPassword } from "../../services/api"; // 🔹 Added resetPassword
import toast from "react-hot-toast";
import { useNavigate } from "react-router-dom";
import { AuthContext } from "../../auth/AuthContext";
import "./Login.css";

const SignupForm = ({ onCancel }) => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("");
  const [companyName, setCompanyName] = useState("");

  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const data = await signupUser(email, password, role, companyName);
      toast.success("Signup successful!");
      navigate("/login");
    } catch (err) {
      console.error(err);
      toast.error("Signup failed");
    }
  };

  return (
    <form className="signup-form" onSubmit={handleSubmit}>
      <input
        type="email"
        placeholder="Email"
        value={email}
        onChange={(e)=>setEmail(e.target.value)}
        required
      />
      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e)=>setPassword(e.target.value)}
        required
      />
      <select value={role} onChange={(e)=>setRole(e.target.value)} required>
        <option value="">Select Role</option>
        <option value="admin">Admin</option>
        <option value="user">User</option>
      </select>

      <select value={companyName}
      onChange={(e) => setCompanyName(e.target.value)} required>
        <option value="">Select Company</option>
        <option value="Company A">Company A</option>
        <option value="Company B">Company B</option>
        </select>

      <button type="submit">Signup</button>
      <p className="signup-text">
        Already have an account?{" "}
        <button type="button" onClick={onCancel}>Back to Login</button>
      </p>
    </form>
  );
};

//  Forgot Password Form
const ForgotPasswordForm = ({ onCancel }) => {
  const [email, setEmail] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (newPassword !== confirmPassword) {
      toast.error("Passwords do not match");
      return;
    }
    try {
      await resetPassword(email, newPassword);
      toast.success("Password reset successful!");
      onCancel(); // go back to login
    } catch (err) {
      console.error(err);
      toast.error("Password reset failed");
    }
  };

  return (
    <form className="forgot-form" onSubmit={handleSubmit}>
      <input
        type="email"
        placeholder="Enter your email"
        value={email}
        onChange={(e)=>setEmail(e.target.value)}
        required
      />
      <input
        type="password"
        placeholder="New Password"
        value={newPassword}
        onChange={(e)=>setNewPassword(e.target.value)}
        required
      />
      <input
        type="password"
        placeholder="Confirm Password"
        value={confirmPassword}
        onChange={(e)=>setConfirmPassword(e.target.value)}
        required
      />
      <button type="submit">Reset Password</button>
      <p className="signup-text">
        Back to{" "}
        <button type="button" onClick={onCancel}>Login</button>
      </p>
    </form>
  );
};
//-------------------Login------------------------
const Login = () => {
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("");
  const [showSignup, setShowSignup] = useState(false);
  const [showForgot, setShowForgot] = useState(false);
  const [companyName, setCompanyName] = useState("");
  const navigate = useNavigate();
  const { login } = useContext(AuthContext);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!role) {
      toast.error("Please choose Admin or User login");
      return;
    }
    try {
      const data = await loginUser(email, password, role);
      login(data);
      // Save token and role consistently
      localStorage.setItem("user", JSON.stringify(data));
      localStorage.setItem("token", data.token);
      localStorage.setItem("role", data.role);
      toast.success("Login successful!");
      navigate("/dashboard");
    } catch (err) {
      //console.error(err);
      toast.error("Login failed");
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <div className="login-icon">👤</div>
          <h2>
            {showSignup ? "Create Account" : showForgot ? "Reset Password" : "Welcome Back!"}
          </h2>
          <p>
            {showSignup
              ? "Fill in details below"
              : showForgot
              ? "Enter email and new password"
              : "Choose Admin or User login"}
          </p>
        </div>

        {showSignup ? (
          <SignupForm onCancel={() => setShowSignup(false)} />
        ) : showForgot ? (
          <ForgotPasswordForm onCancel={() => setShowForgot(false)} />
        ) : (
          <>
            <div className="role-buttons">
              <button
                type="button"
                className={`role-btn ${role === "admin" ? "active" : ""}`}
                onClick={() => setRole("admin")}
              >
                Admin Login
              </button>
              <button
                type="button"
                className={`role-btn ${role === "user" ? "active" : ""}`}
                onClick={() => setRole("user")}
              >
                User Login
              </button>
            </div>

            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label className="form-label">Company</label>
                <select className="form-select" value={companyName}
                 onChange={(e) => setCompanyName(e.target.value)}
                  required>
                    <option value="">Select Company</option>
                    <option value="Company A">Company A</option>
                    <option value="Company B">Company B</option>
                    </select>
                
                <label>Full Name</label>

                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="Enter your full name"
                  required
                />
              </div>

              <div className="input-group">
                <label>Email</label>
                <div className="input-field">
                  <FaEnvelope className="icon" />
                  <input
                    type="email"
                    placeholder="Enter email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                  />
                </div>
              </div>

              <div className="input-group">
                <label>Password</label>
                <div className="input-field">
                  <FaLock className="icon" />
                  <input
                    type="password"
                    placeholder="Enter password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                  />
                </div>
              </div>

              <button type="submit" className="login-btn">Login</button>

              <p className="signup-text">
                Don’t have an account?{" "}
                <button type="button" onClick={() => setShowSignup(true)}>
                  Sign up
                </button>
              </p>
              <p className="signup-text">
                Forgot your password?{" "}
                <button type="button" onClick={() => setShowForgot(true)}>
                  Reset
                </button>
              </p>
            </form>
          </>
        )}
      </div>
    </div>
  );
};

export default Login;
