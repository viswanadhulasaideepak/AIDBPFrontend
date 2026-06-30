import React, { createContext, useState, useEffect } from "react";
import api from "../services/api";

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);

  useEffect(() => {
    const storedUser = localStorage.getItem("user");
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    }
  }, []);

  useEffect(() => {
  if (user?.status === "deactivated") {
    logout();
  }
}, [user]);
   
  

  const login = (data) => {
    const userData = {
      id: data.id,
      email: data.email,
      token: data.token,
      role: data.role,
      company_id: data.company_id,
      status: data.status,
    };

    setUser(userData);
    localStorage.setItem("user", JSON.stringify(userData));
    localStorage.setItem("token", data.token);
  };

  const logout = async () => {
  try {
    await api.post("/logout");
  } catch (error) {
    console.error("Logout API failed:", error);
  }
  setUser(null);
  localStorage.removeItem("user");
  localStorage.removeItem("token");
};

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => React.useContext(AuthContext);