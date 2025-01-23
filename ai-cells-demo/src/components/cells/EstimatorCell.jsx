import React, { useState } from 'react';
import { FileSpreadsheet, Loader2 } from 'lucide-react';
import { useChatStore } from '../../store/chatStore';


const formatExcelDataAsMarkdown = (data) => {
    // Extract headers
    const headers = Object.keys(data[0]);
    
    // Create Markdown table
    const headerRow = `| ${headers.join(' | ')} |`;
    const separator = `| ${headers.map(() => '---').join(' | ')} |`;
    
    const dataRows = data.map(row => 
      `| ${headers.map(header => row[header]).join(' | ')} |`
    );
  
    return [headerRow, separator, ...dataRows].join('\n');
  };


const EstimatorCell = () => { 
  const [loading, setLoading] = useState(false);
  const [excelData, setExcelData] = useState(null);
  const [error, setError] = useState(null);

  const handleEstimate = async () => {
    setLoading(true);
    setError(null);
    setExcelData(null);

    try {
      const response = await fetch('/api/cells/estimator/calculate/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          cdpFilePath: localStorage.getItem('cdp_output_path'),
          annualReportFilePath: localStorage.getItem('annual_report_output_path')
        })
      });

      if (!response.ok) {
        throw new Error('Failed to generate estimate');
      }

      const data = await response.json();
      setExcelData(data.excelData);

      const sampleExcelData = [
        {
          "Quarter": "Q1 2024",
          "Revenue": 500000,
          "Cost": 350000,
          "Margin": 150000,
          "Margin %": "30%"
        },
        {
          "Quarter": "Q2 2024",
          "Revenue": 600000,
          "Cost": 400000,
          "Margin": 200000,
          "Margin %": "33.3%"
        },
        {
          "Quarter": "Q3 2024",
          "Revenue": 750000,
          "Cost": 450000,
          "Margin": 300000,
          "Margin %": "40%"
        }
      ];

      useChatStore.getState().addMessage(
        `## Estimation Results\n\n${formatExcelDataAsMarkdown(sampleExcelData)}`, 
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
            <span>Generating Estimate...</span>
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

      {excelData && renderExcelTable()}
    </div>
  );
};

export default EstimatorCell;