// Admin Dashboard Script
class AdminDashboard {
    constructor() {
        this.initializeElements();
        this.initializeEventListeners();
        this.loadDashboard();
    }

    initializeElements() {
        this.tabBtns = document.querySelectorAll('.tab-btn');
        this.tabContents = document.querySelectorAll('.tab-content');
        this.logoutBtn = document.getElementById('logout-btn');
        this.usersTableBody = document.getElementById('users-table-body');
        this.conversationsTableBody = document.getElementById('conversations-table-body');
        this.userSelect = document.getElementById('user-select');
        this.userDetailContent = document.getElementById('user-detail-content');
        this.conversationModal = document.getElementById('conversation-modal');
        this.closeModalBtn = document.getElementById('close-modal');
        this.modalBody = document.getElementById('modal-body');
    }

    initializeEventListeners() {
        // Tab switching
        this.tabBtns.forEach(btn => {
            btn.addEventListener('click', () => this.switchTab(btn.dataset.tab));
        });

        // Logout
        this.logoutBtn.addEventListener('click', () => this.logout());

        // User select
        this.userSelect.addEventListener('change', (e) => {
            this.loadUserDetails(e.target.value);
        });

        // Close modal
        this.closeModalBtn.addEventListener('click', () => {
            this.conversationModal.classList.remove('active');
        });

        // Click outside modal to close
        this.conversationModal.addEventListener('click', (e) => {
            if (e.target === this.conversationModal) {
                this.conversationModal.classList.remove('active');
            }
        });

        // Search functionality
        document.getElementById('search-users').addEventListener('input', (e) => {
            this.filterTable('users-table-body', e.target.value);
        });

        document.getElementById('search-conversations').addEventListener('input', (e) => {
            this.filterTable('conversations-table-body', e.target.value);
        });
    }

    switchTab(tabName) {
        // Update tab buttons
        this.tabBtns.forEach(btn => {
            btn.classList.toggle('active', btn.dataset.tab === tabName);
        });

        // Update tab contents
        this.tabContents.forEach(content => {
            content.classList.toggle('active', content.id === `${tabName}-tab`);
        });
    }

    async loadDashboard() {
        await this.loadStats();
        await this.loadUsers();
        await this.loadConversations();
    }

    async loadStats() {
        try {
            const response = await fetch('/api/admin/stats');
            const data = await response.json();

            document.getElementById('total-users').textContent = data.stats.total_users;
            document.getElementById('total-conversations').textContent = data.stats.total_conversations;
            document.getElementById('total-messages').textContent = data.stats.total_messages;
        } catch (error) {
            console.error('Error loading stats:', error);
        }
    }

    async loadUsers() {
        try {
            const response = await fetch('/api/admin/users');
            const data = await response.json();

            this.usersTableBody.innerHTML = '';

            if (data.users && data.users.length > 0) {
                // Populate user select dropdown
                this.userSelect.innerHTML = '<option value="">Select a user...</option>';
                
                data.users.forEach(user => {
                    // Add to table
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${user.id}</td>
                        <td><strong>${user.username}</strong></td>
                        <td>${user.email}</td>
                        <td><span class="badge ${user.is_admin ? 'badge-admin' : 'badge-user'}">${user.is_admin ? 'Admin' : 'User'}</span></td>
                        <td>${this.formatDate(user.created_at)}</td>
                        <td>${user.last_login ? this.formatDate(user.last_login) : 'Never'}</td>
                        <td>
                            <button class="btn-view" onclick="adminDashboard.loadUserDetails(${user.id})">View History</button>
                        </td>
                    `;
                    this.usersTableBody.appendChild(row);

                    // Add to select dropdown
                    const option = document.createElement('option');
                    option.value = user.id;
                    option.textContent = `${user.username} (${user.email})`;
                    this.userSelect.appendChild(option);
                });
            } else {
                this.usersTableBody.innerHTML = '<tr><td colspan="7" class="no-data">No users found</td></tr>';
            }
        } catch (error) {
            console.error('Error loading users:', error);
            this.usersTableBody.innerHTML = '<tr><td colspan="7" class="no-data">Error loading users</td></tr>';
        }
    }

    async loadConversations() {
        try {
            const response = await fetch('/api/admin/conversations');
            const data = await response.json();

            this.conversationsTableBody.innerHTML = '';

            if (data.conversations && data.conversations.length > 0) {
                data.conversations.forEach(conv => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${conv.id}</td>
                        <td><strong>${conv.username}</strong></td>
                        <td>${conv.user_email}</td>
                        <td>${conv.title}</td>
                        <td>${conv.message_count}</td>
                        <td>${this.formatDate(conv.created_at)}</td>
                        <td>${this.formatDate(conv.updated_at)}</td>
                        <td>
                            <button class="btn-view" onclick="adminDashboard.viewConversation(${conv.id})">View Chat</button>
                        </td>
                    `;
                    this.conversationsTableBody.appendChild(row);
                });
            } else {
                this.conversationsTableBody.innerHTML = '<tr><td colspan="8" class="no-data">No conversations found</td></tr>';
            }
        } catch (error) {
            console.error('Error loading conversations:', error);
            this.conversationsTableBody.innerHTML = '<tr><td colspan="8" class="no-data">Error loading conversations</td></tr>';
        }
    }

    async loadUserDetails(userId) {
        if (!userId) {
            this.userDetailContent.innerHTML = '<p class="no-data">Select a user to view their conversations</p>';
            return;
        }

        // Switch to user details tab
        this.switchTab('user-details');

        try {
            // Load user info
            const usersResponse = await fetch('/api/admin/users');
            const usersData = await usersResponse.json();
            const user = usersData.users.find(u => u.id == userId);

            // Load conversations
            const convsResponse = await fetch('/api/admin/conversations');
            const convsData = await convsResponse.json();
            const userConversations = convsData.conversations.filter(c => c.username === user.username);

            // Display user info
            let html = `
                <div class="user-info-card">
                    <h3>📋 User Information</h3>
                    <div class="user-info-grid">
                        <div class="info-item">
                            <div class="info-label">Username</div>
                            <div class="info-value">${user.username}</div>
                        </div>
                        <div class="info-item">
                            <div class="info-label">Email</div>
                            <div class="info-value">${user.email}</div>
                        </div>
                        <div class="info-item">
                            <div class="info-label">Registered</div>
                            <div class="info-value">${this.formatDate(user.created_at)}</div>
                        </div>
                        <div class="info-item">
                            <div class="info-label">Last Login</div>
                            <div class="info-value">${user.last_login ? this.formatDate(user.last_login) : 'Never'}</div>
                        </div>
                        <div class="info-item">
                            <div class="info-label">Total Conversations</div>
                            <div class="info-value">${userConversations.length}</div>
                        </div>
                    </div>
                </div>

                <h3 style="margin: 25px 0 15px 0;">💬 Conversation History</h3>
                <div class="conversations-grid">
            `;

            if (userConversations.length > 0) {
                userConversations.forEach(conv => {
                    html += `
                        <div class="conversation-card">
                            <h4>${conv.title}</h4>
                            <div class="conversation-meta">
                                <span>📅 ${this.formatDate(conv.created_at)}</span>
                                <span>💬 ${conv.message_count} messages</span>
                            </div>
                            <div class="conversation-preview">${conv.preview || 'No preview available'}</div>
                            <button class="btn-view" onclick="adminDashboard.viewConversation(${conv.id})">View Full Chat</button>
                        </div>
                    `;
                });
            } else {
                html += '<p class="no-data">No conversations yet</p>';
            }

            html += '</div>';

            this.userDetailContent.innerHTML = html;
        } catch (error) {
            console.error('Error loading user details:', error);
            this.userDetailContent.innerHTML = '<p class="no-data">Error loading user details</p>';
        }
    }

    async viewConversation(conversationId) {
        try {
            const response = await fetch(`/api/conversations/${conversationId}`);
            const data = await response.json();

            this.modalBody.innerHTML = '';

            if (data.messages && data.messages.length > 0) {
                let html = `<h3 style="margin-bottom: 20px; color: #667eea;">${data.conversation.title}</h3>`;
                
                data.messages.forEach(msg => {
                    html += `
                        <div class="message-item message-${msg.sender}">
                            <div class="message-header">
                                <span class="message-sender">${msg.sender === 'user' ? '👤 User' : '🤖 Bot'}</span>
                                <span class="message-time">${this.formatDate(msg.timestamp)}</span>
                            </div>
                            <div class="message-content">${this.escapeHtml(msg.content)}</div>
                            ${msg.sentiment ? `<div style="margin-top: 8px; font-size: 0.85rem; color: #999;">Sentiment: ${msg.sentiment}</div>` : ''}
                        </div>
                    `;
                });

                this.modalBody.innerHTML = html;
            } else {
                this.modalBody.innerHTML = '<p class="no-data">No messages in this conversation</p>';
            }

            this.conversationModal.classList.add('active');
        } catch (error) {
            console.error('Error viewing conversation:', error);
            alert('Failed to load conversation');
        }
    }

    filterTable(tableBodyId, searchTerm) {
        const tableBody = document.getElementById(tableBodyId);
        const rows = tableBody.querySelectorAll('tr');
        
        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            row.style.display = text.includes(searchTerm.toLowerCase()) ? '' : 'none';
        });
    }

   
    formatDate(dateString) {
        const date = new Date(dateString);
        
        return date.toLocaleString('en-IN', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            hour12: true
        });
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    async logout() {
        if (!confirm('Are you sure you want to logout?')) {
            return;
        }

        try {
            await fetch('/api/auth/logout', { method: 'POST' });
            window.location.href = '/login';
        } catch (error) {
            console.error('Logout error:', error);
            window.location.href = '/login';
        }
    }
}

// Initialize dashboard
let adminDashboard;
document.addEventListener('DOMContentLoaded', () => {
    adminDashboard = new AdminDashboard();
});
