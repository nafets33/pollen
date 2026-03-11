import React, { useState, useEffect, useRef, useMemo } from "react";
import ReactModal from "react-modal";
import axios from "axios";
import "./modal.css";

ReactModal.setAppElement("#root");

const THEMES = [
  "nuetral", "RSI", "MACD", "VWAP", "MACD-VWAP-RSI", "Bollinger Bands", "star__storywave_AI",
];
const MODELS = ["MACD", "story__AI"];


interface PieceBudget { total_budget: number; borrow_budget: number; }
interface BudgetMap {
  pieces: { [piece_name: string]: PieceBudget };
  tickers: { [ticker: string]: PieceBudget };
}

function calcBudgets(
  board: Chessboard,
  tickerPowers: { [ticker: string]: TickerPower },
  acctInfo: { buying_power: number; last_equity: number } | undefined,
  cash: number
): BudgetMap {
  if (!acctInfo) return { pieces: {}, tickers: {} };
  const { last_equity, buying_power } = acctInfo;

  const bp  = Object.values(board).reduce((s, p) => s + (p.total_buyng_power_allocation  || 0), 0);
  const bpb = Object.values(board).reduce((s, p) => s + (p.total_borrow_power_allocation || 0), 0);

  const pieces: BudgetMap["pieces"] = {};
  const tickers: BudgetMap["tickers"] = {};

  for (const [name, piece] of Object.entries(board)) {
    const qcp_power  = piece.total_buyng_power_allocation  || 0;
    const qcp_borrow = piece.total_borrow_power_allocation || 0;

    let total_budget = 0;
    if (bp > 0) {
      const base = (qcp_power / bp) * last_equity;
      total_budget = cash > 0 ? base * (1 - cash) : base;
    }

    let borrow_budget = 0;
    if (bpb > 0 && cash < 0) {
      borrow_budget = (qcp_borrow / bpb) * buying_power * Math.abs(cash);
    }

    pieces[name] = { total_budget, borrow_budget };

    // Ticker distribution within this piece
    const pieceTickers = piece.tickers || [];
    const bp_t  = pieceTickers.reduce((s, t) => s + (tickerPowers[t]?.buying_power  || 0), 0);
    const bpb_t = pieceTickers.reduce((s, t) => s + (tickerPowers[t]?.margin_power  || 0), 0);

    for (const ticker of pieceTickers) {
      tickers[ticker] = {
        total_budget:   bp_t  > 0 ? ((tickerPowers[ticker]?.buying_power  || 0) / bp_t)  * total_budget  : 0,
        borrow_budget:  bpb_t > 0 ? ((tickerPowers[ticker]?.margin_power  || 0) / bpb_t) * borrow_budget : 0,
      };
    }
  }
  return { pieces, tickers };
}

const fmt$ = (v: number) => `$${Math.round(v).toLocaleString()}`;


interface TickerPower {
  buying_power: number;
  margin_power: number;
}

interface ChessPiece {
  piece_name: string;
  tickers: string[];
  model: string;
  theme: string;
  total_buyng_power_allocation: number;
  total_borrow_power_allocation: number;
  picture?: string;
}

interface Chessboard {
  [piece_name: string]: ChessPiece;
}

interface TickerSearchModalProps {
  isOpen: boolean;
  closeModal: () => void;
  username: string;
  prod: boolean;
  kwargs: any;
  api: string;
  toastr: any;
  chessboard?: Chessboard;
  ticker_buying_powers?: { [ticker: string]: TickerPower };
  accountInfo?: { buying_power: number; last_equity: number };
  cash_position?: number;
}

const TickerSearchModal: React.FC<TickerSearchModalProps> = ({
  isOpen,
  closeModal,
  username,
  prod,
  kwargs,
  api,
  toastr,
  chessboard: initialChessboard,
  ticker_buying_powers: initialTickerBuyingPowers,
  accountInfo,        // ← add
  cash_position = 0,  // ← add
}) => {
  const [step, setStep] = useState<"list_pieces" | "search" | "configure">("list_pieces");

  // ── Core data ──────────────────────────────────────────────────────────────
  const [chessboard, setChessboard] = useState<Chessboard>(initialChessboard || {});
  const [tickerBuyingPowers, setTickerBuyingPowers] = useState<{ [ticker: string]: TickerPower }>(
    initialTickerBuyingPowers || {}
  );
  const [refreshing, setRefreshing] = useState(false);

  // ── Search ─────────────────────────────────────────────────────────────────
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<string[]>([]);
  const [searchLoading, setSearchLoading] = useState(false);
  const searchInputRef = useRef<HTMLInputElement>(null);

  // ── Configure form ─────────────────────────────────────────────────────────
  const [editingPieceName, setEditingPieceName] = useState<string | null>(null);
  const [pieceName, setPieceName] = useState("New Group");
  const [selectedTickers, setSelectedTickers] = useState<string[]>([]);
  const [tickerAllocations, setTickerAllocations] = useState<{ [ticker: string]: TickerPower }>({});
  const [model, setModel] = useState(MODELS[0]);
  const [theme, setTheme] = useState(THEMES[0]);
  const [buyingPower, setBuyingPower] = useState(0);
  const [borrowPower, setBorrowPower] = useState(0);
  const [loading, setLoading] = useState(false);
const [localCashPosition, setLocalCashPosition] = useState<number>(cash_position);
const [savedCashPosition, setSavedCashPosition] = useState<number>(cash_position);  // ← add
const [savingCash, setSavingCash] = useState(false);
    
    const [expandedPiece, setExpandedPiece] = useState<string | null>(null);
  const [inlineAllocs, setInlineAllocs] = useState<{ [piece_name: string]: { buying_power: number; borrow_power: number } }>({});
  const [savingPiece, setSavingPiece] = useState<string | null>(null);

  const apiBase = api.split("/api/")[0];
  const apiKey = kwargs?.api_key;

   // ── Budget calculations ────────────────────────────────────────────────────
  const savedBudgets = useMemo(
    () => calcBudgets(chessboard, tickerBuyingPowers, accountInfo, localCashPosition),
    [chessboard, tickerBuyingPowers, accountInfo, localCashPosition]
  );

  const previewBudgets = useMemo(() => {
    if (step !== "configure") return savedBudgets;
    const previewBoard: Chessboard = { ...chessboard };
    if (editingPieceName && editingPieceName !== pieceName) delete previewBoard[editingPieceName];
    previewBoard[pieceName] = {
      piece_name: pieceName,
      tickers: selectedTickers,
      model,
      theme,
      total_buyng_power_allocation: buyingPower,
      total_borrow_power_allocation: borrowPower,
    };
    return calcBudgets(previewBoard, { ...tickerBuyingPowers, ...tickerAllocations }, accountInfo, localCashPosition);
  }, [step, chessboard, pieceName, editingPieceName, selectedTickers, buyingPower, borrowPower, tickerAllocations, tickerBuyingPowers, accountInfo, localCashPosition, model, theme]);


    // Board with inline slider values applied (for live $ preview in list view)
  const inlinePreviewBoard = useMemo(() => {
    const board = { ...chessboard };
    for (const [name, alloc] of Object.entries(inlineAllocs)) {
      if (board[name]) {
        board[name] = {
          ...board[name],
          total_buyng_power_allocation: alloc.buying_power,
          total_borrow_power_allocation: alloc.borrow_power,
        };
      }
    }
    return board;
  }, [chessboard, inlineAllocs]);

  const inlineBudgets = useMemo(
    () => calcBudgets(inlinePreviewBoard, tickerBuyingPowers, accountInfo, localCashPosition),
    [inlinePreviewBoard, tickerBuyingPowers, accountInfo, localCashPosition]
  );

  // ── Reset form on modal open ───────────────────────────────────────────────
  useEffect(() => {
    if (isOpen) {

setLocalCashPosition(cash_position);
setSavedCashPosition(cash_position);
      setStep("list_pieces");
      setEditingPieceName(null);
      setPieceName("New Group");
      setSelectedTickers([]);
      setTickerAllocations({});
      setModel(MODELS[0]);
      setTheme(THEMES[0]);
      setBuyingPower(0);
      setBorrowPower(0);
      setSearchQuery("");
      setSearchResults([]);
            setExpandedPiece(null);
    }
  }, [isOpen]);

  // ── Live ticker search ─────────────────────────────────────────────────────
  useEffect(() => {
    if (!searchQuery.trim()) {
      setSearchResults([]);
      return;
    }
    const controller = new AbortController();
    const delay = setTimeout(async () => {
      setSearchLoading(true);
      try {
        const res = await axios.post(
          `${apiBase}/api/data/ticker_search_query`,
          { client_user: username, query: searchQuery.trim().toUpperCase(), prod, api_key: apiKey },
          { signal: controller.signal }
        );
        setSearchResults(res.data?.tickers || []);
      } catch (err: any) {
        if (err.name !== "CanceledError" && err.code !== "ERR_CANCELED") {
          console.error("ticker search error", err);
        }
      } finally {
        setSearchLoading(false);
      }
    }, 300);
    return () => {
      clearTimeout(delay);
      controller.abort();
    };
  }, [searchQuery, apiBase, username, prod, apiKey]);


    // Sync inline allocs whenever chessboard changes (load, refresh, save)
  useEffect(() => {
    const allocs: { [name: string]: { buying_power: number; borrow_power: number } } = {};
    for (const [name, piece] of Object.entries(chessboard)) {
      allocs[name] = {
        buying_power: piece.total_buyng_power_allocation || 0,
        borrow_power: piece.total_borrow_power_allocation || 0,
      };
    }
    setInlineAllocs(allocs);
  }, [chessboard]);


  // ── Helpers ────────────────────────────────────────────────────────────────
  const getTickerPower = (ticker: string): TickerPower =>
    tickerBuyingPowers[ticker] || { buying_power: 0, margin_power: 0 };

const handleSaveCashPosition = async () => {
  setSavingCash(true);
  try {
    const res = await axios.post(`${apiBase}/api/data/update_cash_position`, {
      client_user: username,
      prod,
      api_key: apiKey,
      cash_position: localCashPosition,
    });
    const { status, description, cash_position: returned } = res.data;
    if (status === "success") {
      toastr.success(description || "Cash position saved!", "Success");
      setSavedCashPosition(returned ?? localCashPosition);
    } else {
      toastr.error(description || "Failed to save cash position.");
    }
  } catch (err: any) {
    toastr.error(err.message || "Request failed.");
  } finally {
    setSavingCash(false);
  }
};

  // ── Edit existing piece ────────────────────────────────────────────────────
  const handleEditPiece = (piece: ChessPiece) => {
    const allocations: { [ticker: string]: TickerPower } = {};
    (piece.tickers || []).forEach((t) => {
      allocations[t] = getTickerPower(t);
    });
    setEditingPieceName(piece.piece_name);
    setPieceName(piece.piece_name);
    setSelectedTickers(piece.tickers || []);
    setTickerAllocations(allocations);
    setModel(piece.model || MODELS[0]);
    setTheme(piece.theme || THEMES[0]);
    setBuyingPower(piece.total_buyng_power_allocation || 0);
    setBorrowPower(piece.total_borrow_power_allocation || 0);
    setSearchQuery("");
    setSearchResults([]);
    setStep("configure");
  };

  // ── Select ticker from search (new piece) ─────────────────────────────────
  const handleSelectTicker = (ticker: string) => {
    const power = getTickerPower(ticker);
    setEditingPieceName(null);
    setPieceName(`pawn_${Object.keys(chessboard).length + 1}`);
    setSelectedTickers([ticker]);
    setTickerAllocations({ [ticker]: power });
    setBuyingPower(power.buying_power);
    setBorrowPower(power.margin_power);
    setSearchQuery("");
    setSearchResults([]);
    setStep("configure");
  };

  // ── Add ticker to existing configure selection ─────────────────────────────
  const handleAddTicker = (ticker: string) => {
    if (selectedTickers.includes(ticker)) return;
    setSelectedTickers((prev) => [...prev, ticker]);
    setTickerAllocations((prev) => ({ ...prev, [ticker]: getTickerPower(ticker) }));
    setSearchQuery("");
    setSearchResults([]);
    toastr.success(`${ticker} added`);
  };

  // ── Remove ticker from selection ───────────────────────────────────────────
  const handleRemoveTicker = (ticker: string) => {
    setSelectedTickers((prev) => prev.filter((t) => t !== ticker));
    setTickerAllocations((prev) => {
      const next = { ...prev };
      delete next[ticker];
      return next;
    });
  };

  // ── Per-ticker allocation change ───────────────────────────────────────────
  const handleAllocationChange = (
    ticker: string,
    field: "buying_power" | "margin_power",
    value: number
  ) => {
    setTickerAllocations((prev) => ({
      ...prev,
      [ticker]: { ...prev[ticker], [field]: value },
    }));
  };

  // ── Submit save / delete ───────────────────────────────────────────────────
  const handleSubmit = async (action: "save" | "delete") => {
    if (!pieceName.trim()) {
      toastr.warning("Piece name is required.");
      return;
    }
    if (action === "save" && selectedTickers.length === 0) {
      toastr.warning("At least one ticker is required.");
      return;
    }
    setLoading(true);
    try {
      const ticker_allocations = Object.fromEntries(
        selectedTickers.map((t) => [
          t,
          {
            buying_power: tickerAllocations[t]?.buying_power ?? 0,
            margin_power: tickerAllocations[t]?.margin_power ?? 0,
          },
        ])
      );
      const res = await axios.post(`${apiBase}/api/data/update_chess_piece`, {
        client_user: username,
        prod,
        api_key: apiKey,
        action,
        piece_name: pieceName.trim(),
        original_piece_name: editingPieceName,
        tickers: selectedTickers,
        ticker_allocations,
        model,
        theme,
        buying_power: buyingPower,
        borrow_power: borrowPower,
        cash_position: localCashPosition,
      });

      const {
        status,
        description,
        payload: updatedChessboard,
        payload_2: updatedTickerAllocations,
        cash_position: returnedCashPosition,
      } = res.data;

      if (status === "success") {
        toastr.success(description || "Done!", "Success");

        if (action === "save") {
          // Build updated piece from form state so the list reflects changes
          // even if the backend omits payload/payload_2
          const updatedPiece: ChessPiece = {
            piece_name: pieceName.trim(),
            tickers: selectedTickers,
            model,
            theme,
            total_buyng_power_allocation: buyingPower,
            total_borrow_power_allocation: borrowPower,
          };

          if (updatedChessboard) {
            setChessboard(updatedChessboard);
          } else {
            setChessboard((prev) => {
              const next = { ...prev };
              if (editingPieceName && editingPieceName !== pieceName.trim()) {
                delete next[editingPieceName]; // piece was renamed
              }
              next[pieceName.trim()] = updatedPiece;
              return next;
            });
          }

          if (updatedTickerAllocations) {
            setTickerBuyingPowers(updatedTickerAllocations);
          } else {
            // Merge the per-ticker values the user just set into the global map
            setTickerBuyingPowers((prev) => ({ ...prev, ...ticker_allocations }));
          }
      
          if (returnedCashPosition !== undefined) {
  setLocalCashPosition(returnedCashPosition);
  setSavedCashPosition(returnedCashPosition);   // ← add this line
}


        } else {
          // delete
          if (updatedChessboard) {
            setChessboard(updatedChessboard);
          } else {
            setChessboard((prev) => {
              const next = { ...prev };
              delete next[editingPieceName || pieceName.trim()];
              return next;
            });
          }
        }

        setStep("list_pieces");
      } else {
        toastr.error(description || "Something went wrong.", "Error");
      }
    } catch (err: any) {
      toastr.error(err.message || "Request failed.");
    } finally {
      setLoading(false);
    }
  };


  // ── Inline quick-save (list view sliders) ────────────────────────────────
  const handleInlineSave = async (piece_name: string) => {
    const piece = chessboard[piece_name];
    const alloc = inlineAllocs[piece_name];
    if (!piece || !alloc) return;
    setSavingPiece(piece_name);
    try {
      const ticker_allocations = Object.fromEntries(
        (piece.tickers || []).map((t) => [
          t,
          {
            buying_power: tickerBuyingPowers[t]?.buying_power ?? 0,
            margin_power: tickerBuyingPowers[t]?.margin_power ?? 0,
          },
        ])
      );
      const res = await axios.post(`${apiBase}/api/data/update_chess_piece`, {
        client_user: username,
        prod,
        api_key: apiKey,
        action: "save",
        piece_name,
        original_piece_name: piece_name,
        tickers: piece.tickers,
        ticker_allocations,
        model: piece.model,
        theme: piece.theme,
        buying_power: alloc.buying_power,
        borrow_power: alloc.borrow_power,
        cash_position: localCashPosition,
      });
      const { status, description, 
        payload: updatedChessboard, 
        payload_2: updatedTickers, 
        cash_position: updatedCashPosition } = res.data;
      if (status === "success") {
        toastr.success(description || "Saved!", "Success");
        if (updatedChessboard) {
          setChessboard(updatedChessboard);
        } else {
          setChessboard((prev) => ({
            ...prev,
            [piece_name]: {
              ...piece,
              total_buyng_power_allocation: alloc.buying_power,
              total_borrow_power_allocation: alloc.borrow_power,
            },
          }));
        }
        if (updatedTickers) setTickerBuyingPowers(updatedTickers);
        
        if (updatedCashPosition !== undefined) {
          setLocalCashPosition(updatedCashPosition);
          setSavedCashPosition(updatedCashPosition);
        }
        setExpandedPiece(null);
      } else {
        toastr.error(description || "Something went wrong.", "Error");
      }
    } catch (err: any) {
      toastr.error(err.message || "Request failed.");
    } finally {
      setSavingPiece(null);
    }
  };


  // ── Reusable slider ────────────────────────────────────────────────────────
  const SliderField = ({
    label,
    value,
    onChange,
    color = "#3498db",
  }: {
    label: string;
    value: number;
    onChange: (v: number) => void;
    color?: string;
  }) => (
    <div style={{ flex: "1 1 45%", minWidth: "140px" }}>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          fontSize: "0.8rem",
          fontWeight: "bold",
          marginBottom: "2px",
        }}
      >
        <span>{label}</span>
        <span style={{ color }}>{(value * 100).toFixed(0)}%</span>
      </div>
      <input
        type="range"
        min="0"
        max="1"
        step="0.01"
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        style={{ width: "100%", accentColor: color }}
      />
    </div>
  );

  const chessPieces = Object.values(chessboard);

  // ── Render ─────────────────────────────────────────────────────────────────
  return (
    <ReactModal
      isOpen={isOpen}
      onRequestClose={closeModal}
      style={{
        overlay: {
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          backgroundColor: "rgba(0,0,0,0.45)",
          zIndex: 1100,
        },
        content: {
          overflow: "visible",
          padding: 0,
          inset: "auto",
          position: "relative",
          border: "none",
          background: "transparent",
          width: "85vw",
          maxWidth: "1200px",
          maxHeight: "85vh",
        },
      }}
      ariaHideApp={false}
    >
      <div
        className="my-modal-content"
        style={{
          borderRadius: "12px",
          overflow: "hidden",
          display: "flex",
          flexDirection: "column",
          maxHeight: "85vh",
        }}
      >
        {/* ── Header ────────────────────────────────────────────────────── */}
        <div
          className="modal-header px-3 d-flex justify-content-between align-items-center"
          style={{
            background: "linear-gradient(135deg, #1a3a4a 0%, #0f2533 100%)",
            color: "white",
            flexShrink: 0,
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <span style={{ fontSize: "1.3rem" }}>
              {step === "list_pieces" ? "♟️" : step === "search" ? "🔍" : "⚙️"}
            </span>
            <h5 className="m-0" style={{ color: "white", fontWeight: 700 }}>
              {step === "list_pieces"
                ? "Manage Portfolio Allocations"
                : step === "search"
                ? "Search Ticker"
                : editingPieceName
                ? `Edit: ${editingPieceName}`
                : "Add New Piece"}
            </h5>
          </div>
          <div style={{ display: "flex", gap: "12px", alignItems: "center" }}>
            {/* <button
              onClick={handleRefresh}
              disabled={refreshing}
              style={{
                background: "rgba(255,255,255,0.2)",
                border: "1px solid rgba(255,255,255,0.3)",
                borderRadius: "6px",
                color: "#fff",
                padding: "4px 12px",
                fontSize: "0.85rem",
                cursor: refreshing ? "not-allowed" : "pointer",
                display: "flex",
                alignItems: "center",
                gap: "4px",
              }}
            >
              {refreshing ? (
                <span className="spinner-border spinner-border-sm" role="status" />
              ) : (
                "🔄 Refresh"
              )}
            </button> */}
            <span
              onClick={closeModal}
              style={{ cursor: "pointer", fontSize: "1.4rem", lineHeight: 1, color: "#ccc" }}
            >
              &times;
            </span>
          </div>
        </div>

        {/* ── Body ──────────────────────────────────────────────────────── */}
        <div
          className="modal-body p-3"
          style={{ background: "#fff", overflowY: "auto", flex: 1 }}
        >
          {/* ── LIST PIECES ─────────────────────────────────────────────── */}
          {step === "list_pieces" && (
            <div>
              <div style={{ marginBottom: "14px" }}>
                <button
                  onClick={() => {
                    setStep("search");
                    setTimeout(() => searchInputRef.current?.focus(), 100);
                  }}
                  style={{
                    padding: "6px 14px",
                    background: "linear-gradient(135deg, #2e7d32 0%, #43a047 100%)",
                    color: "#fff",
                    border: "none",
                    borderRadius: "8px",
                    fontWeight: 700,
                    cursor: "pointer",
                    fontSize: "0.8rem",
                    display: "block",
                    marginLeft: "auto",
                  }}
                >
                  ➕ Add New Piece
                </button>
              </div>

              {/* ── Cash Position Slider ─────────────────────────────── */}
              <div
                style={{
                  background: localCashPosition > 0 ? "#f1f8e9" : localCashPosition < 0 ? "#fff3e0" : "#f5f5f5",
                  border: `1px solid ${localCashPosition > 0 ? "#a5d6a7" : localCashPosition < 0 ? "#ffcc80" : "#e0e0e0"}`,
                  borderRadius: "8px",
                  padding: "12px 14px",
                  marginBottom: "14px",
                }}
              >
<div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "6px" }}>
  <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
    <span style={{ fontSize: "0.83rem", fontWeight: 700, color: "#1a3a4a" }}>💵 Cash Position</span>
    {localCashPosition !== savedCashPosition && (
      <span style={{ color: "#f57c00", fontSize: "0.75rem", fontStyle: "italic" }}>unsaved</span>
    )}
  </div>
  <span style={{ fontSize: "0.82rem", fontWeight: 700, color: localCashPosition > 0 ? "#2e7d32" : localCashPosition < 0 ? "#e65100" : "#555" }}>
    {localCashPosition === 0 ? "Neutral (0%)" : localCashPosition > 0
      ? `Cash Reserve: ${(localCashPosition * 100).toFixed(0)}%`
      : `Margin: ${(Math.abs(localCashPosition) * 100).toFixed(0)}%`}
  </span>
</div>
                <input
                  type="range"
                  min="-1"
                  max="1"
                  step="0.01"
                  value={localCashPosition}
                  onChange={(e) => setLocalCashPosition(Number(e.target.value))}
                  style={{
                    width: "100%",
                    accentColor: localCashPosition > 0 ? "#2e7d32" : localCashPosition < 0 ? "#e65100" : "#3498db",
                  }}
                />
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.72rem", color: "#888", marginTop: "2px" }}>
                  <span>← Margin (100%)</span>
                  <span>Neutral</span>
                  <span>Cash Reserve (100%) →</span>
                </div>
                
              </div>

<div
  style={{
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    marginTop: "12px",
  }}
>
  <button
    disabled={savingCash || localCashPosition === savedCashPosition}
    onClick={handleSaveCashPosition}
    style={{
      background: "linear-gradient(135deg, #2e7d32 0%, #43a047 100%)",
      color: "#fff",
      border: "none",
      borderRadius: "6px",
      padding: "5px 18px",
      fontWeight: 700,
      fontSize: "0.9rem",
      cursor: (savingCash || localCashPosition === savedCashPosition) ? "not-allowed" : "pointer",
      opacity: (savingCash || localCashPosition === savedCashPosition) ? 0.6 : 1,
      display: "flex",
      alignItems: "center",
      gap: "6px",
      boxShadow: "0 1px 4px rgba(44, 167, 80, 0.08)",
    }}
  >
    {savingCash
      ? <span className="spinner-border spinner-border-sm" role="status" />
      : "⚡ Save"}
  </button>
</div>

              {chessPieces.length === 0 ? (
                <div style={{ textAlign: "center", padding: "40px 20px", color: "#999" }}>
                  <p style={{ fontSize: "1.2rem", marginBottom: "8px" }}>♟️ No chess pieces yet</p>
                  <p style={{ fontSize: "0.9rem" }}>Click "Add New Piece" to get started</p>
                </div>
              ) : (
                <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: "10px" }}>                  {chessPieces.map((piece) => {
                    const isExpanded = expandedPiece === piece.piece_name;
                    const isSaving = savingPiece === piece.piece_name;
                    const inlineAlloc = inlineAllocs[piece.piece_name] || {
                      buying_power: piece.total_buyng_power_allocation || 0,
                      borrow_power: piece.total_borrow_power_allocation || 0,
                    };
                    const isDirty =
                      inlineAlloc.buying_power !== (piece.total_buyng_power_allocation || 0) ||
                      inlineAlloc.borrow_power !== (piece.total_borrow_power_allocation || 0);
                    return (
                      <div
                        key={piece.piece_name}
                        style={{
                          background: isExpanded ? "#f0f7ff" : "#f8f9fa",
                          border: `1px solid ${isExpanded ? "#3498db" : "#dee2e6"}`,
                          borderRadius: "8px",
                          padding: "12px 14px",
                          transition: "all 0.15s",
                          display: "flex",
                          flexDirection: "column",
                          gap: "8px",
                        }}
                      >
{/* ── Row 1: Name / Model / Buttons ── */}
<div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
  <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
    {/* Configure button */}
    <button
      onClick={(e) => { e.stopPropagation(); handleEditPiece(piece); }}
      title="Configure tickers, model, theme"
      style={{
        background: "none",
        border: "1px solid #ccc",
        borderRadius: "6px",
        cursor: "pointer",
        fontSize: "0.8rem",
        padding: "2px 8px",
        color: "#555",
      }}
    >
      ⚙️
    </button>
    {/* Expand toggle */}
    <button
      onClick={(e) => {
        e.stopPropagation();
        setExpandedPiece(isExpanded ? null : piece.piece_name);
      }}
      title={isExpanded ? "Collapse" : "Adjust allocation"}
      style={{
        background: isExpanded ? "#3498db" : "none",
        border: `1px solid ${isExpanded ? "#3498db" : "#ccc"}`,
        borderRadius: "6px",
        cursor: "pointer",
        fontSize: "0.8rem",
        padding: "2px 8px",
        color: isExpanded ? "#fff" : "#555",
      }}
    >
      {isExpanded ? "▲" : "▼ Alloc"}
    </button>
    <div style={{ fontWeight: 700, fontSize: "1rem", color: "#1a3a4a" }}>
      ♟️ {piece.piece_name}
    </div>
  </div>
  <div
    style={{
      background: "#3498db",
      color: "#fff",
      padding: "2px 10px",
      borderRadius: "12px",
      fontSize: "0.75rem",
      fontWeight: 600,
    }}
  >
    {piece.model}
  </div>
</div>

                        {/* ── Row 2: Budget summary ── */}
                        <div style={{ display: "flex", gap: "14px", fontSize: "0.75rem", color: "#666" }}>
                          <div>
                            <strong style={{ color: "#2e7d32" }}>Group BP:</strong>{" "}
                            {((inlineAlloc.buying_power) * 100).toFixed(0)}%
                            {inlineBudgets.pieces[piece.piece_name] && (
                              <span style={{ color: "#2e7d32", marginLeft: 4 }}>
                                ({fmt$(inlineBudgets.pieces[piece.piece_name].total_budget)})
                              </span>
                            )}
                            {isDirty && (
                              <span style={{ color: "#f57c00", marginLeft: 4, fontStyle: "italic" }}>unsaved</span>
                            )}
                          </div>
                          <div>
                            <strong style={{ color: "#e65100" }}>Margin:</strong>{" "}
                            {((inlineAlloc.borrow_power) * 100).toFixed(0)}%
                            {inlineBudgets.pieces[piece.piece_name] && (
                              <span style={{ color: "#e65100", marginLeft: 4 }}>
                                ({fmt$(inlineBudgets.pieces[piece.piece_name].borrow_budget)})
                              </span>
                            )}
                          </div>
                        </div>

                        {/* ── Inline allocation sliders (expanded) ── */}
                        {isExpanded && (
                          <div
                            style={{
                              background: "#fff",
                              border: "1px solid #d8eaf8",
                              borderRadius: "8px",
                              padding: "12px 14px",
                              display: "flex",
                              flexDirection: "column",
                              gap: "10px",
                            }}
                          >
                            <div style={{ display: "flex", flexWrap: "wrap", gap: "14px" }}>
                              <SliderField
                                label="Buying Power"
                                value={inlineAlloc.buying_power}
                                onChange={(v) =>
                                  setInlineAllocs((prev) => ({
                                    ...prev,
                                    [piece.piece_name]: { ...prev[piece.piece_name], buying_power: v },
                                  }))
                                }
                                color="#2e7d32"
                              />
                              <SliderField
                                label="Margin Power"
                                value={inlineAlloc.borrow_power}
                                onChange={(v) =>
                                  setInlineAllocs((prev) => ({
                                    ...prev,
                                    [piece.piece_name]: { ...prev[piece.piece_name], borrow_power: v },
                                  }))
                                }
                                color="#e65100"
                              />
                            </div>
                            <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
                              <button
                                disabled={isSaving}
                                onClick={() => handleInlineSave(piece.piece_name)}
                                style={{
                                  background: "linear-gradient(135deg, #2e7d32 0%, #43a047 100%)",
                                  color: "#fff",
                                  border: "none",
                                  borderRadius: "6px",
                                  padding: "6px 16px",
                                  fontWeight: 700,
                                  fontSize: "0.82rem",
                                  cursor: isSaving ? "not-allowed" : "pointer",
                                  opacity: isSaving ? 0.7 : 1,
                                  display: "flex",
                                  alignItems: "center",
                                  gap: "6px",
                                }}
                              >
                                {isSaving ? (
                                  <span className="spinner-border spinner-border-sm" role="status" />
                                ) : (
                                  "⚡ Save"
                                )}
                              </button>
                              <button
                                disabled={isSaving}
                                onClick={() => {
                                  setInlineAllocs((prev) => ({
                                    ...prev,
                                    [piece.piece_name]: {
                                      buying_power: piece.total_buyng_power_allocation || 0,
                                      borrow_power: piece.total_borrow_power_allocation || 0,
                                    },
                                  }));
                                  setExpandedPiece(null);
                                }}
                                style={{
                                  background: "none",
                                  border: "1px solid #ccc",
                                  borderRadius: "6px",
                                  padding: "6px 12px",
                                  fontSize: "0.82rem",
                                  cursor: "pointer",
                                  color: "#666",
                                }}
                              >
                                Cancel
                              </button>
                            </div>
                          </div>
                        )}

                        {/* ── Row 3: Ticker chips ── */}
                        <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
                          {(piece.tickers || []).length > 0 ? (
                            piece.tickers.map((ticker) => {
                              const power = tickerBuyingPowers[ticker];
                              return (
                                <div
                                  key={ticker}
                                  style={{
                                    background: "#e3f2fd",
                                    color: "#1565c0",
                                    padding: "4px 10px",
                                    borderRadius: "6px",
                                    fontWeight: 600,
                                    fontSize: "0.82rem",
                                    display: "flex",
                                    flexDirection: "column",
                                    gap: "2px",
                                  }}
                                >
                                  <span>{ticker}</span>
                                  {power && (
                                    <>
                                      <span style={{ fontSize: "0.68rem", color: "#2e7d32" }}>
                                        BP: {(power.buying_power * 100).toFixed(0)}%
                                        {inlineBudgets.tickers[ticker] && ` (${fmt$(inlineBudgets.tickers[ticker].total_budget)})`}
                                      </span>
                                      <span style={{ fontSize: "0.68rem", color: "#6a1b9a" }}>
                                        Margin: {(power.margin_power * 100).toFixed(0)}%
                                        {inlineBudgets.tickers[ticker] && ` (${fmt$(inlineBudgets.tickers[ticker].borrow_budget)})`}
                                      </span>
                                    </>
                                  )}
                                </div>
                              );
                            })
                          ) : (
                            <span style={{ color: "#999", fontStyle: "italic", fontSize: "0.85rem" }}>
                              No tickers
                            </span>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          )}

          {/* ── SEARCH ──────────────────────────────────────────────────── */}
          {step === "search" && (
            <div>
              <button
                type="button"
                onClick={() => {
                  setStep("list_pieces");
                  setSearchQuery("");
                  setSearchResults([]);
                }}
                style={{
                  background: "none",
                  border: "none",
                  color: "#3498db",
                  cursor: "pointer",
                  fontSize: "0.82rem",
                  padding: 0,
                  marginBottom: "12px",
                }}
              >
                ← Back to list
              </button>

              <div style={{ position: "relative", marginBottom: "10px" }}>
                <input
                  ref={searchInputRef}
                  type="text"
                  placeholder="Type a ticker symbol (e.g. AAPL, BTC/USD)…"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && searchResults.length > 0) {
                      handleSelectTicker(searchResults[0]);
                    }
                  }}
                  style={{
                    width: "100%",
                    padding: "10px 40px 10px 14px",
                    fontSize: "0.95rem",
                    border: "2px solid #3498db",
                    borderRadius: "8px",
                    outline: "none",
                    boxSizing: "border-box",
                  }}
                />
                {searchLoading && (
                  <div
                    style={{
                      position: "absolute",
                      right: "12px",
                      top: "50%",
                      transform: "translateY(-50%)",
                      width: "14px",
                      height: "14px",
                      border: "2px solid #3498db",
                      borderTop: "2px solid transparent",
                      borderRadius: "50%",
                      animation: "spin 0.6s linear infinite",
                    }}
                  />
                )}
              </div>

              {searchResults.length > 0 && (
                <div
                  style={{
                    border: "1px solid #e0e0e0",
                    borderRadius: "8px",
                    overflow: "hidden",
                    maxHeight: "300px",
                    overflowY: "auto",
                  }}
                >
                  {searchResults.map((ticker, i) => (
                    <div
                      key={ticker}
                      onClick={() => handleSelectTicker(ticker)}
                      style={{
                        padding: "10px 14px",
                        cursor: "pointer",
                        borderTop: i > 0 ? "1px solid #f0f0f0" : "none",
                        display: "flex",
                        alignItems: "center",
                        gap: "10px",
                        transition: "background 0.12s",
                        fontSize: "0.9rem",
                        fontWeight: 600,
                      }}
                      onMouseEnter={(e) => (e.currentTarget.style.background = "#eef6ff")}
                      onMouseLeave={(e) => (e.currentTarget.style.background = "#fff")}
                    >
                      <span
                        style={{
                          background: "#3498db",
                          color: "#fff",
                          borderRadius: "5px",
                          padding: "2px 8px",
                          fontSize: "0.8rem",
                          fontWeight: 700,
                        }}
                      >
                        {ticker}
                      </span>
                    </div>
                  ))}
                </div>
              )}

              {!searchLoading && searchQuery.trim() && searchResults.length === 0 && (
                <p
                  style={{
                    textAlign: "center",
                    color: "#999",
                    fontSize: "0.85rem",
                    marginTop: "12px",
                  }}
                >
                  No results for &ldquo;{searchQuery}&rdquo; — try a different symbol.
                </p>
              )}

              {!searchQuery.trim() && (
                <p
                  style={{
                    textAlign: "center",
                    color: "#aaa",
                    fontSize: "0.82rem",
                    marginTop: "12px",
                  }}
                >
                  Start typing to search available tickers & crypto symbols.
                </p>
              )}
            </div>
          )}

          {/* ── CONFIGURE ───────────────────────────────────────────────── */}
          {step === "configure" && (
            <div>
              <button
                type="button"
                onClick={() => setStep("list_pieces")}
                style={{
                  background: "none",
                  border: "none",
                  color: "#3498db",
                  cursor: "pointer",
                  fontSize: "0.82rem",
                  padding: 0,
                  marginBottom: "12px",
                }}
              >
                ← Back to list
              </button>

              {/* Piece name */}
              <div style={{ marginBottom: "12px" }}>
                <label
                  style={{
                    fontSize: "0.82rem",
                    fontWeight: "bold",
                    marginBottom: "4px",
                    display: "block",
                  }}
                >
                  Chess Piece Name
                </label>
                <input
                  type="text"
                  value={pieceName}
                  onChange={(e) => setPieceName(e.target.value)}
                  placeholder="e.g. pawn_aapl"
                  style={{
                    width: "100%",
                    padding: "7px 10px",
                    fontSize: "0.88rem",
                    border: "1px solid #ccc",
                    borderRadius: "6px",
                    boxSizing: "border-box",
                  }}
                />
              </div>

              {/* Tickers */}
              <div style={{ marginBottom: "12px" }}>
                <label
                  style={{
                    fontSize: "0.82rem",
                    fontWeight: "bold",
                    marginBottom: "4px",
                    display: "block",
                  }}
                >
                  Symbols / Tickers
                </label>

                {/* Selected chips */}
                <div
                  style={{
                    display: "flex",
                    flexWrap: "wrap",
                    gap: "6px",
                    marginBottom: "8px",
                    minHeight: "36px",
                    padding: "6px",
                    border: "1px solid #e0e0e0",
                    borderRadius: "6px",
                    background: "#fafafa",
                  }}
                >
                  {selectedTickers.length === 0 ? (
                    <span style={{ color: "#999", fontSize: "0.85rem", fontStyle: "italic" }}>
                      No tickers selected
                    </span>
                  ) : (
                    selectedTickers.map((ticker) => (
                      <span
                        key={ticker}
                        style={{
                          background: "#3498db",
                          color: "#fff",
                          padding: "4px 8px",
                          borderRadius: "4px",
                          fontSize: "0.8rem",
                          fontWeight: 600,
                          display: "flex",
                          alignItems: "center",
                          gap: "6px",
                        }}
                      >
                        {ticker}
                        <span
                          onClick={() => handleRemoveTicker(ticker)}
                          style={{ cursor: "pointer", fontSize: "1rem", lineHeight: 1 }}
                        >
                          ×
                        </span>
                      </span>
                    ))
                  )}
                </div>

                {/* Search to add more */}
                <div style={{ position: "relative" }}>
                  <input
                    type="text"
                    placeholder="Search to add more symbols…"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    style={{
                      width: "100%",
                      padding: "7px 10px",
                      fontSize: "0.85rem",
                      border: "1px solid #ccc",
                      borderRadius: "6px",
                      boxSizing: "border-box",
                    }}
                  />
                  {searchLoading && (
                    <div
                      style={{
                        position: "absolute",
                        right: "10px",
                        top: "50%",
                        transform: "translateY(-50%)",
                        width: "12px",
                        height: "12px",
                        border: "2px solid #3498db",
                        borderTop: "2px solid transparent",
                        borderRadius: "50%",
                        animation: "spin 0.6s linear infinite",
                      }}
                    />
                  )}
                </div>

                {searchResults.length > 0 && (
                  <div
                    style={{
                      border: "1px solid #e0e0e0",
                      borderRadius: "6px",
                      marginTop: "6px",
                      maxHeight: "140px",
                      overflowY: "auto",
                    }}
                  >
                    {searchResults.map((ticker, i) => (
                      <div
                        key={ticker}
                        onClick={() => handleAddTicker(ticker)}
                        style={{
                          padding: "6px 10px",
                          cursor: "pointer",
                          borderTop: i > 0 ? "1px solid #f5f5f5" : "none",
                          fontSize: "0.85rem",
                          transition: "background 0.1s",
                        }}
                        onMouseEnter={(e) => (e.currentTarget.style.background = "#f0f8ff")}
                        onMouseLeave={(e) => (e.currentTarget.style.background = "#fff")}
                      >
                        {ticker}
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Model + Theme */}
              <div style={{ display: "flex", gap: "12px", marginBottom: "14px" }}>
                <div style={{ flex: 1 }}>
                  <label
                    style={{
                      fontSize: "0.82rem",
                      fontWeight: "bold",
                      marginBottom: "4px",
                      display: "block",
                    }}
                  >
                    Model
                  </label>
                  <select
                    value={model}
                    onChange={(e) => setModel(e.target.value)}
                    style={{
                      width: "100%",
                      padding: "7px 10px",
                      fontSize: "0.88rem",
                      border: "1px solid #ccc",
                      borderRadius: "6px",
                    }}
                  >
                    {MODELS.map((m) => (
                      <option key={m} value={m}>
                        {m}
                      </option>
                    ))}
                  </select>
                </div>
                <div style={{ flex: 1 }}>
                  <label
                    style={{
                      fontSize: "0.82rem",
                      fontWeight: "bold",
                      marginBottom: "4px",
                      display: "block",
                    }}
                  >
                    Theme
                  </label>
                  <select
                    value={theme}
                    onChange={(e) => setTheme(e.target.value)}
                    style={{
                      width: "100%",
                      padding: "7px 10px",
                      fontSize: "0.88rem",
                      border: "1px solid #ccc",
                      borderRadius: "6px",
                    }}
                  >
                    {THEMES.map((t) => (
                      <option key={t} value={t}>
                        {t}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Group-Level Allocation */}
              <div
                style={{
                  background: "#f7fbff",
                  border: "1px solid #d8eaf8",
                  borderRadius: "8px",
                  padding: "12px 14px",
                  marginBottom: "12px",
                }}
              >
                <p
                  style={{
                    margin: "0 0 10px 0",
                    fontWeight: 700,
                    fontSize: "0.84rem",
                    color: "#1a3a4a",
                  }}
                >
                  Group-Level Allocation
                </p>
                <div style={{ display: "flex", flexWrap: "wrap", gap: "14px" }}>
                  <SliderField
                    label="Buying Power"
                    value={buyingPower}
                    onChange={setBuyingPower}
                    color="#2e7d32"
                  />
                  <SliderField
                    label="Margin Power"
                    value={borrowPower}
                    onChange={setBorrowPower}
                    color="#e65100"
                  />
                </div>
              </div>

                {accountInfo && (
                  <div style={{ marginTop: "8px", fontSize: "0.78rem", display: "flex", gap: "16px" }}>
                    <span style={{ color: "#2e7d32" }}>
                      Preview Budget: <strong>{fmt$(previewBudgets.pieces[pieceName]?.total_budget ?? 0)}</strong>
                    </span>
                    <span style={{ color: "#e65100" }}>
                      Preview Borrow: <strong>{fmt$(previewBudgets.pieces[pieceName]?.borrow_budget ?? 0)}</strong>
                    </span>
                  </div>
                )}

              {/* Per-Ticker Allocation */}
              {selectedTickers.length > 0 && (
                <div
                  style={{
                    background: "#fff8e1",
                    border: "1px solid #ffe082",
                    borderRadius: "8px",
                    padding: "12px 14px",
                    marginBottom: "12px",
                  }}
                >
                  <p
                    style={{
                      margin: "0 0 10px 0",
                      fontWeight: 700,
                      fontSize: "0.84rem",
                      color: "#f57c00",
                    }}
                  >
                    📊 Per-Ticker Allocation
                  </p>
                  <div style={{ display: "flex", flexDirection: "column", gap: "14px" }}>
                    {selectedTickers.map((ticker) => {
                      const alloc = tickerAllocations[ticker] || {
                        buying_power: 0,
                        margin_power: 0,
                      };
                      return (
                        <div
                          key={ticker}
                          style={{
                            background: "#fffde7",
                            border: "1px solid #fff9c4",
                            borderRadius: "6px",
                            padding: "10px",
                          }}
                        >
                          <div
                            style={{
                              fontWeight: 700,
                              fontSize: "0.85rem",
                              marginBottom: "8px",
                              color: "#1a3a4a",
                            }}
                          >
                            {ticker}
                          </div>
                          <div style={{ display: "flex", gap: "14px", flexWrap: "wrap" }}>
                            <SliderField
                              label="Buying Power"
                              value={alloc.buying_power}
                              onChange={(v) =>
                                handleAllocationChange(ticker, "buying_power", v)
                              }
                              color="#2e7d32"
                            />
                            <SliderField
                              label="Margin Power"
                              value={alloc.margin_power}
                              onChange={(v) =>
                                handleAllocationChange(ticker, "margin_power", v)
                              }
                              color="#6a1b9a"
                            />
                                          {accountInfo && (
                            <div style={{ marginTop: "6px", fontSize: "0.73rem", display: "flex", gap: "12px" }}>
                              <span style={{ color: "#2e7d32" }}>
                                Budget: <strong>{fmt$(previewBudgets.tickers[ticker]?.total_budget ?? 0)}</strong>
                              </span>
                              <span style={{ color: "#6a1b9a" }}>
                                Borrow: <strong>{fmt$(previewBudgets.tickers[ticker]?.borrow_budget ?? 0)}</strong>
                              </span>
                            </div>
                          )}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* ── Footer ────────────────────────────────────────────────────── */}
        <div
          className="modal-footer d-flex justify-content-center"
          style={{
            position: "sticky",
            bottom: 0,
            background: "#fff",
            zIndex: 20,
            boxShadow: "0 -2px 10px rgba(0,0,0,0.08)",
            padding: "12px",
            gap: "10px",
            flexShrink: 0,
          }}
        >
          {(step === "list_pieces" || step === "search") && (
            <button type="button" className="btn btn-secondary" onClick={closeModal}>
              Close
            </button>
          )}

          {step === "configure" && (
            <>
              <button
                type="button"
                disabled={loading}
                onClick={() => handleSubmit("save")}
                style={{
                  background: "linear-gradient(135deg, #2e7d32 0%, #43a047 100%)",
                  color: "#fff",
                  border: "none",
                  borderRadius: "8px",
                  padding: "9px 20px",
                  fontWeight: 700,
                  fontSize: "0.9rem",
                  cursor: loading ? "not-allowed" : "pointer",
                  display: "flex",
                  alignItems: "center",
                  gap: "6px",
                  opacity: loading ? 0.7 : 1,
                }}
              >
                {loading ? (
                  <span className="spinner-border spinner-border-sm" role="status" />
                ) : editingPieceName ? (
                  "Save Changes"
                ) : (
                  "➕ Add New Group"
                )}
              </button>

              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => setStep("list_pieces")}
                disabled={loading}
              >
                Cancel
              </button>

              {editingPieceName && (
                <button
                  type="button"
                  disabled={loading}
                  onClick={() => {
                    if (window.confirm(`Delete "${pieceName}"?`)) {
                      handleSubmit("delete");
                    }
                  }}
                  style={{
                    background: "linear-gradient(135deg, #c62828 0%, #d32f2f 100%)",
                    color: "#fff",
                    border: "none",
                    borderRadius: "8px",
                    padding: "7px 15px",
                    fontWeight: 700,
                    fontSize: "0.7rem",
                    cursor: loading ? "not-allowed" : "pointer",
                    display: "flex",
                    alignItems: "center",
                    gap: "6px",
                    opacity: loading ? 0.7 : 1,
                  }}
                >
                  {loading ? (
                    <span className="spinner-border spinner-border-sm" role="status" />
                  ) : (
                    "🗑️ Delete"
                  )}
                </button>
              )}
            </>
          )}
        </div>
      </div>

      <style>{`
        @keyframes spin { to { transform: rotate(360deg); } }
      `}</style>
    </ReactModal>
  );
};

export default TickerSearchModal;