
// Define the structure for response from the backend
interface BackendResponse {
  answer: string;
  sources: string[];
  matched_chunks: Array<{
    content: string;
    source: string;
    score: number;
    metadata?: any;
  }>;
  query_id?: string;
}

class KnowledgeBaseService {
  private backendUrl: string;

  constructor() {
    // Use environment-based configuration for backend URL
    this.backendUrl = typeof window !== 'undefined'
      ? (process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000')
      : 'http://localhost:8000';
  }

  // Call the backend to get an answer based on the query
  async getAnswer(query: string): Promise<string> {
    try {
      // Make request to backend /ask endpoint
      const response = await fetch(`${this.backendUrl}/ask`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(`Backend error: ${response.status} - ${errorData.detail || response.statusText}`);
      }

      const data: BackendResponse = await response.json();

      // Format the response for the chat interface
      let responseText = data.answer;

      // Add sources if available
      if (data.sources && data.sources.length > 0) {
        responseText += `\n\n**Sources:**\n`;
        data.sources.forEach((source, index) => {
          responseText += `- Source ${index + 1}: ${source}\n`;
        });
      }

      // Add matched chunks if available
      if (data.matched_chunks && data.matched_chunks.length > 0) {
        responseText += `\n\n**Relevant Information:**\n`;
        data.matched_chunks.forEach((chunk, index) => {
          responseText += `- **Chunk ${index + 1}** (from ${chunk.source}, score: ${chunk.score.toFixed(2)}):\n  ${chunk.content}\n\n`;
        });
      }

      return responseText;
    } catch (error) {
      console.error('Error fetching answer from backend:', error);
      if (error instanceof TypeError && error.message.includes('fetch')) {
        return "I'm having trouble connecting to the backend server. Please make sure the FastAPI server is running at " + this.backendUrl + " and CORS is properly configured.";
      }
      return `Sorry, I encountered an error processing your request: ${(error as Error).message || 'Unknown error'}. Please try again.`;
    }
  }
}

export const knowledgeBaseService = new KnowledgeBaseService();