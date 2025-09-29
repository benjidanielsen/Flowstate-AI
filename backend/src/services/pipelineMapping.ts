export type PipelineVocabulary = 'frazer' | 'recruiting' | 'sales';

const frazerBuckets = [
  'New Lead',
  'Relationship Building',
  'Invited',
  'Qualified',
  'Video Sent',
  'Follow-up',
  'Signed-up'
] as const;

const recruitingBuckets = [
  'New', 'Qualified', 'Booked', 'Held', 'Joined', 'Lost', 'No-Show'
] as const;

const salesBuckets = [
  'New', 'Qualified', 'Booked', 'Held', 'Won', 'Lost', 'No-Show'
] as const;

// Map canonical statuses -> bucket for each vocabulary
const canonicalToFrazer: Record<string, typeof frazerBuckets[number]> = {
  'Lead': 'New Lead',
  'Relationship': 'Relationship Building',
  'Invited': 'Invited',
  'Qualified': 'Qualified',
  'Presentation Sent': 'Video Sent',
  'Follow-up': 'Follow-up',
  'SIGNED-UP': 'Signed-up',
};

const canonicalToRecruiting: Record<string, typeof recruitingBuckets[number]> = {
  'Lead': 'New',
  'Relationship': 'New',
  'Invited': 'Qualified',
  'Qualified': 'Qualified',
  'Presentation Sent': 'Booked',
  'Follow-up': 'Held',
  'SIGNED-UP': 'Joined',
};

const canonicalToSales: Record<string, typeof salesBuckets[number]> = {
  'Lead': 'New',
  'Relationship': 'New',
  'Invited': 'Qualified',
  'Qualified': 'Qualified',
  'Presentation Sent': 'Booked',
  'Follow-up': 'Held',
  'SIGNED-UP': 'Won',
};

export function aggregateCountsByVocabulary(
  canonicalCounts: Record<string, number>,
  vocab: PipelineVocabulary
) {
  let buckets: string[];
  let mapper: Record<string, string>;
  switch (vocab) {
    case 'frazer':
      buckets = [...frazerBuckets];
      mapper = canonicalToFrazer;
      break;
    case 'recruiting':
      buckets = [...recruitingBuckets];
      mapper = canonicalToRecruiting;
      break;
    case 'sales':
      buckets = [...salesBuckets];
      mapper = canonicalToSales;
      break;
  }
  const result: Record<string, number> = {};
  for (const b of buckets) result[b] = 0;
  for (const [canon, count] of Object.entries(canonicalCounts)) {
    const target = mapper[canon];
    if (target in result) result[target] += count;
  }
  return result;
}

