import React, { useState } from 'react';
import { FileSpreadsheet, Loader2 } from 'lucide-react';
import { useChatStore } from '../../store/chatStore';
import { getSessionId } from '../sessionUtils';
import SAMPLE_DATA from './sample.json';

 
  const formatExcelDataAsMarkdown = (data, excludedColumns = []) => {
    // Extract headers and exclude unwanted columns
    const headers = Object.keys(data[0]).filter(
      (header) => !excludedColumns.includes(header)
    );
  
    // Create Markdown table
    const headerRow = `| ${headers.join(' | ')} |`;
    const separator = `| ${headers.map(() => '---').join(' | ')} |`;
  
    const dataRows = data.map((row) =>
      `| ${headers
        .map((header) => {
          // Replace newline characters in Explanation with <br> for better Markdown formatting
          const cellContent =
            header === "Explanation"
              ? row[header].replace(/\n/g, "<br>")
              : row[header];
          return cellContent;
        })
        .join(" | ")} |`
    );
  
    return [headerRow, separator, ...dataRows].join("\n");
  };
  

  const formatExcelDataAsMarkdownWithStyles = (data, excludedColumns = [], options = {}) => {
    const { tableHeight = "300px", minColumnWidth = "150px" } = options;
  
    // Extract headers and exclude unwanted columns
    const headers = Object.keys(data[0]).filter(
      (header) => !excludedColumns.includes(header)
    );
  
    // Create the table rows with a fixed column width and newline formatting
    const dataRows = data.map((row) =>
      `<tr>${headers
        .map((header) => {
          const cellContent =
            header === "Explanation"
              ? row[header].replace(/\n/g, "<br>")
              : row[header];
          return `<td style="min-width:${minColumnWidth};">${cellContent}</td>`;
        })
        .join("")}</tr>`
    );
  
    // Construct the table in HTML with scrollable div
    const tableHTML = `
    <div style="max-height: ${tableHeight}; overflow-y: auto; border: 1px solid #ccc; padding: 10px;">
      <table style="border-collapse: collapse; width: 100%; text-align: left;">
        <thead>
          <tr>
            ${headers
              .map(
                (header) =>
                  `<th style="min-width:${minColumnWidth}; border-bottom: 1px solid #ccc;">${header}</th>`
              )
              .join("")}
          </tr>
        </thead>
        <tbody>
          ${dataRows.join("\n")}
        </tbody>
      </table>
    </div>`;
  
    return tableHTML;
  };
  
  


const EstimatorCell = () => { 
  const [loading, setLoading] = useState(false);
  const [excelData, setExcelData] = useState(null);
  const [error, setError] = useState(null);

  const handleEstimate = async () => {
    setLoading(true);
    setError(null);
    //setExcelData(null);

    try {
      const response = await fetch('/api/cells/ccf_estimator/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: getSessionId()
        })
      });

      if (!response.ok) {
        throw new Error('Failed to generate estimate');
      }

      const data = await response.json();
      //setExcelData(data.excelData);
 
      console.log('Response data', data);

      useChatStore.getState().addMessage(
        `## <strong>Estimation:</strong>\n\n${formatExcelDataAsMarkdown(data.data.estimates, ["Activity", "Units"])}\n\n## <strong>Explanation:</strong>\n\n${formatExcelDataAsMarkdown(data.data.explanation, ["Activity"])}`, 
        'ai'
      );

    } catch (err) {
      //setError(err.message);
      useChatStore.getState().addMessage(
        `Estimation Error: ${err.message}`, 
        'ai'
      );
    } finally {
      setLoading(false);
    }
  };

  const renderExcelTable = () => {
    if (!excelData) return null;

    return (
      <div className="overflow-x-auto mt-4">
        <table className="w-full border-collapse">
          <thead>
            <tr>
              {Object.keys(excelData[0]).map(header => (
                <th key={header} className="border p-2 bg-muted">
                  {header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {excelData.map((row, index) => (
              <tr key={index} className="hover:bg-muted/50">
                {Object.values(row).map((cell, cellIndex) => (
                  <td key={cellIndex} className="border p-2">
                    {cell}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  return (
    <div className="p-2 space-y-2">
      <button
        onClick={handleEstimate}
        disabled={loading}
        className="w-full flex items-center justify-center px-4 py-2 rounded-md font-medium bg-primary hover:bg-primary/90 text-primary-foreground disabled:cursor-not-allowed disabled:opacity-50"
      >
        {loading ? (
          <>
            <Loader2 className="h-4 w-4 mr-2 animate-spin" />
            <span>Estimating...</span>
          </>
        ) : (
          <>
            <FileSpreadsheet className="h-4 w-4 mr-2" />
            <span>Estimate</span>
          </>
        )}
      </button>

      {error && (
        <div className="p-3 rounded-md bg-destructive/10 text-destructive text-sm">
          {error}
        </div>
      )}

      {/* {excelData && renderExcelTable()} */}
    </div>
  );
};

export default EstimatorCell;