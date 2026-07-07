import React, { createContext, useContext, useState, useEffect } from "react";
import { apiService } from "../services/api";
import type { UserResponse } from "../services/api";

interface AuthContextType {
  currentUser: UserResponse | null;
  isAuthenticated: boolean;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, name: string) => Promise<void>;
  logout: () => Promise<void>;
  updateProfile: (name: string, language?: string, timezone?: string) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [currentUser, setCurrentUser] = useState<UserResponse | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchProfile = async () => {
    try {
      const user = await apiService.getMe();
      setCurrentUser(user);
    } catch (e) {
      // Access token expired, try to refresh
      try {
        const refreshData = await apiService.refreshTokens();
        if (refreshData.access_token) {
          localStorage.setItem("access_token", refreshData.access_token);
          const user = await apiService.getMe();
          setCurrentUser(user);
        } else {
          clearAuth();
        }
      } catch (err) {
        clearAuth();
      }
    } finally {
      setLoading(false);
    }
  };

  const clearAuth = () => {
    setCurrentUser(null);
    localStorage.removeItem("access_token");
  };

  useEffect(() => {
    fetchProfile();
  }, []);

  const login = async (email: string, password: string) => {
    const data = await apiService.loginUser({ email, password });
    if (data.access_token) {
      localStorage.setItem("access_token", data.access_token);
      setCurrentUser(data.user);
    }
  };

  const register = async (email: string, password: string, name: string) => {
    await apiService.registerUser({ email, password, name });
    // Auto login after registration
    await login(email, password);
  };

  const logout = async () => {
    try {
      await apiService.logoutUser();
    } finally {
      clearAuth();
    }
  };

  const updateProfile = async (
    name: string,
    language?: string,
    timezone?: string
  ) => {
    const updated = await apiService.updateMe({ name, language, timezone });
    setCurrentUser(updated);
  };

  return (
    <AuthContext.Provider
      value={{
        currentUser,
        isAuthenticated: !!currentUser,
        loading,
        login,
        register,
        logout,
        updateProfile,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
