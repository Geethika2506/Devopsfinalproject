import { useState, useEffect } from "react";
import axios from "axios";

const BACKEND = "http://127.0.0.1:8001";

function App() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState(""); // UI only, backend ignores
  const [user, setUser] = useState(null);
  const [cart, setCart] = useState(null);

  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [products, setProducts] = useState([]);

  const [orders, setOrders] = useState([]);
  const [errorMsg, setErrorMsg] = useState("");

  // ----------------------------------------
  // Load categories on first render
  // ----------------------------------------
  useEffect(() => {
    axios
      .get(`${BACKEND}/products/categories`)
      .then((res) => {
        setCategories(res.data);
        setErrorMsg("");
      })
      .catch((err) => {
        console.error(err);
        setErrorMsg("Failed to load categories");
      });
  }, []);

  // ----------------------------------------
  // User + Cart
  // ----------------------------------------
  const createUserAndCart = async () => {
    try {
      setErrorMsg("");

      // 1. Create user (only email is used by backend)
      const res = await axios.post(`${BACKEND}/users/`, {
        email,
      });

      const createdUser = res.data;
      setUser(createdUser);
      setPassword(""); // clear UI password

      // 2. Create/get cart for this user
      const cartRes = await axios.post(`${BACKEND}/cart/${createdUser.id}`);
      setCart(cartRes.data);
    } catch (err) {
      console.error(err);
      setErrorMsg("Failed to create user");
    }
  };

  // ----------------------------------------
  // Products from FakeStore via backend
  // ----------------------------------------
  const loadProductsInCategory = async (category) => {
    setSelectedCategory(category);
    setProducts([]);
    try {
      const res = await axios.get(`${BACKEND}/products/category/${category}`);
      setProducts(res.data);
      setErrorMsg("");
    } catch (err) {
      console.error(err);
      setErrorMsg("Failed to load products");
    }
  };

  // ----------------------------------------
  // Cart operations
  // ----------------------------------------
  const addToCart = async (productId) => {
    if (!cart) return;

    try {
      const res = await axios.post(`${BACKEND}/cart/${cart.id}/items`, {
        product_id: productId,
        quantity: 1,
      });
      setCart(res.data);
      setErrorMsg("");
    } catch (err) {
      console.error(err);
      setErrorMsg("Failed to add item to cart");
    }
  };

  // ----------------------------------------
  // Orders
  // ----------------------------------------
  const createOrder = async () => {
    if (!user) return;

    try {
      const res = await axios.post(`${BACKEND}/orders/${user.id}`);
      alert("Order created with total: " + res.data.total.toFixed(2));
      setErrorMsg("");
      loadOrders();
    } catch (err) {
      console.error(err);
      setErrorMsg("Failed to create order");
    }
  };

  const loadOrders = async () => {
    if (!user) return;

    try {
      const res = await axios.get(`${BACKEND}/orders/user/${user.id}`);
      setOrders(res.data);
      setErrorMsg("");
    } catch (err) {
      console.error(err);
      setErrorMsg("Failed to load orders");
    }
  };

  // ----------------------------------------
  // Render helpers
  // ----------------------------------------
  const renderCart = () => {
    if (!cart) return <p>No cart yet. Create a user first.</p>;
    if (!cart.items || cart.items.length === 0)
      return <p>Cart is empty.</p>;

    return (
      <ul>
        {cart.items.map((item) => (
          <li key={item.id}>
            Product ID: {item.product_id} — Qty: {item.quantity}
          </li>
        ))}
      </ul>
    );
  };

  return (
    <div style={{ padding: "40px", fontFamily: "Arial, sans-serif" }}>
      <h1>DevOps Shop Frontend</h1>
      <p>Backend: {BACKEND}</p>

      {errorMsg && (
        <div
          style={{
            color: "white",
            background: "#ffb3b3",
            padding: "10px",
            marginTop: "10px",
          }}
        >
          {errorMsg}
        </div>
      )}

      {/* USER SECTION */}
      <div
        style={{
          border: "1px solid #ccc",
          padding: "20px",
          marginTop: "20px",
        }}
      >
        <h2>User</h2>

        {!user ? (
          <>
            <p>No user yet. Create one:</p>
            <input
              placeholder="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              style={{ padding: "5px" }}
            />
            <input
              placeholder="password (not stored)"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              style={{ marginLeft: "10px", padding: "5px" }}
            />
            <button
              onClick={createUserAndCart}
              style={{ marginLeft: "10px", padding: "5px 10px" }}
            >
              Create user + cart
            </button>
          </>
        ) : (
          <>
            <p>
              User logged in: <b>{user.email}</b>
            </p>
            {cart && <p>Cart ID: {cart.id}</p>}
          </>
        )}
      </div>

      {/* PRODUCTS + CATEGORIES */}
      <div
        style={{
          border: "1px solid #ccc",
          padding: "20px",
          marginTop: "20px",
        }}
      >
        <h2>Products (via FakeStore API → your backend)</h2>

        <h4>Categories:</h4>
        <div>
          {categories.map((c) => (
            <button
              key={c}
              onClick={() => loadProductsInCategory(c)}
              style={{
                marginRight: "10px",
                marginTop: "5px",
                padding: "6px 12px",
                background:
                  selectedCategory === c ? "#333" : "white",
                color: selectedCategory === c ? "white" : "black",
                border: "1px solid #ccc",
                borderRadius: "4px",
                cursor: "pointer",
              }}
            >
              {c}
            </button>
          ))}
        </div>

        <h4 style={{ marginTop: "20px" }}>Products:</h4>
        {products.length === 0 ? (
          <p>No products yet.</p>
        ) : (
          products.map((p) => (
            <div
              key={p.id}
              style={{
                marginBottom: "10px",
                paddingBottom: "10px",
                borderBottom: "1px solid #eee",
              }}
            >
              <b>{p.title}</b> — ${p.price}
              <button
                onClick={() => addToCart(p.id)}
                style={{ marginLeft: "10px", padding: "4px 8px" }}
              >
                Add to cart
              </button>
            </div>
          ))
        )}
      </div>

      {/* CART SECTION */}
      <div
        style={{
          border: "1px solid #ccc",
          padding: "20px",
          marginTop: "20px",
        }}
      >
        <h2>Cart</h2>
        {renderCart()}
      </div>

      {/* ORDERS */}
      <div
        style={{
          border: "1px solid #ccc",
          padding: "20px",
          marginTop: "20px",
          marginBottom: "40px",
        }}
      >
        <h2>Orders</h2>

        <button onClick={createOrder} style={{ padding: "5px 10px" }}>
          Create order from cart
        </button>
        <button
          onClick={loadOrders}
          style={{ marginLeft: "10px", padding: "5px 10px" }}
        >
          Refresh my orders
        </button>

        <div style={{ marginTop: "20px" }}>
          {orders.length === 0 ? (
            <p>No orders yet.</p>
          ) : (
            orders.map((o) => (
              <div key={o.id}>
                Order #{o.id} — Total: ${o.total.toFixed(2)}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
