import React from 'react';

// SEO Component for dynamic meta tags
export const SEO = ({ 
  title = "Oil & Gas Finder - Global Trading Platform",
  description = "Premier global oil & gas trading platform connecting buyers and sellers worldwide.",
  keywords = "oil trading, gas trading, crude oil, natural gas, LNG",
  image = "/og-image.jpg",
  url = "",
  type = "website",
  productType = null,
  location = null,
  price = null
}) => {
  const siteTitle = "Oil & Gas Finder";
  const fullTitle = title.includes(siteTitle) ? title : `${title} | ${siteTitle}`;
  const canonicalUrl = `${window.location.origin}${url}`;
  
  // Generate location-specific content
  const locationKeywords = location ? `, ${location} oil trading, ${location} gas market` : '';
  const productKeywords = productType ? `, ${productType} trading, ${productType} market` : '';
  
  const enhancedKeywords = `${keywords}${locationKeywords}${productKeywords}`;
  const enhancedDescription = location && productType 
    ? `${productType} trading in ${location}. ${description}`
    : description;

  React.useEffect(() => {
    // Update document title
    document.title = fullTitle;
    
    // Update meta tags
    updateMetaTag('description', enhancedDescription);
    updateMetaTag('keywords', enhancedKeywords);
    updateMetaTag('og:title', fullTitle);
    updateMetaTag('og:description', enhancedDescription);
    updateMetaTag('og:image', `${window.location.origin}${image}`);
    updateMetaTag('og:url', canonicalUrl);
    updateMetaTag('og:type', type);
    updateMetaTag('twitter:title', fullTitle);
    updateMetaTag('twitter:description', enhancedDescription);
    updateMetaTag('twitter:image', `${window.location.origin}${image}`);
    
    // Add canonical link
    updateCanonical(canonicalUrl);
    
    // Add structured data if product page
    if (productType && location) {
      addProductStructuredData({
        name: `${productType} in ${location}`,
        description: enhancedDescription,
        location,
        price,
        productType
      });
    }
  }, [fullTitle, enhancedDescription, enhancedKeywords, canonicalUrl, image, productType, location, price]);

  return null; // This component doesn't render anything
};

// Helper function to update meta tags
const updateMetaTag = (property, content) => {
  if (!content) return;
  
  let selector = `meta[name="${property}"]`;
  if (property.startsWith('og:') || property.startsWith('twitter:')) {
    selector = `meta[property="${property}"]`;
  }
  
  let metaTag = document.querySelector(selector);
  if (!metaTag) {
    metaTag = document.createElement('meta');
    if (property.startsWith('og:') || property.startsWith('twitter:')) {
      metaTag.setAttribute('property', property);
    } else {
      metaTag.setAttribute('name', property);
    }
    document.head.appendChild(metaTag);
  }
  metaTag.setAttribute('content', content);
};

// Helper function to update canonical URL
const updateCanonical = (url) => {
  let canonical = document.querySelector('link[rel="canonical"]');
  if (!canonical) {
    canonical = document.createElement('link');
    canonical.setAttribute('rel', 'canonical');
    document.head.appendChild(canonical);
  }
  canonical.setAttribute('href', url);
};

// Add structured data for products
const addProductStructuredData = ({ name, description, location, price, productType }) => {
  const existingScript = document.querySelector('#product-structured-data');
  if (existingScript) {
    existingScript.remove();
  }

  const structuredData = {
    "@context": "https://schema.org",
    "@type": "Product",
    "name": name,
    "description": description,
    "category": "Energy/Oil & Gas",
    "brand": {
      "@type": "Brand",
      "name": "Oil & Gas Finder"
    }
  };

  if (price) {
    structuredData.offers = {
      "@type": "Offer",
      "priceCurrency": "USD",
      "price": price,
      "availability": "https://schema.org/InStock",
      "seller": {
        "@type": "Organization",
        "name": "Oil & Gas Finder"
      }
    };
  }

  if (location) {
    structuredData.locationCreated = {
      "@type": "Place",
      "name": location
    };
  }

  const script = document.createElement('script');
  script.id = 'product-structured-data';
  script.type = 'application/ld+json';
  script.textContent = JSON.stringify(structuredData);
  document.head.appendChild(script);
};

// Local Business Schema Component
export const LocalBusinessSchema = ({ location, address, phone, services = [] }) => {
  React.useEffect(() => {
    const existingScript = document.querySelector('#local-business-schema');
    if (existingScript) {
      existingScript.remove();
    }

    const structuredData = {
      "@context": "https://schema.org",
      "@type": "LocalBusiness",
      "name": `Oil & Gas Finder - ${location}`,
      "description": `Oil and gas trading services in ${location}`,
      "address": {
        "@type": "PostalAddress",
        "addressLocality": location,
        "addressCountry": address?.country || "US"
      },
      "telephone": phone,
      "url": `${window.location.origin}/locations/${location.toLowerCase().replace(/\s+/g, '-')}`,
      "serviceArea": {
        "@type": "GeoCircle",
        "geoMidpoint": {
          "@type": "GeoCoordinates",
          "latitude": address?.lat,
          "longitude": address?.lng
        },
        "geoRadius": "100000"
      },
      "hasOfferCatalog": {
        "@type": "OfferCatalog",
        "name": "Oil & Gas Trading Services",
        "itemListElement": services.map(service => ({
          "@type": "Offer",
          "itemOffered": {
            "@type": "Service",
            "name": service
          }
        }))
      }
    };

    const script = document.createElement('script');
    script.id = 'local-business-schema';
    script.type = 'application/ld+json';
    script.textContent = JSON.stringify(structuredData);
    document.head.appendChild(script);
  }, [location, address, phone, services]);

  return null;
};

// Breadcrumb Schema Component
export const BreadcrumbSchema = ({ items }) => {
  React.useEffect(() => {
    const existingScript = document.querySelector('#breadcrumb-schema');
    if (existingScript) {
      existingScript.remove();
    }

    const structuredData = {
      "@context": "https://schema.org",
      "@type": "BreadcrumbList",
      "itemListElement": items.map((item, index) => ({
        "@type": "ListItem",
        "position": index + 1,
        "name": item.name,
        "item": `${window.location.origin}${item.url}`
      }))
    };

    const script = document.createElement('script');
    script.id = 'breadcrumb-schema';
    script.type = 'application/ld+json';
    script.textContent = JSON.stringify(structuredData);
    document.head.appendChild(script);
  }, [items]);

  return null;
};

export default SEO;