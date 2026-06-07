export type UserRole = "sales_rep" | "territory_manager" | "medical_affairs" | "analyst";

export interface RoleConfig {
  id: UserRole;
  label: string;
  title: string;
  description: string;
  focus: string[];
  sampleQuestions: string[];
  kpis: { label: string; key: string; format: "number" | "currency" | "percent" }[];
}

export const ROLES: Record<UserRole, RoleConfig> = {
  sales_rep: {
    id: "sales_rep",
    label: "Field Sales Rep",
    title: "Territory call planning & HCP engagement",
    description: "Prioritize Gold tier HCPs, track visit cadence, and prep for your next call.",
    focus: ["HCP visits", "Sample allocation", "Call outcomes", "Tier prioritization"],
    sampleQuestions: [
      "Show top cardiologists in Bangalore",
      "Which Gold HCPs have fewer than 3 rep visits?",
      "Show prescription count by HCP tier",
    ],
    kpis: [
      { label: "HCPs in Territory", key: "hcp_count", format: "number" },
      { label: "Visits This Quarter", key: "visits", format: "number" },
      { label: "Gold Tier HCPs", key: "gold_hcps", format: "number" },
      { label: "Samples Distributed", key: "samples", format: "number" },
    ],
  },
  territory_manager: {
    id: "territory_manager",
    label: "Territory Manager",
    title: "Regional performance & rep coverage",
    description: "Monitor territory sales against target and identify coverage gaps across metros.",
    focus: ["Territory ranking", "Rep productivity", "Metro penetration", "Target attainment"],
    sampleQuestions: [
      "Territory performance ranking",
      "Show monthly sales trend for diabetes products",
      "Compare market share between products",
    ],
    kpis: [
      { label: "Territory Sales", key: "territory_sales", format: "currency" },
      { label: "Target Attainment", key: "attainment", format: "percent" },
      { label: "Active Reps", key: "reps", format: "number" },
      { label: "Hospitals Covered", key: "hospitals", format: "number" },
    ],
  },
  medical_affairs: {
    id: "medical_affairs",
    label: "Medical Affairs",
    title: "KOL mapping & referral influence",
    description: "Understand prescriber networks, segmentation rationale, and compliance boundaries.",
    focus: ["KOL identification", "Referral networks", "Tier segmentation", "Compliance"],
    sampleQuestions: [
      "Which doctors influence the largest referral network?",
      "Why is an HCP classified as Gold?",
      "What is the off-label compliance policy?",
    ],
    kpis: [
      { label: "KOL Count", key: "kols", format: "number" },
      { label: "Referral Edges", key: "referrals", format: "number" },
      { label: "Gold Tier HCPs", key: "gold_hcps", format: "number" },
      { label: "Avg Segmentation Score", key: "seg_score", format: "number" },
    ],
  },
  analyst: {
    id: "analyst",
    label: "Commercial Analyst",
    title: "Sales analytics & market intelligence",
    description: "Deep-dive into product performance, Rx trends, and governed Cube metrics.",
    focus: ["Net sales", "Rx volume", "Market share", "Product mix"],
    sampleQuestions: [
      "Generate charts for quarterly sales",
      "Show monthly sales trend for diabetes products",
      "Product performance by therapeutic area",
    ],
    kpis: [
      { label: "Total Net Sales", key: "total_sales", format: "currency" },
      { label: "Total Prescriptions", key: "rx_count", format: "number" },
      { label: "Products Tracked", key: "products", format: "number" },
      { label: "Therapeutic Areas", key: "areas", format: "number" },
    ],
  },
};

export const ROLE_LIST = Object.values(ROLES);
