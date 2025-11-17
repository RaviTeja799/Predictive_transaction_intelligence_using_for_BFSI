import { createContext, useContext, useEffect, useMemo, useState, ReactNode } from "react";

export type UserRole = "Admin" | "Analyst" | "Manager";

export interface AuthenticatedUser {
  id: string;
  name: string;
  role: UserRole;
  permissions: string[];
  lastLogin: string;
}

interface LoginPayload {
  username: string;
  employeeId: string;
  role: UserRole;
}

interface AuthContextValue {
  user: AuthenticatedUser | null;
  isAuthenticated: boolean;
  login: (payload: LoginPayload) => Promise<AuthenticatedUser>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

const rolePermissions: Record<UserRole, string[]> = {
  Admin: ["manage-users", "view-analytics", "tune-models", "override-alerts"],
  Analyst: ["view-analytics", "investigate", "create-cases"],
  Manager: ["view-analytics", "approve-cases", "assign-cases"],
};

const STORAGE_KEY = "transintelliflow:user";

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<AuthenticatedUser | null>(null);

  useEffect(() => {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      try {
        setUser(JSON.parse(stored));
      } catch (error) {
        console.warn("Failed to parse stored user", error);
        localStorage.removeItem(STORAGE_KEY);
      }
    }
  }, []);

  const login = async ({ username, employeeId, role }: LoginPayload) => {
    await new Promise((resolve) => setTimeout(resolve, 400));
    const profile: AuthenticatedUser = {
      id: employeeId || username,
      name: username,
      role,
      permissions: rolePermissions[role] ?? [],
      lastLogin: new Date().toISOString(),
    };
    setUser(profile);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(profile));
    return profile;
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem(STORAGE_KEY);
  };

  const value = useMemo<AuthContextValue>(() => ({
    user,
    isAuthenticated: Boolean(user),
    login,
    logout,
  }), [user]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
