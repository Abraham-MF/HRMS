import { create } from "zustand";
import {
  persist,
  createJSONStorage,
} from "zustand/middleware";

import type {
  User,
  AuthTokens,
} from "@/types/auth.types";

import { loginRequest } from "../api/auth.api";

interface AuthState {
  user: User | null;

  tokens: AuthTokens | null;

  isLogged: boolean;

  loading: boolean;

  login: (
    email: string,
    password: string
  ) => Promise<void>;

  logout: () => void;

  setUser: (user: User) => void;

  setTokens: (
    tokens: AuthTokens
  ) => void;
}

export const useAuthStore =
  create<AuthState>()(
    persist(
      (set) => ({
        user: null,

        tokens: null,

        isLogged: false,

        loading: false,

        async login(email, password) {
          set({
            loading: true,
          });

          try {
            const response =
              await loginRequest(
                email,
                password
              );

            set({
              user: response.user,

              tokens: {
                access:
                  response.access,

                refresh:
                  response.refresh,
              },

              isLogged: true,

              loading: false,
            });
          } catch (error) {
            set({
              loading: false,
              isLogged: false,
            });

            throw error;
          }
        },

        logout() {
          localStorage.removeItem(
            "hrms-auth"
          );

          set({
            user: null,
            tokens: null,
            isLogged: false,
          });

          window.location.replace(
            "/login"
          );
        },

        setUser(user) {
          set({
            user,
            isLogged: true,
          });
        },

        setTokens(tokens) {
          set({
            tokens,
          });
        },
      }),
      {
        name: "hrms-auth",

        storage:
          createJSONStorage(
            () => localStorage
          ),

        partialize(state) {
          return {
            user: state.user,

            tokens: state.tokens,

            isLogged:
              state.isLogged,
          };
        },
      }
    )
  );