import React, { useState } from 'react';
import { Upload, Loader2, FileText, X } from 'lucide-react';
import { useChatStore } from '../../store/chatStore';
import { getSessionId } from '../sessionUtils';

const AnnualReportExtractorCell = () => { 
  const { addMessage } = useChatStore();
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleFileChange = (e) => {
    const selectedFiles = Array.from(e.target.files)
      .filter(file => file.type === 'application/pdf');

    if (selectedFiles.length !== e.target.files.length) {
      setError('Only PDF files are allowed');
    }

    setFiles(prev => [...prev, ...selectedFiles]);
  };

  const removeFile = (index) => {
    setFiles(files.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (files.length === 0) return;

    setLoading(true);
    setError(null);

    const formData = new FormData();
    files.forEach(file => {
      formData.append('files', file);
    });
    formData.append('session_id', getSessionId());

    try {
      const response = await fetch('/api/cells/annual_report_extractor/', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || 'Failed to process files');
      }

      setFiles([]);
      await addMessage(`Your Annual Reports have been processed successfully!<br><br> It available at <em>${data.data.output_path}</em>`,'ai');
      
      return {
        success: true,
        message: data.message,
        filePaths: data.filePaths
      };

    } catch (err) {
      const msg = err.message || 'Failed to process files';
      setError(msg);
      await addMessage(msg,'ai');
      return {
        success: false,
        error: err.message
      };
    } finally {
      setLoading(false);
    }
  };

  const truncateFileName = (fileName, maxLength = 14) => {
    if (fileName.length <= maxLength) return fileName;
    
    const extension = fileName.split('.').pop();
    const nameWithoutExt = fileName.slice(0, fileName.lastIndexOf('.'));
    const truncatedName = nameWithoutExt.slice(0, maxLength - extension.length - 3);
    
    return `${truncatedName}...${extension}`;
  };

  return (
    <div className="p-2 space-y-2">
      <form onSubmit={handleSubmit} className="space-y-2">
        <div className="grid grid-cols-1 gap-2">
          <div className="relative">
            <input
              type="file"
              onChange={handleFileChange}
              multiple
              accept=".pdf"
              className="hidden"
              id="annual-report-upload"
              disabled={loading}
            />
            <label
              htmlFor="annual-report-upload"
              className="flex items-center justify-center w-full p-2 border-2 border-dashed rounded-md cursor-pointer hover:border-primary transition-colors"
            >
              <Upload className="w-4 h-4 mr-2 text-muted-foreground" />
              <span className="text-sm text-muted-foreground">
                {files.length > 0 ? 'Add more PDFs' : 'Upload Reports'}
              </span>
            </label>
          </div>

          {files.length > 0 && (
            <button
              type="submit"
              disabled={loading}
              className="w-full flex items-center justify-center px-4 py-2 rounded-md font-medium bg-primary hover:bg-primary/90 text-primary-foreground disabled:cursor-not-allowed disabled:opacity-50"
            >
              {loading ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  <span>Processing...</span>
                </>
              ) : (
                <>
                  <FileText className="h-4 w-4 mr-2" />
                  <span>Process PDFs</span>
                </>
              )}
            </button>
          )}
        </div>

        {files.length > 0 && (
          <div className="space-y-2 max-h-40 overflow-y-auto">
            {files.map((file, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-2 bg-muted rounded-md"
              >
                <div className="flex items-center space-x-2 min-w-0 flex-1">
                  <FileText className="w-4 h-4 flex-shrink-0" />
                  <span className="text-sm truncate" title={file.name}>
                    {truncateFileName(file.name)}
                  </span>
                </div>
                <button
                  type="button"
                  onClick={() => removeFile(index)}
                  className="p-1 hover:bg-background rounded-full flex-shrink-0 ml-2"
                  title="Remove file"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        )}
      </form>

      {error && (
        <div className="p-3 rounded-md bg-destructive/10 text-destructive text-sm">
          {error}
        </div>
      )}
    </div>
  );
};

export default AnnualReportExtractorCell;