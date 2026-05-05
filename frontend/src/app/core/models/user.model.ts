export interface User {
  id: string;
  email: string;
  full_name: string | null;
  company: string | null;
  role: 'user' | 'admin';
  is_active: boolean;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name?: string;
  company?: string;
}

export interface TokenResponse {
  access_token: string;
}
