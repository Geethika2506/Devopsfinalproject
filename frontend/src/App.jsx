import { useState, useEffect } from 'react'
import './App.css'

const API_BASE = '/api'

// Category display names mapping
const CATEGORY_LABELS = {
  "men's clothing": "👔 Men's Clothing",
  "women's clothing": "👗 Women's Clothing",
  "jewelery": "💎 Jewelry",
  "electronics": "📱 Electronics"
}

function App() {
  const [products, setProducts] = useState([])
  const [categories, setCategories] = useState([])
  const [selectedCategory, setSelectedCategory] = useState(null)
  const [cart, setCart] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [activeTab, setActiveTab] = useState('products')
  const [health, setHealth] = useState(null)

  // Auth state
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(localStorage.getItem('token'))
  const [showAuthModal, setShowAuthModal] = useState(false)
  const [authMode, setAuthMode] = useState('login') // 'login' or 'register'
  const [authForm, setAuthForm] = useState({ email: '', password: '', name: '' })
  const [authError, setAuthError] = useState(null)
  const [authLoading, setAuthLoading] = useState(false)

  // Wishlist state
  const [wishlist, setWishlist] = useState([])
  
  // Reviews state
  const [selectedProduct, setSelectedProduct] = useState(null)
  const [showReviewModal, setShowReviewModal] = useState(false)
  const [productReviews, setProductReviews] = useState({ reviews: [], average_rating: 0, total_reviews: 0 })
  const [reviewForm, setReviewForm] = useState({ rating: 5, comment: '' })

  // User profile state
  const [userOrders, setUserOrders] = useState([])
  const [userReviews, setUserReviews] = useState([])

  // Get user ID from token or default
  const userId = user?.id || 1

  // Fetch products and categories on load
  useEffect(() => {
    fetchCategories()
    fetchProducts()
    checkHealth()
    // Try to get user info if we have a token
    if (token) {
      fetchCurrentUser()
      fetchWishlist()
    }
  }, [])

  // Fetch current user when token changes
  useEffect(() => {
    if (token) {
      fetchCurrentUser()
      fetchWishlist()
    } else {
      setUser(null)
      setWishlist([])
    }
  }, [token])

  const fetchCurrentUser = async () => {
    if (!token) return
    try {
      const res = await fetch(`${API_BASE}/auth/me`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (res.ok) {
        const userData = await res.json()
        setUser(userData)
      } else {
        // Token invalid, clear it
        localStorage.removeItem('token')
        setToken(null)
        setUser(null)
      }
    } catch (err) {
      console.error('Error fetching user:', err)
    }
  }

  const handleLogin = async (e) => {
    e.preventDefault()
    setAuthError(null)
    setAuthLoading(true)
    
    try {
      const res = await fetch(`${API_BASE}/auth/login/json`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: authForm.email,
          password: authForm.password
        })
      })
      
      const data = await res.json()
      
      if (!res.ok) {
        throw new Error(data.detail || 'Login failed')
      }
      
      localStorage.setItem('token', data.access_token)
      setToken(data.access_token)
      setShowAuthModal(false)
      setAuthForm({ email: '', password: '', name: '' })
    } catch (err) {
      setAuthError(err.message)
    } finally {
      setAuthLoading(false)
    }
  }

  const handleRegister = async (e) => {
    e.preventDefault()
    setAuthError(null)
    setAuthLoading(true)
    
    try {
      const res = await fetch(`${API_BASE}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: authForm.email,
          password: authForm.password,
          name: authForm.name || null
        })
      })
      
      const data = await res.json()
      
      if (!res.ok) {
        throw new Error(data.detail || 'Registration failed')
      }
      
      // Auto-login after registration
      setAuthMode('login')
      setAuthError(null)
      alert('Registration successful! Please log in.')
    } catch (err) {
      setAuthError(err.message)
    } finally {
      setAuthLoading(false)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('token')
    setToken(null)
    setUser(null)
    setWishlist([])
  }

  // Wishlist functions
  const fetchWishlist = async () => {
    if (!token) return
    try {
      const res = await fetch(`${API_BASE}/wishlist`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (res.ok) {
        const data = await res.json()
        setWishlist(data.items.map(item => item.product_id))
      }
    } catch (err) {
      console.error('Error fetching wishlist:', err)
    }
  }

  const toggleWishlist = async (productId) => {
    if (!token) {
      setShowAuthModal(true)
      return
    }
    
    const isInWishlist = wishlist.includes(productId)
    
    try {
      if (isInWishlist) {
        await fetch(`${API_BASE}/wishlist/${productId}`, {
          method: 'DELETE',
          headers: { 'Authorization': `Bearer ${token}` }
        })
        setWishlist(prev => prev.filter(id => id !== productId))
      } else {
        await fetch(`${API_BASE}/wishlist`, {
          method: 'POST',
          headers: { 
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ product_id: productId })
        })
        setWishlist(prev => [...prev, productId])
      }
    } catch (err) {
      console.error('Error updating wishlist:', err)
    }
  }

  // Review functions
  const openReviewModal = async (product) => {
    setSelectedProduct(product)
    setShowReviewModal(true)
    setReviewForm({ rating: 5, comment: '' })
    
    try {
      const res = await fetch(`${API_BASE}/reviews/product/${product.id}`)
      if (res.ok) {
        const data = await res.json()
        setProductReviews(data)
      }
    } catch (err) {
      console.error('Error fetching reviews:', err)
    }
  }

  const submitReview = async (e) => {
    e.preventDefault()
    if (!token) {
      setShowAuthModal(true)
      return
    }
    
    try {
      const res = await fetch(`${API_BASE}/reviews`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          product_id: selectedProduct.id,
          rating: reviewForm.rating,
          comment: reviewForm.comment
        })
      })
      
      if (res.ok) {
        // Refresh reviews
        const reviewsRes = await fetch(`${API_BASE}/reviews/product/${selectedProduct.id}`)
        if (reviewsRes.ok) {
          setProductReviews(await reviewsRes.json())
        }
        setReviewForm({ rating: 5, comment: '' })
        alert('Review submitted!')
      } else {
        const error = await res.json()
        alert(error.detail || 'Failed to submit review')
      }
    } catch (err) {
      console.error('Error submitting review:', err)
    }
  }

  // User profile functions
  const fetchUserOrders = async () => {
    if (!token) return
    try {
      const res = await fetch(`${API_BASE}/orders/`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (res.ok) {
        const data = await res.json()
        setUserOrders(data)
      }
    } catch (err) {
      console.error('Error fetching orders:', err)
    }
  }

  const fetchUserReviews = async () => {
    if (!token) return
    try {
      const res = await fetch(`${API_BASE}/reviews/user/me`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (res.ok) {
        const data = await res.json()
        setUserReviews(data)
      }
    } catch (err) {
      console.error('Error fetching user reviews:', err)
    }
  }

  // Fetch user data when profile tab is selected
  useEffect(() => {
    if (activeTab === 'profile' && token) {
      fetchUserOrders()
      fetchUserReviews()
    }
  }, [activeTab, token])

  // Refetch products when category changes
  useEffect(() => {
    fetchProducts(selectedCategory)
  }, [selectedCategory])

  const checkHealth = async () => {
    try {
      const res = await fetch(`${API_BASE}/health`)
      const data = await res.json()
      setHealth(data)
    } catch (err) {
      setHealth({ status: 'error', message: err.message })
    }
  }

  const fetchCategories = async () => {
    try {
      const res = await fetch(`${API_BASE}/products/categories`)
      if (!res.ok) throw new Error('Failed to fetch categories')
      const data = await res.json()
      setCategories(data)
    } catch (err) {
      console.error('Error fetching categories:', err)
    }
  }

  const fetchProducts = async (category = null) => {
    try {
      setLoading(true)
      const url = category 
        ? `${API_BASE}/products/?category=${encodeURIComponent(category)}`
        : `${API_BASE}/products/`
      const res = await fetch(url)
      if (!res.ok) throw new Error('Failed to fetch products')
      const data = await res.json()
      setProducts(data)
      setError(null)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const addToCart = (product) => {
    setCart(prev => {
      const existing = prev.find(item => item.id === product.id)
      if (existing) {
        return prev.map(item => 
          item.id === product.id 
            ? { ...item, quantity: item.quantity + 1 }
            : item
        )
      }
      return [...prev, { ...product, quantity: 1 }]
    })
  }

  const removeFromCart = (productId) => {
    setCart(prev => prev.filter(item => item.id !== productId))
  }

  const updateQuantity = (productId, delta) => {
    setCart(prev => prev.map(item => {
      if (item.id === productId) {
        const newQty = item.quantity + delta
        return newQty > 0 ? { ...item, quantity: newQty } : item
      }
      return item
    }).filter(item => item.quantity > 0))
  }

  const cartTotal = cart.reduce((sum, item) => sum + item.price * item.quantity, 0)

  const placeOrder = async () => {
    if (cart.length === 0) return alert('Cart is empty!')
    if (!token) {
      setShowAuthModal(true)
      return alert('Please login to place an order')
    }
    
    try {
      const orderData = {
        items: cart.map(item => ({
          product_id: item.id,
          quantity: item.quantity
        }))
      }
      
      const res = await fetch(`${API_BASE}/orders/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(orderData)
      })
      
      if (!res.ok) {
        const error = await res.json()
        throw new Error(error.detail || 'Failed to place order')
      }
      
      const order = await res.json()
      alert(`Order #${order.id} placed successfully! Total: $${order.total.toFixed(2)}`)
      setCart([])
    } catch (err) {
      alert('Error placing order: ' + err.message)
    }
  }

  return (
    <div className="app">
      <header className="header">
        <h1>🛍️ THE SHOP</h1>
        <div className="header-right">
          <div className="auth-section">
            {user ? (
              <div className="user-info">
                <span>👤 {user.name || user.email}</span>
                <button onClick={handleLogout} className="logout-btn">Logout</button>
              </div>
            ) : (
              <button onClick={() => setShowAuthModal(true)} className="login-btn">
                Login / Register
              </button>
            )}
          </div>
        </div>
      </header>

      {/* Auth Modal */}
      {showAuthModal && (
        <div className="modal-overlay" onClick={() => setShowAuthModal(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <button className="modal-close" onClick={() => setShowAuthModal(false)}>✕</button>
            <h2>{authMode === 'login' ? 'Login' : 'Register'}</h2>
            
            {authError && <div className="auth-error">{authError}</div>}
            
            <form onSubmit={authMode === 'login' ? handleLogin : handleRegister}>
              {authMode === 'register' && (
                <div className="form-group">
                  <label>Name (optional)</label>
                  <input
                    type="text"
                    value={authForm.name}
                    onChange={e => setAuthForm({...authForm, name: e.target.value})}
                    placeholder="Your name"
                  />
                </div>
              )}
              <div className="form-group">
                <label>Email</label>
                <input
                  type="email"
                  value={authForm.email}
                  onChange={e => setAuthForm({...authForm, email: e.target.value})}
                  placeholder="you@example.com"
                  required
                />
              </div>
              <div className="form-group">
                <label>Password</label>
                <input
                  type="password"
                  value={authForm.password}
                  onChange={e => setAuthForm({...authForm, password: e.target.value})}
                  placeholder="Min 6 characters"
                  minLength={6}
                  required
                />
              </div>
              <button type="submit" className="submit-btn" disabled={authLoading}>
                {authLoading ? 'Please wait...' : (authMode === 'login' ? 'Login' : 'Register')}
              </button>
            </form>
            
            <div className="auth-switch">
              {authMode === 'login' ? (
                <p>Don't have an account? <button onClick={() => {setAuthMode('register'); setAuthError(null)}}>Register</button></p>
              ) : (
                <p>Already have an account? <button onClick={() => {setAuthMode('login'); setAuthError(null)}}>Login</button></p>
              )}
            </div>
          </div>
        </div>
      )}

      <nav className="nav">
        <button 
          className={activeTab === 'products' ? 'active' : ''} 
          onClick={() => setActiveTab('products')}
        >
          Products ({products.length})
        </button>
        <button 
          className={activeTab === 'wishlist' ? 'active' : ''} 
          onClick={() => setActiveTab('wishlist')}
        >
          ❤️ Wishlist ({wishlist.length})
        </button>
        <button 
          className={activeTab === 'cart' ? 'active' : ''} 
          onClick={() => setActiveTab('cart')}
        >
          Cart ({cart.length})
        </button>
        {token && (
          <button 
            className={activeTab === 'profile' ? 'active' : ''} 
            onClick={() => {
              setActiveTab('profile')
              fetchUserOrders()
              fetchUserReviews()
            }}
          >
            👤 My Profile
          </button>
        )}
      </nav>

      <main className="main">
        {error && <div className="error">Error: {error}</div>}
        
        {activeTab === 'products' && (
          <div className="products-section">
            <h2>Products</h2>
            
            {/* Category Filters */}
            <div className="category-filters">
              <button 
                className={selectedCategory === null ? 'active' : ''}
                onClick={() => setSelectedCategory(null)}
              >
                🏪 All Products
              </button>
              {categories.map(cat => (
                <button
                  key={cat}
                  className={selectedCategory === cat ? 'active' : ''}
                  onClick={() => setSelectedCategory(cat)}
                >
                  {CATEGORY_LABELS[cat] || cat}
                </button>
              ))}
            </div>

            {loading ? (
              <p>Loading products...</p>
            ) : (
              <div className="products-grid">
                {products.map(product => (
                  <div key={product.id} className="product-card">
                    <button 
                      className={`wishlist-btn ${wishlist.includes(product.id) ? 'active' : ''}`}
                      onClick={() => toggleWishlist(product.id)}
                      title={wishlist.includes(product.id) ? 'Remove from wishlist' : 'Add to wishlist'}
                    >
                      {wishlist.includes(product.id) ? '❤️' : '🤍'}
                    </button>
                    <img 
                      src={product.image || 'https://via.placeholder.com/150'} 
                      alt={product.title}
                      className="product-image"
                    />
                    <div className="product-info">
                      <h3 className="product-title">{product.title}</h3>
                      <p className="product-category">{product.category}</p>
                      <p className="product-price">${product.price.toFixed(2)}</p>
                      <div className="product-rating" onClick={() => openReviewModal(product)} style={{cursor: 'pointer'}}>
                        ⭐ {product.rating_rate} ({product.rating_count} reviews)
                      </div>
                      <div className="product-actions">
                        <button 
                          className="add-to-cart-btn"
                          onClick={() => addToCart(product)}
                        >
                          Add to Cart
                        </button>
                        <button 
                          className="review-btn"
                          onClick={() => openReviewModal(product)}
                        >
                          Reviews
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'wishlist' && (
          <div className="wishlist-section">
            <h2>❤️ My Wishlist</h2>
            {!token ? (
              <p className="empty-wishlist">Please <button onClick={() => setShowAuthModal(true)}>login</button> to view your wishlist</p>
            ) : wishlist.length === 0 ? (
              <p className="empty-wishlist">Your wishlist is empty. Click the heart icon on products to add them!</p>
            ) : (
              <div className="products-grid">
                {products.filter(p => wishlist.includes(p.id)).map(product => (
                  <div key={product.id} className="product-card">
                    <button 
                      className="wishlist-btn active"
                      onClick={() => toggleWishlist(product.id)}
                    >
                      ❤️
                    </button>
                    <img 
                      src={product.image || 'https://via.placeholder.com/150'} 
                      alt={product.title}
                      className="product-image"
                    />
                    <div className="product-info">
                      <h3 className="product-title">{product.title}</h3>
                      <p className="product-price">${product.price.toFixed(2)}</p>
                      <button 
                        className="add-to-cart-btn"
                        onClick={() => addToCart(product)}
                      >
                        Add to Cart
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'cart' && (
          <div className="cart-section">
            <h2>Shopping Cart</h2>
            {cart.length === 0 ? (
              <p className="empty-cart">Your cart is empty</p>
            ) : (
              <>
                <div className="cart-items">
                  {cart.map(item => (
                    <div key={item.id} className="cart-item">
                      <img 
                        src={item.image || 'https://via.placeholder.com/80'} 
                        alt={item.title}
                        className="cart-item-image"
                      />
                      <div className="cart-item-info">
                        <h4>{item.title}</h4>
                        <p>${item.price.toFixed(2)}</p>
                      </div>
                      <div className="cart-item-quantity">
                        <button onClick={() => updateQuantity(item.id, -1)}>-</button>
                        <span>{item.quantity}</span>
                        <button onClick={() => updateQuantity(item.id, 1)}>+</button>
                      </div>
                      <div className="cart-item-total">
                        ${(item.price * item.quantity).toFixed(2)}
                      </div>
                      <button 
                        className="remove-btn"
                        onClick={() => removeFromCart(item.id)}
                      >
                        ✕
                      </button>
                    </div>
                  ))}
                </div>
                <div className="cart-summary">
                  <div className="cart-total">
                    <strong>Total: ${cartTotal.toFixed(2)}</strong>
                  </div>
                  <button className="checkout-btn" onClick={placeOrder}>
                    Place Order
                  </button>
                </div>
              </>
            )}
          </div>
        )}

        {activeTab === 'profile' && token && (
          <div className="profile-section">
            <h2>👤 My Profile</h2>
            
            {/* My Orders Section */}
            <div className="profile-orders">
              <h3>📦 My Orders</h3>
              {userOrders.length === 0 ? (
                <p className="empty-message">You haven't placed any orders yet.</p>
              ) : (
                <div className="orders-list">
                  {userOrders.map(order => (
                    <div key={order.id} className="order-card">
                      <div className="order-header">
                        <span className="order-id">Order #{order.id}</span>
                        <span className={`order-status ${order.status}`}>{order.status}</span>
                        <span className="order-date">{new Date(order.created_at).toLocaleDateString()}</span>
                      </div>
                      <div className="order-items">
                        {order.items?.map((item, idx) => (
                          <div key={idx} className="order-item">
                            <span className="item-name">{item.product?.title || `Product #${item.product_id}`}</span>
                            <span className="item-qty">x{item.quantity}</span>
                            <span className="item-price">${(item.price * item.quantity).toFixed(2)}</span>
                          </div>
                        ))}
                      </div>
                      <div className="order-total">
                        <strong>Total: ${order.total?.toFixed(2)}</strong>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* My Reviews Section */}
            <div className="profile-reviews">
              <h3>⭐ My Reviews</h3>
              {userReviews.length === 0 ? (
                <p className="empty-message">You haven't written any reviews yet.</p>
              ) : (
                <div className="reviews-list">
                  {userReviews.map(review => (
                    <div key={review.id} className="review-card">
                      <div className="review-header">
                        <span className="review-product">
                          {products.find(p => p.id === review.product_id)?.title || `Product #${review.product_id}`}
                        </span>
                        <span className="review-rating">
                          {'⭐'.repeat(review.rating)}
                        </span>
                        <span className="review-date">{new Date(review.created_at).toLocaleDateString()}</span>
                      </div>
                      {review.comment && (
                        <p className="review-comment">{review.comment}</p>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
      </main>

      {/* Review Modal */}
      {showReviewModal && selectedProduct && (
        <div className="modal-overlay" onClick={() => setShowReviewModal(false)}>
          <div className="modal review-modal" onClick={e => e.stopPropagation()}>
            <button className="modal-close" onClick={() => setShowReviewModal(false)}>✕</button>
            <h2>Reviews for {selectedProduct.title}</h2>
            
            <div className="review-summary">
              <span className="avg-rating">⭐ {productReviews.average_rating.toFixed(1)}</span>
              <span className="total-reviews">({productReviews.total_reviews} reviews)</span>
            </div>
            
            {token && (
              <form onSubmit={submitReview} className="review-form">
                <h3>Write a Review</h3>
                <div className="rating-input">
                  <label>Rating:</label>
                  <div className="star-rating">
                    {[1, 2, 3, 4, 5].map(star => (
                      <button
                        key={star}
                        type="button"
                        className={reviewForm.rating >= star ? 'star active' : 'star'}
                        onClick={() => setReviewForm({...reviewForm, rating: star})}
                      >
                        ⭐
                      </button>
                    ))}
                  </div>
                </div>
                <div className="form-group">
                  <label>Comment (optional)</label>
                  <textarea
                    value={reviewForm.comment}
                    onChange={e => setReviewForm({...reviewForm, comment: e.target.value})}
                    placeholder="Share your thoughts about this product..."
                    rows={3}
                  />
                </div>
                <button type="submit" className="submit-btn">Submit Review</button>
              </form>
            )}
            
            {!token && (
              <p className="login-prompt">
                <button onClick={() => { setShowReviewModal(false); setShowAuthModal(true); }}>Login</button> to write a review
              </p>
            )}
            
            <div className="reviews-list">
              <h3>Customer Reviews</h3>
              {productReviews.reviews.length === 0 ? (
                <p className="no-reviews">No reviews yet. Be the first to review!</p>
              ) : (
                productReviews.reviews.map(review => (
                  <div key={review.id} className="review-item">
                    <div className="review-header">
                      <span className="review-rating">{'⭐'.repeat(review.rating)}</span>
                      <span className="review-date">{new Date(review.created_at).toLocaleDateString()}</span>
                    </div>
                    {review.comment && <p className="review-comment">{review.comment}</p>}
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}

      <footer className="footer">
        <p>DevOps Final Project - Online Store API Demo</p>
      </footer>
    </div>
  )
}

export default App
