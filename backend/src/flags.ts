import fs from 'fs';
import yaml from 'js-yaml';

type FlagMap = Record<string, boolean>;
let flags: FlagMap = {};

export function loadFlags(path = 'config/flags.yaml') {
  const contents = fs.readFileSync(path, 'utf8');
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
