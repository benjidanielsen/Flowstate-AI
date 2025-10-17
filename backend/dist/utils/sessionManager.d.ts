/**
 * Session Management Utility
 * Handles Redis-based session storage and management
 */
export interface SessionData {
    userId: string;
    email: string;
    role: string;
    createdAt: number;
    lastActivity: number;
    metadata?: Record<string, any>;
}
export declare class SessionManager {
    private redis;
    private readonly SESSION_PREFIX;
    private readonly SESSION_TTL;
    private readonly ACTIVITY_UPDATE_INTERVAL;
    constructor(redisUrl?: string);
    /**
     * Create a new session
     */
    createSession(sessionId: string, data: Omit<SessionData, 'createdAt' | 'lastActivity'>): Promise<void>;
    /**
     * Get session data
     */
    getSession(sessionId: string): Promise<SessionData | null>;
    /**
     * Update session data
     */
    updateSession(sessionId: string, updates: Partial<SessionData>): Promise<void>;
    /**
     * Update last activity timestamp
     */
    updateActivity(sessionId: string): Promise<void>;
    /**
     * Delete a session
     */
    deleteSession(sessionId: string): Promise<void>;
    /**
     * Get all sessions for a user
     */
    getUserSessions(userId: string): Promise<Array<{
        sessionId: string;
        data: SessionData;
    }>>;
    /**
     * Delete all sessions for a user
     */
    deleteUserSessions(userId: string): Promise<number>;
    /**
     * Check if a session exists and is valid
     */
    isSessionValid(sessionId: string): Promise<boolean>;
    /**
     * Get session TTL in seconds
     */
    getSessionTTL(sessionId: string): Promise<number>;
    /**
     * Refresh session TTL
     */
    refreshSession(sessionId: string): Promise<void>;
    /**
     * Get active session count
     */
    getActiveSessionCount(): Promise<number>;
    /**
     * Cleanup expired sessions (Redis handles this automatically, but this can be used for manual cleanup)
     */
    cleanupExpiredSessions(): Promise<number>;
    /**
     * Close Redis connection
     */
    close(): Promise<void>;
    /**
     * Get the full Redis key for a session
     */
    private getSessionKey;
}
export declare const sessionManager: SessionManager;
//# sourceMappingURL=sessionManager.d.ts.map