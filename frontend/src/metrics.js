/**
 * Per-response metrics, mirroring scripts/score_context_file.py.
 * Classifies a question into a rubric section, then derives:
 *   - context_perfect status for that section (always SUPPORTED here)
 *   - how many of the 5 peer context files would be RISKY/MISSING on it
 *   - grounding signals in the response text
 */

// Mirrors SECTION_KEYWORDS in scripts/score_context_file.py — same keyword
// sets used to classify both context files and incoming questions.
export const SECTION_KEYWORDS = {
  schema: [
    'schema', 'column', 'columns', 'field', 'fields',
    'attribute', 'attributes', 'definition', 'definitions',
    'type', 'dataset structure',
  ],
  statistics: [
    'statistics', 'total', 'records', 'features', 'count', 'counts',
    'percentage', 'percent', 'top values', 'distribution', 'how many',
    'row count', 'number of',
  ],
  coverage: [
    'coverage', 'country', 'countries', 'geographic', 'source',
    'sources', 'theme', 'themes', 'availability', 'varies', 'where',
  ],
  missing_data: [
    'missing', 'missing values', 'missingness', 'null', 'nulls',
    'incomplete', 'unavailable', 'empty', 'blank',
  ],
  version: [
    'release', 'version', 'generated', 'date', 'month', 'when',
  ],
  examples: [
    'example', 'examples', 'prompt', 'prompts',
    'query', 'queries', 'user:',
  ],
  unsupported_guidance: [
    'why', 'cause', 'reason', 'because', 'speculate',
  ],
}

export const SECTION_LABELS = {
  schema:               'Schema',
  statistics:           'Statistics',
  coverage:             'Coverage',
  missing_data:         'Missing data',
  version:              'Versioning',
  examples:             'Example queries',
  unsupported_guidance: 'Unsupported / causal',
}

export function classifyQuestion(text) {
  const low = text.toLowerCase()
  let best = { section: 'statistics', hits: [], score: 0 }
  for (const [section, kws] of Object.entries(SECTION_KEYWORDS)) {
    const hits = kws.filter((k) => low.includes(k))
    if (hits.length > best.score) {
      best = { section, hits, score: hits.length }
    }
  }
  return best
}

const RISK_WORDS = [
  'likely', 'probably', 'may be', 'could be', 'seems', 'appears',
  'typically', 'usually', 'often', 'suggests', 'might',
]

const REFUSAL_PHRASES = [
  'does not provide', 'not stated', 'unavailable', 'cannot answer',
  'not enough information', 'do not have', 'is not specified',
  'no information', 'cannot determine',
]

export function scoreResponse(answer) {
  const low = (answer || '').toLowerCase()
  const numbers = (answer.match(/\b\d{1,3}(,\d{3})+|\b\d{3,}\b/g) || [])
  const refused = REFUSAL_PHRASES.some((p) => low.includes(p))
  const speculation = RISK_WORDS.filter((w) => low.includes(w))
  return {
    numbersCited: numbers.length,
    refused,
    speculationHits: speculation,
  }
}

/**
 * Given scores.json (list of per-file results), summarize how a given
 * rubric section fares across the 5 peer context files (excluding
 * context_perfect, which is the system context).
 */
export function peerStatusForSection(scoresJson, section) {
  const peers = scoresJson.filter(
    (f) => !f.file.toLowerCase().includes('context_perfect')
  )
  const byStatus = { SUPPORTED: 0, RISKY: 0, UNKNOWN: 0 }
  // section -> question id, mirrors QUESTION_SECTION in score_context_file.py
  const sectionToQid = {
    schema:               'q1_schema',
    statistics:           'q2_statistics',
    coverage:             'q3_coverage',
    missing_data:         'q4_missing_data',
    version:              'q5_version',
    examples:             'q6_prompt_examples',
    unsupported_guidance: 'q7_unsupported',
  }
  const qid = sectionToQid[section]
  for (const file of peers) {
    const status = file.statuses?.[qid] || 'UNKNOWN'
    if (status in byStatus) byStatus[status] += 1
  }
  return { peers: peers.length, ...byStatus }
}
