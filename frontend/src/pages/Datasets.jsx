// ============================================================
// IMPORTS
// ============================================================

import { useEffect, useRef, useState } from 'react';
import { useParams } from 'react-router-dom';

import authApi from '../api/auth_api';
import { getProjectDatasets } from '../api/project_data_api';

// ============================================================
// DATASETS PAGE
// ============================================================

function Datasets() {
  const { workspaceId, projectId } = useParams();

  const fileInputRef = useRef(null);

  // ==========================================================
  // STATE: FILE UPLOAD
  // ==========================================================

  const [selectedFile, setSelectedFile] = useState(null);
  const [dragging, setDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  // ==========================================================
  // STATE: DATASETS
  // ==========================================================

  const [datasets, setDatasets] = useState([]);
  const [loadingDatasets, setLoadingDatasets] = useState(true);

  // ==========================================================
  // STATE: DATASET DETAILS
  // ==========================================================

  const [selectedDataset, setSelectedDataset] = useState(null);
  const [previewData, setPreviewData] = useState(null);
  const [profileData, setProfileData] = useState(null);

  const [loadingPreview, setLoadingPreview] = useState(false);
  const [loadingProfile, setLoadingProfile] = useState(false);

  // ==========================================================
  // STATE: MESSAGES
  // ==========================================================

  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  // ==========================================================
  // ERROR HANDLER
  // ==========================================================

  const getErrorMessage = (error, fallbackMessage) => {
    const detail = error?.response?.data?.detail;

    if (typeof detail === 'string') {
      return detail;
    }

    if (Array.isArray(detail)) {
      return detail.map((item) => item?.msg || fallbackMessage).join(', ');
    }

    return fallbackMessage;
  };

  // ==========================================================
  // DATASET LOADING
  // ==========================================================

  const loadDatasets = async () => {
    if (!workspaceId || !projectId) {
      setError('Workspace or project information is missing.');
      setLoadingDatasets(false);
      return;
    }

    try {
      setLoadingDatasets(true);
      setError('');

      const data = await getProjectDatasets(
        Number(projectId),
        Number(workspaceId),
      );

      setDatasets(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error('Dataset loading failed:', error);

      setError(getErrorMessage(error, 'Failed to load datasets.'));
    } finally {
      setLoadingDatasets(false);
    }
  };

  // ==========================================================
  // INITIAL DATASET LOAD
  // ==========================================================

  useEffect(() => {
    loadDatasets();
  }, [workspaceId, projectId]);

  // ==========================================================
  // FILE VALIDATION
  // ==========================================================

  const validateFile = (file) => {
    if (!file) {
      return 'Please select a file.';
    }

    if (!file.name.toLowerCase().endsWith('.csv')) {
      return 'Only CSV files are allowed.';
    }

    const maxSize = 50 * 1024 * 1024;

    if (file.size > maxSize) {
      return 'File size must be less than 50 MB.';
    }

    if (file.size === 0) {
      return 'The selected CSV file is empty.';
    }

    return '';
  };

  // ==========================================================
  // FILE SELECTION
  // ==========================================================

  const handleFileSelect = (file) => {
    setMessage('');
    setError('');

    const validationError = validateFile(file);

    if (validationError) {
      setSelectedFile(null);
      setError(validationError);
      return;
    }

    setSelectedFile(file);
  };

  // ==========================================================
  // FILE INPUT HANDLER
  // ==========================================================

  const handleInputChange = (event) => {
    const file = event.target.files?.[0];

    handleFileSelect(file);
  };

  // ==========================================================
  // DRAG AND DROP
  // ==========================================================

  const handleDrop = (event) => {
    event.preventDefault();

    setDragging(false);

    if (uploading) {
      return;
    }

    const file = event.dataTransfer.files?.[0];

    handleFileSelect(file);
  };

  // ==========================================================
  // DATASET UPLOAD
  // ==========================================================

  const handleUpload = async () => {
    if (!selectedFile) {
      setError('Please select a CSV file first.');
      return;
    }

    if (!workspaceId || !projectId) {
      setError('Workspace or project information is missing.');
      return;
    }

    try {
      setUploading(true);
      setUploadProgress(0);
      setMessage('');
      setError('');

      const formData = new FormData();

      formData.append('file', selectedFile);

      const response = await authApi.post('/datasets/upload', formData, {
        params: {
          project_id: Number(projectId),
          workspace_id: Number(workspaceId),
        },

        onUploadProgress: (progressEvent) => {
          if (!progressEvent.total) {
            return;
          }

          const progress = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total,
          );

          setUploadProgress(progress);
        },
      });

      setUploadProgress(100);

      setMessage(`Dataset "${response.data.name}" uploaded successfully.`);

      setSelectedFile(null);

      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }

      await loadDatasets();
    } catch (error) {
      console.error('Dataset upload failed:', error);

      setError(getErrorMessage(error, 'Failed to upload dataset.'));
    } finally {
      setUploading(false);
    }
  };

  // ==========================================================
  // DATASET PREVIEW
  // ==========================================================

  const handlePreview = async (dataset) => {
    if (!workspaceId || !projectId) {
      setError('Workspace or project information is missing.');
      return;
    }

    try {
      setSelectedDataset(dataset);

      setPreviewData(null);
      setProfileData(null);

      setLoadingPreview(true);

      setError('');
      setMessage('');
    } catch (error) {
      console.error('Dataset preview setup failed:', error);
      setError('Failed to prepare dataset preview.');
      return;
    }

    try {
      const response = await authApi.get(`/datasets/${dataset.id}/preview`, {
        params: {
          project_id: Number(projectId),
          workspace_id: Number(workspaceId),
        },
      });

      setPreviewData(response.data);
    } catch (error) {
      console.error('Dataset preview failed:', error);

      setError(getErrorMessage(error, 'Failed to load dataset preview.'));

      setSelectedDataset(null);
    } finally {
      setLoadingPreview(false);
    }
  };

  // ==========================================================
  // DATASET PROFILE
  // ==========================================================

  const handleProfile = async (dataset) => {
    if (!workspaceId || !projectId) {
      setError('Workspace or project information is missing.');
      return;
    }

    try {
      setSelectedDataset(dataset);

      setPreviewData(null);
      setProfileData(null);

      setLoadingProfile(true);

      setError('');
      setMessage('');

      const response = await authApi.get(`/datasets/${dataset.id}/profile`, {
        params: {
          project_id: Number(projectId),
          workspace_id: Number(workspaceId),
        },
      });

      setProfileData(response.data);
    } catch (error) {
      console.error('Dataset profiling failed:', error);

      setError(getErrorMessage(error, 'Failed to generate dataset profile.'));

      setSelectedDataset(null);
    } finally {
      setLoadingProfile(false);
    }
  };

  // ==========================================================
  // CLOSE DATASET DETAILS
  // ==========================================================

  const closeDatasetDetails = () => {
    setSelectedDataset(null);
    setPreviewData(null);
    setProfileData(null);

    setLoadingPreview(false);
    setLoadingProfile(false);
  };

  // ==========================================================
  // PROFILE VALUE FORMATTER
  // ==========================================================

  const renderProfileValue = (value) => {
    if (value === null || value === undefined) {
      return '—';
    }

    if (typeof value === 'number') {
      return Number.isInteger(value) ? value : Number(value.toFixed(2));
    }

    return String(value);
  };

  // ==========================================================
  // RENDER: PAGE
  // ==========================================================

  return (
    <div className='min-h-screen bg-stone-50 px-4 py-8 text-slate-900 sm:px-6 lg:px-8'>
      <div className='mx-auto max-w-6xl'>
        {/* ====================================================
            1. PAGE HEADER
        ===================================================== */}

        <div className='mb-8'>
          <p className='text-xs font-semibold uppercase tracking-[0.18em] text-slate-400'>
            DataPulse
          </p>

          <h1 className='mt-2 text-3xl font-bold tracking-tight text-slate-950'>
            Datasets
          </h1>

          <p className='mt-2 max-w-2xl text-sm leading-6 text-slate-500'>
            Upload and manage the datasets connected to this project.
          </p>
        </div>

        {/* ====================================================
            2. UPLOAD DATASET
        ===================================================== */}

        <div className='rounded-3xl border border-stone-200 bg-white p-6 shadow-sm sm:p-8'>
          <h2 className='text-lg font-semibold text-slate-900'>
            Upload Dataset
          </h2>

          <p className='mt-1 text-sm text-slate-500'>
            Upload a CSV file to start analyzing your data.
          </p>

          {/* --------------------------------------------------
              2.1 DRAG AND DROP
          --------------------------------------------------- */}

          <div
            onDragEnter={(event) => {
              event.preventDefault();

              if (!uploading) {
                setDragging(true);
              }
            }}
            onDragOver={(event) => {
              event.preventDefault();

              if (!uploading) {
                setDragging(true);
              }
            }}
            onDragLeave={(event) => {
              event.preventDefault();
              setDragging(false);
            }}
            onDrop={handleDrop}
            className={`mt-6 rounded-2xl border-2 border-dashed p-10 text-center transition ${
              dragging
                ? 'border-slate-500 bg-slate-50'
                : 'border-stone-300 bg-stone-50'
            }`}
          >
            <div className='mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-white text-2xl shadow-sm'>
              ↑
            </div>

            <h3 className='mt-5 text-lg font-semibold text-slate-900'>
              Drop your CSV file here
            </h3>

            <p className='mt-2 text-sm text-slate-500'>
              or choose a file from your computer
            </p>

            <button
              type='button'
              onClick={() => fileInputRef.current?.click()}
              disabled={uploading}
              className='mt-6 rounded-xl bg-slate-900 px-5 py-2.5 text-sm font-medium text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50'
            >
              Choose CSV
            </button>

            <input
              ref={fileInputRef}
              type='file'
              accept='.csv,text/csv'
              onChange={handleInputChange}
              disabled={uploading}
              className='hidden'
            />

            <p className='mt-4 text-xs text-slate-400'>
              CSV files only · Maximum 50 MB
            </p>
          </div>

          {/* --------------------------------------------------
              2.2 SELECTED FILE
          --------------------------------------------------- */}

          {selectedFile && (
            <div className='mt-6 rounded-2xl border border-stone-200 bg-stone-50 p-4'>
              <div className='flex items-center justify-between gap-4'>
                <div className='min-w-0'>
                  <p className='truncate text-sm font-semibold text-slate-800'>
                    {selectedFile.name}
                  </p>

                  <p className='mt-1 text-xs text-slate-500'>
                    {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>

                <button
                  type='button'
                  disabled={uploading}
                  onClick={() => {
                    setSelectedFile(null);
                    setError('');

                    if (fileInputRef.current) {
                      fileInputRef.current.value = '';
                    }
                  }}
                  className='shrink-0 rounded-lg border border-stone-200 bg-white px-3 py-2 text-xs font-medium text-slate-600 hover:bg-stone-100 disabled:cursor-not-allowed disabled:opacity-50'
                >
                  Remove
                </button>
              </div>
            </div>
          )}

          {/* --------------------------------------------------
              2.3 UPLOAD PROGRESS
          --------------------------------------------------- */}

          {uploading && (
            <div className='mt-5 rounded-2xl border border-stone-200 bg-stone-50 p-4'>
              <div className='flex items-center justify-between text-sm'>
                <span className='font-medium text-slate-700'>
                  Uploading dataset...
                </span>

                <span className='font-semibold text-slate-900'>
                  {uploadProgress}%
                </span>
              </div>

              <div className='mt-3 h-2 overflow-hidden rounded-full bg-stone-200'>
                <div
                  className='h-full rounded-full bg-slate-900 transition-all duration-200'
                  style={{
                    width: `${uploadProgress}%`,
                  }}
                />
              </div>
            </div>
          )}

          {/* --------------------------------------------------
              2.4 ERROR
          --------------------------------------------------- */}

          {error && (
            <div className='mt-5 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700'>
              {error}
            </div>
          )}

          {/* --------------------------------------------------
              2.5 SUCCESS
          --------------------------------------------------- */}

          {message && (
            <div className='mt-5 rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700'>
              {message}
            </div>
          )}

          {/* --------------------------------------------------
              2.6 UPLOAD BUTTON
          --------------------------------------------------- */}

          <div className='mt-6 flex justify-end'>
            <button
              type='button'
              onClick={handleUpload}
              disabled={!selectedFile || uploading}
              className='rounded-xl bg-slate-900 px-5 py-2.5 text-sm font-medium text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50'
            >
              {uploading ? `Uploading ${uploadProgress}%` : 'Upload Dataset'}
            </button>
          </div>
        </div>

        {/* ====================================================
            3. DATASET LIST
        ===================================================== */}

        <div className='mt-8'>
          <div className='mb-4 flex items-center justify-between'>
            <div>
              <h2 className='text-xl font-semibold text-slate-950'>
                Your Datasets
              </h2>

              <p className='mt-1 text-sm text-slate-500'>
                Datasets currently connected to this project.
              </p>
            </div>

            <span className='rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-600'>
              {datasets.length} {datasets.length === 1 ? 'dataset' : 'datasets'}
            </span>
          </div>

          {/* --------------------------------------------------
              3.1 DATASET LOADING
          --------------------------------------------------- */}

          {loadingDatasets ? (
            <div className='rounded-2xl border border-stone-200 bg-white p-8 text-center shadow-sm'>
              <div className='mx-auto h-7 w-7 animate-spin rounded-full border-4 border-stone-200 border-t-slate-700' />

              <p className='mt-3 text-sm text-slate-500'>Loading datasets...</p>
            </div>
          ) : datasets.length === 0 ? (
            /* ------------------------------------------------
               3.2 EMPTY DATASET STATE
            ------------------------------------------------- */

            <div className='rounded-2xl border border-dashed border-stone-300 bg-white p-10 text-center'>
              <p className='text-sm font-medium text-slate-700'>
                No datasets yet
              </p>

              <p className='mt-1 text-sm text-slate-500'>
                Upload your first CSV file to start analyzing data.
              </p>
            </div>
          ) : (
            /* ------------------------------------------------
               3.3 DATASET TABLE
            ------------------------------------------------- */

            <div className='overflow-hidden rounded-2xl border border-stone-200 bg-white shadow-sm'>
              <div className='divide-y divide-stone-100'>
                {datasets.map((dataset) => (
                  <div
                    key={dataset.id}
                    className='flex flex-col gap-4 p-5 transition hover:bg-stone-50 sm:flex-row sm:items-center sm:justify-between'
                  >
                    <div className='min-w-0'>
                      <h3 className='truncate text-sm font-semibold text-slate-900'>
                        {dataset.name}
                      </h3>

                      <div className='mt-2 flex flex-wrap gap-x-4 gap-y-1 text-xs text-slate-500'>
                        <span>Dataset ID: {dataset.id}</span>

                        <span>Project ID: {dataset.project_id}</span>

                        {dataset.created_at && (
                          <span>
                            Uploaded:{' '}
                            {new Date(dataset.created_at).toLocaleString()}
                          </span>
                        )}
                      </div>
                    </div>

                    <div className='flex shrink-0 items-center gap-3'>
                      <button
                        type='button'
                        onClick={() => handlePreview(dataset)}
                        disabled={loadingPreview || loadingProfile}
                        className='rounded-lg border border-stone-200 bg-white px-3 py-1.5 text-xs font-medium text-slate-700 transition hover:bg-stone-100 disabled:cursor-not-allowed disabled:opacity-50'
                      >
                        Preview
                      </button>

                      <button
                        type='button'
                        onClick={() => handleProfile(dataset)}
                        disabled={loadingPreview || loadingProfile}
                        className='rounded-lg bg-slate-900 px-3 py-1.5 text-xs font-medium text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50'
                      >
                        Profile
                      </button>

                      <span className='rounded-lg bg-emerald-50 px-3 py-1.5 text-xs font-medium text-emerald-700'>
                        Ready
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* ====================================================
            4. DATASET DETAILS
        ===================================================== */}

        {selectedDataset && (
          <div className='mt-8 rounded-3xl border border-stone-200 bg-white shadow-sm'>
            {/* ------------------------------------------------
                4.1 DETAILS HEADER
            ------------------------------------------------- */}

            <div className='flex flex-col gap-4 border-b border-stone-200 p-6 sm:flex-row sm:items-center sm:justify-between'>
              <div>
                <p className='text-xs font-semibold uppercase tracking-[0.16em] text-slate-400'>
                  {profileData ? 'Dataset Profile' : 'Dataset Preview'}
                </p>

                <h2 className='mt-1 text-xl font-semibold text-slate-950'>
                  {selectedDataset.name}
                </h2>

                {/* --------------------------------------------
                    4.1.1 PREVIEW SUMMARY
                --------------------------------------------- */}

                {previewData && (
                  <div className='mt-2 flex flex-wrap gap-2'>
                    <span className='rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600'>
                      {previewData.row_count} rows
                    </span>

                    <span className='rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600'>
                      {previewData.columns?.length || 0} columns
                    </span>
                  </div>
                )}

                {/* --------------------------------------------
                    4.1.2 PROFILE SUMMARY
                --------------------------------------------- */}

                {profileData?.profile?.summary && (
                  <div className='mt-3 flex flex-wrap gap-2'>
                    <span className='rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600'>
                      {profileData.profile.summary.row_count} rows
                    </span>

                    <span className='rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600'>
                      {profileData.profile.summary.column_count} columns
                    </span>

                    <span className='rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600'>
                      {profileData.profile.summary.duplicate_rows.count}{' '}
                      duplicate rows
                    </span>
                  </div>
                )}
              </div>

              {/* ------------------------------------------------
                  4.1.3 CLOSE
              ------------------------------------------------- */}

              <button
                type='button'
                onClick={closeDatasetDetails}
                className='self-start rounded-lg border border-stone-200 bg-white px-3 py-2 text-xs font-medium text-slate-600 transition hover:bg-stone-100 sm:self-auto'
              >
                Close
              </button>
            </div>

            {/* ==================================================
                4.2 LOADING: PREVIEW
            ================================================== */}

            {loadingPreview ? (
              <div className='p-10 text-center'>
                <div className='mx-auto h-7 w-7 animate-spin rounded-full border-4 border-stone-200 border-t-slate-700' />

                <p className='mt-3 text-sm text-slate-500'>
                  Loading dataset preview...
                </p>
              </div>
            ) : loadingProfile ? (
              /* =================================================
                 4.3 LOADING: PROFILE
              ================================================= */

              <div className='p-10 text-center'>
                <div className='mx-auto h-7 w-7 animate-spin rounded-full border-4 border-stone-200 border-t-slate-700' />

                <p className='mt-3 text-sm text-slate-500'>
                  Analyzing dataset...
                </p>
              </div>
            ) : profileData?.profile ? (
              /* =================================================
                 4.4 PROFILE VIEW
              ================================================= */

              <div className='p-6'>
                {/* ----------------------------------------------
                    4.4.1 PROFILE SUMMARY CARDS
                ----------------------------------------------- */}

                <div className='grid gap-4 sm:grid-cols-2 lg:grid-cols-4'>
                  <div className='rounded-2xl bg-stone-50 p-4'>
                    <p className='text-xs font-medium uppercase tracking-wide text-slate-400'>
                      Rows
                    </p>

                    <p className='mt-2 text-2xl font-bold text-slate-950'>
                      {profileData.profile.summary.row_count}
                    </p>
                  </div>

                  <div className='rounded-2xl bg-stone-50 p-4'>
                    <p className='text-xs font-medium uppercase tracking-wide text-slate-400'>
                      Columns
                    </p>

                    <p className='mt-2 text-2xl font-bold text-slate-950'>
                      {profileData.profile.summary.column_count}
                    </p>
                  </div>

                  <div className='rounded-2xl bg-stone-50 p-4'>
                    <p className='text-xs font-medium uppercase tracking-wide text-slate-400'>
                      Duplicate Rows
                    </p>

                    <p className='mt-2 text-2xl font-bold text-slate-950'>
                      {profileData.profile.summary.duplicate_rows.count}
                    </p>

                    <p className='mt-1 text-xs text-slate-500'>
                      {profileData.profile.summary.duplicate_rows.percentage}%
                      of dataset
                    </p>
                  </div>

                  <div className='rounded-2xl bg-stone-50 p-4'>
                    <p className='text-xs font-medium uppercase tracking-wide text-slate-400'>
                      Numeric Columns
                    </p>

                    <p className='mt-2 text-2xl font-bold text-slate-950'>
                      {profileData.profile.summary.numeric_columns.length}
                    </p>
                  </div>
                </div>

                {/* =================================================
                    4.4.3 COLUMN ANALYSIS
                ================================================== */}

                <div className='mt-8'>
                  <div className='mb-4'>
                    <h3 className='text-lg font-semibold text-slate-950'>
                      Column Analysis
                    </h3>

                    <p className='mt-1 text-sm text-slate-500'>
                      Statistical and structural information for every column.
                    </p>
                  </div>

                  <div className='space-y-4'>
                    {profileData.profile.columns.map((column) => (
                      <div
                        key={column.column}
                        className='rounded-2xl border border-stone-200 bg-white p-5'
                      >
                        {/* ==================================
                              4.4.3.1 COLUMN HEADER
                          =================================== */}

                        <div className='flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between'>
                          <div>
                            <h4 className='font-semibold text-slate-900'>
                              {column.column}
                            </h4>

                            <div className='mt-2 flex flex-wrap gap-2'>
                              <span className='rounded-full bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-600'>
                                {column.data_type}
                              </span>

                              <span className='rounded-full bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-600'>
                                {Math.round(column.data_type_confidence * 100)}%
                                confidence
                              </span>

                              {column.is_constant && (
                                <span className='rounded-full bg-amber-50 px-2.5 py-1 text-xs font-medium text-amber-700'>
                                  Constant
                                </span>
                              )}

                              {column.is_high_cardinality && (
                                <span className='rounded-full bg-amber-50 px-2.5 py-1 text-xs font-medium text-amber-700'>
                                  High Cardinality
                                </span>
                              )}
                            </div>
                          </div>

                          <div className='text-sm text-slate-500'>
                            {column.unique_count} unique values
                          </div>
                        </div>

                        {/* ==================================
                              4.4.3.2 BASIC METRICS
                          =================================== */}

                        <div className='mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-4'>
                          <div className='rounded-xl bg-stone-50 p-3'>
                            <p className='text-xs text-slate-400'>Missing</p>

                            <p className='mt-1 font-semibold text-slate-800'>
                              {column.missing_percentage}%
                            </p>
                          </div>

                          <div className='rounded-xl bg-stone-50 p-3'>
                            <p className='text-xs text-slate-400'>Non-null</p>

                            <p className='mt-1 font-semibold text-slate-800'>
                              {column.non_null_count}
                            </p>
                          </div>

                          <div className='rounded-xl bg-stone-50 p-3'>
                            <p className='text-xs text-slate-400'>Unique</p>

                            <p className='mt-1 font-semibold text-slate-800'>
                              {column.unique_count}
                            </p>
                          </div>

                          <div className='rounded-xl bg-stone-50 p-3'>
                            <p className='text-xs text-slate-400'>Unique %</p>

                            <p className='mt-1 font-semibold text-slate-800'>
                              {column.unique_percentage}%
                            </p>
                          </div>
                        </div>

                        {/* ==================================
                              4.4.3.3 NUMERIC STATISTICS
                          =================================== */}

                        {column.statistics && (
                          <div className='mt-5'>
                            <h5 className='text-sm font-semibold text-slate-800'>
                              Numerical Statistics
                            </h5>

                            <div className='mt-3 grid gap-3 sm:grid-cols-2 lg:grid-cols-4'>
                              <div className='rounded-xl border border-stone-200 p-3'>
                                <p className='text-xs text-slate-400'>
                                  Minimum
                                </p>

                                <p className='mt-1 font-semibold text-slate-800'>
                                  {renderProfileValue(column.statistics.min)}
                                </p>
                              </div>

                              <div className='rounded-xl border border-stone-200 p-3'>
                                <p className='text-xs text-slate-400'>
                                  Maximum
                                </p>

                                <p className='mt-1 font-semibold text-slate-800'>
                                  {renderProfileValue(column.statistics.max)}
                                </p>
                              </div>

                              <div className='rounded-xl border border-stone-200 p-3'>
                                <p className='text-xs text-slate-400'>Mean</p>

                                <p className='mt-1 font-semibold text-slate-800'>
                                  {renderProfileValue(column.statistics.mean)}
                                </p>
                              </div>

                              <div className='rounded-xl border border-stone-200 p-3'>
                                <p className='text-xs text-slate-400'>Median</p>

                                <p className='mt-1 font-semibold text-slate-800'>
                                  {renderProfileValue(column.statistics.median)}
                                </p>
                              </div>

                              <div className='rounded-xl border border-stone-200 p-3'>
                                <p className='text-xs text-slate-400'>
                                  Standard Deviation
                                </p>

                                <p className='mt-1 font-semibold text-slate-800'>
                                  {renderProfileValue(column.statistics.std)}
                                </p>
                              </div>

                              <div className='rounded-xl border border-stone-200 p-3'>
                                <p className='text-xs text-slate-400'>Q1</p>

                                <p className='mt-1 font-semibold text-slate-800'>
                                  {renderProfileValue(
                                    column.statistics.quantiles['25'],
                                  )}
                                </p>
                              </div>

                              <div className='rounded-xl border border-stone-200 p-3'>
                                <p className='text-xs text-slate-400'>
                                  Q2 / Median
                                </p>

                                <p className='mt-1 font-semibold text-slate-800'>
                                  {renderProfileValue(
                                    column.statistics.quantiles['50'],
                                  )}
                                </p>
                              </div>

                              <div className='rounded-xl border border-stone-200 p-3'>
                                <p className='text-xs text-slate-400'>Q3</p>

                                <p className='mt-1 font-semibold text-slate-800'>
                                  {renderProfileValue(
                                    column.statistics.quantiles['75'],
                                  )}
                                </p>
                              </div>
                            </div>

                            {/* --------------------------------
                                  OUTLIER ANALYSIS
                              --------------------------------- */}

                            {column.statistics.outliers && (
                              <div className='mt-4 rounded-xl border border-stone-200 p-4'>
                                <div className='flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between'>
                                  <div>
                                    <p className='text-sm font-semibold text-slate-800'>
                                      Outliers
                                    </p>

                                    <p className='mt-1 text-xs text-slate-500'>
                                      Detected using the IQR method.
                                    </p>
                                  </div>

                                  <span className='rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-700'>
                                    {column.statistics.outliers.count} outliers
                                  </span>
                                </div>

                                <div className='mt-3 grid gap-3 sm:grid-cols-3'>
                                  <div>
                                    <p className='text-xs text-slate-400'>
                                      Percentage
                                    </p>

                                    <p className='mt-1 text-sm font-semibold text-slate-800'>
                                      {column.statistics.outliers.percentage}%
                                    </p>
                                  </div>

                                  <div>
                                    <p className='text-xs text-slate-400'>
                                      Lower Bound
                                    </p>

                                    <p className='mt-1 text-sm font-semibold text-slate-800'>
                                      {renderProfileValue(
                                        column.statistics.outliers.lower_bound,
                                      )}
                                    </p>
                                  </div>

                                  <div>
                                    <p className='text-xs text-slate-400'>
                                      Upper Bound
                                    </p>

                                    <p className='mt-1 text-sm font-semibold text-slate-800'>
                                      {renderProfileValue(
                                        column.statistics.outliers.upper_bound,
                                      )}
                                    </p>
                                  </div>
                                </div>
                              </div>
                            )}
                          </div>
                        )}

                        {/* ==================================
                              4.4.3.4 DATE PROFILE
                          =================================== */}

                        {column.date_profile && (
                          <div className='mt-5'>
                            <h5 className='text-sm font-semibold text-slate-800'>
                              Date Profile
                            </h5>

                            <div className='mt-3 grid gap-3 sm:grid-cols-2 lg:grid-cols-4'>
                              <div className='rounded-xl border border-stone-200 p-3'>
                                <p className='text-xs text-slate-400'>
                                  Earliest
                                </p>

                                <p className='mt-1 text-sm font-semibold text-slate-800'>
                                  {renderProfileValue(column.date_profile.min)}
                                </p>
                              </div>

                              <div className='rounded-xl border border-stone-200 p-3'>
                                <p className='text-xs text-slate-400'>Latest</p>

                                <p className='mt-1 text-sm font-semibold text-slate-800'>
                                  {renderProfileValue(column.date_profile.max)}
                                </p>
                              </div>

                              <div className='rounded-xl border border-stone-200 p-3'>
                                <p className='text-xs text-slate-400'>Range</p>

                                <p className='mt-1 text-sm font-semibold text-slate-800'>
                                  {renderProfileValue(
                                    column.date_profile.range_days,
                                  )}{' '}
                                  days
                                </p>
                              </div>

                              <div className='rounded-xl border border-stone-200 p-3'>
                                <p className='text-xs text-slate-400'>
                                  Frequency
                                </p>

                                <p className='mt-1 text-sm font-semibold capitalize text-slate-800'>
                                  {renderProfileValue(
                                    column.date_profile.frequency,
                                  )}
                                </p>
                              </div>
                            </div>
                          </div>
                        )}

                        {/* ==================================
                              4.4.3.5 CATEGORICAL PROFILE
                          =================================== */}

                        {column.categorical_profile?.top_values?.length > 0 && (
                          <div className='mt-5'>
                            <div className='flex items-center justify-between gap-4'>
                              <div>
                                <h5 className='text-sm font-semibold text-slate-800'>
                                  Top Values
                                </h5>

                                <p className='mt-1 text-xs text-slate-500'>
                                  Most frequent values in this column.
                                </p>
                              </div>

                              <span className='text-xs text-slate-400'>
                                Top 10
                              </span>
                            </div>

                            <div className='mt-3 overflow-hidden rounded-xl border border-stone-200'>
                              <div className='divide-y divide-stone-100'>
                                {column.categorical_profile.top_values.map(
                                  (item, index) => (
                                    <div
                                      key={`${column.column}-${item.value}-${index}`}
                                      className='flex items-center justify-between gap-4 px-4 py-3'
                                    >
                                      <span className='min-w-0 truncate text-sm font-medium text-slate-700'>
                                        {item.value}
                                      </span>

                                      <div className='flex shrink-0 items-center gap-3'>
                                        <span className='text-xs text-slate-400'>
                                          {item.percentage}%
                                        </span>

                                        <span className='min-w-10 rounded-md bg-slate-100 px-2 py-1 text-center text-xs font-semibold text-slate-600'>
                                          {item.count}
                                        </span>
                                      </div>
                                    </div>
                                  ),
                                )}
                              </div>
                            </div>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ) : previewData ? (
              /* =================================================
                 4.5 PREVIEW VIEW
              ================================================= */

              <div className='p-6'>
                <div className='overflow-x-auto rounded-2xl border border-stone-200'>
                  <table className='min-w-full text-left text-sm'>
                    <thead className='bg-stone-50'>
                      <tr>
                        {previewData.columns.map((column) => (
                          <th
                            key={column}
                            className='whitespace-nowrap border-b border-stone-200 px-4 py-3 text-xs font-semibold uppercase tracking-wide text-slate-500'
                          >
                            {column}
                          </th>
                        ))}
                      </tr>
                    </thead>

                    <tbody className='divide-y divide-stone-100'>
                      {previewData.preview?.length === 0 ? (
                        <tr>
                          <td
                            colSpan={previewData.columns?.length || 1}
                            className='px-4 py-8 text-center text-sm text-slate-500'
                          >
                            No preview rows available.
                          </td>
                        </tr>
                      ) : (
                        previewData.preview.map((row, rowIndex) => (
                          <tr
                            key={rowIndex}
                            className='transition hover:bg-stone-50'
                          >
                            {previewData.columns.map((column) => (
                              <td
                                key={column}
                                className='whitespace-nowrap px-4 py-3 text-slate-700'
                              >
                                {row[column] === null ||
                                row[column] === undefined
                                  ? '—'
                                  : String(row[column])}
                              </td>
                            ))}
                          </tr>
                        ))
                      )}
                    </tbody>
                  </table>
                </div>

                <p className='mt-3 text-xs text-slate-400'>
                  Showing the available preview rows from this dataset.
                </p>
              </div>
            ) : (
              /* =================================================
                 4.6 NO DETAILS
              ================================================= */

              <div className='p-10 text-center text-sm text-slate-500'>
                Dataset details are unavailable.
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

// ============================================================
// EXPORT
// ============================================================

export default Datasets;
