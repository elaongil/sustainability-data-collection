import { create } from "zustand";
import { useCellStore } from "./cellStore";

const isWikipediaUrl = (text) => {
  try {
    const url = new URL(text);
    return url.hostname.includes("wikipedia.org");
  } catch {
    return false;
  }
};

const RESPONSE_TEMPLATES = {
  basic: "I am a basic AI assistant. I can only provide simple responses.",
  entity: "I noticed {entities} in your message.",
  semantic: "Based on the context, I understand that {analysis}.",
  full: "I noticed {entities} in your message. {analysis}",
  wikipedia: "Here are the extracted tables from Wikipedia:\n\n\n{tableData}",
  entitySemantic:
    "I noticed {entities} in your message. Based on this context, {analysis}",
  wikipediaEnhanced:
    "Based on your request about {entities}, I found these tables from Wikipedia:\n\n\n{tableData}\n\n\nThis information suggests that {analysis}",
};

const PROCESSING_DELAYS = {
  entity: 500,
  semantic: 1000,
  response: 1200,
  cache: 300,
  wikipedia: 800,
};

const createMessage = (content, type = "user") => ({
  id: Date.now(),
  content,
  type,
  timestamp: new Date().toISOString(),
});

export const useChatStore = create((set, get) => ({
  messages: [],
  isProcessing: false,
  processingSteps: [],

  addMessage: async (content, type = "user") => {
    const message = createMessage(content, type);
    set((state) => ({
      messages: [...state.messages, message],
    }));

    if (type === "user") {
      await get().processMessage(content);
    }
  },

  processMessage: async (content) => {
    set({ isProcessing: true, processingSteps: [] });
    const { cells } = useCellStore.getState();
    const activeProcessors = cells.filter((cell) => cell.active);

    console.log("activeProcessors", activeProcessors);
    // Check if required cells are active and properly connected
    const hasResponseGenerator = activeProcessors.some(
      (cell) => cell.id === "response-generation"
    );
    const hasWikipediaExtractor = activeProcessors.some(
      (cell) => cell.id === "wikipedia-extractor"
    );
    const connections = useCellStore.getState().getActiveConnections();

    // Check if Wikipedia Extractor is connected to Response Generator
    const isWikiConnectedToResponse = connections.some(
      (conn) =>
        conn.source === "wikipedia-extractor" &&
        conn.target === "response-generation"
    );

    if (
      !hasResponseGenerator ||
      (hasWikipediaExtractor && !isWikiConnectedToResponse)
    ) {
      set({ isProcessing: false, processingSteps: [] });
      const message = !hasResponseGenerator
        ? "Please activate the Response Generation cell to process messages."
        : "Please ensure the Wikipedia Extractor is connected to the Response Generation cell.";
      await get().addMessage(message, "ai");
      return;
    }

    let response = "";
    let entities = "";
    let analysis = "";
    let tableData = "";

    // Simulate processing through active cells
    for (const cell of activeProcessors) {
      set((state) => ({
        processingSteps: [...state.processingSteps, cell.id],
      }));

      await new Promise((resolve) =>
        setTimeout(resolve, PROCESSING_DELAYS[cell.id.split("-")[0]])
      );

      switch (cell.id) {
        case "wikipedia-extractor":
          if (isWikipediaUrl(content)) {
            try {
              let apiResponse, responseData;
              apiResponse = await fetch("/api/cells/wikipedia/extract/", {
                method: "POST",
                headers: {
                  "Content-Type": "application/json",
                },
                body: JSON.stringify({ source: content }),
              });

              responseData = await apiResponse.json();
              console.log("Wikipedia API Response:", responseData);

              // Log the full response for debugging
              console.log("Response status:", apiResponse.status);
              console.log("Response data:", responseData);

              // Check for error conditions in order of priority
              if (!responseData || !responseData.data) {
                throw new Error("Invalid response format from server");
              }

              if (responseData.data.error) {
                throw new Error(responseData.data.error);
              }

              if (!apiResponse.ok) {
                throw new Error(`HTTP error! status: ${apiResponse.status}`);
              }

              // Format extracted tables
              if (
                responseData.data.tables &&
                responseData.data.tables.length > 0
              ) {
                tableData = responseData.data.tables
                  .map((table) => {
                    // Clean and format table data
                    // Clean and format data
                    const title = table.title ? `### ${table.title}\n\n` : "";
                    const cleanHeaders = table.headers.map((h) =>
                      (h || "").toString().trim().replace(/[|]/g, "\\|")
                    );
                    const cleanData = table.data.map((row) =>
                      row.map((cell) =>
                        (cell || "").toString().trim().replace(/[|]/g, "\\|")
                      )
                    );

                    // Build table markdown with proper spacing
                    const headers = cleanHeaders.join(" | ");
                    const separator = cleanHeaders.map(() => "---").join(" | ");
                    const rows = cleanData
                      .map((row) => row.join(" | "))
                      .join("\n");

                    // Combine with proper newlines and spacing
                    return `${title}| ${headers} |\n| ${separator} |\n| ${rows} |`;
                  })
                  .join("\n\n");
              } else {
                tableData = "No tables found";
              }

              if (!entities) entities = "Wikipedia article tables";
              if (!analysis)
                analysis =
                  "the tables contain structured data from the Wikipedia article";
            } catch (error) {
              console.error("Wikipedia extraction error:", error);
              const errorMessage = error.message || "Unknown error occurred";
              const technicalDetails = [];
              if (apiResponse?.status)
                technicalDetails.push(`Status Code: ${apiResponse.status}`);
              if (responseData?.data?.error)
                technicalDetails.push(
                  `Server Error: ${responseData.data.error}`
                );
              if (error.stack)
                technicalDetails.push(`Stack Trace: ${error.stack}`);

              tableData = `### Wikipedia Extractor Error\n\n**Error Message:**\n${errorMessage}\n\n**Technical Details:**\n\`\`\`\n${technicalDetails.join(
                "\n"
              )}\n\`\`\``;
            }
          }
          break;
        case "cdp-extractor":
          try {
            const fileComponent = document.createElement("div");
            fileComponent.innerHTML = `
              <div class="file-processing-result">
                <h4>File Processing Results:</h4>
                <ul>
                  ${responseData.filePaths
                    .map(
                      (path) => `
                    <li>Processed file available at: ${path}</li>
                  `
                    )
                    .join("")}
                </ul>
                <p>${responseData.message}</p>
              </div>
            `;

            entities = "uploaded files";
            analysis = "files have been processed and are ready for use";
          } catch (error) {
            console.error("File extraction error:", error);
            entities = "file processing error";
            analysis = "there was an error processing the uploaded files";
          }
          break;
        case "entity-recognition":
          entities =
            "AI models, specifically GPT and BERT series, their developers like OpenAI and Google";
          break;
        case "semantic-analysis":
          analysis =
            "there is a trend of increasing model size and complexity, with a shift from open-source to proprietary licenses";
          break;
        case "response-generation":
          const activeIds = activeProcessors.map((c) => c.id);
          const connections = useCellStore.getState().getActiveConnections();

          if (activeProcessors.length === 1) {
            response = RESPONSE_TEMPLATES.basic;
          } else if (activeIds.includes("wikipedia-extractor")) {
            // Enhanced Wikipedia response when combined with other cells
            if (
              activeIds.includes("semantic-analysis") ||
              activeIds.includes("entity-recognition")
            ) {
              response = RESPONSE_TEMPLATES.wikipediaEnhanced
                .replace("{tableData}", tableData)
                .replace("{entities}", entities)
                .replace("{analysis}", analysis);
            } else {
              response = RESPONSE_TEMPLATES.wikipedia.replace(
                "{tableData}",
                tableData
              );
            }
          } else {
            // Check for connected cell combinations
            const hasEntitySemantic =
              activeIds.includes("entity-recognition") &&
              activeIds.includes("semantic-analysis");

            if (activeProcessors.length >= 3) {
              response = RESPONSE_TEMPLATES.full
                .replace("{entities}", entities)
                .replace("{analysis}", analysis);
            } else if (hasEntitySemantic) {
              response = RESPONSE_TEMPLATES.entitySemantic
                .replace("{entities}", entities)
                .replace("{analysis}", analysis);
            } else if (activeIds.includes("entity-recognition")) {
              response = RESPONSE_TEMPLATES.entity.replace(
                "{entities}",
                entities
              );
            } else if (activeIds.includes("semantic-analysis")) {
              response = RESPONSE_TEMPLATES.semantic.replace(
                "{analysis}",
                analysis
              );
            }
          }
          break;
        case "cache-management":
          // Simulate cache check/update
          break;
      }
    }

    // If we have an active Wikipedia Extractor but no response, generate a Wikipedia response
    if (
      !response &&
      activeProcessors.some((cell) => cell.id === "wikipedia-extractor")
    ) {
      response = RESPONSE_TEMPLATES.wikipedia.replace("{tableData}", tableData);
    }

    set({ isProcessing: false, processingSteps: [] });
    await get().addMessage(response, "ai");
  },

  clearChat: () =>
    set({ messages: [], isProcessing: false, processingSteps: [] }),
}));
