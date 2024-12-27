let currentDialogue = null;
let currentPersonas = null;

async function startDialogue() {
    const theme = document.getElementById('theme-input').value;
    if (!theme) {
        alert('テーマを入力してください');
        return;
    }

    try {
        const response = await fetch('/start_dialogue', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ theme })
        });

        const data = await response.json();
        if (response.ok) {
            currentDialogue = data.dialogue_id;
            currentPersonas = data.personas;
            
            // Display personas
            displayPersonas(data.personas);
            
            // Clear chat and start conversation
            document.getElementById('chat-messages').innerHTML = '';
            await generateNextMessage('persona_a');
        } else {
            alert('エラーが発生しました: ' + data.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('エラーが発生しました');
    }
}

function displayPersonas(personas) {
    const personaContainer = document.getElementById('persona-container');
    personaContainer.innerHTML = `
        <div class="row">
            <div class="col-md-6">
                <div class="persona-card">
                    <i class="fas ${personas.persona_a.icon} fa-2x mb-2"></i>
                    <h3>${personas.persona_a.name}</h3>
                    <p>${personas.persona_a.description}</p>
                </div>
            </div>
            <div class="col-md-6">
                <div class="persona-card">
                    <i class="fas ${personas.persona_b.icon} fa-2x mb-2"></i>
                    <h3>${personas.persona_b.name}</h3>
                    <p>${personas.persona_b.description}</p>
                </div>
            </div>
        </div>
    `;
}

async function generateNextMessage(speaker) {
    if (!currentDialogue) return;

    const chatMessages = document.getElementById('chat-messages');
    const messages = Array.from(chatMessages.children).map(msg => ({
        speaker: msg.dataset.speaker,
        content: msg.querySelector('.message-content').textContent
    }));

    try {
        const response = await fetch('/generate_message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                dialogue_id: currentDialogue,
                last_messages: messages,
                current_speaker: speaker
            })
        });

        const data = await response.json();
        if (response.ok) {
            appendMessage(data.message, speaker);
            
            // Generate next message after a short delay
            setTimeout(() => {
                generateNextMessage(speaker === 'persona_a' ? 'persona_b' : 'persona_a');
            }, 2000);
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

function appendMessage(content, speaker) {
    const chatMessages = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message message-${speaker}`;
    messageDiv.dataset.speaker = speaker;

    const persona = speaker === 'persona_a' ? currentPersonas.persona_a : currentPersonas.persona_b;
    
    messageDiv.innerHTML = `
        <div class="d-flex align-items-center mb-1">
            <div class="persona-icon bg-${speaker === 'persona_a' ? 'primary' : 'secondary'}">
                <i class="fas ${persona.icon}"></i>
            </div>
            <strong>${persona.name}</strong>
            <small class="timestamp ms-2">${new Date().toLocaleTimeString()}</small>
        </div>
        <div class="message-content">${content}</div>
    `;

    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}
