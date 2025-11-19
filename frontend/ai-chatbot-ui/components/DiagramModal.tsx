import React, { useEffect } from "react";
import { createPortal } from "react-dom";
import { GraphvizDiagram } from "./GraphvizDiagram";

interface DiagramModalProps {
    isOpen: boolean;
    onClose: () => void;
    code: string;
}

export const DiagramModal: React.FC<DiagramModalProps> = ({
    isOpen,
    onClose,
    code,
}) => {
    // Prevent scrolling when modal is open
    useEffect(() => {
        if (isOpen) {
            document.body.style.overflow = "hidden";
        } else {
            document.body.style.overflow = "unset";
        }
        return () => {
            document.body.style.overflow = "unset";
        };
    }, [isOpen]);

    if (!isOpen) return null;

    return createPortal(
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm animate-in fade-in duration-200">
            <div className="relative w-full max-w-7xl h-[90vh] bg-white dark:bg-gray-900 rounded-xl shadow-2xl flex flex-col animate-in zoom-in-95 duration-200">
                {/* Header */}
                <div className="flex items-center justify-between p-4 border-b dark:border-gray-700 bg-gradient-to-r from-blue-600 to-blue-700 rounded-t-xl">
                    <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                        </svg>
                        System Diagram
                    </h3>
                    <button
                        onClick={onClose}
                        className="p-2 text-white hover:text-gray-200 transition-colors rounded-lg hover:bg-white/10"
                        aria-label="Close modal"
                    >
                        <svg
                            className="w-6 h-6"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                        >
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M6 18L18 6M6 6l12 12"
                            />
                        </svg>
                    </button>
                </div>

                {/* Content */}
                <div className="flex-1 overflow-hidden bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
                    <div className="w-full h-full p-8">
                        <div className="w-full h-full bg-white dark:bg-gray-900 rounded-lg shadow-lg border-2 border-gray-200 dark:border-gray-700">
                            <GraphvizDiagram code={code} />
                        </div>
                    </div>
                </div>

                {/* Footer */}
                <div className="p-4 border-t dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50 rounded-b-xl flex justify-between items-center">
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                        Use mouse wheel to zoom • Click and drag to pan
                    </p>
                    <button
                        onClick={onClose}
                        className="px-6 py-2 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white rounded-lg transition-all shadow-md hover:shadow-lg"
                    >
                        Close
                    </button>
                </div>
            </div>

            {/* Backdrop click to close */}
            <div className="absolute inset-0 -z-10" onClick={onClose} />
        </div>,
        document.body
    );
};
