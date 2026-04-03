import { createContext, useContext, useMemo, useState } from "react";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);

  const login = ({ username, password }) => {
    // Replace this with your real API call
    if (username === "admin" && password === "password") {
      setUser({
        username: "admin",
        permissions: ["read:home", "read:admin"],
      });
      return { ok: true };
    }

    if (username === "user" && password === "password") {
      setUser({
        username: "user",
        permissions: ["read:home"],
      });
      return { ok: true };
    }

    return { ok: false, error: "Invalid username or password" };
  };

  const logout = () => {
    setUser(null);
  };


  const createUser = ({ username, password }) => {
    if (username && password) {
      // TODO: Implement username and password validation, and handle errors (e.g., username already exists, password strength requirements)
      // Simulate user creation and login

      setUser({
        username,
        permissions: ["read:home"], // Default permissions for new users
      });
      return { ok: true };
    }

    return { ok: false, error: "Username and password are required" };
  };

  const hasPermission = (permission) => {
    if (!user) return false;
    return user.permissions.includes(permission);
  };

  const value = useMemo(
    () => ({
      user,
      login,
      logout,
      createUser,
      hasPermission,
      isAuthenticated: !!user,
    }),
    [user]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }

  return context;
}