// MindMend Chat Interface
class ChatInterface {
    constructor() {
        this.chatMessages = document.getElementById('chat-messages');
        this.userInput = document.getElementById('user-input');
        this.sendBtn = document.getElementById('send-btn');
        this.resetBtn = document.getElementById('reset-btn');
        this.resourcesSection = document.getElementById('resources-section');
        this.resourcesContent = document.getElementById('resources-content');
        
        this.initializeEventListeners();
    }
    
    initializeEventListeners() {
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        
        this.userInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        this.resetBtn.addEventListener('click', () => this.resetChat());
        
        this.userInput.addEventListener('input', () => {
            this.userInput.style.height = 'auto';
            this.userInput.style.height = this.userInput.scrollHeight + 'px';
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
                    message: message
                })
            });
            
            const data = await response.json();
            
            this.removeTypingIndicator();
            
            // Display bot response
            this.displayMessage(data.message, 'bot', data.sentiment);
            
            // Show resources IN CHAT if provided
            if (data.show_resources && data.resources) {
                this.displayResourcesInChat(data.resources);
            }
            
            if (data.is_crisis) {
                this.displayEmergencyInChat(data.emergency_resources);
            }
            
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
        const timestamp = new Date().toLocaleTimeString([], { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
        
        let sentimentIcon = '';
        if (sentiment === 'negative') sentimentIcon = '😢';
        else if (sentiment === 'positive') sentimentIcon = '😊';
        else if (sentiment === 'neutral') sentimentIcon = '😐';
        
        messageDiv.innerHTML = `
            <div class="message-avatar">${avatar}</div>
            <div class="message-content">
                <p>${this.escapeHtml(text)} ${sentimentIcon}</p>
                <span class="timestamp">${timestamp}</span>
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
        
        // Display Videos
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
        
        // Display Exercises
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
        
        // Display Articles
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
        
        // Display Professional Resources
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
                <span class="timestamp">${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
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
                <span class="timestamp">${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
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
    
    async resetChat() {
        if (!confirm('Are you sure you want to reset the chat? This will clear all conversation history.')) {
            return;
        }
        
        try {
            await fetch('/api/reset', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            this.chatMessages.innerHTML = `
                <div class="bot-message">
                    <div class="message-avatar">🤖</div>
                    <div class="message-content">
                        <p>Hello! I'm MindMend, your mental health support companion. I'm here to listen, understand, and provide support. How are you feeling today?</p>
                        <span class="timestamp"></span>
                    </div>
                </div>
            `;
            
        } catch (error) {
            console.error('Error resetting chat:', error);
            alert('Failed to reset chat. Please try again.');
        }
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
