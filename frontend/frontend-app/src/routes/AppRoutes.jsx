import {
    BrowserRouter,
    Routes,
    Route
} from "react-router-dom";

import Dashboard
    from "../pages/Dashboard";

import Login
    from "../pages/Login";

import Register
    from "../pages/Register";

import ProtectedRoute
    from "../components/ProtectedRoute";

function AppRoutes() {

    return (

        <BrowserRouter>

            <Routes>

                <Route
                    path="/login"
                    element={<Login />}
                />

                <Route
                    path="/register"
                    element={<Register />}
                />

                <Route
                    path="/"
                    element={
                        <ProtectedRoute>

                            <Dashboard />

                        </ProtectedRoute>
                    }
                />

            </Routes>

        </BrowserRouter>

    );
}

export default AppRoutes;