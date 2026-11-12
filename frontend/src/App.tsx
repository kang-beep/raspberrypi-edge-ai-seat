import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { AuthProvider } from "./auth/AuthContext";
import { Layout } from "./components/Layout";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { ToastProvider } from "./components/Toast";
import { LoginPage } from "./pages/LoginPage";
import { ProfilePage } from "./pages/ProfilePage";
import { RegisterPage } from "./pages/RegisterPage";
import { SeatManagePage } from "./pages/SeatManagePage";
import { SeatReservePage } from "./pages/SeatReservePage";
import { SettingsPage } from "./pages/SettingsPage";
import { UserHomePage } from "./pages/UserHomePage";

export function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <ToastProvider>
          <Routes>
            <Route element={<Layout />}>
              <Route path="login" element={<LoginPage />} />
              <Route path="register" element={<RegisterPage />} />

              <Route element={<ProtectedRoute roles={["user", "admin"]} />}>
                <Route index element={<UserHomePage />} />
                <Route path="seats" element={<SeatReservePage />} />
                <Route path="profile" element={<ProfilePage />} />
                <Route
                  path="enroll"
                  element={<Navigate to="/profile#face" replace />}
                />
              </Route>

              <Route element={<ProtectedRoute roles={["admin"]} />}>
                <Route
                  path="admin"
                  element={<Navigate to="/admin/seats" replace />}
                />
                <Route path="admin/seats" element={<SeatManagePage />} />
                <Route path="admin/settings" element={<SettingsPage />} />
              </Route>

              <Route path="*" element={<Navigate to="/login" replace />} />
            </Route>
          </Routes>
        </ToastProvider>
      </BrowserRouter>
    </AuthProvider>
  );
}
