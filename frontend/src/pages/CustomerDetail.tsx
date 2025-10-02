import React, { useEffect, useState, useCallback } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { ArrowLeft, Edit, Phone, Mail, Calendar, Plus, MessageSquare, ArrowRight, CheckCircle } from 'lucide-react';
import { customerApi, interactionApi } from '../services/api';
import { Customer, Interaction, PipelineStatus, InteractionType } from '../types';
import { format } from 'date-fns';
import QualificationQuestionnaire from '../components/QualificationQuestionnaire';

const CustomerDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [customer, setCustomer] = useState<Customer | null>(null);
  const [interactions, setInteractions] = useState<Interaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [editMode, setEditMode] = useState(false);
  const [showAddInteraction, setShowAddInteraction] = useState(false);
  const [showQualification, setShowQualification] = useState(false);

  const fetchCustomerData = useCallback(async (customerId: string) => {
    try {
      setLoading(true);
      const [customerData, interactionsData] = await Promise.all([
        customerApi.getById(customerId),
        interactionApi.getByCustomer(customerId)
      ]);
      setCustomer(customerData);
      setInteractions(interactionsData);
    } catch (error) {
      console.error('Error fetching customer data:', error);
      navigate('/customers');
    } finally {
      setLoading(false);
    }
  }, [navigate]);

  useEffect(() => {
    if (id) {
      fetchCustomerData(id);
    }
  }, [id, fetchCustomerData]);

  const handleMoveToNextStage = async () => {
    if (!customer) return;
    
    try {
      const updatedCustomer = await customerApi.moveToNextStage(customer.id);
      setCustomer(updatedCustomer);
    } catch (error) {
      console.error('Error moving to next stage:', error);
    }
  };

  const getStatusColor = (status: PipelineStatus) => {
    switch (status) {
      case PipelineStatus.LEAD:
        return 'bg-gray-100 text-gray-800 border-gray-300';
      case PipelineStatus.RELATIONSHIP:
        return 'bg-blue-100 text-blue-800 border-blue-300';
      case PipelineStatus.INVITED:
        return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case PipelineStatus.QUALIFIED:
        return 'bg-orange-100 text-orange-800 border-orange-300';
      case PipelineStatus.PRESENTATION_SENT:
        return 'bg-purple-100 text-purple-800 border-purple-300';
      case PipelineStatus.FOLLOW_UP:
        return 'bg-indigo-100 text-indigo-800 border-indigo-300';
      case PipelineStatus.SIGNED_UP:
        return 'bg-green-100 text-green-800 border-green-300';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const getInteractionIcon = (type: InteractionType) => {
    switch (type) {
      case InteractionType.CALL:
        return <Phone size={16} />;
      case InteractionType.EMAIL:
        return <Mail size={16} />;
      case InteractionType.MEETING:
        return <Calendar size={16} />;
      default:
        return <MessageSquare size={16} />;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!customer) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">Customer not found</p>
        <Link to="/customers" className="text-primary-600 hover:text-primary-700">
          Return to customers
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <button
            onClick={() => navigate('/customers')}
            className="p-2 text-gray-400 hover:text-gray-600 rounded-md"
          >
            <ArrowLeft size={20} />
          </button>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{customer.name}</h1>
            <p className="text-gray-600">Customer Details</p>
          </div>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={() => setEditMode(!editMode)}
            className="flex items-center space-x-2 px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors"
          >
            <Edit size={16} />
            <span>{editMode ? 'Cancel Edit' : 'Edit'}</span>
          </button>
          {customer.status !== PipelineStatus.SIGNED_UP && (
            <button
              onClick={handleMoveToNextStage}
              className="flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 transition-colors"
            >
              <ArrowRight size={16} />
              <span>Next Stage</span>
            </button>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Customer Profile */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Profile</h2>
            
            {editMode ? (
              <CustomerEditForm
                customer={customer}
                onSave={(updatedCustomer) => {
                  setCustomer(updatedCustomer);
                  setEditMode(false);
                }}
                onCancel={() => setEditMode(false)}
              />
            ) : (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-500">Status</span>
                  <span className={`px-3 py-1 rounded-full text-sm font-medium border ${getStatusColor(customer.status)}`}>
                    {customer.status}
                  </span>
                </div>

                {customer.email && (
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-500">Email</span>
                    <a href={`mailto:${customer.email}`} className="text-primary-600 hover:text-primary-700">
                      {customer.email}
                    </a>
                  </div>
                )}

                {customer.phone && (
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-500">Phone</span>
                    <a href={`tel:${customer.phone}`} className="text-primary-600 hover:text-primary-700">
                      {customer.phone}
                    </a>
                  </div>
                )}

                <div className="flex items-start justify-between">
                  <span className="text-sm font-medium text-gray-500">Created</span>
                  <span className="text-sm text-gray-900">
                    {format(new Date(customer.created_at), 'PPP')}
                  </span>
                </div>

                <div className="flex items-start justify-between">
                  <span className="text-sm font-medium text-gray-500">Last Updated</span>
                  <span className="text-sm text-gray-900">
                    {format(new Date(customer.updated_at), 'PPp')}
                  </span>
                </div>
              </div>
            )}
          </div>

          {/* Prospect's WHY (Qualification) */}
          {customer.prospect_why && (
            <div className="bg-white rounded-lg shadow p-6 mt-6">
              <div className="flex items-center space-x-2 mb-4">
                <CheckCircle size={20} className="text-green-600" />
                <h2 className="text-xl font-semibold text-gray-900">Prospect's WHY</h2>
              </div>
              <div className="p-4 bg-green-50 rounded-lg border border-green-200">
                <p className="text-sm text-gray-700 whitespace-pre-wrap">{customer.prospect_why}</p>
              </div>
              <p className="mt-2 text-xs text-gray-500">
                Qualified using the Frazer Method
              </p>
            </div>
          )}

          {/* Notes */}
          <div className="bg-white rounded-lg shadow p-6 mt-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Notes</h2>
            {customer.notes ? (
              <div className="prose prose-sm max-w-none">
                <p className="text-gray-700 whitespace-pre-wrap">{customer.notes}</p>
              </div>
            ) : (
              <p className="text-gray-500 italic">No notes added yet</p>
            )}
          </div>

          {/* Interactions History */}
          <div className="bg-white rounded-lg shadow p-6 mt-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-gray-900">Interactions</h2>
              <button
                onClick={() => setShowAddInteraction(true)}
                className="flex items-center space-x-2 px-3 py-2 text-sm bg-primary-600 text-white rounded-md hover:bg-primary-700 transition-colors"
              >
                <Plus size={16} />
                <span>Add Interaction</span>
              </button>
            </div>

            {interactions.length === 0 ? (
              <p className="text-gray-500 italic">No interactions recorded yet</p>
            ) : (
              <div className="space-y-4">
                {interactions.map((interaction) => (
                  <div key={interaction.id} className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg">
                    <div className="flex-shrink-0 p-2 bg-white rounded-md shadow-sm">
                      {getInteractionIcon(interaction.type)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-2">
                        <span className="text-sm font-medium text-gray-900 capitalize">
                          {interaction.type}
                        </span>
                        <span className="text-xs text-gray-500">
                          {format(new Date(interaction.created_at), 'PPp')}
                        </span>
                      </div>
                      <p className="text-sm text-gray-700 mt-1">{interaction.content}</p>
                      {interaction.scheduled_for && (
                        <p className="text-xs text-gray-500 mt-1">
                          Scheduled for: {format(new Date(interaction.scheduled_for), 'PPp')}
                        </p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Next Steps Sidebar */}
        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Next Steps</h2>
            {customer.next_action ? (
              <div className="space-y-3">
                <div className="p-3 bg-blue-50 rounded-lg border border-blue-200">
                  <p className="text-sm font-medium text-blue-900">{customer.next_action}</p>
                  {customer.next_action_date && (
                    <p className="text-xs text-blue-700 mt-1">
                      Due: {format(new Date(customer.next_action_date), 'PPp')}
                    </p>
                  )}
                </div>
              </div>
            ) : (
              <p className="text-gray-500 italic">No next action defined</p>
            )}
          </div>

          {/* Quick Actions */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h2>
            <div className="space-y-2">
              {customer.email && (
                <a
                  href={`mailto:${customer.email}`}
                  className="flex items-center space-x-2 w-full px-3 py-2 text-sm text-gray-700 bg-gray-50 rounded-md hover:bg-gray-100 transition-colors"
                >
                  <Mail size={16} />
                  <span>Send Email</span>
                </a>
              )}
              {customer.phone && (
                <a
                  href={`tel:${customer.phone}`}
                  className="flex items-center space-x-2 w-full px-3 py-2 text-sm text-gray-700 bg-gray-50 rounded-md hover:bg-gray-100 transition-colors"
                >
                  <Phone size={16} />
                  <span>Call</span>
                </a>
              )}
              <button
                onClick={() => setShowAddInteraction(true)}
                className="flex items-center space-x-2 w-full px-3 py-2 text-sm text-gray-700 bg-gray-50 rounded-md hover:bg-gray-100 transition-colors"
              >
                <MessageSquare size={16} />
                <span>Add Note</span>
              </button>
              {customer.status === PipelineStatus.INVITED && !customer.prospect_why && (
                <button
                  onClick={() => setShowQualification(true)}
                  className="flex items-center space-x-2 w-full px-3 py-2 text-sm text-white bg-blue-600 rounded-md hover:bg-blue-700 transition-colors"
                >
                  <CheckCircle size={16} />
                  <span>Qualify Prospect</span>
                </button>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Add Interaction Modal */}
      {showAddInteraction && (
        <AddInteractionModal
          customerId={customer.id}
          onClose={() => setShowAddInteraction(false)}
          onSuccess={() => {
            setShowAddInteraction(false);
            fetchCustomerData(customer.id);
          }}
        />
      )}

      {/* Qualification Questionnaire Modal */}
      {showQualification && (
        <QualificationQuestionnaire
          customer={customer}
          onComplete={(updatedCustomer) => {
            setCustomer(updatedCustomer);
            setShowQualification(false);
          }}
          onCancel={() => setShowQualification(false)}
        />
      )}
    </div>
  );
};

// Customer Edit Form Component
interface CustomerEditFormProps {
  customer: Customer;
  onSave: (customer: Customer) => void;
  onCancel: () => void;
}

const CustomerEditForm: React.FC<CustomerEditFormProps> = ({ customer, onSave, onCancel }) => {
  const [formData, setFormData] = useState({
    name: customer.name,
    email: customer.email || '',
    phone: customer.phone || '',
    status: customer.status,
    notes: customer.notes || '',
    next_action: customer.next_action || '',
    next_action_date: customer.next_action_date
      ? new Date(customer.next_action_date).toISOString().slice(0, 16)
      : ''
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      setLoading(true);
      const updatedCustomer = await customerApi.update(customer.id, {
        ...formData,
        next_action_date: formData.next_action_date ? new Date(formData.next_action_date) : undefined
      });
      onSave(updatedCustomer);
    } catch (error) {
      console.error('Error updating customer:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
        <input
          type="text"
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
        <input
          type="email"
          value={formData.email}
          onChange={(e) => setFormData({ ...formData, email: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Phone</label>
        <input
          type="tel"
          value={formData.phone}
          onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
        <select
          value={formData.status}
          onChange={(e) => setFormData({ ...formData, status: e.target.value as PipelineStatus })}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
        >
          {Object.values(PipelineStatus).map((status) => (
            <option key={status} value={status}>
              {status}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Next Action</label>
        <input
          type="text"
          value={formData.next_action}
          onChange={(e) => setFormData({ ...formData, next_action: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Next Action Date</label>
        <input
          type="datetime-local"
          value={formData.next_action_date}
          onChange={(e) => setFormData({ ...formData, next_action_date: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Notes</label>
        <textarea
          value={formData.notes}
          onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
          rows={4}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
        />
      </div>

      <div className="flex justify-end space-x-3 pt-4">
        <button
          type="button"
          onClick={onCancel}
          className="px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors"
        >
          Cancel
        </button>
        <button
          type="submit"
          disabled={loading}
          className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 transition-colors disabled:opacity-50"
        >
          {loading ? 'Saving...' : 'Save Changes'}
        </button>
      </div>
    </form>
  );
};

// Add Interaction Modal Component
interface AddInteractionModalProps {
  customerId: string;
  onClose: () => void;
  onSuccess: () => void;
}

const AddInteractionModal: React.FC<AddInteractionModalProps> = ({ customerId, onClose, onSuccess }) => {
  const [formData, setFormData] = useState({
    type: InteractionType.NOTE,
    content: '',
    scheduled_for: ''
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.content) return;

    try {
      setLoading(true);
      await interactionApi.create({
        customer_id: customerId,
        type: formData.type,
        content: formData.content,
        scheduled_for: formData.scheduled_for ? new Date(formData.scheduled_for) : undefined,
        completed: false
      });
      onSuccess();
    } catch (error) {
      console.error('Error creating interaction:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Add Interaction</h2>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
            <select
              value={formData.type}
              onChange={(e) => setFormData({ ...formData, type: e.target.value as InteractionType })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              {Object.values(InteractionType).map((type) => (
                <option key={type} value={type}>
                  {type.charAt(0).toUpperCase() + type.slice(1)}
                </option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Content</label>
            <textarea
              value={formData.content}
              onChange={(e) => setFormData({ ...formData, content: e.target.value })}
              rows={4}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Scheduled For (Optional)</label>
            <input
              type="datetime-local"
              value={formData.scheduled_for}
              onChange={(e) => setFormData({ ...formData, scheduled_for: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
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
              disabled={loading || !formData.content}
              className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 transition-colors disabled:opacity-50"
            >
              {loading ? 'Adding...' : 'Add Interaction'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CustomerDetail;
