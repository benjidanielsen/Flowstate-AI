import { safeLogger } from './piiRedaction';

/**
 * Lightweight tracer stub to avoid hard dependency on OpenTelemetry modules.
 * If OpenTelemetry packages are installed, this can be replaced with a full implementation.
 */
export const tracer = {
  startSpan: (_name: string) => ({
    end: () => {},
  }),
};

safeLogger.info('OpenTelemetry tracer stub initialized');
