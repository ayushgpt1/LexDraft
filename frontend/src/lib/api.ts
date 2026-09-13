import type { GenerateResponse, ProgressEvent } from './types';

// Local FastAPI backend (backend/main.py)
export const API_BASE_URL = 'https://lexdraft-ged1.onrender.com';
export const WS_BASE_URL = API_BASE_URL
  .replace('http://', 'ws://')
  .replace('https://', 'wss://');

export const PIPELINE_STAGES = [
  'Extract Case Information',
  'Map Reply Points',
  'Generate Affidavit',
  'Validate Document',
  'Evaluate Document',
] as const;

/**
 * Reference documents preloaded with the frontend (bundled under
 * `frontend/public/reference/`). The backend POST /generate accepts a single
 * `reference_file` field, so the format/structural rules document
 * ("01 Affidavit Format Explained.pdf") is sent as that field. The sample
 * affidavit is shown as a preloaded reference only and is never uploaded.
 */
export interface PreloadedReferenceDocument {
  file_name: string;
  description: string;
  /** Path of the bundled PDF; omitted for display-only documents. */
  asset_path?: string;
}

export const PRELOADED_REFERENCE_DOCUMENTS: PreloadedReferenceDocument[] = [
  {
    file_name: '01 Affidavit Format Explained.pdf',
    description: 'Format & structural rules for the Affidavit in Reply',
    asset_path: '/reference/01 Affidavit Format Explained.pdf',
  },
  {
    file_name: '02 Affidavit in Reply Sample.docx.pdf',
    description: 'Sample Affidavit in Reply document',
  },
];

/**
 * Fetch the preloaded reference document that is sent to the backend as
 * `reference_file` and wrap it in a File for the multipart upload.
 */
export async function loadPreloadedReferenceFile(): Promise<File> {
  const doc = PRELOADED_REFERENCE_DOCUMENTS.find(
    (candidate) => candidate.asset_path !== undefined
  );

  if (!doc?.asset_path) {
    throw new Error('No preloaded reference document is configured.');
  }

  try {
    const response = await fetch(encodeURI(doc.asset_path));
    if (!response.ok) {
      throw new Error(`Request failed (HTTP ${response.status}).`);
    }
    const blob = await response.blob();
    return new File([blob], doc.file_name, { type: 'application/pdf' });
  } catch {
    throw new Error(
      `Could not load the preloaded reference document "${doc.file_name}".`
    );
  }
}

/**
 * POST /generate — multipart/form-data.
 *
 * Supports configurable reference materials per generation run:
 * - `format_file` (optional): Uploaded Format Explained PDF. If omitted,
 *   the default bundled "01 Affidavit Format Explained.pdf" is used.
 * - `sample_file` (optional): Uploaded Sample Affidavit PDF. If omitted,
 *   the default bundled "02 Affidavit in Reply Sample.docx.pdf" is used.
 * - `case_file` (required): Case Information PDF.
 *
 * A `run_id` query parameter associates the request with an open
 * /ws/progress WebSocket for live progress updates.
 */
export async function generateAffidavit(
  caseFile: File,
  formatFile?: File,
  sampleFile?: File,
  runId?: string
): Promise<GenerateResponse> {
  const formData = new FormData();
  formData.append('case_file', caseFile);

  if (formatFile) {
    formData.append('format_file', formatFile);
  }

  if (sampleFile) {
    formData.append('sample_file', sampleFile);
  }

  const query = runId ? `?run_id=${encodeURIComponent(runId)}` : '';

  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}/generate${query}`, {
      method: 'POST',
      body: formData,
    });
  } catch {
    throw new Error(
      'Could not reach the LexDraft backend. Please try again.'
    );
  }

  if (!response.ok) {
    throw new Error(await extractErrorMessage(response));
  }

  return (await response.json()) as GenerateResponse;
}

/**
 * Open the progress WebSocket for a run id and register the
 * on-message handler. `ready` resolves once the connection is open
 * (or rejects if the socket cannot be established), so callers can
 * connect BEFORE POSTing /generate and miss no stage event.
 */
export function connectProgressSocket(
  runId: string,
  onEvent: (event: ProgressEvent) => void
): { socket: WebSocket; ready: Promise<void> } {
  const socket = new WebSocket(
    `${WS_BASE_URL}/ws/progress?run_id=${encodeURIComponent(runId)}`
  );

  socket.onmessage = (event: MessageEvent) => {
    try {
      onEvent(JSON.parse(event.data) as ProgressEvent);
    } catch {
      // ignore malformed frames
    }
  };

  const ready = new Promise<void>((resolve, reject) => {
    if (socket.readyState === WebSocket.OPEN) {
      resolve();
      return;
    }

    socket.onopen = () => resolve();
    socket.onerror = () =>
      reject(new Error('Could not connect to the progress service.'));
  });

  return { socket, ready };
}

/**
 * Close the progress WebSocket if it is still open. Safe to call
 * multiple times; no-op once the socket is already closed.
 */
export function closeProgressSocket(
  socket: WebSocket | null | undefined
): void {
  if (!socket) return;
  try {
    if (
      socket.readyState === WebSocket.OPEN ||
      socket.readyState === WebSocket.CONNECTING
    ) {
      socket.close();
    }
  } catch {
    // ignore
  }
}

/**
 * GET /download — fetch the generated DOCX from the backend
 * and trigger a browser download.
 */
export async function downloadDocx(): Promise<void> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}/download`);
  } catch {
    throw new Error(
      'Could not reach the LexDraft backend. Please try again.'
    );
  }

  if (!response.ok) {
    if (response.status === 404) {
      throw new Error('No generated affidavit is available yet. Generate an affidavit first.');
    }
    throw new Error(await extractErrorMessage(response));
  }

  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = 'generated_affidavit.docx';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

async function extractErrorMessage(response: Response): Promise<string> {
  try {
    const body = (await response.json()) as { detail?: unknown };
    if (typeof body?.detail === 'string') return body.detail;
    if (body?.detail != null) return JSON.stringify(body.detail);
  } catch {
    // fall through to the generic message
  }
  return `Request failed (HTTP ${response.status}).`;
}
