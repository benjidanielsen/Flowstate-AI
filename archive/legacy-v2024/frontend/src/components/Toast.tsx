import React from 'react';
import { useToast } from '../contexts/ToastContext';

const Toasts: React.FC = () => {
  const { toasts, remove } = useToast();

  return (
    <div className="fixed top-4 right-4 z-50 flex flex-col space-y-2">
      {toasts.map((t) => (
        <div
          key={t.id}
          className={`px-3 py-2 rounded shadow text-sm ${t.type === 'error' ? 'bg-red-500 text-white' : 'bg-green-600 text-white'}`}
          onClick={() => remove(t.id)}
        >
          {t.message}
        </div>
      ))}
    </div>
  );
};

export default Toasts;
