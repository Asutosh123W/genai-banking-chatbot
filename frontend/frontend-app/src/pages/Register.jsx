import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

function Register() {

  const navigate = useNavigate();

  const [username, setUsername] =
    useState("");

  const [email, setEmail] =
    useState("");

  const [password, setPassword] =
    useState("");

  const [confirmPassword,
    setConfirmPassword] =
    useState("");

  const [loading, setLoading] =
    useState(false);

  const handleRegister = async (e) => {

    e.preventDefault();

    if (
      password !== confirmPassword
    ) {

      alert(
        "Passwords do not match"
      );

      return;
    }

    setLoading(true);

    try {

      const response = await fetch(
        "https://genai-rag-backend-asu-a8cjhsevdhbgftg9.centralindia-01.azurewebsites.net/auth/register",
        {
          method: "POST",
          headers: {
            "Content-Type":
              "application/json"
          },
          body: JSON.stringify({
            username,
            email,
            password
          })
        }
      );

      const data =
        await response.json();

      if (
        data.message ===
        "User created successfully"
      ) {

        alert(
          "Registration successful. Please login."
        );

        navigate("/login");

      } else {

        alert(
          data.message ||
          "Registration failed"
        );
      }

    } catch (error) {

      console.log(error);

      alert(
        "Unable to register."
      );

    }

    setLoading(false);

  };

  return (
  <div className="login-container">

    <div className="auth-card">

      <h1 className="auth-title">
        Create Account
      </h1>

      <p className="auth-subtitle">
        Start using the AI Banking Assistant
      </p>

      <form
        onSubmit={handleRegister}
      >

        <input
          type="text"
          placeholder="Username"
          value={username}
          onChange={(e) =>
            setUsername(
              e.target.value
            )
          }
        />

        <input
          type="email"
          placeholder="Email Address"
          value={email}
          onChange={(e) =>
            setEmail(
              e.target.value
            )
          }
        />

        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) =>
            setPassword(
              e.target.value
            )
          }
        />

        <input
          type="password"
          placeholder="Confirm Password"
          value={confirmPassword}
          onChange={(e) =>
            setConfirmPassword(
              e.target.value
            )
          }
        />

        <button
          type="submit"
          disabled={loading}
        >
          {
            loading
              ? "Creating..."
              : "Create Account"
          }
        </button>

      </form>

      <p>
        Already have an account?{" "}
        <Link to="/login">
          Login
        </Link>
      </p>

    </div>

  </div>
);
}

export default Register;