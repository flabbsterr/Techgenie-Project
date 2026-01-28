let tickets = JSON.parse(localStorage.getItem('tickets')) || [];
let ticketIdCounter = JSON.parse(localStorage.getItem('ticketIdCounter')) || 1;

function saveTickets() {
    localStorage.setItem('tickets', JSON.stringify(tickets));
    localStorage.setItem('ticketIdCounter', JSON.stringify(ticketIdCounter));
}

function showPage(pageName) {
    const pages = document.querySelectorAll('.page');
    pages.forEach(page => page.style.display = 'none');
    
    const selectedPage = document.getElementById(pageName);
    if (selectedPage) {
        selectedPage.style.display = 'block';
        
        if (pageName === 'my-tickets') {
            loadMyTickets();
        } else if (pageName === 'it-dashboard') {
            loadDashboard();
        }
    }
}

function submitTicket(event) {
    event.preventDefault();
    
    const name = document.getElementById('name').value.trim();
    const issue = document.getElementById('issue').value.trim();
    
    if (name && issue) {
        const newTicket = {
            id: ticketIdCounter,
            name: name,
            issue: issue,
            status: 'Open',
            priority: 'Medium',
            createdAt: new Date().toLocaleString()
        };
        
        tickets.push(newTicket);
        ticketIdCounter++;
        saveTickets();
        
        document.getElementById('log-form').reset();
        alert('Ticket submitted successfully!');
        showPage('my-tickets');
    }
}

function loadMyTickets() {
    const tbody = document.getElementById('my-tickets-list');
    tbody.innerHTML = '';
    
    tickets.forEach(ticket => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${ticket.id}</td>
            <td>${ticket.issue}</td>
            <td><span class="status-${ticket.status.toLowerCase().replace(' ', '-')}">${ticket.status}</span></td>
            <td><span class="priority-${ticket.priority.toLowerCase()}">${ticket.priority}</span></td>
        `;
        tbody.appendChild(row);
    });
    
    if (tickets.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" style="text-align: center;">No tickets found</td></tr>';
    }
}

function loadDashboard() {
    const tbody = document.getElementById('dashboard-list');
    tbody.innerHTML = '';
    
    let openCount = 0;
    
    tickets.forEach(ticket => {
        if (ticket.status === 'Open') {
            openCount++;
        }
        
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${ticket.id}</td>
            <td>${ticket.name}</td>
            <td>${ticket.issue}</td>
            <td>
                <select id="status-${ticket.id}" style="width: 100%; padding: 5px;">
                    <option value="Open" ${ticket.status === 'Open' ? 'selected' : ''}>Open</option>
                    <option value="In Progress" ${ticket.status === 'In Progress' ? 'selected' : ''}>In Progress</option>
                    <option value="Closed" ${ticket.status === 'Closed' ? 'selected' : ''}>Closed</option>
                </select>
            </td>
            <td>
                <select id="priority-${ticket.id}" style="width: 100%; padding: 5px;">
                    <option value="Low" ${ticket.priority === 'Low' ? 'selected' : ''}>Low</option>
                    <option value="Medium" ${ticket.priority === 'Medium' ? 'selected' : ''}>Medium</option>
                    <option value="High" ${ticket.priority === 'High' ? 'selected' : ''}>High</option>
                </select>
            </td>
            <td>
                <button class="small" onclick="updateTicket(${ticket.id})">Save</button>
            </td>
        `;
        tbody.appendChild(row);
    });
    
    document.getElementById('open-count').textContent = openCount;
    
    if (tickets.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align: center;">No tickets found</td></tr>';
    }
}

function updateTicket(ticketId) {
    const status = document.getElementById(`status-${ticketId}`).value;
    const priority = document.getElementById(`priority-${ticketId}`).value;
    
    const ticket = tickets.find(t => t.id === ticketId);
    if (ticket) {
        ticket.status = status;
        ticket.priority = priority;
        saveTickets();
        loadDashboard();
        alert('Ticket updated successfully!');
    }
}

showPage('log-ticket');
