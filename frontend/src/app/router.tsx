import { createBrowserRouter, Navigate, Outlet, useNavigate } from "react-router-dom";
import { useAuthStore } from "@/modules/auth/store/authStore";
import type { UserRole } from "@/types/auth.types";

import DashboardLayout  from "@/shared/components/layout/dashboard";
import LoginPage        from "@/modules/auth/page/Loginpage";
import DashboardPage    from "@/modules/dashboard/page/dashboard";
import EmployeeListPage from "@/modules/empleados/pages/list_empleados";
import EmployeeFormPage from "@/modules/empleados/components/form_empleados";
import NominasPage      from "@/modules/nominas/pages/NominasPage";
import AsistenciaPage   from "@/modules/asistencia/pages/AsistenciaPage";
import DocumentsPage    from "@/modules/documentos/pages/DocumentsPage";
import apiClient        from "@/shared/utils/api-client";
import type { EmployeeFormData } from "@/shared/utils/validators";

const RequireAuth = ({ allowedRoles }: { allowedRoles?: UserRole[] }) => {
  const { isLogged, user } = useAuthStore();
  if (!isLogged) return <Navigate to="/login" replace />;
  if (allowedRoles && user && !allowedRoles.includes(user.role))
    return <Navigate to="/dashboard" replace />;
  return <Outlet />;
};

// Página temporal para Vacaciones (usa el mismo componente de Asistencia en tab permisos)
function VacationsPage() {
  return <AsistenciaPage initialTab="permisos" />;
}

function EmployeeNewPage() {
  const navigate = useNavigate();
  const handleSubmit = async (data: EmployeeFormData) => {
    await apiClient.post("/employees/", data);
    navigate("/employees");
  };
  return <EmployeeFormPage onSubmit={handleSubmit} />;
}

function EmployeeEditPage() {
  const navigate = useNavigate();
  const handleSubmit = async (data: EmployeeFormData) => {
    await apiClient.post("/employees/", data);
    navigate("/employees");
  };
  return <EmployeeFormPage onSubmit={handleSubmit} />;
}

export const router = createBrowserRouter([
  { path: "/login", element: <LoginPage /> },

  {
    element: <RequireAuth />,
    children: [
      {
        element: <DashboardLayout />,
        children: [
          { path: "/",          element: <Navigate to="/dashboard" replace /> },
          { path: "/dashboard", element: <DashboardPage /> },

          {
            element: <RequireAuth allowedRoles={["ADMIN", "HR", "SUPERVISOR", "EMPLOYEE"]} />,
            children: [
              { path: "/attendance", element: <AsistenciaPage /> },
              { path: "/vacations",  element: <VacationsPage /> },
            ],
          },

          {
            element: <RequireAuth allowedRoles={["ADMIN", "HR", "SUPERVISOR"]} />,
            children: [
              { path: "/employees", element: <EmployeeListPage /> },
            ],
          },

          {
            element: <RequireAuth allowedRoles={["ADMIN", "HR"]} />,
            children: [
              { path: "/payroll",            element: <NominasPage /> },
              { path: "/documents",          element: <DocumentsPage /> },
              { path: "/employees/new",      element: <EmployeeNewPage /> },
              { path: "/employees/edit/:id", element: <EmployeeEditPage /> },
            ],
          },
        ],
      },
    ],
  },

  { path: "*", element: <Navigate to="/dashboard" replace /> },
]);