// --- GLOBAL STATE ---
let state = {
    products: [],
    cart: JSON.parse(localStorage.getItem('luxeCart')) || [],
    user: JSON.parse(localStorage.getItem('luxeUser')) || null
};

// --- API HANDLING ---
const api = {
    fetchProducts: async () => {
        try {
            const res = await fetch('https://fakestoreapi.com/products');
            state.products = await res.json();
            ui.renderProducts(state.products);
        } catch (err) {
            console.error(err);
        }
    }
};

// --- ROUTER ---
const router = {
    navigate: (viewId) => {
        // Hide all sections
        document.querySelectorAll('.view-section').forEach(el => el.classList.add('hidden'));
        // Show target section
        document.getElementById(`view-${viewId}`).classList.remove('hidden');
        
        // Logic when entering specific views
        if (viewId === 'cart') cart.render();
        if (viewId === 'checkout') {
            if (!state.user) {
                router.navigate('login');
                ui.showToast('Please login to checkout');
                return;
            }
            cart.renderCheckout();
        }
        window.scrollTo(0,0);
    },
    filterCat: (cat) => {
        router.navigate('home');
        // Find button and click it programmatically to reuse filter logic
        const btn = Array.from(document.querySelectorAll('.filter-btn'))
            .find(b => b.textContent.toLowerCase().includes(cat.split(' ')[0]));
        if(btn) filterProducts(cat, btn);
    }
};

// --- AUTHENTICATION ---
const auth = {
    toggleAuth: () => {
        if (state.user) auth.logout();
        else router.navigate('login');
    },
    login: (e) => {
        e.preventDefault();
        // Simulate Backend Login
        state.user = { name: "Demo User", email: "user@example.com" };
        localStorage.setItem('luxeUser', JSON.stringify(state.user));
        ui.updateAuthUI();
        router.navigate('home');
        ui.showToast(`Welcome back, ${state.user.name}`);
    },
    logout: () => {
        state.user = null;
        localStorage.removeItem('luxeUser');
        ui.updateAuthUI();
        router.navigate('home');
        ui.showToast('Logged out successfully');
    }
};

// --- CART LOGIC ---
const cart = {
    add: (productId) => {
        const product = state.products.find(p => p.id === productId);
        const existing = state.cart.find(item => item.id === productId);

        if (existing) {
            existing.qty++;
        } else {
            state.cart.push({ ...product, qty: 1 });
        }
        cart.save();
        ui.updateCartCount();
        ui.showToast('Added to cart');
    },
    remove: (productId) => {
        state.cart = state.cart.filter(item => item.id !== productId);
        cart.save();
        cart.render();
        ui.updateCartCount();
    },
    changeQty: (productId, change) => {
        const item = state.cart.find(item => item.id === productId);
        if (item) {
            item.qty += change;
            if (item.qty <= 0) cart.remove(productId);
            else {
                cart.save();
                cart.render();
            }
        }
    },
    save: () => {
        localStorage.setItem('luxeCart', JSON.stringify(state.cart));
    },
    calculate: () => {
        const subtotal = state.cart.reduce((sum, item) => sum + (item.price * item.qty), 0);
        const tax = subtotal * 0.05;
        return { subtotal, tax, total: subtotal + tax };
    },
    render: () => {
        const container = document.getElementById('cart-items-container');
        if (state.cart.length === 0) {
            container.innerHTML = '<div style="padding:20px; text-align:center">Your cart is empty. <a onclick="router.navigate(\'home\')" style="color:var(--accent); cursor:pointer">Go Shop</a></div>';
            document.getElementById('subtotal').innerText = '$0.00';
            document.getElementById('total').innerText = '$0.00';
            return;
        }

        container.innerHTML = state.cart.map(item => `
            <div class="cart-item">
                <img src="${item.image}" class="cart-img" alt="${item.title}">
                <div class="cart-details">
                    <h4 style="font-size:0.9rem; margin-bottom:5px;">${item.title}</h4>
                    <div style="color:var(--primary); font-weight:700">$${item.price}</div>
                    <div class="qty-control">
                        <button class="qty-btn" onclick="cart.changeQty(${item.id}, -1)">-</button>
                        <span style="font-size:0.9rem; width:20px; text-align:center">${item.qty}</span>
                        <button class="qty-btn" onclick="cart.changeQty(${item.id}, 1)">+</button>
                    </div>
                </div>
                <button onclick="cart.remove(${item.id})" style="background:none; border:none; color:var(--danger); cursor:pointer"><i class="fas fa-trash"></i></button>
            </div>
        `).join('');

        const { subtotal, tax, total } = cart.calculate();
        document.getElementById('subtotal').innerText = `$${subtotal.toFixed(2)}`;
        document.getElementById('tax').innerText = `$${tax.toFixed(2)}`;
        document.getElementById('total').innerText = `$${total.toFixed(2)}`;
    },
    renderCheckout: () => {
        const { total } = cart.calculate();
        document.getElementById('checkout-total').innerText = `$${total.toFixed(2)}`;
        document.getElementById('checkout-summary-items').innerHTML = state.cart.map(i => 
            `<div style="display:flex; justify-content:space-between; font-size:0.85rem; margin-bottom:5px;">
                <span style="width:70%; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${i.qty}x ${i.title}</span>
                <span>$${(i.price * i.qty).toFixed(2)}</span>
            </div>`
        ).join('');
    }
};

// --- UI FUNCTIONS ---
const ui = {
    renderProducts: (products) => {
        const grid = document.getElementById('product-grid');
        grid.innerHTML = products.map(product => `
            <div class="product-card">
                <div class="image-container">
                    <img src="${product.image}" alt="${product.title}" class="product-image">
                </div>
                <div class="product-info">
                    <div class="product-category">${product.category}</div>
                    <h3 class="product-title">${product.title}</h3>
                    <div class="price-row">
                        <span class="price">$${product.price}</span>
                        <button class="add-btn" onclick="cart.add(${product.id})">
                            <i class="fas fa-plus"></i>
                        </button>
                    </div>
                </div>
            </div>
        `).join('');
    },
    updateCartCount: () => {
        const count = state.cart.reduce((sum, item) => sum + item.qty, 0);
        document.getElementById('cart-count').innerText = count;
    },
    updateAuthUI: () => {
        const icon = document.getElementById('user-icon');
        if (state.user) {
            icon.classList.remove('fa-user');
            icon.classList.add('fa-sign-out-alt');
            icon.title = "Logout";
        } else {
            icon.classList.remove('fa-sign-out-alt');
            icon.classList.add('fa-user');
            icon.title = "Login";
        }
    },
    showToast: (msg) => {
        const toast = document.getElementById('toast');
        toast.innerText = msg;
        toast.classList.add('show');
        setTimeout(() => toast.classList.remove('show'), 3000);
    }
};

// --- HELPER FUNCTIONS ---
function filterProducts(category, btn) {
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    
    if (category === 'all') ui.renderProducts(state.products);
    else ui.renderProducts(state.products.filter(p => p.category === category));
}

function processPayment(e) {
    e.preventDefault();
    const btn = e.target.querySelector('button[type="submit"]');
    const originalText = btn.innerText;
    
    // Simulate processing
    btn.innerText = "Processing...";
    btn.disabled = true;
    
    setTimeout(() => {
        state.cart = [];
        cart.save();
        ui.updateCartCount();
        alert("Payment Successful! Thank you for your order.");
        router.navigate('home');
        btn.innerText = originalText;
        btn.disabled = false;
    }, 2000);
}

// --- INITIALIZATION ---
window.onload = () => {
    api.fetchProducts();
    ui.updateCartCount();
    ui.updateAuthUI();
};