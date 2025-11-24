import { useCallback, useEffect, useMemo, useState } from 'react';
import axios from 'axios';

const useApiClient = (apiKey) => {
  const client = useMemo(() => axios.create({ baseURL: '/api' }), []);

  useEffect(() => {
    if (apiKey) {
      client.defaults.headers.common['x-api-key'] = apiKey;
    } else {
      delete client.defaults.headers.common['x-api-key'];
    }
  }, [apiKey, client]);

  return client;
};

const initialProduct = { name: '', price: '', description: '' };
const initialCustomer = { name: '', email: '' };
const initialOrder = { customer_id: '', product_id: '', quantity: 1 };

function App() {
  const [apiKey, setApiKey] = useState(() => localStorage.getItem('apiKey') ?? '');
  const [products, setProducts] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [productForm, setProductForm] = useState(initialProduct);
  const [customerForm, setCustomerForm] = useState(initialCustomer);
  const [orderForm, setOrderForm] = useState(initialOrder);

  const api = useApiClient(apiKey);

  useEffect(() => {
    localStorage.setItem('apiKey', apiKey);
  }, [apiKey]);

  const fetchAll = useCallback(async () => {
    if (!apiKey) {
      setError('Enter your API key to start making requests.');
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
  }, [api, apiKey]);

  useEffect(() => {
    fetchAll();
  }, [fetchAll]);

  const handleCreate = async (type) => {
    try {
      if (type === 'product') {
        await api.post('/products', {
          ...productForm,
          price: Number(productForm.price || 0),
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
          quantity: Number(orderForm.quantity) || 1,
        });
        setOrderForm(initialOrder);
      }
      fetchAll();
    } catch (err) {
      const detail = err.response?.data?.detail;
      setError(typeof detail === 'string' ? detail : err.message);
    }
  };

  const disabled = loading || !apiKey;

  return (
    <main>
      <header>
        <div>
          <h1>Store Control Panel</h1>
          <p>Backed by FastAPI + SQLite. Use the forms to seed quick demo data.</p>
        </div>
        <button onClick={fetchAll} disabled={disabled}>
          {loading ? 'Refreshing…' : 'Refresh Data'}
        </button>
      </header>

      <section className="api-key-banner">
        <strong>API Key</strong>
        <p>Requests require the same API key configured on the backend (header `x-api-key`).</p>
        <input
          aria-label="API key"
          placeholder="Enter API key"
          value={apiKey}
          onChange={(event) => setApiKey(event.target.value.trim())}
        />
      </section>

      {error && (
        <div className="card" style={{ borderLeft: '4px solid #f87171' }}>
          <strong>Something went wrong:</strong>
          <p>{error}</p>
        </div>
      )}

      <div className="grid">
        <article className="card">
          <div className="badge">Products ({products.length})</div>
          <h2>Catalog</h2>
          <form
            onSubmit={(event) => {
              event.preventDefault();
              handleCreate('product');
            }}
          >
            <input
              required
              placeholder="Name"
              value={productForm.name}
              onChange={(event) => setProductForm((prev) => ({ ...prev, name: event.target.value }))}
            />
            <input
              required
              type="number"
              min="0"
              step="0.01"
              placeholder="Price"
              value={productForm.price}
              onChange={(event) => setProductForm((prev) => ({ ...prev, price: event.target.value }))}
            />
            <input
              placeholder="Description"
              value={productForm.description}
              onChange={(event) => setProductForm((prev) => ({ ...prev, description: event.target.value }))}
            />
            <button type="submit" disabled={disabled}>
              Add Product
            </button>
          </form>
          <table className="table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Price</th>
              </tr>
            </thead>
            <tbody>
              {products.map((product) => (
                <tr key={product.id}>
                  <td>{product.name}</td>
                  <td>${product.price.toFixed(2)}</td>
                </tr>
              ))}
              {products.length === 0 && (
                <tr>
                  <td colSpan={2}>No products yet.</td>
                </tr>
              )}
            </tbody>
          </table>
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
                  {product.name}
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
                  <td>{customers.find((customer) => customer.id === order.customer_id)?.name ?? order.customer_id}</td>
                  <td>{products.find((product) => product.id === order.product_id)?.name ?? order.product_id}</td>
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
