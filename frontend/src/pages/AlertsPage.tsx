import React, { useEffect, useState, useMemo } from 'react';
import { WeatherApi } from '../services/api';
import { Card } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { AlertModal } from '../components/alerts/AlertModal';
import type { AlertItem, AlertSeverity, AlertType, DistrictName } from '../types/weather';
import { APP_CONFIG } from '../data/config';
import { 
  Bell, 
  Search, 
  Filter, 
  ArrowUpDown, 
  Calendar, 
  AlertTriangle, 
  CheckCircle2, 
  Info,
  Clock,
  Eye
} from 'lucide-react';

export const AlertsPage: React.FC = () => {
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedAlert, setSelectedAlert] = useState<AlertItem | null>(null);

  // Filters state
  const [searchQuery, setSearchQuery] = useState('');
  const [districtFilter, setDistrictFilter] = useState<string>('all');
  const [severityFilter, setSeverityFilter] = useState<string>('all');
  const [leadDayFilter, setLeadDayFilter] = useState<string>('all');
  const [typeFilter, setTypeFilter] = useState<string>('all');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [sortField, setSortField] = useState<'timestamp' | 'leadDay' | 'bustProbability' | 'reliability'>('bustProbability');
  const [sortAsc, setSortAsc] = useState(false);

  useEffect(() => {
    WeatherApi.getAlerts().then((res) => {
      setAlerts(res);
      setLoading(false);
    });
  }, []);

  const filteredAlerts = useMemo(() => {
    return alerts
      .filter((alert) => {
        // Search query
        if (searchQuery) {
          const q = searchQuery.toLowerCase();
          const matchTitle = alert.title.toLowerCase().includes(q);
          const matchDistrict = alert.district.toLowerCase().includes(q);
          const matchExpl = alert.explanation.toLowerCase().includes(q);
          if (!matchTitle && !matchDistrict && !matchExpl) return false;
        }

        // District filter
        if (districtFilter !== 'all' && alert.district !== districtFilter) {
          return false;
        }

        // Severity filter
        if (severityFilter !== 'all' && alert.severity !== severityFilter) {
          return false;
        }

        // Lead Day filter
        if (leadDayFilter !== 'all' && alert.leadDay !== Number(leadDayFilter)) {
          return false;
        }

        // Alert Type filter
        if (typeFilter !== 'all' && alert.alertType !== typeFilter) {
          return false;
        }

        // Status filter
        if (statusFilter !== 'all' && alert.status !== statusFilter) {
          return false;
        }

        return true;
      })
      .sort((a, b) => {
        let valA = a[sortField];
        let valB = b[sortField];
        if (sortAsc) {
          return valA > valB ? 1 : -1;
        }
        return valA < valB ? 1 : -1;
      });
  }, [alerts, searchQuery, districtFilter, severityFilter, leadDayFilter, typeFilter, statusFilter, sortField, sortAsc]);

  const getSeverityBadge = (severity: AlertSeverity) => {
    switch (severity) {
      case 'critical':
      case 'high':
        return <Badge variant="rose" size="xs" dot>{severity.toUpperCase()}</Badge>;
      case 'moderate':
        return <Badge variant="amber" size="xs" dot>{severity.toUpperCase()}</Badge>;
      case 'low':
      default:
        return <Badge variant="blue" size="xs" dot>{severity.toUpperCase()}</Badge>;
    }
  };

  const getStatusBadge = (status: AlertItem['status']) => {
    switch (status) {
      case 'Active':
        return <Badge variant="rose" size="xs">ACTIVE</Badge>;
      case 'Investigating':
        return <Badge variant="amber" size="xs">INVESTIGATING</Badge>;
      case 'Resolved':
      default:
        return <Badge variant="emerald" size="xs">RESOLVED</Badge>;
    }
  };

  const toggleSort = (field: typeof sortField) => {
    if (sortField === field) {
      setSortAsc(!sortAsc);
    } else {
      setSortField(field);
      setSortAsc(false);
    }
  };

  return (
    <div className="space-y-6 font-sans">
      {/* Header */}
      <div className="bg-white rounded-xl border border-slate-200/90 shadow-2xs p-6 space-y-3">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1.5">
              <Badge variant="rose" size="xs" dot>
                Live Anomaly Feed
              </Badge>
              <Badge variant="slate" size="xs">
                Threshold Driven
              </Badge>
            </div>
            <h1 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight">
              Forecast Alerts &amp; Historical Anomaly Log
            </h1>
            <p className="text-xs sm:text-sm text-slate-500 mt-1 max-w-3xl leading-relaxed">
              Real-time audit log of forecast uncertainty spikes, low reliability events, and potential forecast-bust detections.
            </p>
          </div>

          <div className="flex items-center gap-3 text-xs">
            <span className="text-slate-500">Active Alerts:</span>
            <span className="px-2.5 py-1 rounded-full bg-rose-50 text-rose-700 font-bold border border-rose-200">
              {alerts.filter(a => a.status === 'Active').length} Active
            </span>
          </div>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white rounded-xl border border-slate-200/90 p-4 shadow-2xs space-y-3">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-6 gap-3">
          {/* Search Box */}
          <div className="lg:col-span-2 relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              placeholder="Search by title, district, or explanation..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-slate-50 border border-slate-200 text-slate-900 text-xs rounded-lg pl-9 pr-3 py-2 focus:bg-white focus:ring-2 focus:ring-slate-900 focus:border-slate-900 transition-all"
            />
          </div>

          {/* District Filter */}
          <div>
            <select
              value={districtFilter}
              onChange={(e) => setDistrictFilter(e.target.value)}
              className="w-full bg-slate-50 border border-slate-200 text-slate-900 text-xs rounded-lg px-3 py-2 focus:bg-white focus:ring-2 focus:ring-slate-900 cursor-pointer"
            >
              <option value="all">All Districts</option>
              {APP_CONFIG.studyDistricts.map((d) => (
                <option key={d} value={d}>
                  {d}
                </option>
              ))}
              <option value="Regional">Regional Scope</option>
            </select>
          </div>

          {/* Severity Filter */}
          <div>
            <select
              value={severityFilter}
              onChange={(e) => setSeverityFilter(e.target.value)}
              className="w-full bg-slate-50 border border-slate-200 text-slate-900 text-xs rounded-lg px-3 py-2 focus:bg-white focus:ring-2 focus:ring-slate-900 cursor-pointer"
            >
              <option value="all">All Severities</option>
              <option value="critical">Critical</option>
              <option value="high">High</option>
              <option value="moderate">Moderate</option>
              <option value="low">Low</option>
            </select>
          </div>

          {/* Lead Day Filter */}
          <div>
            <select
              value={leadDayFilter}
              onChange={(e) => setLeadDayFilter(e.target.value)}
              className="w-full bg-slate-50 border border-slate-200 text-slate-900 text-xs rounded-lg px-3 py-2 focus:bg-white focus:ring-2 focus:ring-slate-900 cursor-pointer"
            >
              <option value="all">All Lead Days</option>
              {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((d) => (
                <option key={d} value={d}>
                  Day {d} ({d * 24}h)
                </option>
              ))}
            </select>
          </div>

          {/* Status Filter */}
          <div>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="w-full bg-slate-50 border border-slate-200 text-slate-900 text-xs rounded-lg px-3 py-2 focus:bg-white focus:ring-2 focus:ring-slate-900 cursor-pointer"
            >
              <option value="all">All Statuses</option>
              <option value="Active">Active</option>
              <option value="Investigating">Investigating</option>
              <option value="Resolved">Resolved</option>
            </select>
          </div>
        </div>

        <div className="flex items-center justify-between text-xs text-slate-500 pt-1">
          <span>
            Showing <strong>{filteredAlerts.length}</strong> of {alerts.length} historical events
          </span>
          <button
            onClick={() => {
              setSearchQuery('');
              setDistrictFilter('all');
              setSeverityFilter('all');
              setLeadDayFilter('all');
              setTypeFilter('all');
              setStatusFilter('all');
            }}
            className="text-slate-600 hover:text-slate-900 underline cursor-pointer"
          >
            Reset Filters
          </button>
        </div>
      </div>

      {/* Alerts Table */}
      <Card noPadding className="overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-xs text-left border-collapse">
            <thead className="bg-slate-50/90 text-slate-700 font-semibold border-b border-slate-200">
              <tr>
                <th
                  onClick={() => toggleSort('timestamp')}
                  className="py-3 px-4 cursor-pointer hover:bg-slate-100 transition-colors"
                >
                  <div className="flex items-center gap-1.5">
                    <span>Time</span>
                    <ArrowUpDown className="w-3 h-3 text-slate-400" />
                  </div>
                </th>
                <th className="py-3 px-4">District</th>
                <th className="py-3 px-4">Alert Title &amp; Reason</th>
                <th
                  onClick={() => toggleSort('leadDay')}
                  className="py-3 px-4 cursor-pointer hover:bg-slate-100 transition-colors"
                >
                  <div className="flex items-center gap-1.5">
                    <span>Lead Day</span>
                    <ArrowUpDown className="w-3 h-3 text-slate-400" />
                  </div>
                </th>
                <th
                  onClick={() => toggleSort('reliability')}
                  className="py-3 px-4 cursor-pointer hover:bg-slate-100 transition-colors"
                >
                  <div className="flex items-center gap-1.5">
                    <span>Reliability (R)</span>
                    <ArrowUpDown className="w-3 h-3 text-slate-400" />
                  </div>
                </th>
                <th
                  onClick={() => toggleSort('bustProbability')}
                  className="py-3 px-4 cursor-pointer hover:bg-slate-100 transition-colors"
                >
                  <div className="flex items-center gap-1.5">
                    <span>Bust Prob</span>
                    <ArrowUpDown className="w-3 h-3 text-slate-400" />
                  </div>
                </th>
                <th className="py-3 px-4">Severity</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filteredAlerts.length > 0 ? (
                filteredAlerts.map((alert) => (
                  <tr
                    key={alert.id}
                    className="hover:bg-slate-50/70 transition-colors"
                  >
                    <td className="py-3 px-4 font-mono text-[11px] text-slate-500 whitespace-nowrap">
                      {alert.timestamp}
                    </td>
                    <td className="py-3 px-4 font-bold text-slate-900">
                      {alert.district}
                    </td>
                    <td className="py-3 px-4 max-w-sm">
                      <div className="font-semibold text-slate-900">
                        {alert.title}
                      </div>
                      <div className="text-[11px] text-slate-500 line-clamp-1 mt-0.5">
                        {alert.explanation}
                      </div>
                    </td>
                    <td className="py-3 px-4 font-mono font-medium text-slate-700 whitespace-nowrap">
                      Day {alert.leadDay} ({alert.leadDay * 24}h)
                    </td>
                    <td className="py-3 px-4 font-mono font-bold text-slate-900">
                      {alert.reliability.toFixed(2)}
                    </td>
                    <td className="py-3 px-4 font-mono font-bold">
                      <span
                        className={
                          alert.bustProbability >= 70
                            ? 'text-rose-600'
                            : alert.bustProbability >= 35
                            ? 'text-amber-600'
                            : 'text-emerald-600'
                        }
                      >
                        {alert.bustProbability}%
                      </span>
                    </td>
                    <td className="py-3 px-4 whitespace-nowrap">
                      {getSeverityBadge(alert.severity)}
                    </td>
                    <td className="py-3 px-4 whitespace-nowrap">
                      {getStatusBadge(alert.status)}
                    </td>
                    <td className="py-3 px-4 text-right whitespace-nowrap">
                      <button
                        onClick={() => setSelectedAlert(alert)}
                        className="p-1.5 rounded-lg border border-slate-200 text-slate-600 hover:text-slate-900 hover:bg-slate-100 transition-colors inline-flex items-center gap-1 cursor-pointer"
                        title="View Full Diagnostics"
                      >
                        <Eye className="w-3.5 h-3.5" />
                        <span className="text-[11px] font-semibold">Inspect</span>
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={9} className="py-8 text-center text-slate-400 italic">
                    No alerts match the selected filter criteria.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Alert Diagnostics Drawer / Modal */}
      <AlertModal
        alert={selectedAlert}
        onClose={() => setSelectedAlert(null)}
      />
    </div>
  );
};
