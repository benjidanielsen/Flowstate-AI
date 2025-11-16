import { AlertTriangle } from 'lucide-react';

interface ErrorStateProps {
  message: string;
  onRetry?: () => void;
  title?: string;
}

const ErrorState = ({ message, onRetry, title = 'Something went wrong' }: ErrorStateProps) => (
  <div
    role="alert"
    className="flex flex-col gap-3 rounded-lg border border-red-200 bg-red-50 p-4 text-red-800 sm:flex-row sm:items-center sm:justify-between"
  >
    <div className="flex items-start gap-2">
      <AlertTriangle className="h-5 w-5" aria-hidden="true" />
      <div>
        <p className="text-sm font-semibold">{title}</p>
        <p className="text-sm text-red-700">{message}</p>
      </div>
    </div>
    {onRetry && (
      <button
        type="button"
        onClick={onRetry}
        className="inline-flex items-center justify-center rounded-md bg-red-600 px-3 py-1.5 text-sm font-semibold text-white shadow-sm transition hover:bg-red-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-red-700"
      >
        Try again
      </button>
    )}
  </div>
);

export default ErrorState;
