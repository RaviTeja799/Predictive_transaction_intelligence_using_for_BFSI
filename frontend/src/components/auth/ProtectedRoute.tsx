import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuth, UserRole } from "@/context/AuthContext";

interface ProtectedRouteProps {
  allowedRoles?: UserRole[];
}

const ProtectedRoute = ({ allowedRoles }: ProtectedRouteProps) => {
  const { user, isAuthenticated } = useAuth();
  const location = useLocation();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  // Role-based access control
  if (user) {
    // Users can only access /transaction page
    if (user.role === "User") {
      if (location.pathname !== "/transaction") {
        return <Navigate to="/transaction" replace />;
      }
    } 
    // Other roles cannot access /transaction page (it's User-only)
    else {
      if (location.pathname === "/transaction") {
        return <Navigate to="/dashboard" replace />;
      }
    }
  }

  if (allowedRoles && user && !allowedRoles.includes(user.role)) {
    return <Navigate to="/dashboard" replace />;
  }

  return <Outlet />;
};

export default ProtectedRoute;
