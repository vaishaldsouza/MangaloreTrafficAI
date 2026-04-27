"use client";
import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";

function isTokenExpired(token: string): boolean {
  try {
    const payload = JSON.parse(atob(token.split(".")[1]));
    return payload.exp * 1000 < Date.now();
  } catch {
    return true;
  }
}

export function useAuth() {
  const [user, setUser] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const token = localStorage.getItem("token");
    const storedUser = localStorage.getItem("user");
    if (token && storedUser && !isTokenExpired(token)) {
      setUser(storedUser);
    } else {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      if (window.location.pathname !== "/login") router.push("/login");
    }
    setLoading(false);
  }, [router]);

  // Token expiry warning logic
  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token || !user) return;
    try {
      const exp = JSON.parse(atob(token.split(".")[1])).exp * 1000;
      const msLeft = exp - Date.now();
      const warnAt = msLeft - 5 * 60 * 1000;   // 5 min before
      if (warnAt > 0) {
        const t = setTimeout(() => {
          alert("Session expiring in 5 minutes. Please save your work.");
        }, warnAt);
        return () => clearTimeout(t);
      }
    } catch {}
  }, [user]);

  const login = useCallback(async (username: string, password: string) => {
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({ username, password }),
    });
    if (!res.ok) throw new Error("Invalid credentials");
    const { access_token } = await res.json();
    localStorage.setItem("token", access_token);
    localStorage.setItem("user", username);
    setUser(username);
    router.push("/");
  }, [router]);

  const logout = useCallback(() => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    setUser(null);
    router.push("/login");
  }, [router]);

  // Helper for authenticated API calls
  const authFetch = useCallback((url: string, options: RequestInit = {}) => {
    const token = localStorage.getItem("token");
    return fetch(url, {
      ...options,
      headers: {
        ...options.headers,
        Authorization: `Bearer ${token}`,
      },
    });
  }, []);

  return { user, loading, login, logout, isAuthenticated: !!user, authFetch };
}
