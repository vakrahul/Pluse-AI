import { Suspense } from "react";
import { ChatInterface } from "@/components/chat/ChatInterface";

export default function ChatPage() {
  return (
    <div className="mx-auto max-w-6xl space-y-6">
      <div>
        <p className="text-sm font-medium text-pulse-600">HCP Copilot</p>
        <h1 className="font-display text-3xl text-clinical-ink">Ask your healthcare data</h1>
        <p className="mt-1 text-clinical-muted">
          Natural language queries routed to Cube analytics, Neo4j networks, or compliance knowledge.
        </p>
      </div>
      <Suspense fallback={<div className="animate-pulse text-clinical-muted">Loading copilot...</div>}>
        <ChatInterface />
      </Suspense>
    </div>
  );
}
