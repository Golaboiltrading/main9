import React, { useState, useCallback, useMemo } from 'react';

// Enhanced input validation utilities
const validateTradeData = (tradeData) => {
  const errors = {};
  
  // Commodity validation with sanitization
  if (!tradeData.commodity || !tradeData.commodity.trim()) {
    errors.commodity = 'Commodity is required';
  } else {
    const sanitizedCommodity = tradeData.commodity.replace(/[^a-zA-Z0-9\s]/g, '');
    if (sanitizedCommodity !== tradeData.commodity) {
      errors.commodity = 'Invalid characters in commodity name';
    }
  }
  
  // Quantity validation
  if (!tradeData.quantity || isNaN(tradeData.quantity) || parseFloat(tradeData.quantity) <= 0) {
    errors.quantity = 'Quantity must be a positive number';
  }
  
  // Price validation
  if (!tradeData.price || isNaN(tradeData.price) || parseFloat(tradeData.price) <= 0) {
    errors.price = 'Price must be a positive number';
  }
  
  // Email validation
  if (tradeData.contactEmail) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(tradeData.contactEmail)) {
      errors.contactEmail = 'Invalid email format';
    }
  }
  
  // XSS prevention - check for script tags
  const xssPatterns = [
    /<script[^>]*>.*?<\/script>/gi,
    /javascript:/gi,
    /on\w+\s*=/gi,
    /<iframe/gi,
    /<object/gi,
    /<embed/gi
  ];
  
  Object.keys(tradeData).forEach(key => {
    if (typeof tradeData[key] === 'string') {
      xssPatterns.forEach(pattern => {
        if (pattern.test(tradeData[key])) {
          errors[key] = 'Invalid content detected';
        }
      });
    }
  });
  
  return errors;
};

// MongoDB injection prevention for client-side
const sanitizeMongoInput = (input) => {
  if (typeof input !== 'string') return input;
  
  // Remove MongoDB operators
  const mongoOperators = ['$where', '$ne', '$gt', '$gte', '$lt', '$lte', '$in', '$nin', '$or', '$and', '$not', '$nor'];
  let sanitized = input;
  
  mongoOperators.forEach(op => {
    const regex = new RegExp(`\\${op}`, 'gi');
    sanitized = sanitized.replace(regex, '');
  });
  
  // Remove dangerous characters
  sanitized = sanitized.replace(/[{}$\\]/g, '');
  
  return sanitized;
};

// Enhanced Trade Form Component with comprehensive validation
const SecureTradeForm = React.memo(({ onSubmit, onCancel }) => {
  const [formData, setFormData] = useState({
    commodity: '',
    quantity: '',
    price: '',
    location: '',
    description: '',
    contactEmail: '',
    contactPerson: '',
    contactPhone: ''
  });
  
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  // Memoized validation to prevent unnecessary re-renders
  const validationErrors = useMemo(() => {
    return validateTradeData(formData);
  }, [formData]);
  
  const isFormValid = useMemo(() => {
    return Object.keys(validationErrors).length === 0 && 
           formData.commodity && formData.quantity && formData.price;
  }, [validationErrors, formData.commodity, formData.quantity, formData.price]);
  
  // Secure input handler with sanitization
  const handleInputChange = useCallback((field) => (event) => {
    const rawValue = event.target.value;
    
    // Apply sanitization based on field type
    let sanitizedValue = rawValue;
    
    if (field === 'commodity' || field === 'location') {
      // Remove potentially dangerous characters for text fields
      sanitizedValue = rawValue.replace(/[<>"'&{}$\\]/g, '');
    } else if (field === 'quantity' || field === 'price') {
      // Only allow numbers and decimal points
      sanitizedValue = rawValue.replace(/[^0-9.]/g, '');
    } else if (field === 'description') {
      // HTML escape for description
      sanitizedValue = rawValue
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#x27;');
    }
    
    // Apply MongoDB sanitization
    sanitizedValue = sanitizeMongoInput(sanitizedValue);
    
    setFormData(prev => ({
      ...prev,
      [field]: sanitizedValue
    }));
    
    // Clear field-specific error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: undefined
      }));
    }
  }, [errors]);
  
  const handleSubmit = useCallback(async (event) => {
    event.preventDefault();
    
    const currentErrors = validateTradeData(formData);
    if (Object.keys(currentErrors).length > 0) {
      setErrors(currentErrors);
      return;
    }
    
    setIsSubmitting(true);
    
    try {
      // Additional client-side security checks before submission
      const secureData = {
        ...formData,
        // Double-sanitize critical fields
        commodity: sanitizeMongoInput(formData.commodity),
        description: sanitizeMongoInput(formData.description),
        location: sanitizeMongoInput(formData.location)
      };
      
      await onSubmit(secureData);
    } catch (error) {
      setErrors({ submit: 'Failed to submit trade. Please try again.' });
    } finally {
      setIsSubmitting(false);
    }
  }, [formData, onSubmit]);
  
  return (
    <div className="max-w-2xl mx-auto bg-white rounded-lg shadow-md p-6">
      <h2 className="text-2xl font-bold mb-6 text-gray-900">Create Secure Trade Listing</h2>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Commodity Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Commodity *
          </label>
          <select
            value={formData.commodity}
            onChange={handleInputChange('commodity')}
            className={`w-full p-3 border rounded-md ${
              validationErrors.commodity ? 'border-red-500' : 'border-gray-300'
            } focus:ring-2 focus:ring-blue-500 focus:border-transparent`}
            required
          >
            <option value="">Select Commodity</option>
            <option value="crude_oil">Crude Oil</option>
            <option value="natural_gas">Natural Gas</option>
            <option value="lng">LNG</option>
            <option value="gasoline">Gasoline</option>
            <option value="diesel">Diesel</option>
            <option value="jet_fuel">Jet Fuel</option>
          </select>
          {validationErrors.commodity && (
            <p className="mt-1 text-sm text-red-600">{validationErrors.commodity}</p>
          )}
        </div>
        
        {/* Quantity */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Quantity (barrels/units) *
          </label>
          <input
            type="text"
            value={formData.quantity}
            onChange={handleInputChange('quantity')}
            placeholder="e.g., 10000"
            className={`w-full p-3 border rounded-md ${
              validationErrors.quantity ? 'border-red-500' : 'border-gray-300'
            } focus:ring-2 focus:ring-blue-500 focus:border-transparent`}
            required
          />
          {validationErrors.quantity && (
            <p className="mt-1 text-sm text-red-600">{validationErrors.quantity}</p>
          )}
        </div>
        
        {/* Price */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Price per Unit ($) *
          </label>
          <input
            type="text"
            value={formData.price}
            onChange={handleInputChange('price')}
            placeholder="e.g., 75.50"
            className={`w-full p-3 border rounded-md ${
              validationErrors.price ? 'border-red-500' : 'border-gray-300'
            } focus:ring-2 focus:ring-blue-500 focus:border-transparent`}
            required
          />
          {validationErrors.price && (
            <p className="mt-1 text-sm text-red-600">{validationErrors.price}</p>
          )}
        </div>
        
        {/* Location */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Location
          </label>
          <input
            type="text"
            value={formData.location}
            onChange={handleInputChange('location')}
            placeholder="e.g., Houston, TX"
            className={`w-full p-3 border rounded-md ${
              validationErrors.location ? 'border-red-500' : 'border-gray-300'
            } focus:ring-2 focus:ring-blue-500 focus:border-transparent`}
          />
          {validationErrors.location && (
            <p className="mt-1 text-sm text-red-600">{validationErrors.location}</p>
          )}
        </div>
        
        {/* Description */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Description
          </label>
          <textarea
            value={formData.description}
            onChange={handleInputChange('description')}
            placeholder="Additional details about the trade..."
            rows={4}
            className={`w-full p-3 border rounded-md ${
              validationErrors.description ? 'border-red-500' : 'border-gray-300'
            } focus:ring-2 focus:ring-blue-500 focus:border-transparent`}
          />
          {validationErrors.description && (
            <p className="mt-1 text-sm text-red-600">{validationErrors.description}</p>
          )}
        </div>
        
        {/* Contact Information */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Contact Person
            </label>
            <input
              type="text"
              value={formData.contactPerson}
              onChange={handleInputChange('contactPerson')}
              placeholder="John Doe"
              className={`w-full p-3 border rounded-md ${
                validationErrors.contactPerson ? 'border-red-500' : 'border-gray-300'
              } focus:ring-2 focus:ring-blue-500 focus:border-transparent`}
            />
            {validationErrors.contactPerson && (
              <p className="mt-1 text-sm text-red-600">{validationErrors.contactPerson}</p>
            )}
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Contact Email
            </label>
            <input
              type="email"
              value={formData.contactEmail}
              onChange={handleInputChange('contactEmail')}
              placeholder="john@company.com"
              className={`w-full p-3 border rounded-md ${
                validationErrors.contactEmail ? 'border-red-500' : 'border-gray-300'
              } focus:ring-2 focus:ring-blue-500 focus:border-transparent`}
            />
            {validationErrors.contactEmail && (
              <p className="mt-1 text-sm text-red-600">{validationErrors.contactEmail}</p>
            )}
          </div>
        </div>
        
        {/* Contact Phone */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Contact Phone
          </label>
          <input
            type="tel"
            value={formData.contactPhone}
            onChange={handleInputChange('contactPhone')}
            placeholder="+1-555-123-4567"
            className={`w-full p-3 border rounded-md ${
              validationErrors.contactPhone ? 'border-red-500' : 'border-gray-300'
            } focus:ring-2 focus:ring-blue-500 focus:border-transparent`}
          />
          {validationErrors.contactPhone && (
            <p className="mt-1 text-sm text-red-600">{validationErrors.contactPhone}</p>
          )}
        </div>
        
        {/* Submit Error */}
        {errors.submit && (
          <div className="p-3 bg-red-50 border border-red-200 rounded-md">
            <p className="text-sm text-red-600">{errors.submit}</p>
          </div>
        )}
        
        {/* Form Actions */}
        <div className="flex justify-end space-x-4 pt-4">
          <button
            type="button"
            onClick={onCancel}
            className="px-6 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-500"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={!isFormValid || isSubmitting}
            className={`px-6 py-2 rounded-md text-white font-medium focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              isFormValid && !isSubmitting
                ? 'bg-blue-600 hover:bg-blue-700'
                : 'bg-gray-400 cursor-not-allowed'
            }`}
          >
            {isSubmitting ? 'Creating...' : 'Create Trade Listing'}
          </button>
        </div>
      </form>
      
      {/* Security Indicator */}
      <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-md">
        <p className="text-sm text-green-700">
          🔒 This form uses advanced security validation to protect against XSS and injection attacks.
        </p>
      </div>
    </div>
  );
});

// Security-enhanced API service
class SecureApiService {
  constructor(baseURL) {
    this.baseURL = baseURL || process.env.REACT_APP_BACKEND_URL;
  }
  
  // Secure request wrapper with CSRF protection
  async secureRequest(endpoint, options = {}) {
    const token = localStorage.getItem('authToken');
    
    const defaultHeaders = {
      'Content-Type': 'application/json',
      'X-Requested-With': 'XMLHttpRequest', // CSRF protection
      ...(token && { 'Authorization': `Bearer ${token}` })
    };
    
    const requestOptions = {
      ...options,
      headers: {
        ...defaultHeaders,
        ...options.headers
      }
    };
    
    // Sanitize request body if present
    if (requestOptions.body && typeof requestOptions.body === 'string') {
      try {
        const parsed = JSON.parse(requestOptions.body);
        const sanitized = this.sanitizeRequestData(parsed);
        requestOptions.body = JSON.stringify(sanitized);
      } catch (e) {
        console.warn('Could not sanitize request body:', e);
      }
    }
    
    const response = await fetch(`${this.baseURL}${endpoint}`, requestOptions);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return response.json();
  }
  
  sanitizeRequestData(data) {
    if (typeof data !== 'object' || data === null) return data;
    
    const sanitized = {};
    
    for (const [key, value] of Object.entries(data)) {
      if (typeof value === 'string') {
        sanitized[key] = sanitizeMongoInput(value);
      } else if (typeof value === 'object') {
        sanitized[key] = this.sanitizeRequestData(value);
      } else {
        sanitized[key] = value;
      }
    }
    
    return sanitized;
  }
  
  // Secure trade creation
  async createTrade(tradeData) {
    return this.secureRequest('/api/listings', {
      method: 'POST',
      body: JSON.stringify(tradeData)
    });
  }
  
  // Secure trade search with filters
  async searchTrades(filters = {}) {
    const sanitizedFilters = this.sanitizeRequestData(filters);
    const queryParams = new URLSearchParams(sanitizedFilters).toString();
    return this.secureRequest(`/api/listings?${queryParams}`);
  }
}

export {
  SecureTradeForm,
  SecureApiService,
  validateTradeData,
  sanitizeMongoInput
};