import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { api } from "../services/api"

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [authLoading, setAuthLoading] = useState(true);

  const login = async ({ username, password }) => {
    try {
      const response = await api.post("/api/v1/auth/login", {
        email: username,
        password,
      });

      if (response.data?.user) {
        setUser(response.data.user);
        return { ok: true };
      }

      const meResponse = await api.get("/api/v1/auth/me");
      if (meResponse.data?.user) {
        setUser(meResponse.data.user);
        return { ok: true };
      }

      return { ok: false, error: "Login failed" };
    } catch (error) {
      return {
        ok: false,
        error: error?.response?.data?.detail || "Login failed",
      };
    }
  };

  const logout = async () => {
    try {
      await api.post("/api/v1/auth/logout");
    } catch (_) {
      // ignore logout API errors and still clear local user state
    } finally {
      setUser(null);
    }
  };

  const createUser = async ({ username, password }) => {
    try {
      const response = await api.post("/api/v1/auth/register", {
        email: username,
        password,
      });

      if (response.data?.user) {
        setUser(response.data.user);
        return { ok: true };
      }

      return { ok: false, error: "User creation failed" };
    } catch (error) {
      return {
        ok: false,
        error: error?.response?.data?.detail || "User creation failed",
      };
    }
  };

  const hasPermission = (permission) => {
    if (!user) return false;
    return (user.permissions || []).includes(permission);
  };

  useEffect(() => {
    const loadCurrentUser = async () => {
      try {
        const response = await api.get("/api/v1/auth/me");
        if (response.data?.user) {
          setUser(response.data.user);
        } else {
          setUser(null);
        }
      } catch (_) {
        setUser(null);
      } finally {
        setAuthLoading(false);
      }
    };

    loadCurrentUser();
  }, []);

  const value = useMemo(
    () => ({
      user,
      login,
      logout,
      createUser,
      hasPermission,
      isAuthenticated: !!user,
      authLoading,
    }),
    [user, authLoading]
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