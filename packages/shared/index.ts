export type Role = 'admin' | 'analista' | 'cliente';

export interface UserDTO {
  id: number;
  email: string;
  full_name: string;
  role: Role;
  tenant_id: number;
}
