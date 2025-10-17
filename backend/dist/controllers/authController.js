"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.login = exports.register = void 0;
const authService_1 = require("../services/authService");
const logger_1 = __importDefault(require("../utils/logger"));
const authService = new authService_1.AuthService();
const register = async (req, res) => {
    try {
        const { username, password } = req.body;
        if (!username || !password) {
            return res.status(400).json({ message: 'Username and password are required' });
        }
        const existingUser = await authService.findUserByUsername(username);
        if (existingUser) {
            return res.status(409).json({ message: 'User already exists' });
        }
        const user = await authService.registerUser(username, password);
        logger_1.default.info(`User registered successfully: ${username}`);
        res.status(201).json({ message: 'User registered successfully', user: { id: user.id, username: user.username } });
    }
    catch (error) {
        console.error('Registration error:', error);
        res.status(500).json({ message: 'Internal server error' });
    }
};
exports.register = register;
const login = async (req, res) => {
    try {
        const { username, password } = req.body;
        if (!username || !password) {
            return res.status(400).json({ message: 'Username and password are required' });
        }
        const user = await authService.validateUser(username, password);
        if (!user) {
            return res.status(401).json({ message: 'Invalid credentials' });
        }
        const token = authService.generateToken(user);
        logger_1.default.info(`User logged in successfully: ${username}`);
        res.status(200).json({ message: 'Login successful', token });
    }
    catch (error) {
        console.error('Login error:', error);
        res.status(500).json({ message: 'Internal server error' });
    }
};
exports.login = login;
//# sourceMappingURL=authController.js.map