import React, { useState, useEffect } from 'react';
import { SEO, BreadcrumbSchema } from './SEO';

// Blog System for Content Marketing and SEO
export const BlogSystem = () => {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchBlogPosts();
  }, []);

  const fetchBlogPosts = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/blog/posts`);
      const data = await response.json();
      setPosts(data);
    } catch (error) {
      console.error('Error fetching blog posts:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="flex justify-center items-center h-64">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
    </div>;
  }

  return (
    <div className="bg-white">
      <SEO 
        title="Oil & Gas Market Insights | Industry News & Analysis"
        description="Stay updated with the latest oil and gas market trends, trading insights, and industry analysis from global energy experts."
        keywords="oil market news, gas trading insights, energy market analysis, petroleum industry trends"
        url="/blog"
      />
      
      <BreadcrumbSchema items={[
        { name: "Home", url: "/" },
        { name: "Blog", url: "/blog" }
      ]} />

      {/* Hero Section */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-800 text-white py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-4xl font-bold mb-4">Oil & Gas Market Insights</h1>
            <p className="text-xl text-blue-100 max-w-3xl mx-auto">
              Expert analysis, market trends, and trading insights to keep you ahead in the global energy market.
            </p>
          </div>
        </div>
      </div>

      {/* Featured Post */}
      {posts.length > 0 && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="bg-gradient-to-r from-gray-50 to-blue-50 rounded-lg p-8 mb-12">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
              <div>
                <span className="inline-block bg-blue-600 text-white px-3 py-1 rounded-full text-sm font-semibold mb-4">
                  Featured
                </span>
                <h2 className="text-3xl font-bold text-gray-900 mb-4">
                  {posts[0].title}
                </h2>
                <p className="text-gray-600 text-lg mb-6">
                  {posts[0].excerpt}
                </p>
                <div className="flex items-center text-gray-500 text-sm mb-6">
                  <span>{new Date(posts[0].created_at).toLocaleDateString()}</span>
                  <span className="mx-2">•</span>
                  <span>{posts[0].read_time} min read</span>
                  <span className="mx-2">•</span>
                  <span className="text-blue-600">{posts[0].category}</span>
                </div>
                <button 
                  onClick={() => window.location.href = `/blog/${posts[0].slug}`}
                  className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Read Full Article
                </button>
              </div>
              <div className="lg:order-first">
                <img 
                  src={posts[0].featured_image || '/images/blog/default-featured.jpg'} 
                  alt={posts[0].title}
                  className="w-full h-64 object-cover rounded-lg shadow-lg"
                />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Blog Grid */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-12">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {posts.slice(1).map((post) => (
            <BlogCard key={post.id} post={post} />
          ))}
        </div>
      </div>

      {/* Newsletter Signup */}
      <NewsletterSignup />
    </div>
  );
};

// Individual Blog Card Component
const BlogCard = ({ post }) => {
  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow">
      <img 
        src={post.featured_image || '/images/blog/default-thumb.jpg'} 
        alt={post.title}
        className="w-full h-48 object-cover"
      />
      <div className="p-6">
        <div className="flex items-center text-sm text-gray-500 mb-3">
          <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs font-semibold">
            {post.category}
          </span>
          <span className="ml-auto">{new Date(post.created_at).toLocaleDateString()}</span>
        </div>
        <h3 className="text-xl font-semibold text-gray-900 mb-3 line-clamp-2">
          {post.title}
        </h3>
        <p className="text-gray-600 mb-4 line-clamp-3">
          {post.excerpt}
        </p>
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-500">{post.read_time} min read</span>
          <button 
            onClick={() => window.location.href = `/blog/${post.slug}`}
            className="text-blue-600 hover:text-blue-800 font-semibold text-sm"
          >
            Read More →
          </button>
        </div>
      </div>
    </div>
  );
};

// Newsletter Signup Component for Lead Generation
const NewsletterSignup = () => {
  const [email, setEmail] = useState('');
  const [subscribed, setSubscribed] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/newsletter/subscribe`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, source: 'blog_newsletter' })
      });
      setSubscribed(true);
      setEmail('');
      
      // Track conversion
      if (window.gtag) {
        window.gtag('event', 'newsletter_signup', {
          event_category: 'engagement',
          event_label: 'blog_newsletter'
        });
      }
    } catch (error) {
      console.error('Newsletter signup error:', error);
    } finally {
      setLoading(false);
    }
  };

  if (subscribed) {
    return (
      <div className="bg-green-50 border-l-4 border-green-400 p-4 mx-4 mb-8">
        <div className="flex">
          <div className="ml-3">
            <p className="text-sm text-green-700">
              ✅ Successfully subscribed! You'll receive weekly market insights and trading opportunities.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gradient-to-r from-blue-600 to-blue-800 py-12">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <h3 className="text-2xl font-bold text-white mb-4">
          Get Weekly Market Insights
        </h3>
        <p className="text-blue-100 mb-8 max-w-2xl mx-auto">
          Join 10,000+ energy professionals receiving exclusive market analysis, trading opportunities, and industry insights.
        </p>
        <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-4 max-w-md mx-auto">
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="Enter your email address"
            required
            className="flex-1 px-4 py-3 rounded-lg border-0 focus:ring-2 focus:ring-blue-300"
          />
          <button
            type="submit"
            disabled={loading}
            className="bg-white text-blue-600 px-6 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors disabled:opacity-50"
          >
            {loading ? 'Subscribing...' : 'Subscribe'}
          </button>
        </form>
        <p className="text-blue-200 text-sm mt-4">
          No spam, unsubscribe anytime. Your data is protected.
        </p>
      </div>
    </div>
  );
};

// Individual Blog Post Component
export const BlogPost = ({ slug }) => {
  const [post, setPost] = useState(null);
  const [loading, setLoading] = useState(true);
  const [relatedPosts, setRelatedPosts] = useState([]);

  useEffect(() => {
    fetchBlogPost();
  }, [slug]);

  const fetchBlogPost = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/blog/posts/${slug}`);
      const data = await response.json();
      setPost(data.post);
      setRelatedPosts(data.related_posts || []);
    } catch (error) {
      console.error('Error fetching blog post:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="flex justify-center items-center h-64">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
    </div>;
  }

  if (!post) {
    return <div className="text-center py-12">
      <h2 className="text-2xl font-bold text-gray-900">Post not found</h2>
    </div>;
  }

  return (
    <div className="bg-white">
      <SEO 
        title={`${post.title} | Oil & Gas Finder Blog`}
        description={post.excerpt}
        keywords={post.keywords}
        url={`/blog/${post.slug}`}
        type="article"
      />
      
      <BreadcrumbSchema items={[
        { name: "Home", url: "/" },
        { name: "Blog", url: "/blog" },
        { name: post.title, url: `/blog/${post.slug}` }
      ]} />

      {/* Article Header */}
      <div className="bg-gray-50 py-12">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <span className="inline-block bg-blue-600 text-white px-3 py-1 rounded-full text-sm font-semibold mb-4">
              {post.category}
            </span>
            <h1 className="text-4xl font-bold text-gray-900 mb-4">{post.title}</h1>
            <div className="flex items-center justify-center text-gray-500 text-sm">
              <span>{new Date(post.created_at).toLocaleDateString()}</span>
              <span className="mx-2">•</span>
              <span>{post.read_time} min read</span>
              <span className="mx-2">•</span>
              <span>By {post.author}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Article Content */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {post.featured_image && (
          <img 
            src={post.featured_image} 
            alt={post.title}
            className="w-full h-64 object-cover rounded-lg shadow-lg mb-8"
          />
        )}
        
        <div 
          className="prose prose-lg max-w-none"
          dangerouslySetInnerHTML={{ __html: post.content }}
        />

        {/* Call to Action */}
        <div className="bg-blue-50 rounded-lg p-8 mt-12 text-center">
          <h3 className="text-2xl font-bold text-gray-900 mb-4">
            Ready to Start Trading?
          </h3>
          <p className="text-gray-600 mb-6">
            Join thousands of energy professionals on our global trading platform.
          </p>
          <button 
            onClick={() => window.location.href = '/register'}
            className="bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
          >
            Start Trading Today
          </button>
        </div>
      </div>

      {/* Related Posts */}
      {relatedPosts.length > 0 && (
        <div className="bg-gray-50 py-12">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <h3 className="text-2xl font-bold text-gray-900 mb-8 text-center">
              Related Articles
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {relatedPosts.map((relatedPost) => (
                <BlogCard key={relatedPost.id} post={relatedPost} />
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export { BlogSystem, BlogPost };