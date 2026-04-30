import React, { useState, useEffect } from 'react';
import { getCsvFiles, getCsvData, CsvFileInfo, CsvData } from '../services/apiService';

export default function DataPage() {
    const [csvFiles, setCsvFiles] = useState<CsvFileInfo[]>([]);
    const [selectedFile, setSelectedFile] = useState<CsvFileInfo | null>(null);
    const [csvData, setCsvData] = useState<CsvData | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [currentPage, setCurrentPage] = useState(1);
    const rowsPerPage = 20;

    // 載入 CSV 檔案列表
    useEffect(() => {
        loadCsvFiles();
    }, []);

    const loadCsvFiles = async () => {
        setLoading(true);
        setError(null);
        try {
            const files = await getCsvFiles();
            setCsvFiles(files);
        } catch (err) {
            setError(err instanceof Error ? err.message : '載入檔案列表失敗');
        } finally {
            setLoading(false);
        }
    };

    const loadCsvData = async (file: CsvFileInfo) => {
        setLoading(true);
        setError(null);
        setSelectedFile(file);
        setCurrentPage(1);
        try {
            const data = await getCsvData(file.folder, file.filename);
            setCsvData(data);
        } catch (err) {
            setError(err instanceof Error ? err.message : '載入資料失敗');
            setCsvData(null);
        } finally {
            setLoading(false);
        }
    };

    // 分頁邏輯
    const totalPages = csvData ? Math.ceil(csvData.row_count / rowsPerPage) : 0;
    const startIndex = (currentPage - 1) * rowsPerPage;
    const endIndex = startIndex + rowsPerPage;
    const currentData = csvData ? csvData.data.slice(startIndex, endIndex) : [];

    // 按資料夾分組
    const groupedFiles = csvFiles.reduce((acc, file) => {
        if (!acc[file.folder]) {
            acc[file.folder] = [];
        }
        acc[file.folder].push(file);
        return acc;
    }, {} as Record<string, CsvFileInfo[]>);

    return (
        <div className="space-y-6">
            {/* 標題 */}
            <div className="text-center">
                <h2 className="text-4xl font-bold text-white mb-2">CSV 資料展示</h2>
                <p className="text-gray-400">查看所有收集到的歷史資料和技術指標</p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
                {/* 左側：檔案列表 */}
                <div className="lg:col-span-1">
                    <div className="bg-black/30 backdrop-blur-lg rounded-lg p-4 border border-white/10 sticky top-4">
                        <h3 className="text-xl font-semibold text-white mb-4">資料夾</h3>

                        {loading && csvFiles.length === 0 && (
                            <div className="flex justify-center py-8">
                                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-400"></div>
                            </div>
                        )}

                        <div className="space-y-4 max-h-[600px] overflow-y-auto">
                            {Object.entries(groupedFiles).map(([folder, files]) => (
                                <div key={folder} className="space-y-2">
                                    <div className="text-sm font-semibold text-purple-400">
                                        {folder}
                                    </div>
                                    {files.map((file) => (
                                        <button
                                            key={`${file.folder}-${file.filename}`}
                                            onClick={() => loadCsvData(file)}
                                            className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-all ${selectedFile?.folder === file.folder && selectedFile?.filename === file.filename
                                                    ? 'bg-purple-600 text-white'
                                                    : 'bg-white/5 text-gray-300 hover:bg-white/10'
                                                }`}
                                        >
                                            <div className="font-medium truncate">{file.filename}</div>
                                            <div className="text-xs text-gray-400 mt-1">
                                                {(file.size / 1024).toFixed(1)} KB
                                            </div>
                                        </button>
                                    ))}
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                {/* 右側：資料展示 */}
                <div className="lg:col-span-3">
                    {error && (
                        <div className="bg-red-500/20 border border-red-500/50 rounded-lg p-4 text-red-200 mb-4">
                            {error}
                        </div>
                    )}

                    {!selectedFile && !loading && (
                        <div className="bg-black/30 backdrop-blur-lg rounded-lg p-12 border border-white/10 text-center">
                            <div className="text-gray-400 text-lg">請選擇一個 CSV 檔案查看資料</div>
                        </div>
                    )}

                    {loading && selectedFile && (
                        <div className="bg-black/30 backdrop-blur-lg rounded-lg p-12 border border-white/10">
                            <div className="flex items-center justify-center">
                                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-400"></div>
                            </div>
                        </div>
                    )}

                    {csvData && !loading && (
                        <div className="bg-black/30 backdrop-blur-lg rounded-lg border border-white/10 overflow-hidden">
                            {/* 資料資訊 */}
                            <div className="p-4 border-b border-white/10">
                                <h3 className="text-xl font-semibold text-white mb-2">{csvData.filename}</h3>
                                <div className="flex items-center space-x-4 text-sm text-gray-400">
                                    <span>總行數: {csvData.row_count}</span>
                                    <span>欄位數: {csvData.columns.length}</span>
                                    <span>資料夾: {csvData.folder}</span>
                                </div>
                            </div>

                            {/* 資料表格 */}
                            <div className="overflow-x-auto">
                                <table className="w-full">
                                    <thead className="bg-purple-900/30">
                                        <tr>
                                            {csvData.columns.map((col) => (
                                                <th
                                                    key={col}
                                                    className="px-4 py-3 text-left text-xs font-semibold text-purple-300 uppercase tracking-wider"
                                                >
                                                    {col}
                                                </th>
                                            ))}
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y divide-white/5">
                                        {currentData.map((row, idx) => (
                                            <tr key={idx} className="hover:bg-white/5 transition-colors">
                                                {csvData.columns.map((col) => (
                                                    <td key={col} className="px-4 py-3 text-sm text-gray-300 whitespace-nowrap">
                                                        {typeof row[col] === 'number'
                                                            ? row[col].toFixed(4)
                                                            : row[col]?.toString() || '-'}
                                                    </td>
                                                ))}
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>

                            {/* 分頁控制 */}
                            {totalPages > 1 && (
                                <div className="p-4 border-t border-white/10 flex items-center justify-between">
                                    <div className="text-sm text-gray-400">
                                        顯示 {startIndex + 1} - {Math.min(endIndex, csvData.row_count)} / {csvData.row_count} 筆
                                    </div>
                                    <div className="flex space-x-2">
                                        <button
                                            onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                                            disabled={currentPage === 1}
                                            className="px-3 py-1 bg-purple-600 text-white rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-purple-700 transition-colors"
                                        >
                                            上一頁
                                        </button>
                                        <span className="px-3 py-1 text-gray-300">
                                            {currentPage} / {totalPages}
                                        </span>
                                        <button
                                            onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                                            disabled={currentPage === totalPages}
                                            className="px-3 py-1 bg-purple-600 text-white rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-purple-700 transition-colors"
                                        >
                                            下一頁
                                        </button>
                                    </div>
                                </div>
                            )}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
