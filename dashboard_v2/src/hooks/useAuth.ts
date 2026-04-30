"use client";
import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";

export function useAuth() {
  const [user, setUser] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const token = localStorage.getItem("token");
    const storedUser = localStorage.getItem("user");

    if (token && storedUser) {
      try {
        const payload = JSON.parse(atob(token.split(".")[1]));
        if (payload.exp * 1000 < Date.now()) {
          localStorage.removeItem("token");
          localStorage.removeItem("user");
          router.push("/login");
        } else {
          setUser(storedUser);
        }
      } catch {
        router.push("/login");
      }
    } else if (window.location.pathname !== "/login" && window.location.pathname !== "/register") {
      router.push("/login");
    }
    setLoading(false);
  }, [router]);

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

  return { user, loading, login, logout, isAuthenticated: !!user };
}
