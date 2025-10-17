import { User } from '../types';
export declare class AuthService {
    private db;
    registerUser(username: string, password_plain: string): Promise<User>;
    findUserByUsername(username: string): Promise<User | null>;
    validateUser(username: string, password_plain: string): Promise<User | null>;
    generateToken(user: User): string;
    verifyToken(token: string): any;
}
//# sourceMappingURL=authService.d.ts.map