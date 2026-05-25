"use client";

import { useState, useRef } from "react";
import { Upload, FileText, CheckCircle, XCircle } from "lucide-react";
import toast from "react-hot-toast";

interface ResumeUploaderProps {
  onUpload: (base64: string, fileName: string) => void;
}

export default function ResumeUploader({ onUpload }: ResumeUploaderProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [file, setFile] = useState<{ name: string; size: string } | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFile = (selectedFile: File) => {
    const validTypes = [
      "application/pdf",
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ];

    if (!validTypes.includes(selectedFile.type)) {
      toast.error("Please upload a PDF or DOCX file.");
      return;
    }

    if (selectedFile.size > 5 * 1024 * 1024) {
      toast.error("File size must be less than 5MB.");
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      const result = e.target?.result as string;
      const base64 = result.split(",")[1];
      onUpload(base64, selectedFile.name);
      setFile({
        name: selectedFile.name,
        size: (selectedFile.size / 1024 / 1024).toFixed(2) + "MB",
      });
      toast.success("Resume processed successfully!");
    };
    reader.readAsDataURL(selectedFile);
  };

  return (
    <div
      onDragOver={(e) => {
        e.preventDefault();
        setIsDragging(true);
      }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={(e) => {
        e.preventDefault();
        setIsDragging(false);
        if (e.dataTransfer.files?.[0]) handleFile(e.dataTransfer.files[0]);
      }}
      onClick={() => fileInputRef.current?.click()}
      className={`
        border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all
        ${isDragging ? "border-indigo-500 bg-indigo-500/10" : "border-gray-800 hover:border-gray-700 hover:bg-gray-800/20"}
        ${file ? "bg-green-500/5 border-green-500/30" : ""}
      `}
    >
      <input
        type="file"
        ref={fileInputRef}
        onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
        accept=".pdf,.docx"
        className="hidden"
      />

      <div className="space-y-4">
        {file ? (
          <div className="flex flex-col items-center space-y-2">
            <div className="bg-green-500/20 p-3 rounded-full">
              <CheckCircle className="text-green-500" size={32} />
            </div>
            <div>
              <p className="font-semibold text-white">{file.name}</p>
              <p className="text-gray-500 text-xs">{file.size}</p>
            </div>
            <button 
              onClick={(e) => {
                e.stopPropagation();
                setFile(null);
                onUpload("", "");
              }}
              className="text-gray-500 hover:text-red-400 text-xs flex items-center gap-1"
            >
              <XCircle size={12} /> Remove
            </button>
          </div>
        ) : (
          <>
            <div className="bg-gray-800/50 p-4 rounded-full w-fit mx-auto">
              <Upload className="text-gray-400" size={32} />
            </div>
            <div className="space-y-1">
              <p className="font-semibold">Drop your resume here</p>
              <p className="text-gray-500 text-sm">or click to browse from your computer</p>
            </div>
            <p className="text-gray-600 text-xs">PDF or DOCX, max 5MB</p>
          </>
        )}
      </div>
    </div>
  );
}
