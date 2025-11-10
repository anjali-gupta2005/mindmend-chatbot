class ChatInterface {
    constructor() {
        this.chatMessages = document.getElementById('chat-messages');
        this.userInput = document.getElementById('user-input');
        this.sendBtn = document.getElementById('send-btn');
        this.newChatBtn = document.getElementById('new-chat-btn');
        this.logoutBtn = document.getElementById('logout-btn');
        this.toggleSidebarBtn = document.getElementById('toggle-sidebar-btn');
        this.sidebar = document.getElementById('sidebar');
        this.conversationsList = document.getElementById('conversations-list');
        
        this.currentConversationId = null;
        
        this.initializeEventListeners();
        this.loadConversations();
    }
    
    initializeEventListeners() {
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        
        this.userInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        this.newChatBtn.addEventListener('click', () => this.startNewChat());
        this.logoutBtn.addEventListener('click', () => this.logout());
        this.toggleSidebarBtn.addEventListener('click', () => this.toggleSidebar());
        
        this.userInput.addEventListener('input', () => {
            this.userInput.style.height = 'auto';
            this.userInput.style.height = this.userInput.scrollHeight + 'px';
        });
        const backdrop = document.getElementById('sidebar-backdrop');
                if (backdrop) {
                    backdrop.addEventListener('click', () => this.toggleSidebar());
            }

        document.addEventListener('click', (e) => {
            if (window.innerWidth <= 768) {
                 if (this.sidebar.classList.contains('open') && 
            !this.sidebar.contains(e.target) && 
            !this.toggleSidebarBtn.contains(e.target)) {
            this.toggleSidebar();
            }
                 }
        });

    }
    
    async loadConversations() {
        try {
            const response = await fetch('/api/conversations');
            const data = await response.json();
            
            this.conversationsList.innerHTML = '';
            
            if (data.conversations && data.conversations.length > 0) {
                data.conversations.forEach(conv => {
                    this.addConversationToSidebar(conv);
                });
            } else {
                this.conversationsList.innerHTML = '<div class="no-conversations">No conversations yet. Start chatting!</div>';
            }
        } catch (error) {
            console.error('Error loading conversations:', error);
            this.conversationsList.innerHTML = '<div class="no-conversations">Failed to load conversations</div>';
        }
    }
    
    addConversationToSidebar(conversation) {
        const convDiv = document.createElement('div');
        convDiv.className = 'conversation-item';
        convDiv.dataset.id = conversation.id;
        
        const date = new Date(conversation.updated_at);
        const timeAgo = this.getTimeAgo(date);
        
        convDiv.innerHTML = `
            <div class="conversation-title">${conversation.title}</div>
            <div class="conversation-meta">
                <span class="conversation-preview">${conversation.preview || 'New conversation'}</span>
                <span class="conversation-time">${timeAgo}</span>
            </div>
            <button class="btn-delete-conversation" data-id="${conversation.id}" title="Delete conversation">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="3 6 5 6 21 6"></polyline>
                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                </svg>
            </button>
        `;
        
        convDiv.addEventListener('click', (e) => {
            if (!e.target.closest('.btn-delete-conversation')) {
                this.loadConversation(conversation.id);
            }
        });
        
        const deleteBtn = convDiv.querySelector('.btn-delete-conversation');
        deleteBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            this.deleteConversation(conversation.id);
        });
        
        this.conversationsList.appendChild(convDiv);
    }
    
   async loadConversation(conversationId) {
    try {
        const response = await fetch(`/api/conversations/${conversationId}`);
        const data = await response.json();
        
        this.currentConversationId = conversationId;
        this.chatMessages.innerHTML = '';
        
        if (data.messages && data.messages.length > 0) {
            data.messages.forEach(msg => {
                this.displayMessage(msg.content, msg.sender, msg.sentiment);
            });
        }
        
        document.querySelectorAll('.conversation-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`[data-id="${conversationId}"]`)?.classList.add('active');
        
        if (window.innerWidth <= 768) {
            this.toggleSidebar();
        }
        
    } catch (error) {
        console.error('Error loading conversation:', error);
    }
}

    
    async deleteConversation(conversationId) {
        if (!confirm('Delete this conversation? This action cannot be undone.')) {
            return;
        }
        
        try {
            const response = await fetch(`/api/conversations/${conversationId}`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                document.querySelector(`[data-id="${conversationId}"]`)?.remove();
                
                if (this.currentConversationId === conversationId) {
                    this.startNewChat();
                }
                
                this.loadConversations();
            }
        } catch (error) {
            console.error('Error deleting conversation:', error);
            alert('Failed to delete conversation');
        }
    }
    
    startNewChat() {
        this.currentConversationId = null;
        this.chatMessages.innerHTML = `
            <div class="bot-message">
                <div class="message-avatar">🤖</div>
                <div class="message-content">
                    <p>Hello! I'm MindMend, your mental health support companion. I'm here to listen, understand, and provide support. How are you feeling today?</p>
                </div>
            </div>
        `;
        
        document.querySelectorAll('.conversation-item').forEach(item => {
            item.classList.remove('active');
        });
    }
    
    async sendMessage() {
        const message = this.userInput.value.trim();
        
        if (!message) return;
        
        this.displayMessage(message, 'user');
        this.userInput.value = '';
        this.userInput.style.height = 'auto';
        this.sendBtn.disabled = true;
        this.showTypingIndicator();
        
        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: message,
                    conversation_id: this.currentConversationId
                })
            });
            
            const data = await response.json();
            
            this.removeTypingIndicator();
            
            if (data.conversation_id) {
                this.currentConversationId = data.conversation_id;
            }
            
            this.displayMessage(data.message, 'bot', data.sentiment);
            
            if (data.show_resources && data.resources) {
                this.displayResourcesInChat(data.resources);
            }
            
            if (data.is_crisis) {
                this.displayEmergencyInChat(data.emergency_resources);
            }
            
            this.loadConversations();
            
        } catch (error) {
            console.error('Error:', error);
            this.removeTypingIndicator();
            this.displayMessage(
                'Sorry, I encountered an error. Please try again.',
                'bot'
            );
        } finally {
            this.sendBtn.disabled = false;
            this.userInput.focus();
        }
    }
    
    displayMessage(text, sender, sentiment = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `${sender}-message`;
        
        const avatar = sender === 'bot' ? '🤖' : '👤';
        
        let sentimentIcon = '';
        if (sentiment === 'negative') sentimentIcon = '😢';
        else if (sentiment === 'positive') sentimentIcon = '😊';
        else if (sentiment === 'neutral') sentimentIcon = '😐';
        
        messageDiv.innerHTML = `
            <div class="message-avatar">${avatar}</div>
            <div class="message-content">
                <p>${this.escapeHtml(text)} ${sentimentIcon}</p>
            </div>
        `;
        
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    displayResourcesInChat(resources) {
        const resourceDiv = document.createElement('div');
        resourceDiv.className = 'bot-message';
        
        let resourcesHTML = `
            <div class="message-avatar">🤖</div>
            <div class="message-content resource-message">
                <h3 style="color: #667eea; margin-bottom: 15px;">📚 Helpful Resources for You</h3>
        `;
        
        if (resources.videos && resources.videos.length > 0) {
            resourcesHTML += '<h4 style="color: #555; font-size: 1rem; margin: 15px 0 10px 0;">🎥 Helpful Videos</h4>';
            resources.videos.forEach(video => {
                resourcesHTML += `
                    <div style="background: #f0f4ff; padding: 12px; margin: 8px 0; border-radius: 8px; border-left: 3px solid #667eea;">
                        <a href="${video.url}" target="_blank" style="color: #667eea; text-decoration: none; font-weight: 600; display: block; margin-bottom: 5px;">
                            ${video.title}
                        </a>
                        <p style="margin: 5px 0; font-size: 0.85rem; color: #666;">${video.description}</p>
                        <span style="font-size: 0.8rem; color: #999;">${video.duration} • ${video.type}</span>
                    </div>
                `;
            });
        }
        
        if (resources.exercises && resources.exercises.length > 0) {
            resourcesHTML += '<h4 style="color: #555; font-size: 1rem; margin: 15px 0 10px 0;">💪 Exercises to Try</h4>';
            resources.exercises.forEach(exercise => {
                resourcesHTML += `
                    <div style="background: #fff8e1; padding: 12px; margin: 8px 0; border-radius: 8px; border-left: 3px solid #ffa726;">
                        <strong style="color: #333; display: block; margin-bottom: 5px;">${exercise.name}</strong>
                        <p style="margin: 5px 0; font-size: 0.9rem; color: #555;">${exercise.description}</p>
                        <span style="font-size: 0.8rem; color: #999;">${exercise.duration} • ${exercise.benefit}</span>
                    </div>
                `;
            });
        }
        
        if (resources.articles && resources.articles.length > 0) {
            resourcesHTML += '<h4 style="color: #555; font-size: 1rem; margin: 15px 0 10px 0;">📖 Helpful Articles</h4>';
            resources.articles.forEach(article => {
                resourcesHTML += `
                    <div style="background: #e8f5e9; padding: 12px; margin: 8px 0; border-radius: 8px; border-left: 3px solid #66bb6a;">
                        <a href="${article.url}" target="_blank" style="color: #2e7d32; text-decoration: none; font-weight: 600; display: block; margin-bottom: 5px;">
                            ${article.title}
                        </a>
                        <p style="margin: 5px 0; font-size: 0.85rem; color: #555;">${article.summary}</p>
                    </div>
                `;
            });
        }
        
        if (resources.professional_resources && resources.professional_resources.length > 0) {
            resourcesHTML += '<h4 style="color: #555; font-size: 1rem; margin: 15px 0 10px 0;">🏥 Professional Support</h4>';
            resources.professional_resources.forEach(resource => {
                resourcesHTML += `
                    <div style="background: #fce4ec; padding: 12px; margin: 8px 0; border-radius: 8px; border-left: 3px solid #ec407a;">
                        <strong style="color: #333; display: block; margin-bottom: 5px;">${resource.name}</strong>
                        <p style="margin: 5px 0; font-size: 0.85rem; color: #555;">${resource.description}</p>
                        ${resource.url ? `<a href="${resource.url}" target="_blank" style="color: #c2185b; font-size: 0.85rem;">Visit Website</a>` : ''}
                        ${resource.number ? `<p style="margin: 5px 0; font-size: 0.85rem; color: #666;">📞 ${resource.number}</p>` : ''}
                    </div>
                `;
            });
        }
        
        resourcesHTML += `
            </div>
        `;
        
        resourceDiv.innerHTML = resourcesHTML;
        this.chatMessages.appendChild(resourceDiv);
        this.scrollToBottom();
    }
    
    displayEmergencyInChat(resources) {
        const emergencyDiv = document.createElement('div');
        emergencyDiv.className = 'bot-message';
        
        let emergencyHTML = `
            <div class="message-avatar">🤖</div>
            <div class="message-content" style="background: #ffebee; border: 2px solid #f44336;">
                <h3 style="color: #c62828; margin-bottom: 10px;">⚠️ Emergency Resources - Please Reach Out Now</h3>
        `;
        
        resources.forEach(resource => {
            emergencyHTML += `
                <div style="background: white; padding: 10px; margin: 8px 0; border-radius: 5px;">
                    <strong style="color: #d32f2f;">${resource.service}</strong>
                    ${resource.number ? `<p style="margin: 5px 0; color: #c62828; font-weight: 600;">📞 ${resource.number}</p>` : ''}
                    ${resource.instruction ? `<p style="margin: 5px 0; color: #555;">${resource.instruction}</p>` : ''}
                </div>
            `;
        });
        
        emergencyHTML += `
            </div>
        `;
        
        emergencyDiv.innerHTML = emergencyHTML;
        this.chatMessages.appendChild(emergencyDiv);
        this.scrollToBottom();
    }
    
    showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'bot-message typing-message';
        typingDiv.innerHTML = `
            <div class="message-avatar">🤖</div>
            <div class="message-content">
                <div class="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        `;
        this.chatMessages.appendChild(typingDiv);
        this.scrollToBottom();
    }
    
    removeTypingIndicator() {
        const typingMessage = this.chatMessages.querySelector('.typing-message');
        if (typingMessage) {
            typingMessage.remove();
        }
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
    
   toggleSidebar() {
    this.sidebar.classList.toggle('open');
    const backdrop = document.getElementById('sidebar-backdrop');
    if (backdrop) {
        backdrop.classList.toggle('active');
    }
}

    
    getTimeAgo(date) {
        const now = new Date();
        const messageDate = new Date(date);
        const seconds = Math.floor((now - messageDate) / 1000);
        
        if (seconds < 60) return 'Just now';
        if (seconds < 3600) return Math.floor(seconds / 60) + 'm ago';
        if (seconds < 86400) return Math.floor(seconds / 3600) + 'h ago';
        if (seconds < 604800) return Math.floor(seconds / 86400) + 'd ago';
        
        return messageDate.toLocaleDateString('en-IN', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric'
        });
    }
    
    scrollToBottom() {
        setTimeout(() => {
            this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        }, 100);
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new ChatInterface();
});
