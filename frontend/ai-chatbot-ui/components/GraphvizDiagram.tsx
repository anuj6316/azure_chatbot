import React, { useEffect, useRef } from "react";
import { graphviz } from "d3-graphviz";

interface GraphvizDiagramProps {
    code: string;
}

export const GraphvizDiagram: React.FC<GraphvizDiagramProps> = ({ code }) => {
    const ref = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (ref.current && code) {
            try {
                // Basic cleaning of the code
                let cleanCode = code.replace(/```dot\n?/gi, '').replace(/```graphviz\n?/gi, '').replace(/```\n?/g, '').trim();

                // Ensure it starts with digraph or graph
                if (!cleanCode.toLowerCase().startsWith('digraph') && !cleanCode.toLowerCase().startsWith('graph')) {
                    // If not, wrap it in a digraph if it looks like edges
                    if (cleanCode.includes('->')) {
                        cleanCode = `digraph { ${cleanCode} }`;
                    }
                }

                // Clear previous diagram
                ref.current.innerHTML = '';

                graphviz(ref.current)
                    .width("100%")
                    .height("auto")
                    .fit(true)
                    .zoom(true)
                    .renderDot(cleanCode);

            } catch (error) {
                console.error("Graphviz rendering failed:", error);
                if (ref.current) {
                    ref.current.innerHTML = "<p class='text-red-500 text-xs'>Failed to render diagram</p>";
                }
            }
        }
    }, [code]);

    return <div className="graphviz my-4 border rounded-lg p-2 bg-white dark:bg-gray-800 overflow-hidden" style={{ minHeight: '300px' }} ref={ref} />;
};
