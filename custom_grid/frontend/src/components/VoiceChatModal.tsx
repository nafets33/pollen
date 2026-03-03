import React, { useState, useRef, useEffect } from "react";

interface Message {
  id: number;
  content: string;
  role: "user" | "assistant";
  timestamp: Date;
}

interface OzzProps {
  onSendMessage?: (message: string, history: Message[]) => Promise<string>;
  placeholder?: string;
  maxHeight?: number;
  username?: string;
  kwargs?: any;
  api?: string;
  prod?: boolean;
}

const Ozz: React.FC<OzzProps> = ({
  onSendMessage,
  placeholder = "Pollen here to help with your Portfolio...",
  maxHeight = 400,
  username,
  kwargs,
  api,
  prod
}) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isExpanded, setIsExpanded] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      id: Date.now(),
      content: input,
      role: "user",
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");

    // Auto-open full screen modal when sending from compact row
    if (!isModalOpen) {
      setIsModalOpen(true);
    }

    setIsLoading(true);

    try {
      const response = onSendMessage
        ? await onSendMessage(input, messages)
        : `Response to: "${input}"`;

      const assistantMessage: Message = {
        id: Date.now() + 1,
        content: response,
        role: "assistant",
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error("Error sending message:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClear = () => {
    setMessages([]);
    setIsExpanded(false);
  };

  // REMOVED: const ChatRow = () => ( ... )
  // REMOVED: const HalfScreenModal = () => ( ... )
  // Now JSX is directly in return:

  return (
    <>
      {/* ChatRow - inlined directly */}
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          background: "linear-gradient(135deg, #f8fffe 0%, #f0f9f7 100%)",
          borderRadius: "12px",
          border: "1px solid #e0ebe9",
          boxShadow: "0 2px 8px rgba(0,0,0,0.06)",
          overflow: "hidden",
          transition: "all 0.3s ease",
          maxWidth: "100%",
        }}
      >
        {/* Show chat history only when modal closed and messages exist */}
        {!isModalOpen && messages.length > 0 && (
          <div
            style={{
              height: "200px",
              overflowY: "auto",
              padding: "12px 16px",
              borderBottom: "1px solid #e0ebe2ff",
            }}
          >
            {messages.map((msg) => (
              <div
                key={msg.id}
                style={{
                  display: "flex",
                  justifyContent: msg.role === "user" ? "flex-end" : "flex-start",
                  marginBottom: "8px",
                }}
              >
                <div
                  style={{
                    maxWidth: "80%",
                    padding: "10px 14px",
                    borderRadius: msg.role === "user"
                      ? "16px 16px 4px 16px"
                      : "16px 16px 16px 4px",
                    background: msg.role === "user"
                      ? "linear-gradient(135deg, #a5a2a2ff 0%, #e1dae9ff 100%)"
                      : "#ffffff",
                    color: msg.role === "user" ? "#2d3748" : "#2d3748",
                    boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
                    fontSize: "14px",
                    lineHeight: "1.5",
                    wordBreak: "break-word",
                  }}
                >
                  {msg.content}
                </div>
              </div>
            ))}
            {isLoading && (
              <div style={{ display: "flex", justifyContent: "flex-start", marginBottom: "8px" }}>
                <div
                  style={{
                    padding: "10px 14px",
                    borderRadius: "16px 16px 16px 4px",
                    background: "#ffffff",
                    boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
                  }}
                >
                  <div style={{ display: "flex", gap: "4px" }}>
                    {[0, 1, 2].map((i) => (
                      <div
                        key={i}
                        style={{
                          width: "8px",
                          height: "8px",
                          borderRadius: "50%",
                          background: "#667eea",
                          animation: `bounce 1.4s ease-in-out ${i * 0.2}s infinite`,
                        }}
                      />
                    ))}
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}

        <div
          style={{
            display: "flex",
            alignItems: "center",
            padding: "10px 12px",
            gap: "10px",
          }}
        >
          <div
            style={{
              width: "32px",
              height: "32px",
              borderRadius: "50%",
              background: "linear-gradient(135deg, #e0f4e6ff 0%, #e3f5e8ff 100%)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              flexShrink: 0,
            }}
          >
            <span style={{ fontSize: "16px" }}>⚡</span>
          </div>

          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && handleSend()}
            placeholder={placeholder}
            style={{
              flex: 1,
              padding: "10px 14px",
              border: "1px solid #e2e8f0",
              borderRadius: "20px",
              fontSize: "14px",
              outline: "none",
              transition: "border-color 0.2s, box-shadow 0.2s",
            }}
            onFocus={(e) => {
              e.target.style.borderColor = "#667eea";
              e.target.style.boxShadow = "0 0 0 3px rgba(102,126,234,0.1)";
            }}
            onBlur={(e) => {
              e.target.style.borderColor = "#e2e8f0";
              e.target.style.boxShadow = "none";
            }}
          />

          <button
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            style={{
              padding: "10px 16px",
              background: input.trim() && !isLoading
                ? "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
                : "#e2e8f0",
              color: input.trim() && !isLoading ? "#ffffff" : "#a0aec0",
              border: "none",
              borderRadius: "20px",
              fontWeight: "600",
              fontSize: "14px",
              cursor: input.trim() && !isLoading ? "pointer" : "not-allowed",
              transition: "all 0.2s",
              flexShrink: 0,
            }}
          >
            Send
          </button>

          {messages.length > 0 && (
            <button
              onClick={handleClear}
              style={{
                padding: "8px",
                background: "transparent",
                border: "1px solid #e2e8f0",
                borderRadius: "50%",
                cursor: "pointer",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                transition: "all 0.2s",
              }}
              title="Clear chat"
            >
              ✕
            </button>
          )}

          <button
            onClick={() => setIsModalOpen(true)}
            style={{
              padding: "8px",
              background: "transparent",
              border: "1px solid #e2e8f0",
              borderRadius: "50%",
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              transition: "all 0.2s",
            }}
            title="Expand to full view"
          >
            ⛶
          </button>
        </div>

        <style>
          {`
            @keyframes bounce {
              0%, 80%, 100% { transform: translateY(0); }
              40% { transform: translateY(-6px); }
            }
          `}
        </style>
      </div>

      {/* Modal - inlined directly */}
      {isModalOpen && (
        <>
          <div
            onClick={() => setIsModalOpen(false)}
            style={{
              position: "fixed",
              top: 0,
              left: 0,
              width: "100vw",
              height: "100vh",
              background: "rgba(0,0,0,0.3)",
              zIndex: 9998,
            }}
          />
          <div
            style={{
              position: "fixed",
              top: 0,
              right: 0,
              width: "89%",
              height: "100vh",
              background: "#ffffff",
              boxShadow: "-4px 0 20px rgba(0,0,0,0.15)",
              zIndex: 9999,
              display: "flex",
              flexDirection: "column",
              animation: "slideIn 0.3s ease",
            }}
          >
            <div
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                padding: "4px 8px",
                borderBottom: "1px solid #e2e8f0",
                background: "linear-gradient(135deg, #8d91a2ff 0%, #4ba271ff 100%)",
                color: "#ffffff",
              }}
            >
              <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                <span style={{ fontSize: "14px" }}>⚡</span>
                <span style={{ fontWeight: "400", fontSize: "13px" }}>Pollen AI Portfolio Manager</span>
              </div>
              <button
                onClick={() => setIsModalOpen(false)}
                style={{
                  background: "rgba(255,255,255,0.2)",
                  border: "none",
                  borderRadius: "8px",
                  padding: "4px 8px",
                  color: "#ffffff",
                  cursor: "pointer",
                  fontSize: "12px",
                  fontWeight: "600",
                }}
              >
                ✕ Close
              </button>
            </div>

            <div
              style={{
                flex: 1,
                overflowY: "auto",
                padding: "20px",
                background: "#f8fffe",
              }}
            >
              {messages.length === 0 && (
                <div
                  style={{
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    justifyContent: "center",
                    height: "100%",
                    color: "#a0aec0",
                  }}
                >
                  <span style={{ fontSize: "23px", marginBottom: "12px" }}>💬</span>
                  <p style={{ fontSize: "18px" }}>Lets Allocate To Utilities, Lets Gamble Today on TQQQ.. Ask anything</p>
                </div>
              )}
              {messages.map((msg) => (
                <div
                  key={msg.id}
                  style={{
                    display: "flex",
                    justifyContent: msg.role === "user" ? "flex-end" : "flex-start",
                    marginBottom: "12px",
                  }}
                >
                  <div
                    style={{
                      maxWidth: "70%",
                      padding: "12px 16px",
                      borderRadius: msg.role === "user"
                        ? "18px 18px 4px 18px"
                        : "18px 18px 18px 4px",
                      background: msg.role === "user"
                        ? "linear-gradient(135deg, #e5e7f0ff 0%, #162b18ff 100%)"
                        : "#ffffff",
                      color: msg.role === "user" ? "#e9f1eaff" : "#1d2431ff",
                      boxShadow: "0 2px 6px rgba(0,0,0,0.08)",
                      fontSize: "15px",
                      lineHeight: "1.6",
                    }}
                  >
                    {msg.content}
                  </div>
                </div>
              ))}
              {isLoading && (
                <div style={{ display: "flex", justifyContent: "flex-start" }}>
                  <div
                    style={{
                      padding: "12px 16px",
                      borderRadius: "18px 18px 18px 4px",
                      background: "#ffffff",
                      boxShadow: "0 2px 6px rgba(0,0,0,0.08)",
                    }}
                  >
                    <div style={{ display: "flex", gap: "6px" }}>
                      {[0, 1, 2].map((i) => (
                        <div
                          key={i}
                          style={{
                            width: "10px",
                            height: "10px",
                            borderRadius: "50%",
                            background: "#579169ff",
                            animation: `bounce 1.4s ease-in-out ${i * 0.2}s infinite`,
                          }}
                        />
                      ))}
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            <div
              style={{
                padding: "16px 20px",
                borderTop: "1px solid #e2e8f0",
                background: "#ffffff",
                display: "flex",
                gap: "12px",
              }}
            >
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && handleSend()}
                placeholder={placeholder}
                style={{
                  flex: 1,
                  padding: "14px 18px",
                  border: "2px solid #e2e8f0",
                  borderRadius: "24px",
                  fontSize: "15px",
                  outline: "none",
                }}
              />
              <button
                onClick={handleSend}
                disabled={!input.trim() || isLoading}
                style={{
                  padding: "5px 12px",
                  background: input.trim() && !isLoading
                    ? "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
                    : "#e2e8f0",
                  color: input.trim() && !isLoading ? "#ffffff" : "#a0aec0",
                  border: "none",
                  borderRadius: "12px",
                  fontWeight: "600",
                  fontSize: "15px",
                  cursor: input.trim() && !isLoading ? "pointer" : "not-allowed",
                }}
              >
                Send
              </button>
            </div>

            <style>
              {`
                @keyframes slideIn {
                  from { transform: translateX(100%); }
                  to { transform: translateX(0); }
                }
              `}
            </style>
          </div>
        </>
      )}
    </>
  );
};

export default Ozz;