// ----------------------------
// SHOW TABS
// ----------------------------

function showTab(tabId) {

    // Hide all sections
    const sections = document.querySelectorAll('.section');

    sections.forEach(section => {
        section.style.display = 'none';
    });

    // Show selected section
    document.getElementById('tab-' + tabId).style.display = 'block';
}

// ----------------------------
// STYLISH TOAST NOTIFICATION
// ----------------------------

function showToast(message, type = 'info', duration = 3500) {

    let container = document.getElementById('toast-container');

    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        document.body.appendChild(container);
    }

    const icons = { success: '✓', error: '✕', info: 'i', warn: '!' };

    const toast = document.createElement('div');
    toast.className = 'toast ' + type;

    // icon + message + close button + progress bar
    const icon = document.createElement('div');
    icon.className = 'icon';
    icon.textContent = icons[type] || 'i';

    const msg = document.createElement('div');
    msg.className = 'msg';
    msg.textContent = message;            // textContent = safe from injection

    const closeBtn = document.createElement('button');
    closeBtn.className = 'close';
    closeBtn.setAttribute('aria-label', 'close');
    closeBtn.innerHTML = '&times;';

    const bar = document.createElement('div');
    bar.className = 'bar';
    bar.style.animationDuration = duration + 'ms';

    toast.appendChild(icon);
    toast.appendChild(msg);
    toast.appendChild(closeBtn);
    toast.appendChild(bar);

    container.appendChild(toast);

    const remove = () => {
        toast.classList.add('hide');
        toast.addEventListener('animationend', () => toast.remove(), { once: true });
    };

    closeBtn.addEventListener('click', remove);
    setTimeout(remove, duration);
}

// ----------------------------
// DEFAULT TAB
// ----------------------------

window.onload = function () {

    showTab('dashboard');

    loadRooms();

    loadCustomers();

    loadReservations();

    loadPayments();

    updateDashboard();
};

// ----------------------------
// UPDATE CLOCK
// ----------------------------

function updateClock() {

    const clock = document.getElementById('clock');

    const now = new Date();

    clock.innerHTML = now.toLocaleString();
}

setInterval(updateClock, 1000);

// ----------------------------
// API URL
// ----------------------------

const API = "";
// --------------------------------------
// SUBMIT RESERVATION
// --------------------------------------

async function submitReservation() {

    try {

        // ----------------------------
        // GET FORM VALUES
        // ----------------------------

        const customerName =
            document.getElementById('r-name').value;

        const phone =
            document.getElementById('r-phone').value;

        const email =
            document.getElementById('r-email').value;

        const address =
            document.getElementById('r-address').value;

        const roomId =
            document.getElementById('r-room').value;

        const checkin =
            document.getElementById('r-checkin').value;

        const checkout =
            document.getElementById('r-checkout').value;

        // ----------------------------
        // VALIDATION
        // ----------------------------

        if (
            !customerName ||
            !phone ||
            !roomId ||
            !checkin ||
            !checkout
        ) {

            showToast("Please fill all required fields", "warn");

            return;
        }

        // ----------------------------
        // ADD CUSTOMER
        // ----------------------------

        const customerResponse = await fetch(
            API + '/add_customer',
            {
                method: 'POST',

                headers: {
                    'Content-Type': 'application/json'
                },

                body: JSON.stringify({

                    customer_name: customerName,

                    phone: phone,

                    email: email,

                    address: address
                })
            }
        );

        const customerData =
            await customerResponse.json();

        // ----------------------------
        // GET CUSTOMER ID
        // ----------------------------

        const customerId =
            customerData.customer_id;

        // ----------------------------
        // ADD RESERVATION
        // ----------------------------

        const reservationResponse = await fetch(
            API + '/add_reservation',
            {
                method: 'POST',

                headers: {
                    'Content-Type': 'application/json'
                },

                body: JSON.stringify({

                    customer_id: customerId,

                    room_id: parseInt(roomId),

                    check_in_date: checkin,

                    check_out_date: checkout
                })
            }
        );

        const reservationData =
            await reservationResponse.json();

        // ----------------------------
        // SUCCESS
        // ----------------------------

        if (reservationResponse.ok) {

            showToast("Reservation Added Successfully", "success");

            loadRooms();

            loadReservations();

            updateDashboard();

        } else {

            showToast(reservationData.error, "error");
        }

    } catch (error) {

        console.log(error);

        showToast("Reservation Failed", "error");
    }
}

// ----------------------------
// LOAD ROOMS
// ----------------------------

async function loadRooms() {

    try {

        const response = await fetch(API + '/rooms');

        const rooms = await response.json();

        const container =
            document.getElementById('room-map-container');

        const roomSelect =
            document.getElementById('r-room');

        const checkoutSelect =
            document.getElementById('co-room');

        container.innerHTML = '';

        roomSelect.innerHTML =
            '<option value="">-- Select Room --</option>';

        checkoutSelect.innerHTML =
            '<option value="">-- Select Room --</option>';

        rooms.forEach(room => {

            let color = '#81c784';

            if (room.status === 'Booked')
                color = '#e57373';

            if (room.status === 'Maintenance')
                color = '#ffb74d';

            container.innerHTML += `
                <div style="
                    background:${color};
                    padding:15px;
                    margin:10px;
                    border-radius:10px;
                    display:inline-block;
                    width:180px;
                    color:white;
                ">
                    <h3>Room ${room.room_number}</h3>
                    <p>${room.room_type}</p>
                    <p>₹${room.price}</p>
                    <p>${room.status}</p>
                </div>
            `;

            if (room.status === 'Available') {

                roomSelect.innerHTML += `
                    <option value="${room.room_id}">
                        Room ${room.room_number}
                    </option>
                `;
            }

            if (room.status === 'Booked') {

                checkoutSelect.innerHTML += `
                    <option value="${room.room_id}">
                        Room ${room.room_number}
                    </option>
                `;
            }
        });

    } catch (error) {

        console.log(error);
    }
}

// ----------------------------
// LOAD CUSTOMERS
// ----------------------------

async function loadCustomers() {

    try {

        const response =
            await fetch(API + '/customers');

        const customers =
            await response.json();

        const tbody =
            document.getElementById('cust-tbody');

        tbody.innerHTML = '';

        customers.forEach(customer => {

            tbody.innerHTML += `
                <tr>
                    <td>${customer.customer_id}</td>
                    <td>${customer.customer_name}</td>
                    <td>${customer.phone}</td>
                    <td>${customer.email}</td>
                    <td>${customer.address}</td>
                </tr>
            `;
        });

    } catch (error) {

        console.log(error);
    }
}

// ----------------------------
// WORK OUT A RESERVATION'S STATUS
// ----------------------------
function getReservationStatus(r) {

    // If the backend already sends a status, use it
    if (r.status) return r.status;

    // Otherwise calculate it from the dates
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    const checkIn  = new Date(r.check_in_date);
    const checkOut = new Date(r.check_out_date);

    if (today < checkIn)  return 'Upcoming';
    if (today > checkOut) return 'Completed';
    return 'Active';
}

// ----------------------------
// LOAD RESERVATIONS
// ----------------------------
async function loadReservations() {

    try {

        const response = await fetch(API + '/reservations');
        const reservations = await response.json();

        const tbody = document.getElementById('res-tbody');
        tbody.innerHTML = '';

        // map each status to a CSS badge class
        const statusClass = {
            'Upcoming':  'badge-upcoming',
            'Active':    'badge-active',
            'Completed': 'badge-completed',
            'Cancelled': 'badge-cancelled',
            'Confirmed': 'badge-active'
        };

        reservations.forEach(r => {

            const status = getReservationStatus(r);
            const cls = statusClass[status] || 'badge-upcoming';

            tbody.innerHTML += `
                <tr>
                    <td>${r.reservation_id}</td>
                    <td>${r.customer_id}</td>
                    <td>${r.room_id}</td>
                    <td>${r.check_in_date}</td>
                    <td>${r.check_out_date}</td>
                    <td><span class="badge ${cls}">${status}</span></td>
                </tr>
            `;
        });

    } catch (error) {
        console.log(error);
    }
}
// ----------------------------
// LOAD PAYMENTS
// ----------------------------

async function loadPayments() {

    try {

        const response =
            await fetch(API + '/payments');

        const payments =
            await response.json();

        const tbody =
            document.getElementById('pay-tbody');

        tbody.innerHTML = '';

        payments.forEach(payment => {

            tbody.innerHTML += `
                <tr>
                    <td>${payment.payment_id}</td>
                    <td>${payment.reservation_id}</td>
                    <td>${payment.amount}</td>
                    <td>${payment.payment_method}</td>
                </tr>
            `;
        });

    } catch (error) {

        console.log(error);
    }
}

// ----------------------------
// DASHBOARD
// ----------------------------

async function updateDashboard() {

    const response =
        await fetch(API + '/rooms');

    const rooms =
        await response.json();

    document.getElementById('s-total').innerHTML =
        rooms.length;

    document.getElementById('s-avail').innerHTML =
        rooms.filter(r => r.status === 'Available').length;

    document.getElementById('s-booked').innerHTML =
        rooms.filter(r => r.status === 'Booked').length;

    document.getElementById('s-maint').innerHTML =
        rooms.filter(r => r.status === 'Maintenance').length;
}
// ----------------------------
// PROCESS CHECKOUT
// ----------------------------

async function processCheckout() {

    try {

        // ----------------------------
        // GET ROOM ID
        // ----------------------------

        const roomId =
            document.getElementById('co-room').value;

        if (!roomId) {

            showToast("Please select a room", "warn");

            return;
        }

        // ----------------------------
        // API CALL
        // ----------------------------

        const response = await fetch(
            API + '/checkout',
            {
                method: 'POST',

                headers: {
                    'Content-Type': 'application/json'
                },

                body: JSON.stringify({
                    room_id: parseInt(roomId)
                })
            }
        );

        const result = await response.json();

        // ----------------------------
        // SUCCESS
        // ----------------------------

        if (response.ok) {

            showToast(result.message, "success");

            // reload data
            loadRooms();

            loadReservations();

            updateDashboard();

        } else {

            showToast(result.error, "error");
        }

    } catch (error) {

        console.log(error);

        showToast("Checkout Failed", "error");
    }
}

// ----------------------------
// ADD PAYMENT
// ----------------------------

async function addPayment() {

    try {

        // ----------------------------
        // GET VALUES
        // ----------------------------

        const reservationId =
            document.getElementById('p-resid').value;

        const amount =
            document.getElementById('p-amount').value;

        const method =
            document.getElementById('p-method').value;

        // ----------------------------
        // VALIDATION
        // ----------------------------

        if (!reservationId || !amount) {

            showToast("Please fill all fields", "warn");

            return;
        }

        // ----------------------------
        // API CALL
        // ----------------------------

        const response = await fetch(
            API + '/add_payment',
            {
                method: 'POST',

                headers: {
                    'Content-Type': 'application/json'
                },

                body: JSON.stringify({

                    reservation_id: parseInt(reservationId),

                    amount: parseFloat(amount),

                    payment_method: method
                })
            }
        );

        const result = await response.json();

        // ----------------------------
        // SUCCESS
        // ----------------------------

        if (response.ok) {

            showToast(result.message, "success");

            loadPayments();

        } else {

            showToast(result.error, "error");
        }

    } catch (error) {

        console.log(error);

        showToast("Payment Failed", "error");
    }
}