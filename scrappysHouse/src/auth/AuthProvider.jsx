import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { api } from "../services/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [authLoading, setAuthLoading] = useState(true);
  const [authError, setAuthError] = useState(null);

  const login = async ({ username, password }) => {
    try {
      setAuthError(null);

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

      const message = "Login failed";
      setAuthError(message);
      return { ok: false, error: message };
    } catch (error) {
      const message =
        error?.response?.data?.detail ||
        error?.response?.data?.message ||
        "Login failed";

      setAuthError(message);
      setUser(null);

      return {
        ok: false,
        error: message,
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
      setAuthError(null);
    }
  };

  const createUser = async ({ username, password }) => {
    try {
      setAuthError(null);

      const response = await api.post("/api/v1/auth/register", {
        email: username,
        password,
      });

      if (response.data?.ok === true) {
        const loginResult = await login({ username, password });

        if (!loginResult.ok) {
          const message = loginResult.error || "User created but login failed";
          setAuthError(message);
          return { ok: false, error: message };
        }

        return { ok: true };
      }

      const message = response.data?.message || "User creation failed";
      setAuthError(message);
      return { ok: false, error: message };
    } catch (error) {
      const message =
        error?.response?.data?.detail ||
        error?.response?.data?.message ||
        "User creation failed";

      setAuthError(message);

      return {
        ok: false,
        error: message,
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
        setAuthError(null);

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
      authError,
      login,
      logout,
      createUser,
      hasPermission,
      isAuthenticated: !!user,
      authLoading,
      clearAuthError: () => setAuthError(null),
    }),
    [user, authError, authLoading]
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