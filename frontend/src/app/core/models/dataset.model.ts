export interface Dataset {
  id: string;
  original_name: string;
  file_size: number | null;
  row_count: number | null;
  columns: Record<string, string> | null;
  status: 'pending' | 'processed' | 'error';
  error_msg: string | null;
  upload_date: string;
}

export interface DatasetPreview {
  columns: string[];
  sample_rows: Record<string, unknown>[];
  stats: Record<string, unknown>;
  missing_required: string[];
}
