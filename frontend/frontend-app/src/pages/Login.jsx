import { useState } from "react";
import { Link } from "react-router-dom";

import {
  Navigate,
  useNavigate
} from "react-router-dom";

import { useAuth }
  from "../context/AuthContext";

function Login() {

  const [email, setEmail] =
    useState("");

  const [password, setPassword] =
    useState("");

  const {
    login,
    isAuthenticated
  } = useAuth();

  const navigate =
    useNavigate();

  if (isAuthenticated) {

    return <Navigate to="/" />;
  }

  const handleLogin = async (e) => {

    e.preventDefault();

    try {

      const response = await fetch(
        "https://genai-rag-backend-asu-a8cjhsevdhbgftg9.centralindia-01.azurewebsites.net/auth/login",
        {
          method: "POST",
          headers: {
            "Content-Type":
              "application/json"
          },
          body: JSON.stringify({
            email,
            password
          })
        }
      );

      const data =
        await response.json();

      if (
  data.access_token &&
  data.token_type === "bearer"
) {

  const meResponse =
    await fetch(
      "https://genai-rag-backend-asu-a8cjhsevdhbgftg9.centralindia-01.azurewebsites.net/auth/me",
      {
        headers: {
          Authorization:
            `Bearer ${data.access_token}`
        }
      }
    );

  const userData =
    await meResponse.json();

  login(
    data.access_token,
    userData
  );

  navigate("/");

} else {

        alert(
          "Invalid email or password"
        );
      }

    } catch (error) {

      console.error(error);

      alert(
        "Unable to connect to server"
      );
    }
  };

  return (
  <div className="login-container">

    <div className="auth-card">

      <h1 className="auth-title">
        QuarryAI
      </h1>

      <p className="auth-subtitle">
        AI-powered Banking Assistant
      </p>

      <form onSubmit={handleLogin}>

        <input
          type="email"
          placeholder="Email Address"
          value={email}
          onChange={(e) =>
            setEmail(e.target.value)
          }
        />

        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) =>
            setPassword(e.target.value)
          }
        />

        <button type="submit">
          Sign In
        </button>

      </form>

      <p>
        Don't have an account?{" "}
        <Link to="/register">
          Register
        </Link>
      </p>

    </div>

  </div>
);
}

export default Login;