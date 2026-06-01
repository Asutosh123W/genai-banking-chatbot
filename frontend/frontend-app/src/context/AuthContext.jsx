import {
  createContext,
  useContext,
  useState
} from "react";

const AuthContext =
  createContext();

export function AuthProvider({
  children
}) {

  const [token, setToken] =
    useState(
      localStorage.getItem(
        "token"
      )
    );

  const [user, setUser] =
    useState(
      JSON.parse(
        localStorage.getItem(
          "user"
        )
      ) || null
    );

  const login = (
    jwtToken,
    userData
  ) => {

    localStorage.setItem(
      "token",
      jwtToken
    );

    localStorage.setItem(
      "user",
      JSON.stringify(
        userData
      )
    );

    setToken(jwtToken);

    setUser(userData);
  };

  const logout = () => {

    localStorage.removeItem(
      "token"
    );

    localStorage.removeItem(
      "user"
    );

    setToken(null);

    setUser(null);
  };

  return (

    <AuthContext.Provider
      value={{
        token,
        user,
        login,
        logout,
        isAuthenticated:
          !!token
      }}
    >

      {children}

    </AuthContext.Provider>
  );
}

export function useAuth() {

  return useContext(
    AuthContext
  );
}