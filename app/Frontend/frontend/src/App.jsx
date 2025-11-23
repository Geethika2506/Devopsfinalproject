import React, { useState, useEffect } from 'react';
import { ShoppingCart, Package, User, LogIn, LogOut, Plus, Minus, Trash2, Search, Star, ArrowRight, ShoppingBag, TrendingUp, Tag, Heart, Menu, X } from 'lucide-react';

const API_URL = 'http://127.0.0.1:8001'; 

export default function App() {
  const [products, setProducts] = useState([]);
  const [cart, setCart] = useState([]);
  const [user, setUser] = useState(null);
  const [view, setView] = useState('products'); 
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [username, setUsername] = useState('');
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    fetchProducts();
    const token = localStorage.getItem('token');
    if (token) fetchUserProfile(token);
  }, []);

  const fetchProducts = async () => {
    try {
      setLoading(true);
      const res = await fetch(`${API_URL}/products`);
      if (res.ok) {
        const data = await res.json();
        setProducts(data);
        setError('');
      } else {
        setError('Backend is offline. Please run "python main.py"');
      }
    } catch (err) {
      console.error(err);
      setError('Could not connect. Make sure the Python backend is running on port 8000.');
    } finally {
      setLoading(false);
    }
  };

  const fetchUserProfile = async (token) => {
    try {
      const res = await fetch(`${API_URL}/users/me`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setUser(data);
      }
    } catch (err) { console.error(err); }
  };

  const handleLogin = async () => {
    setError('');
    try {
      const formData = new URLSearchParams();
      formData.append('username', email);
      formData.append('password', password);

      const res = await fetch(`${API_URL}/token`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData
      });

      if (res.ok) {
        const data = await res.json();
        localStorage.setItem('token', data.access_token);
        await fetchUserProfile(data.access_token);
        setView('products');
        setEmail(''); setPassword('');
      } else {
        setError('Invalid credentials');
      }
    } catch (err) {
      console.error(err);
      setError('Login failed');
    }
  };

  const handleRegister = async () => {
    setError('');
    try {
      const res = await fetch(`${API_URL}/users`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password, username })
      });

      if (res.ok) {
        setView('login');
        setError('Success! Please login.');
      } else {
        const data = await res.json();
        setError(data.detail || 'Registration failed');
      }
    } catch (err) { 
      console.error(err); 
      setError('Registration failed'); 
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setUser(null);
    setCart([]);
    setView('products');
  };

  const addToCart = (product) => {
    const existing = cart.find(item => item.id === product.id);
    if (existing) {
      setCart(cart.map(item => item.id === product.id ? { ...item, quantity: item.quantity + 1 } : item));
    } else {
      setCart([...cart, { ...product, quantity: 1 }]);
    }
  };

  const updateQuantity = (productId, delta) => {
    setCart(cart.map(item =>
      item.id === productId ? { ...item, quantity: Math.max(0, item.quantity + delta) } : item
    ).filter(item => item.quantity > 0));
  };

  const removeFromCart = (productId) => setCart(cart.filter(item => item.id !== productId));
  const getTotalPrice = () => cart.reduce((sum, item) => sum + (item.price * item.quantity), 0).toFixed(2);
  const getTotalItems = () => cart.reduce((sum, item) => sum + item.quantity, 0);

  const handleCheckout = async () => {
    if (!user) { setView('login'); return; }
    const token = localStorage.getItem('token');
    try {
      const orderItems = cart.map(item => ({ product_id: item.id, quantity: item.quantity, price: item.price }));
      const res = await fetch(`${API_URL}/orders`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ items: orderItems })
      });
      if (res.ok) { alert('Order placed successfully!'); setCart([]); setView('products'); } 
    } catch (err) { 
      console.error(err); 
      alert('Checkout failed'); 
    }
  };

  const filteredProducts = products.filter(p => 
    p.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    p.description?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="h-screen w-screen bg-slate-50 flex flex-col overflow-x-hidden overflow-y-auto">
      
      {/* TOP BAR */}
      <div className="bg-orange-600 text-white py-2 px-4 text-center text-sm font-medium w-full">
        🎉 Free shipping on orders over $50 | Shop now and save big!
      </div>

      {/* NAVBAR */}
      <header className="sticky top-0 z-50 bg-white shadow-md w-full">
        <div className="max-w-7xl mx-auto px-4 sm:px-6">
          <div className="flex items-center justify-between h-16">
            {/* LOGO */}
            <div className="flex items-center gap-3 cursor-pointer" onClick={() => setView('products')}>
              <div className="w-10 h-10 bg-gradient-to-br from-orange-500 to-pink-500 rounded-lg flex items-center justify-center text-white shadow-lg">
                <ShoppingBag size={24} />
              </div>
              <div>
                <h1 className="text-xl font-bold text-slate-800">MiniStore</h1>
                <p className="text-xs text-slate-500 hidden sm:block">Your Online Marketplace</p>
              </div>
            </div>

            {/* SEARCH BAR */}
            <div className="hidden md:flex flex-1 max-w-2xl mx-8">
              <div className="relative w-full">
                <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-slate-400" size={20} />
                <input
                  type="text"
                  placeholder="Search for products..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-12 pr-4 py-3 bg-slate-100 border border-slate-200 rounded-full focus:outline-none focus:ring-2 focus:ring-orange-500 focus:bg-white transition-all"
                />
              </div>
            </div>

            {/* RIGHT SIDE */}
            <div className="flex items-center gap-4">
              <button onClick={() => setView('cart')} className="relative group">
                <div className="p-2 hover:bg-orange-50 rounded-full transition-colors">
                  <ShoppingCart className={`w-6 h-6 ${view === 'cart' ? 'text-orange-600' : 'text-slate-600'}`} />
                  {cart.length > 0 && (
                    <span className="absolute -top-1 -right-1 w-5 h-5 bg-orange-600 text-white text-xs font-bold flex items-center justify-center rounded-full">{getTotalItems()}</span>
                  )}
                </div>
              </button>

              {user ? (
                <div className="flex items-center gap-2">
                  <div className="hidden sm:flex items-center gap-2 px-3 py-2 bg-slate-100 rounded-lg">
                    <User size={16} className="text-slate-600" />
                    <span className="text-sm font-medium text-slate-700">{user.username}</span>
                  </div>
                  <button onClick={handleLogout} className="p-2 text-slate-500 hover:text-red-600 hover:bg-red-50 rounded-lg transition-all">
                    <LogOut size={18} />
                  </button>
                </div>
              ) : (
                <button onClick={() => setView('login')} className="flex items-center gap-2 px-4 py-2 bg-orange-600 text-white rounded-lg font-medium text-sm hover:bg-orange-700 transition-all shadow-md">
                  <LogIn size={16} /> Sign In
                </button>
              )}
            </div>
          </div>

          {/* MOBILE SEARCH */}
          <div className="md:hidden pb-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400" size={18} />
              <input
                type="text"
                placeholder="Search products..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 bg-slate-100 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
              />
            </div>
          </div>
        </div>
      </header>

      {/* MAIN CONTENT */}
      <main className="flex-1 w-full bg-slate-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-8">
        
        {error && (
          <div className={`mb-6 p-4 rounded-lg flex items-center gap-3 ${error.includes('Success') ? 'bg-green-50 border border-green-200 text-green-700' : 'bg-red-50 border border-red-200 text-red-700'}`}>
            <div className="w-2 h-2 rounded-full bg-current"></div>
            <p className="font-medium">{error}</p>
          </div>
        )}

        {/* PRODUCTS VIEW */}
        {view === 'products' && (
          <div>
            {/* HERO BANNER */}
            <div className="bg-gradient-to-r from-orange-500 via-pink-500 to-purple-500 rounded-2xl p-8 md:p-12 mb-8 text-white shadow-xl">
              <div className="max-w-2xl">
                <div className="inline-block px-4 py-1 bg-white/20 rounded-full text-sm font-semibold mb-4">
                  ✨ New Arrivals
                </div>
                <h2 className="text-4xl md:text-5xl font-bold mb-4">Shop Everything You Need</h2>
                <p className="text-lg mb-6 text-white/90">Discover amazing products at unbeatable prices. From electronics to fashion, we have it all!</p>
                <button className="px-6 py-3 bg-white text-orange-600 font-bold rounded-lg hover:bg-orange-50 transition-all shadow-lg flex items-center gap-2">
                  Shop Now <ArrowRight size={18} />
                </button>
              </div>
            </div>

            {/* CATEGORIES */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
              {['Electronics', 'Fashion', 'Home & Garden', 'Sports'].map((cat) => (
                <div key={cat} className="bg-white p-4 rounded-lg shadow-sm hover:shadow-md transition-shadow cursor-pointer text-center border border-slate-200">
                  <div className="w-12 h-12 bg-orange-100 rounded-full flex items-center justify-center mx-auto mb-2">
                    <Tag className="text-orange-600" size={24} />
                  </div>
                  <p className="font-semibold text-slate-800">{cat}</p>
                </div>
              ))}
            </div>

            {/* PRODUCTS GRID */}
            <div className="mb-6 flex items-center justify-between">
              <h3 className="text-2xl font-bold text-slate-800">Featured Products</h3>
              <p className="text-slate-500">{filteredProducts.length} items</p>
            </div>
            
            {loading ? (
               <div className="text-center py-32">
                 <div className="w-16 h-16 border-4 border-orange-200 border-t-orange-600 rounded-full animate-spin mx-auto mb-4"></div>
                 <p className="text-slate-500 font-medium">Loading products...</p>
               </div>
            ) : filteredProducts.length === 0 ? (
              <div className="text-center py-32 bg-white rounded-lg shadow-sm">
                <Package size={64} className="text-slate-300 mx-auto mb-4" />
                <p className="text-slate-600 font-semibold text-lg">No products found</p>
                <p className="text-slate-400 text-sm mt-2">Try a different search or check your backend</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 pb-12">
                {filteredProducts.map((product) => (
                  <div key={product.id} className="group bg-white rounded-xl border border-slate-200 shadow-sm hover:shadow-lg transition-all duration-300 overflow-hidden">
                    <div className="relative h-48 bg-slate-100 flex items-center justify-center overflow-hidden">
                      <Package size={64} className="text-slate-300 group-hover:scale-110 transition-transform duration-300" />
                      <button className="absolute top-3 right-3 p-2 bg-white rounded-full shadow-md hover:bg-orange-50 transition-colors">
                        <Heart size={18} className="text-slate-400 hover:text-orange-600" />
                      </button>
                      <div className="absolute top-3 left-3 px-3 py-1 bg-orange-600 text-white text-xs font-bold rounded-full">
                        HOT
                      </div>
                    </div>
                    <div className="p-4">
                      <h3 className="font-semibold text-slate-800 mb-1 line-clamp-2 group-hover:text-orange-600 transition-colors">{product.name}</h3>
                      <p className="text-slate-500 text-sm mb-3 line-clamp-1">{product.description || 'Quality product at great price'}</p>
                      
                      <div className="flex items-center gap-1 mb-3">
                        {[...Array(5)].map((_, i) => (
                          <Star key={i} size={12} className="fill-yellow-400 text-yellow-400" />
                        ))}
                        <span className="text-xs text-slate-500 ml-1">(4.5)</span>
                      </div>

                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-2xl font-bold text-orange-600">${product.price}</p>
                          <p className="text-xs text-slate-400 line-through">$99.99</p>
                        </div>
                        <button 
                          onClick={() => addToCart(product)}
                          className="p-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-all shadow-md hover:shadow-lg"
                        >
                          <Plus size={20} />
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* CART VIEW */}
        {view === 'cart' && (
          <div className="pb-12">
            <h2 className="text-3xl font-bold text-slate-800 mb-6">Shopping Cart ({getTotalItems()} items)</h2>
            {cart.length === 0 ? (
              <div className="text-center py-16 bg-white rounded-lg shadow-sm">
                <ShoppingCart size={64} className="text-slate-300 mx-auto mb-4" />
                <p className="text-slate-600 font-semibold text-xl mb-2">Your cart is empty</p>
                <p className="text-slate-400 mb-6">Add products to get started</p>
                <button onClick={() => setView('products')} className="px-6 py-3 bg-orange-600 text-white font-semibold rounded-lg hover:bg-orange-700 transition-all">
                  Continue Shopping
                </button>
              </div>
            ) : (
              <div className="grid lg:grid-cols-3 gap-6">
                {/* CART ITEMS */}
                <div className="lg:col-span-2 space-y-4">
                  {cart.map((item) => (
                    <div key={item.id} className="bg-white rounded-lg p-4 shadow-sm border border-slate-200">
                      <div className="flex gap-4">
                        <div className="w-24 h-24 bg-slate-100 rounded-lg flex items-center justify-center flex-shrink-0">
                          <Package size={40} className="text-slate-300" />
                        </div>
                        <div className="flex-1">
                          <h3 className="font-semibold text-slate-800 mb-1">{item.name}</h3>
                          <p className="text-slate-500 text-sm mb-3">In Stock • Ships in 1-2 days</p>
                          
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2">
                              <button 
                                onClick={() => updateQuantity(item.id, -1)}
                                className="w-8 h-8 bg-slate-100 hover:bg-slate-200 rounded flex items-center justify-center transition-colors"
                              >
                                <Minus size={16} />
                              </button>
                              <span className="w-12 text-center font-medium">{item.quantity}</span>
                              <button 
                                onClick={() => updateQuantity(item.id, 1)}
                                className="w-8 h-8 bg-slate-100 hover:bg-slate-200 rounded flex items-center justify-center transition-colors"
                              >
                                <Plus size={16} />
                              </button>
                            </div>
                            
                            <div className="text-right">
                              <p className="text-xl font-bold text-slate-800">${(item.price * item.quantity).toFixed(2)}</p>
                              <button 
                                onClick={() => removeFromCart(item.id)}
                                className="text-sm text-red-600 hover:text-red-700 font-medium mt-1"
                              >
                                Remove
                              </button>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                {/* ORDER SUMMARY */}
                <div className="lg:col-span-1">
                  <div className="bg-white rounded-lg p-6 shadow-md border border-slate-200 sticky top-24">
                    <h3 className="text-xl font-bold text-slate-800 mb-4">Order Summary</h3>
                    
                    <div className="space-y-3 mb-4 pb-4 border-b border-slate-200">
                      <div className="flex justify-between text-slate-600">
                        <span>Subtotal ({getTotalItems()} items)</span>
                        <span>${getTotalPrice()}</span>
                      </div>
                      <div className="flex justify-between text-slate-600">
                        <span>Shipping</span>
                        <span className="text-green-600 font-medium">FREE</span>
                      </div>
                      <div className="flex justify-between text-slate-600">
                        <span>Tax</span>
                        <span>${(getTotalPrice() * 0.1).toFixed(2)}</span>
                      </div>
                    </div>
                    
                    <div className="flex justify-between text-xl font-bold text-slate-800 mb-6">
                      <span>Total</span>
                      <span className="text-orange-600">${(parseFloat(getTotalPrice()) * 1.1).toFixed(2)}</span>
                    </div>
                    
                    <button 
                      onClick={handleCheckout}
                      className="w-full py-4 bg-orange-600 text-white font-bold rounded-lg hover:bg-orange-700 transition-all shadow-md hover:shadow-lg mb-3"
                    >
                      Proceed to Checkout
                    </button>
                    
                    <button 
                      onClick={() => setView('products')}
                      className="w-full py-3 bg-slate-100 text-slate-700 font-medium rounded-lg hover:bg-slate-200 transition-all"
                    >
                      Continue Shopping
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* LOGIN VIEW */}
        {view === 'login' && (
          <div className="max-w-md mx-auto mt-12">
            <div className="bg-white rounded-2xl p-8 shadow-lg border border-slate-200">
              <div className="text-center mb-8">
                <div className="w-16 h-16 bg-gradient-to-br from-orange-500 to-pink-500 rounded-full flex items-center justify-center text-white shadow-lg mx-auto mb-4">
                  <User size={32} />
                </div>
                <h2 className="text-2xl font-bold text-slate-800 mb-2">Welcome Back!</h2>
                <p className="text-slate-500">Sign in to your account</p>
              </div>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">Email</label>
                  <input 
                    type="email"
                    placeholder="Enter your email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 transition-all"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">Password</label>
                  <input 
                    type="password"
                    placeholder="Enter your password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 transition-all"
                  />
                </div>
                <button 
                  onClick={handleLogin}
                  className="w-full py-3 bg-orange-600 text-white font-bold rounded-lg hover:bg-orange-700 transition-all shadow-md"
                >
                  Sign In
                </button>
                <div className="text-center pt-4 border-t border-slate-200">
                  <p className="text-slate-600 text-sm mb-2">Don't have an account?</p>
                  <button onClick={() => setView('register')} className="text-orange-600 hover:text-orange-700 font-semibold">
                    Create Account
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* REGISTER VIEW */}
        {view === 'register' && (
          <div className="max-w-md mx-auto mt-12">
            <div className="bg-white rounded-2xl p-8 shadow-lg border border-slate-200">
              <div className="text-center mb-8">
                <div className="w-16 h-16 bg-gradient-to-br from-orange-500 to-pink-500 rounded-full flex items-center justify-center text-white shadow-lg mx-auto mb-4">
                  <ShoppingBag size={32} />
                </div>
                <h2 className="text-2xl font-bold text-slate-800 mb-2">Create Account</h2>
                <p className="text-slate-500">Join MiniStore today</p>
              </div>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">Username</label>
                  <input 
                    type="text"
                    placeholder="Choose a username"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 transition-all"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">Email</label>
                  <input 
                    type="email"
                    placeholder="Enter your email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 transition-all"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">Password</label>
                  <input 
                    type="password"
                    placeholder="Create a password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 transition-all"
                  />
                </div>
                <button 
                  onClick={handleRegister}
                  className="w-full py-3 bg-orange-600 text-white font-bold rounded-lg hover:bg-orange-700 transition-all shadow-md"
                >
                  Create Account
                </button>
                <div className="text-center pt-4 border-t border-slate-200">
                  <p className="text-slate-600 text-sm mb-2">Already have an account?</p>
                  <button onClick={() => setView('login')} className="text-orange-600 hover:text-orange-700 font-semibold">
                    Sign In
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
        </div>
      </main>

      {/* FOOTER */}
      <footer className="bg-slate-900 text-white py-10 w-full">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <div className="w-8 h-8 bg-gradient-to-br from-orange-500 to-pink-500 rounded-lg flex items-center justify-center">
                  <ShoppingBag size={20} />
                </div>
                <span className="text-lg font-bold">MiniStore</span>
              </div>
              <p className="text-slate-400 text-sm">Your trusted online marketplace for quality products at amazing prices.</p>
            </div>
            <div>
              <h4 className="font-semibold mb-3">Shop</h4>
              <ul className="space-y-2 text-slate-400 text-sm">
                <li>Electronics</li>
                <li>Fashion</li>
                <li>Home & Garden</li>
                <li>Sports</li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-3">Support</h4>
              <ul className="space-y-2 text-slate-400 text-sm">
                <li>Help Center</li>
                <li>Track Order</li>
                <li>Returns</li>
                <li>Contact Us</li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-3">Company</h4>
              <ul className="space-y-2 text-slate-400 text-sm">
                <li>About Us</li>
                <li>Careers</li>
                <li>Privacy Policy</li>
                <li>Terms of Service</li>
              </ul>
            </div>
          </div>
          <div className="border-t border-slate-800 pt-6 text-center text-slate-400 text-sm">
            <p>© 2024 MiniStore. All rights reserved. Built with React & FastAPI</p>
          </div>
        </div>
      </footer>
    </div>
  );
}