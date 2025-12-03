import { useCallback, useEffect, useMemo, useState } from 'react';
import axios from 'axios';

const fakestoreCategories = [
  'electronics',
  'jewelery',
  "men's clothing",
  "women's clothing",
  'general',
];

const normalizeRating = (rating) => ({
  rate: Number(rating?.rate ?? 0),
  count: Number(rating?.count ?? 0),
});

const useApiClient = (token) => {
  const client = useMemo(() => axios.create({ baseURL: '/api' }), []);

  useEffect(() => {
    if (token) {
      client.defaults.headers.common.Authorization = `Bearer ${token}`;
    } else {
      delete client.defaults.headers.common.Authorization;
    }
  }, [token, client]);

  return client;
};

const initialProduct = {
  title: '',
  price: '',
  description: '',
  category: fakestoreCategories[0],
  image: '',
  rating: { rate: '0', count: '0' },
};
const initialCustomer = { name: '', email: '' };
const initialOrder = { customer_id: '', product_id: '', quantity: 1 };

const toNumber = (value, fallback = 0) => {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : fallback;
};

const formatCurrency = (value) => {
  const parsed = Number(value ?? 0);
  return Number.isFinite(parsed) ? parsed.toFixed(2) : '0.00';
};

function App() {
  const [token, setToken] = useState(() => localStorage.getItem('token') ?? '');
  const [authUser, setAuthUser] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem('user'));
    } catch {
      return null;
    }
  });
  const [loginForm, setLoginForm] = useState({ email: '', password: '' });
  const [registerForm, setRegisterForm] = useState({ email: '', password: '' });
  const [products, setProducts] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [productForm, setProductForm] = useState(initialProduct);
  const [customerForm, setCustomerForm] = useState(initialCustomer);
  const [orderForm, setOrderForm] = useState(initialOrder);

  const api = useApiClient(token);

  useEffect(() => {
    if (token) {
      localStorage.setItem('token', token);
    } else {
      localStorage.removeItem('token');
    }
  }, [token]);

  useEffect(() => {
    if (authUser) {
      localStorage.setItem('user', JSON.stringify(authUser));
    } else {
      localStorage.removeItem('user');
    }
  }, [authUser]);

  const loadProfile = useCallback(async () => {
    if (!token) {
      setAuthUser(null);
      return;
    }

    try {
      const response = await api.get('/auth/me');
      setAuthUser(response.data);
    } catch (err) {
      console.error('Profile fetch failed', err);
      setAuthUser(null);
      setToken('');
    }
  }, [api, token]);

  const fetchAll = useCallback(async () => {
    if (!token) {
      setError('Log in to start making requests.');
      setProducts([]);
      setCustomers([]);
      setOrders([]);
      return;
    }

    setLoading(true);
    setError('');
    try {
      const [productsRes, customersRes, ordersRes] = await Promise.all([
        api.get('/products'),
        api.get('/customers'),
        api.get('/orders'),
      ]);

      setProducts(productsRes.data);
      setCustomers(customersRes.data);
      setOrders(ordersRes.data);
    } catch (err) {
      const detail = err.response?.data?.detail;
      setError(typeof detail === 'string' ? detail : err.message);
    } finally {
      setLoading(false);
    }
  }, [api, token]);

  useEffect(() => {
    loadProfile();
    fetchAll();
  }, [fetchAll, loadProfile]);

  const handleLogin = async (credentials = loginForm) => {
    setError('');
    try {
      const params = new URLSearchParams();
      params.append('username', credentials.email);
      params.append('password', credentials.password);
      const response = await api.post('/auth/token', params, {
        headers: { 'content-type': 'application/x-www-form-urlencoded' },
      });
      setToken(response.data.access_token);
      setAuthUser({ email: credentials.email });
      setLoginForm({ email: '', password: '' });
    } catch (err) {
      const detail = err.response?.data?.detail;
      setError(typeof detail === 'string' ? detail : err.message);
    }
  };

  const handleRegister = async () => {
    setError('');
    try {
      const creds = { ...registerForm };
      await api.post('/auth/register', creds);
      setRegisterForm({ email: '', password: '' });
      await handleLogin(creds);
    } catch (err) {
      const detail = err.response?.data?.detail;
      setError(typeof detail === 'string' ? detail : err.message);
    }
  };

  const handleLogout = () => {
    setToken('');
    setAuthUser(null);
    setProducts([]);
    setCustomers([]);
    setOrders([]);
  };

  const handleCreate = async (type) => {
    try {
      if (type === 'product') {
        await api.post('/products', {
          ...productForm,
          price: toNumber(productForm.price, 0),
          rating: {
            rate: toNumber(productForm.rating.rate, 0),
            count: Math.max(0, Math.trunc(toNumber(productForm.rating.count, 0))),
          },
        });
        setProductForm(initialProduct);
      } else if (type === 'customer') {
        await api.post('/customers', customerForm);
        setCustomerForm(initialCustomer);
      } else if (type === 'order') {
        await api.post('/orders', {
          ...orderForm,
          customer_id: Number(orderForm.customer_id),
          product_id: Number(orderForm.product_id),
          quantity: Math.max(1, Math.trunc(Number(orderForm.quantity) || 1)),
        });
        setOrderForm(initialOrder);
      }
      fetchAll();
    } catch (err) {
      const detail = err.response?.data?.detail;
      setError(typeof detail === 'string' ? detail : err.message);
    }
  };

  const disabled = loading || !token;
  const customerLookup = useMemo(
    () => Object.fromEntries(customers.map((customer) => [customer.id, customer])),
    [customers],
  );
  const productLookup = useMemo(
    () => Object.fromEntries(products.map((product) => [product.id, product])),
    [products],
  );

  return (
    <main>
      <header>
        <div>
          <h1>Store Control Panel</h1>
          <p>Matches FakeStore products schema while still talking to your FastAPI backend.</p>
        </div>
        <button onClick={fetchAll} disabled={disabled}>
          {loading ? 'Refreshing…' : 'Refresh Data'}
        </button>
      </header>

      <section className="auth-banner">
        {authUser ? (
          <div className="auth-success">
            <p>
              Signed in as <strong>{authUser.email}</strong>
            </p>
            <button onClick={handleLogout}>Log out</button>
          </div>
        ) : (
          <div className="auth-grid">
            <form
              onSubmit={(event) => {
                event.preventDefault();
                handleRegister();
              }}
            >
              <h3>Create account</h3>
              <input
                required
                type="email"
                placeholder="Email"
                value={registerForm.email}
                onChange={(event) =>
                  setRegisterForm((prev) => ({ ...prev, email: event.target.value }))
                }
              />
              <input
                required
                type="password"
                placeholder="Password"
                value={registerForm.password}
                onChange={(event) =>
                  setRegisterForm((prev) => ({ ...prev, password: event.target.value }))
                }
              />
              <button type="submit">Register</button>
            </form>

            <form
              onSubmit={(event) => {
                event.preventDefault();
                handleLogin();
              }}
            >
              <h3>Log in</h3>
              <input
                required
                type="email"
                placeholder="Email"
                value={loginForm.email}
                onChange={(event) => setLoginForm((prev) => ({ ...prev, email: event.target.value }))}
              />
              <input
                required
                type="password"
                placeholder="Password"
                value={loginForm.password}
                onChange={(event) => setLoginForm((prev) => ({ ...prev, password: event.target.value }))}
              />
              <button type="submit">Access dashboard</button>
            </form>
          </div>
        )}
      </section>

      {error && (
        <div className="card" style={{ borderLeft: '4px solid #f87171' }}>
          <strong>Something went wrong:</strong>
          <p>{error}</p>
        </div>
      )}

      <div className="grid" aria-disabled={!token}>
        <article className="card">
          <div className="badge">Products ({products.length})</div>
          <h2>Catalog (FakeStore-compatible)</h2>
          <p>Fields: title, price, category, description, image, rating.</p>
          <form
            onSubmit={(event) => {
              event.preventDefault();
              handleCreate('product');
            }}
          >
            <input
              required
              placeholder="Title"
              value={productForm.title}
              onChange={(event) => setProductForm((prev) => ({ ...prev, title: event.target.value }))}
            />
            <select
              value={productForm.category}
              onChange={(event) => setProductForm((prev) => ({ ...prev, category: event.target.value }))}
            >
              {fakestoreCategories.map((category) => (
                <option key={category} value={category}>
                  {category}
                </option>
              ))}
            </select>
            <input
              required
              type="number"
              min="0"
              step="0.01"
              placeholder="Price"
              value={productForm.price}
              onChange={(event) => setProductForm((prev) => ({ ...prev, price: event.target.value }))}
            />
            <textarea
              rows={3}
              placeholder="Description"
              value={productForm.description}
              onChange={(event) => setProductForm((prev) => ({ ...prev, description: event.target.value }))}
            />
            <input
              type="url"
              placeholder="Image URL"
              value={productForm.image}
              onChange={(event) => setProductForm((prev) => ({ ...prev, image: event.target.value }))}
            />
            <div className="inline-fields">
              <input
                type="number"
                min="0"
                max="5"
                step="0.1"
                placeholder="Rating (0-5)"
                value={productForm.rating.rate}
                onChange={(event) =>
                  setProductForm((prev) => ({
                    ...prev,
                    rating: { ...prev.rating, rate: event.target.value },
                  }))
                }
              />
              <input
                type="number"
                min="0"
                placeholder="Rating count"
                value={productForm.rating.count}
                onChange={(event) =>
                  setProductForm((prev) => ({
                    ...prev,
                    rating: { ...prev.rating, count: event.target.value },
                  }))
                }
              />
            </div>
            <button type="submit" disabled={disabled}>
              Add Product
            </button>
          </form>

          {products.length > 0 ? (
            <div className="product-grid">
              {products.map((product) => {
                const rating = normalizeRating(product.rating);
                return (
                  <div className="product-card" key={product.id}>
                    {product.image ? (
                      <img src={product.image} alt={product.title} loading="lazy" />
                    ) : (
                      <div className="product-placeholder">No image</div>
                    )}
                    <div className="product-meta">
                      <span className="product-category">{product.category}</span>
                      <h3>{product.title}</h3>
                      <p className="product-price">${formatCurrency(product.price)}</p>
                      <p className="product-rating">⭐ {rating.rate.toFixed(1)} ({rating.count})</p>
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="empty-state">
              No products yet. Seed via the CLI (`python -m backend.cli seed-fakestore`) or add one above.
            </div>
          )}
        </article>

        <article className="card">
          <div className="badge">Customers ({customers.length})</div>
          <h2>Accounts</h2>
          <form
            onSubmit={(event) => {
              event.preventDefault();
              handleCreate('customer');
            }}
          >
            <input
              required
              placeholder="Full name"
              value={customerForm.name}
              onChange={(event) => setCustomerForm((prev) => ({ ...prev, name: event.target.value }))}
            />
            <input
              required
              type="email"
              placeholder="Email"
              value={customerForm.email}
              onChange={(event) => setCustomerForm((prev) => ({ ...prev, email: event.target.value }))}
            />
            <button type="submit" disabled={disabled}>
              Add Customer
            </button>
          </form>
          <table className="table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Email</th>
              </tr>
            </thead>
            <tbody>
              {customers.map((customer) => (
                <tr key={customer.id}>
                  <td>{customer.name}</td>
                  <td>{customer.email}</td>
                </tr>
              ))}
              {customers.length === 0 && (
                <tr>
                  <td colSpan={2}>No customers yet.</td>
                </tr>
              )}
            </tbody>
          </table>
        </article>

        <article className="card" style={{ gridColumn: '1 / -1' }}>
          <div className="badge">Orders ({orders.length})</div>
          <h2>Orders</h2>
          <form
            onSubmit={(event) => {
              event.preventDefault();
              handleCreate('order');
            }}
          >
            <select
              required
              value={orderForm.customer_id}
              onChange={(event) => setOrderForm((prev) => ({ ...prev, customer_id: event.target.value }))}
            >
              <option value="">Select customer</option>
              {customers.map((customer) => (
                <option key={customer.id} value={customer.id}>
                  {customer.name}
                </option>
              ))}
            </select>
            <select
              required
              value={orderForm.product_id}
              onChange={(event) => setOrderForm((prev) => ({ ...prev, product_id: event.target.value }))}
            >
              <option value="">Select product</option>
              {products.map((product) => (
                <option key={product.id} value={product.id}>
                  {product.title}
                </option>
              ))}
            </select>
            <input
              required
              type="number"
              min="1"
              placeholder="Quantity"
              value={orderForm.quantity}
              onChange={(event) => setOrderForm((prev) => ({ ...prev, quantity: event.target.value }))}
            />
            <button type="submit" disabled={disabled}>
              Link Order
            </button>
          </form>
          <table className="table">
            <thead>
              <tr>
                <th>Order #</th>
                <th>Customer</th>
                <th>Product</th>
                <th>Qty</th>
              </tr>
            </thead>
            <tbody>
              {orders.map((order) => (
                <tr key={order.id}>
                  <td>{order.id}</td>
                  <td>{customerLookup[order.customer_id]?.name ?? order.customer_id}</td>
                  <td>{productLookup[order.product_id]?.title ?? order.product_id}</td>
                  <td>{order.quantity}</td>
                </tr>
              ))}
              {orders.length === 0 && (
                <tr>
                  <td colSpan={4}>No orders yet.</td>
                </tr>
              )}
            </tbody>
          </table>
        </article>
      </div>
    </main>
  );
}

export default App;
