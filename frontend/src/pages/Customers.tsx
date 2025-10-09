import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Plus, Search, Filter, ArrowRight, X } from 'lucide-react';
import { customerApi } from '../services/api';
import { Customer, PipelineStatus } from '../types';
import { useDebounce } from '../hooks/useDebounce';
import HighlightText from '../components/HighlightText';

const Customers: React.FC = () => {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState<PipelineStatus | "">("");
  const [sourceFilter, setSourceFilter] = useState("");
  const [countryFilter, setCountryFilter] = useState("");
  const [languageFilter, setLanguageFilter] = useState("");
  const [nextActionFilter, setNextActionFilter] = useState("");
  const [sortBy, setSortBy] = useState("updated_at");
  const [sortOrder, setSortOrder] = useState<"ASC" | "DESC">("DESC");
  const [showCreateModal, setShowCreateModal] = useState(false);
  
  // Debounce search term for better performance
  const debouncedSearchTerm = useDebounce(searchTerm, 300);

  useEffect(() => {
    fetchCustomers();
  }, [debouncedSearchTerm, statusFilter, sourceFilter, countryFilter, languageFilter, nextActionFilter, sortBy, sortOrder]);

  const fetchCustomers = async () => {
    try {
      setLoading(true);
      const data = await customerApi.getAll({
        search: debouncedSearchTerm,
        status: statusFilter === "" ? undefined : statusFilter,
        source: sourceFilter === "" ? undefined : sourceFilter,
        country: countryFilter === "" ? undefined : countryFilter,
        language: languageFilter === "" ? undefined : languageFilter,
        next_action: nextActionFilter === "" ? undefined : nextActionFilter,
        sortBy,
        sortOrder,
      });
      setCustomers(data);
    } catch (error) {
      console.error("Error fetching customers:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleMoveToNextStage = async (customerId: string) => {
    try {
      await customerApi.moveToNextStage(customerId);
      fetchCustomers(); // Refresh the list
    } catch (error) {
      console.error('Error moving customer to next stage:', error);
    }
  };

  const getStatusColor = (status: PipelineStatus) => {
    switch (status) {
      case PipelineStatus.LEAD:
        return 'bg-gray-100 text-gray-800';
      case PipelineStatus.RELATIONSHIP:
        return 'bg-blue-100 text-blue-800';
      case PipelineStatus.INVITED:
        return 'bg-yellow-100 text-yellow-800';
      case PipelineStatus.QUALIFIED:
        return 'bg-orange-100 text-orange-800';
      case PipelineStatus.PRESENTATION_SENT:
        return 'bg-purple-100 text-purple-800';
      case PipelineStatus.FOLLOW_UP:
        return 'bg-indigo-100 text-indigo-800';
      case PipelineStatus.SIGNED_UP:
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Customers</h1>
          <p className="text-gray-600">Manage your customer pipeline</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="bg-primary-600 text-white px-4 py-2 rounded-md hover:bg-primary-700 transition-colors flex items-center space-x-2"
        >
          <Plus size={20} />
          <span>Add Customer</span>
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white p-4 rounded-lg shadow">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
              <input
                type="text"
                placeholder="Search by name, email, phone, status, or notes..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-10 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                aria-label="Search customers"
              />
              {searchTerm && (
                <button
                  onClick={() => setSearchTerm('')}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
                  aria-label="Clear search"
                >
                  <X size={20} />
                </button>
              )}
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4 mt-4">
              <select
                value={sourceFilter}
                onChange={(e) => setSourceFilter(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                aria-label="Filter by source"
              >
                <option value="">All Sources</option>
                {Array.from(new Set(customers.map(c => c.source).filter(Boolean))).map(source => (
                  <option key={source} value={source}>{source}</option>
                ))}
              </select>
              <select
                value={countryFilter}
                onChange={(e) => setCountryFilter(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                aria-label="Filter by country"
              >
                <option value="">All Countries</option>
                {Array.from(new Set(customers.map(c => c.country).filter(Boolean))).map(country => (
                  <option key={country} value={country}>{country}</option>
                ))}
              </select>
              <select
                value={languageFilter}
                onChange={(e) => setLanguageFilter(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                aria-label="Filter by language"
              >
                <option value="">All Languages</option>
                {Array.from(new Set(customers.map(c => c.language).filter(Boolean))).map(language => (
                  <option key={language} value={language}>{language}</option>
                ))}
              </select>
              <select
                value={nextActionFilter}
                onChange={(e) => setNextActionFilter(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                aria-label="Filter by next action"
              >
                <option value="">All Next Actions</option>
                {/* Add next action options here */}
              </select>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                aria-label="Sort by"
              >
                <option value="updated_at">Last Updated</option>
                <option value="created_at">Date Created</option>
                <option value="name">Name</option>
                <option value="status">Status</option>
              </select>
              <select
                value={sortOrder}
                onChange={(e) => setSortOrder(e.target.value as 'ASC' | 'DESC')}
                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                aria-label="Sort order"
              >
                <option value="DESC">Descending</option>
                <option value="ASC">Ascending</option>
              </select>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <Filter size={20} className="text-gray-400" />
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value as PipelineStatus | '')}
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              aria-label="Filter by status"
            >
              <option value="">All Statuses</option>
              {Object.values(PipelineStatus).map((status) => (
                <option key={status} value={status}>
                  {status}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {(searchTerm || statusFilter || sourceFilter || countryFilter || languageFilter || nextActionFilter) && (
        <p className="text-sm text-gray-600 mt-2">
          Showing {customers.length} customers
          {searchTerm && ` matching "${searchTerm}"`}
        </p>
      )}

      {/* Customer List */}
      <div className="bg-white shadow rounded-lg">
        {customers.length === 0 ? (
          <div className="p-12 text-center">
            <p className="text-gray-500">No customers found</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {customers.map((customer) => (
              <div key={customer.id} className="p-6 hover:bg-gray-50 transition-colors border-b border-gray-100 last:border-b-0">
                <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <h3 className="text-lg font-semibold text-gray-900 truncate">
                      <Link
                        to={`/customers/${customer.id}`}
                        className="hover:text-primary-600 transition-colors"
                      >
                        <HighlightText text={customer.name} highlight={debouncedSearchTerm} />
                      </Link>
                    </h3>
                    <div className="flex flex-wrap items-center gap-x-4 text-sm text-gray-500 mt-1">
                      {customer.email && (
                        <span className="flex items-center gap-1">
                          <Mail size={14} className="text-gray-400" />
                          <HighlightText text={customer.email} highlight={debouncedSearchTerm} />
                        </span>
                      )}
                      {customer.phone && (
                        <span className="flex items-center gap-1">
                          <Phone size={14} className="text-gray-400" />
                          <HighlightText text={customer.phone} highlight={debouncedSearchTerm} />
                        </span>
                      )}
                      {customer.country && (
                        <span className="flex items-center gap-1">
                          <span className="text-gray-400">📍</span>
                          <HighlightText text={customer.country} highlight={debouncedSearchTerm} />
                        </span>
                      )}
                      {customer.language && (
                        <span className="flex items-center gap-1">
                          <span className="text-gray-400">🗣️</span>
                          <HighlightText text={customer.language} highlight={debouncedSearchTerm} />
                        </span>
                      )}
                    </div>
                    {customer.notes && (
                      <p className="text-sm text-gray-600 mt-2 max-w-full sm:max-w-md truncate">{customer.notes}</p>
                    )}
                    {customer.next_action && (
                      <div className="mt-2 flex items-center gap-2">
                        <Calendar size={16} className="text-gray-500" />
                        <span className="text-sm font-medium text-gray-700">Next Action: </span>
                        <span className="text-sm text-gray-600">{customer.next_action}</span>
                        {customer.next_action_date && (
                          <span className="text-sm text-gray-500 ml-1">
                            ({new Date(customer.next_action_date).toLocaleDateString()})
                          </span>
                        )}
                      </div>
                    )}
                  </div>
                  
                  <div className="flex flex-col items-end sm:items-center space-y-2 sm:space-y-0 sm:flex-row sm:space-x-4 mt-4 sm:mt-0">
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(customer.status)}`}
                    >
                      {customer.status}
                    </span>
                    
                    {customer.status !== PipelineStatus.SIGNED_UP && (
                      <button
                        onClick={() => handleMoveToNextStage(customer.id)}
                        className="p-2 text-gray-400 hover:text-primary-600 transition-colors rounded-full bg-gray-100 hover:bg-gray-200"
                        title="Move to next stage"
                      >
                        <ArrowRight size={16} />
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Create Customer Modal */}
      {showCreateModal && (
        <CreateCustomerModal
          onClose={() => setShowCreateModal(false)}
          onSuccess={() => {
            setShowCreateModal(false);
            fetchCustomers();
          }}
        />
      )}
    </div>
  );
};

// Create Customer Modal Component
interface CreateCustomerModalProps {
  onClose: () => void;
  onSuccess: () => void;
}

const CreateCustomerModal: React.FC<CreateCustomerModalProps> = ({ onClose, onSuccess }) => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    notes: '',
    status: PipelineStatus.LEAD,
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.name) return;

    try {
      setLoading(true);
      await customerApi.create(formData);
      onSuccess();
    } catch (error) {
      console.error('Error creating customer:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Add New Customer</h2>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Name *</label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
            <input
              type="email"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Phone</label>
            <input
              type="tel"
              value={formData.phone}
              onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
            <select
              value={formData.status}
              onChange={(e) => setFormData({ ...formData, status: e.target.value as PipelineStatus })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            >
              {Object.values(PipelineStatus).map((status) => (
                <option key={status} value={status}>
                  {status}
                </option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Notes</label>
            <textarea
              value={formData.notes}
              onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>
          
          <div className="flex justify-end space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading || !formData.name}
              className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Creating...' : 'Create Customer'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Customers;