export interface User {
  id: string;
  full_name: string;
  email: string;
  profile_image?: string | null;
  phone_number?: string | null;
  role?: string;
}

export type LoginCredentials = Pick<User, 'email'> & {
  password: string;
};

export interface RegisterCredentials {
  full_name: string;
  email: string;
  password: string;
}

export interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (credentials: RegisterCredentials) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}
