export type UserRole =
  | "ADMIN"
  | "HR"
  | "SUPERVISOR"
  | "EMPLOYEE";

export interface User {
  id: string;
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  role: UserRole;
}

export interface AuthTokens {
  access: string;
  refresh: string;
}
