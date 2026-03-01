import { useEffect, useMemo, useState } from 'react'
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import {
  BadgeDollarSign,
  Boxes,
  Crown,
  Download,
  LayoutDashboard,
  Search,
  ShieldAlert,
  ShoppingBag,
  TrendingUp,
  Users,
} from 'lucide-react'
import './index.css'

type SalesTrend = { order_month: string; total_orders: number; total_revenue: number; mom_growth_pct: number }
type RegionRevenue = { region: string; region_revenue: number; active_customers: number }
type Rfm = {
  customer_id: string
  frequency: number
  monetary: number
  recency_days: number
  segment: string
  region: string
  r_score: number
  f_score: number
  m_score: number
}
type Cohort = { cohort_month: string; cohort_index: number; retention_rate: number }
type Clv = { customer_id: string; predicted_purchases_90d: number; predicted_clv: number }
type Rule = { antecedents: string; consequents: string; confidence: number; lift: number }

type Payload = {
  kpi_summary: { total_revenue: number; total_customers: number; total_orders: number; avg_order_value: number }
  sales_trend: SalesTrend[]
  revenue_by_region: RegionRevenue[]
  top_products_revenue: Array<{ product_name: string; product_revenue: number }>
  rfm: Rfm[]
  cohort: Cohort[]
  clv: Clv[]
  market_basket: Rule[]
  champions: Rfm[]
  churn_risk: Rfm[]
}

const COLORS = ['#0ea5e9', '#14b8a6', '#f59e0b', '#84cc16', '#f97316', '#6366f1']

const money = (v: number) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(v || 0)
const num = (v: number) => new Intl.NumberFormat('en-US').format(v || 0)

function toDate(value: string): Date {
  const d = new Date(value)
  return Number.isNaN(d.getTime()) ? new Date() : d
}

function downloadCsv(name: string, rows: Record<string, unknown>[]) {
  if (!rows.length) return
  const headers = Object.keys(rows[0])
  const lines = [headers.join(',')]
  rows.forEach((row) => {
    const vals = headers.map((h) => {
      const raw = row[h] ?? ''
      const text = String(raw).replaceAll('"', '""')
      return `"${text}"`
    })
    lines.push(vals.join(','))
  })
  const blob = new Blob([lines.join('\n')], { type: 'text/csv;charset=utf-8;' })
  const a = document.createElement('a')
  a.href = URL.createObjectURL(blob)
  a.download = `${name}.csv`
  a.click()
  URL.revokeObjectURL(a.href)
}

function App() {
  const [data, setData] = useState<Payload | null>(null)
  const [loading, setLoading] = useState(true)
  const [loadError, setLoadError] = useState<string | null>(null)
  const [region, setRegion] = useState('All')
  const [segment, setSegment] = useState('All')
  const [monthWindow, setMonthWindow] = useState<'All' | '3' | '6' | '12'>('12')
  const [searchCustomer, setSearchCustomer] = useState('')

  useEffect(() => {
    setLoading(true)
    fetch('/data/dashboard_payload.json')
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`)
        return r.json()
      })
      .then((json) => {
        setData(json)
        setLoadError(null)
      })
      .catch((e) => setLoadError(String(e)))
      .finally(() => setLoading(false))
  }, [])

  const regions = useMemo(() => (!data ? ['All'] : ['All', ...Array.from(new Set(data.rfm.map((x) => x.region || 'Unknown')))]), [data])
  const segments = useMemo(() => (!data ? ['All'] : ['All', ...Array.from(new Set(data.rfm.map((x) => x.segment)))]), [data])

  const filteredRfm = useMemo(() => {
    if (!data) return []
    return data.rfm
      .filter((x) => (region === 'All' ? true : x.region === region))
      .filter((x) => (segment === 'All' ? true : x.segment === segment))
  }, [data, region, segment])

  const trendFiltered = useMemo(() => {
    if (!data) return []
    const rows = [...data.sales_trend]
    if (monthWindow === 'All') return rows
    const last = rows.length ? toDate(rows[rows.length - 1].order_month) : new Date()
    const months = Number(monthWindow)
    return rows.filter((r) => {
      const d = toDate(r.order_month)
      const diff = (last.getFullYear() - d.getFullYear()) * 12 + (last.getMonth() - d.getMonth())
      return diff < months
    })
  }, [data, monthWindow])

  const segmentRevenue = useMemo(() => {
    const map = new Map<string, number>()
    filteredRfm.forEach((x) => map.set(x.segment, (map.get(x.segment) || 0) + Number(x.monetary || 0)))
    return Array.from(map.entries()).map(([segment, revenue]) => ({ segment, revenue })).sort((a, b) => b.revenue - a.revenue)
  }, [filteredRfm])

  const topClv = useMemo(() => {
    if (!data) return []
    return [...data.clv].sort((a, b) => Number(b.predicted_clv || 0) - Number(a.predicted_clv || 0)).slice(0, 10)
  }, [data])

  const spotlight = useMemo(() => {
    if (!searchCustomer.trim()) return null
    const key = searchCustomer.trim().toLowerCase()
    return filteredRfm.find((x) => x.customer_id.toLowerCase().includes(key)) ?? null
  }, [filteredRfm, searchCustomer])

  const cohortMatrix = useMemo(() => {
    if (!data) return { rows: [] as string[], cols: [] as number[], matrix: [] as number[][] }
    const rows = Array.from(new Set(data.cohort.map((c) => c.cohort_month))).sort()
    const cols = Array.from(new Set(data.cohort.map((c) => Number(c.cohort_index)))).sort((a, b) => a - b).slice(0, 10)
    const matrix = rows.slice(0, 10).map((row) => cols.map((col) => {
      const hit = data.cohort.find((c) => c.cohort_month === row && Number(c.cohort_index) === col)
      return hit ? Number(hit.retention_rate) : 0
    }))
    return { rows: rows.slice(0, 10), cols, matrix }
  }, [data])

  const campaignPriority = useMemo(() => {
    if (!data) return []
    return [...data.churn_risk]
      .filter((x) => (region === 'All' ? true : x.region === region))
      .map((x) => ({
        ...x,
        priority_score: Number(x.recency_days || 0) * 0.55 + Number(x.monetary || 0) * 0.001 + Number(x.frequency || 0) * 4,
      }))
      .sort((a, b) => b.priority_score - a.priority_score)
      .slice(0, 12)
  }, [data, region])

  if (loading) return <div className="state-screen">Loading dashboard...</div>
  if (loadError || !data) return <div className="state-screen">Data load issue: {loadError}</div>

  const growth = trendFiltered.length > 1
    ? ((Number(trendFiltered[trendFiltered.length - 1].total_revenue || 0) - Number(trendFiltered[trendFiltered.length - 2].total_revenue || 0))
      / Math.max(Number(trendFiltered[trendFiltered.length - 2].total_revenue || 1), 1)) * 100
    : 0
  const championRate = filteredRfm.length ? (filteredRfm.filter((x) => x.segment === 'Champions').length / filteredRfm.length) * 100 : 0
  const churnRate = filteredRfm.length ? (filteredRfm.filter((x) => ['Churn Risk', 'At Risk', 'Hibernating'].includes(x.segment)).length / filteredRfm.length) * 100 : 0
  const avgFrequency = filteredRfm.length ? filteredRfm.reduce((a, b) => a + Number(b.frequency || 0), 0) / filteredRfm.length : 0
  const insights = [
    championRate < 8
      ? `Champion share ${championRate.toFixed(1)}% is low. Launch VIP retention + referral strategy.`
      : `Champion share ${championRate.toFixed(1)}% is healthy. Increase premium upsell bundles.`,
    churnRate > 25
      ? `Churn risk ${churnRate.toFixed(1)}% is elevated. Trigger urgency-based save campaigns this week.`
      : `Churn risk ${churnRate.toFixed(1)}% is manageable. Focus on new customer activation journeys.`,
    growth < 0
      ? `Latest monthly growth is negative (${growth.toFixed(2)}%). Re-balance channel spend by region.`
      : `Latest monthly growth is positive (${growth.toFixed(2)}%). Scale top-performing product clusters.`,
  ]

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-dot" />
          <div>
            <h2>Consumer360</h2>
            <p>Retail Analytics Suite</p>
          </div>
        </div>

        <nav className="nav">
          <a href="#overview"><LayoutDashboard size={16} /> Overview</a>
          <a href="#segments"><Users size={16} /> Segments</a>
          <a href="#retention"><TrendingUp size={16} /> Retention</a>
          <a href="#clv"><BadgeDollarSign size={16} /> CLV Desk</a>
          <a href="#campaigns"><ShieldAlert size={16} /> Campaigns</a>
          <a href="#products"><Boxes size={16} /> Products</a>
        </nav>

        <div className="side-card">
          <p>Filters</p>
          <label>Region</label>
          <select value={region} onChange={(e) => setRegion(e.target.value)}>
            {regions.map((r) => <option key={r}>{r}</option>)}
          </select>
          <label>Segment</label>
          <select value={segment} onChange={(e) => setSegment(e.target.value)}>
            {segments.map((s) => <option key={s}>{s}</option>)}
          </select>
          <label>Window</label>
          <select value={monthWindow} onChange={(e) => setMonthWindow(e.target.value as 'All' | '3' | '6' | '12')}>
            <option value="3">Last 3 Months</option>
            <option value="6">Last 6 Months</option>
            <option value="12">Last 12 Months</option>
            <option value="All">All Months</option>
          </select>
        </div>

        <div className="side-actions">
          <button onClick={() => downloadCsv('champions_export', data.champions as unknown as Record<string, unknown>[])}><Download size={14} /> Export Champions</button>
          <button onClick={() => downloadCsv('churn_risk_export', data.churn_risk as unknown as Record<string, unknown>[])}><Download size={14} /> Export Churn Risk</button>
        </div>

        <div className="side-kpi">
          <p>MoM Growth</p>
          <strong className={growth >= 0 ? 'good' : 'bad'}>{growth.toFixed(2)}%</strong>
        </div>
      </aside>

      <main className="content">
        <section id="overview" className="hero">
          <h1>Executive Retail Intelligence Dashboard</h1>
          <p>Professional weekly command center for value customers, churn prevention, and growth opportunities.</p>
        </section>

        <section className="kpi-grid">
          <article className="kpi"><span>Total Revenue</span><strong>{money(data.kpi_summary.total_revenue)}</strong><ShoppingBag size={18} /></article>
          <article className="kpi"><span>Customers</span><strong>{num(data.kpi_summary.total_customers)}</strong><Users size={18} /></article>
          <article className="kpi"><span>Total Orders</span><strong>{num(data.kpi_summary.total_orders)}</strong><Boxes size={18} /></article>
          <article className="kpi"><span>Avg Order Value</span><strong>{money(data.kpi_summary.avg_order_value)}</strong><Crown size={18} /></article>
        </section>

        <section className="kpi-grid secondary">
          <article className="kpi mini"><span>Champion Share</span><strong>{championRate.toFixed(1)}%</strong></article>
          <article className="kpi mini"><span>Churn Risk Share</span><strong>{churnRate.toFixed(1)}%</strong></article>
          <article className="kpi mini"><span>Avg Frequency</span><strong>{avgFrequency.toFixed(2)}</strong></article>
          <article className="kpi mini"><span>Filtered Customers</span><strong>{num(filteredRfm.length)}</strong></article>
        </section>

        <section className="two-col">
          <article className="card">
            <h3>Revenue Trend</h3>
            <ResponsiveContainer width="100%" height={280}>
              <AreaChart data={trendFiltered}>
                <defs>
                  <linearGradient id="revGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#0ea5e9" stopOpacity={0.35} />
                    <stop offset="95%" stopColor="#0ea5e9" stopOpacity={0.04} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#dbe4f0" />
                <XAxis dataKey="order_month" tick={{ fill: '#51617a', fontSize: 11 }} />
                <YAxis tick={{ fill: '#51617a', fontSize: 11 }} />
                <Tooltip formatter={(v) => money(Number(v ?? 0))} />
                <Area type="monotone" dataKey="total_revenue" stroke="#0284c7" fill="url(#revGrad)" strokeWidth={2.2} />
              </AreaChart>
            </ResponsiveContainer>
          </article>

          <article className="card">
            <h3>Revenue by Region</h3>
            <ResponsiveContainer width="100%" height={280}>
              <PieChart>
                <Pie data={data.revenue_by_region} dataKey="region_revenue" nameKey="region" innerRadius={62} outerRadius={98}>
                  {data.revenue_by_region.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                </Pie>
                <Tooltip formatter={(v) => money(Number(v ?? 0))} />
              </PieChart>
            </ResponsiveContainer>
            <div className="chips">
              {data.revenue_by_region.map((x, i) => <span key={x.region}><i style={{ background: COLORS[i % COLORS.length] }} />{x.region}</span>)}
            </div>
          </article>
        </section>

        <section className="two-col">
          <article className="card">
            <h3><Search size={16} /> Customer Spotlight</h3>
            <input
              className="search-input"
              value={searchCustomer}
              onChange={(e) => setSearchCustomer(e.target.value)}
              placeholder="Search customer id, e.g. C00045"
            />
            <div className="spotlight-box">
              {spotlight ? (
                <>
                  <p><strong>{spotlight.customer_id}</strong> | {spotlight.segment}</p>
                  <p>Region: {spotlight.region}</p>
                  <p>Monetary: {money(Number(spotlight.monetary || 0))}</p>
                  <p>Frequency: {spotlight.frequency} | Recency: {spotlight.recency_days} days</p>
                </>
              ) : (
                <p>Type customer id to view profile insights.</p>
              )}
            </div>
          </article>

          <article className="card">
            <h3>Strategic Insights</h3>
            <ul className="rules">
              {insights.map((x, idx) => <li key={idx}>{x}</li>)}
            </ul>
          </article>
        </section>

        <section id="segments" className="two-col">
          <article className="card">
            <h3>Segment Revenue</h3>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={segmentRevenue}>
                <CartesianGrid strokeDasharray="3 3" stroke="#dbe4f0" />
                <XAxis dataKey="segment" tick={{ fill: '#51617a', fontSize: 10 }} />
                <YAxis tick={{ fill: '#51617a', fontSize: 11 }} />
                <Tooltip formatter={(v) => money(Number(v ?? 0))} />
                <Bar dataKey="revenue" fill="#14b8a6" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </article>

          <article className="card">
            <h3>RFM Distribution</h3>
            <ResponsiveContainer width="100%" height={280}>
              <ScatterChart>
                <CartesianGrid strokeDasharray="3 3" stroke="#dbe4f0" />
                <XAxis type="number" dataKey="frequency" tick={{ fill: '#51617a', fontSize: 11 }} />
                <YAxis type="number" dataKey="monetary" tick={{ fill: '#51617a', fontSize: 11 }} />
                <Tooltip formatter={(v) => Number(v ?? 0).toFixed(2)} />
                <Scatter data={filteredRfm.slice(0, 1800)} fill="#6366f1" />
              </ScatterChart>
            </ResponsiveContainer>
          </article>
        </section>

        <section id="retention" className="two-col">
          <article className="card">
            <h3>Cohort Retention Matrix</h3>
            <div className="cohort-head">
              <span>Cohort</span>
              <div>{cohortMatrix.cols.map((c) => <b key={c}>M{c}</b>)}</div>
            </div>
            {cohortMatrix.rows.map((r, rIndex) => (
              <div className="cohort-row" key={r}>
                <span>{r.slice(0, 7)}</span>
                <div>
                  {cohortMatrix.matrix[rIndex].map((v, idx) => (
                    <i key={idx} style={{ background: `rgba(20,184,166,${0.12 + Math.min(v, 0.8)})` }}>{Math.round(v * 100)}%</i>
                  ))}
                </div>
              </div>
            ))}
          </article>

          <article id="clv" className="card">
            <h3>Top CLV Customers</h3>
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Customer</th>
                    <th>Predicted CLV</th>
                    <th>90D Purchases</th>
                  </tr>
                </thead>
                <tbody>
                  {topClv.map((x) => (
                    <tr key={x.customer_id}>
                      <td>{x.customer_id}</td>
                      <td>{money(Number(x.predicted_clv || 0))}</td>
                      <td>{Number(x.predicted_purchases_90d || 0).toFixed(2)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </article>
        </section>

        <section id="campaigns" className="two-col">
          <article className="card">
            <h3>Campaign Priority Queue</h3>
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Customer</th>
                    <th>Segment</th>
                    <th>Score</th>
                    <th>Monetary</th>
                  </tr>
                </thead>
                <tbody>
                  {campaignPriority.map((x) => (
                    <tr key={x.customer_id}>
                      <td>{x.customer_id}</td>
                      <td>{x.segment}</td>
                      <td>{x.priority_score.toFixed(1)}</td>
                      <td>{money(Number(x.monetary || 0))}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </article>

          <article id="products" className="card">
            <h3>Top Products by Revenue</h3>
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Product</th>
                    <th>Revenue</th>
                  </tr>
                </thead>
                <tbody>
                  {data.top_products_revenue.slice(0, 12).map((p) => (
                    <tr key={p.product_name}>
                      <td>{p.product_name}</td>
                      <td>{money(Number(p.product_revenue || 0))}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <h4>Top Basket Opportunities</h4>
            <ul className="rules">
                {data.market_basket.slice(0, 5).map((r, i) => (
                  <li key={i}>{r.antecedents} {'->'} {r.consequents} ({(Number(r.confidence || 0) * 100).toFixed(1)}% conf)</li>
                ))}
              {!data.market_basket.length && <li>No basket rules on current threshold.</li>}
            </ul>
          </article>
        </section>
      </main>
    </div>
  )
}

export default App


