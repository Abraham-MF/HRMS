import api from "@/shared/api/axios";
import type { User } from "@/types/auth.types";

export interface LoginResponse {
  access: string;
  refresh: string;
  user: User;
}

export async function loginRequest(
  email: string,
  password: string
) {
  const { data } = await api.post<LoginResponse>(
    "/auth/login/",
    {
      email,
      password,
    }
  );

  return data;
}

export async function refreshToken(
  refresh: string
) {
  const { data } = await api.post("/auth/refresh/", {
    refresh,
  });

  return data;
}