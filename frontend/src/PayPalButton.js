import React, { useEffect, useRef } from 'react';

const PayPalButton = ({ 
  amount, 
  currency = 'USD', 
  description = 'Oil & Gas Finder Payment',
  onSuccess,
  onError,
  onCancel,
  style = {}
}) => {
  const paypalRef = useRef();

  useEffect(() => {
    // Load PayPal SDK script
    const script = document.createElement('script');
    script.src = 'https://www.paypal.com/sdk/js?client-id=AeA1QIZXiflr8-L3Ca2qgFwzd-TFbJSGm7Jl-EMshlq3c8EABL1WoNGBx74xJJSIgqiOpCJPpv8Vp0sI&currency=USD';
    script.async = true;
    
    script.onload = () => {
      if (window.paypal) {
        window.paypal.Buttons({
          style: {
            color: 'blue',
            shape: 'rect',
            label: 'paypal',
            layout: 'vertical',
            ...style
          },
          createOrder: (data, actions) => {
            return actions.order.create({
              purchase_units: [{
                amount: {
                  value: amount.toString(),
                  currency_code: currency
                },
                description: description
              }]
            });
          },
          onApprove: async (data, actions) => {
            try {
              const order = await actions.order.capture();
              if (onSuccess) {
                onSuccess(order);
              }
            } catch (error) {
              console.error('PayPal capture error:', error);
              if (onError) {
                onError(error);
              }
            }
          },
          onError: (err) => {
            console.error('PayPal error:', err);
            if (onError) {
              onError(err);
            }
          },
          onCancel: (data) => {
            console.log('PayPal cancelled:', data);
            if (onCancel) {
              onCancel(data);
            }
          }
        }).render(paypalRef.current);
      }
    };

    document.head.appendChild(script);

    return () => {
      // Cleanup
      if (document.head.contains(script)) {
        document.head.removeChild(script);
      }
    };
  }, [amount, currency, description, onSuccess, onError, onCancel, style]);

  return (
    <div className="paypal-button-container">
      <div ref={paypalRef} className="paypal-button"></div>
    </div>
  );
};

export default PayPalButton;