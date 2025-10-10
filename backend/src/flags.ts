import fs from 'fs';
import path from 'path';
import yaml from 'js-yaml';

type FlagMap = Record<string, boolean>;
let flags: FlagMap = {};

const DEFAULT_LOCATIONS = [
  path.resolve(process.cwd(), 'config/flags.yaml'),
  path.resolve(__dirname, '../../config/flags.yaml'),
  path.resolve(__dirname, '../config/flags.yaml'),
];

export function loadFlags(filePath?: string) {
  const candidatePaths = filePath ? [filePath] : DEFAULT_LOCATIONS;
  const resolvedPath = candidatePaths.find((candidate) => fs.existsSync(candidate));

  if (!resolvedPath) {
    flags = {};
    return;
  }

  const contents = fs.readFileSync(resolvedPath, 'utf8');
  const doc = yaml.load(contents) as any;
  const items = (doc?.flags ?? {}) as Record<string, { default?: boolean }>;
  flags = Object.fromEntries(
    Object.entries(items).map(([key, value]) => [key, Boolean(value?.default)])
  );
}

export function isEnabled(name: string): boolean {
  const envKey = `FLAG_${name.toUpperCase()}`;
  if (process.env[envKey] !== undefined) {
    return process.env[envKey]!.toLowerCase() === 'true';
  }
  return flags[name] ?? false;
}

loadFlags();
