import clsx from 'clsx';

interface SkeletonProps {
  className?: string;
  animate?: boolean;
}

const Skeleton = ({ className = '', animate = true }: SkeletonProps) => (
  <div
    className={clsx('rounded-md bg-gray-200', animate && 'animate-pulse', className)}
    role="status"
    aria-live="polite"
    aria-busy="true"
  >
    <span className="sr-only">Loading…</span>
  </div>
);

export default Skeleton;
