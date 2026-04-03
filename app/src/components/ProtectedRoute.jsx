import { Navigate, Outlet, useLocation } from "react-router";
import { useAuth } from "../auth/AuthProvider";

export default function ProtectedRoute({ requiredPermission }) {
  const { isAuthenticated, hasPermission } = useAuth();
  const location = useLocation();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  if (requiredPermission && !hasPermission(requiredPermission)) {
    return <Navigate to="/unauthorized" replace />;
  }

  return <Outlet />;
}