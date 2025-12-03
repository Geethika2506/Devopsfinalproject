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
    }
  }, [])

  // Fetch current user when token changes
  useEffect(() => {
    if (token) {
      fetchCurrentUser()
    } else {
      setUser(null)
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
  }

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
          'X-User-ID': userId.toString()
        },
        body: JSON.stringify(orderData)
      })
      
      if (!res.ok) throw new Error('Failed to place order')
      
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
          className={activeTab === 'cart' ? 'active' : ''} 
          onClick={() => setActiveTab('cart')}
        >
          Cart ({cart.length})
        </button>
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
                    <img 
                      src={product.image || 'https://via.placeholder.com/150'} 
                      alt={product.title}
                      className="product-image"
                    />
                    <div className="product-info">
                      <h3 className="product-title">{product.title}</h3>
                      <p className="product-category">{product.category}</p>
                      <p className="product-price">${product.price.toFixed(2)}</p>
                      <div className="product-rating">
                        ⭐ {product.rating_rate} ({product.rating_count} reviews)
                      </div>
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
      </main>

      <footer className="footer">
        <p>DevOps Final Project - Online Store API Demo</p>
      </footer>
    </div>
  )
}

export default App
