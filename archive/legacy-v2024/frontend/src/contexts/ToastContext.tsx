import React, { createContext, useContext, useState, ReactNode } from 'react';

type Toast = { id: string; message: string; type?: 'success' | 'error' };

type ToastContextValue = {
  toasts: Toast[];
  push: (message: string, type?: Toast['type']) => void;
  remove: (id: string) => void;
};

const ToastContext = createContext<ToastContextValue | undefined>(undefined);

export const ToastProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const push = (message: string, type: Toast['type'] = 'success') => {
    const id = Math.random().toString(36).slice(2, 9);
    const t = { id, message, type };
    setToasts((s) => [t, ...s]);
    // auto-remove after 4s
    setTimeout(() => setToasts((s) => s.filter((x) => x.id !== id)), 4000);
  };

  const remove = (id: string) => setToasts((s) => s.filter((x) => x.id !== id));

  return <ToastContext.Provider value={{ toasts, push, remove }}>{children}</ToastContext.Provider>;
};

export const useToast = () => {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error('useToast must be used within ToastProvider');
  return ctx;
};

export default ToastContext;
