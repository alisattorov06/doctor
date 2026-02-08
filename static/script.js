let currentTypingInstance = null
let isLoading = false
let abortController = null

const chatContainer = document.getElementById('chat-messages')
const input = document.getElementById('message-input')
const sendButton = document.getElementById('send-button')

function setSendLoading(active) {
    isLoading = active

    if (active) {
        sendButton.innerHTML = '<i class="fas fa-stop"></i>'
        sendButton.classList.remove('btn-primary')
        sendButton.classList.add('btn-danger')
        sendButton.disabled = false
    } else {
        sendButton.innerHTML = '<i class="fas fa-paper-plane me-2"></i>'
        sendButton.classList.remove('btn-danger')
        sendButton.classList.add('btn-primary')
        sendButton.disabled = false
    }
}

function addMessage(text, isUser = false) {
    const messageDiv = document.createElement('div')
    messageDiv.className = `mb-3 ${isUser ? 'text-end' : 'text-start'}`

    const bubble = document.createElement('div')
    bubble.className = `d-inline-block p-3 rounded-4 shadow-sm ${isUser ? 'user-message text-white' : 'ai-message text-white'}`
    bubble.style.maxWidth = '80%'
    bubble.style.wordBreak = 'break-word'

    bubble.innerHTML = `
        <div class="fw-bold">
            <i class="fas ${isUser ? 'fa-user' : 'fa-robot'} me-2"></i>
            ${isUser ? 'Siz' : 'Doctor AI'}
        </div>
        ${text}
    `

    messageDiv.appendChild(bubble)
    chatContainer.appendChild(messageDiv)
    chatContainer.scrollTop = chatContainer.scrollHeight
}

function addTypingIndicator() {
    const indicator = document.createElement('div')
    indicator.id = 'typing-indicator'
    indicator.className = 'mb-3 text-start'

    indicator.innerHTML = `
        <div class="d-inline-block p-3 rounded-4 shadow-sm bg-light" style="max-width:80%">
            <div class="fw-bold text-primary">
                <i class="fas fa-robot me-2"></i>Doctor AI
            </div>
            <div class="typing-dots d-flex mt-2">
                <span class="bg-primary rounded-circle me-1" style="width:8px;height:8px"></span>
                <span class="bg-primary rounded-circle me-1" style="width:8px;height:8px"></span>
                <span class="bg-primary rounded-circle" style="width:8px;height:8px"></span>
            </div>
        </div>
    `

    chatContainer.appendChild(indicator)
    chatContainer.scrollTop = chatContainer.scrollHeight
}

function removeTypingIndicator() {
    document.getElementById('typing-indicator')?.remove()
}

function renderMarkdown(text) {
    return DOMPurify.sanitize(marked.parse(text))
}

function typeMessage(element, text, onDone) {
    currentTypingInstance?.destroy()

    currentTypingInstance = new Typed(element, {
        strings: [text],
        typeSpeed: 20,
        showCursor: false,
        onComplete: () => {
            currentTypingInstance = null
            onDone && onDone()
        }
    })
}

async function sendMessage() {
    if (isLoading && abortController) {
        abortController.abort()
        currentTypingInstance?.destroy()
        currentTypingInstance = null
        removeTypingIndicator()
        setSendLoading(false)
        return
    }

    if (currentTypingInstance) return

    const message = input.value.trim()
    if (!message) return

    addMessage(message, true)
    input.value = ''
    setSendLoading(true)

    abortController = new AbortController()
    addTypingIndicator()

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message }),
            signal: abortController.signal
        })

        if (!response.ok) throw new Error()

        const data = await response.json()
        removeTypingIndicator()

        const aiWrapper = document.createElement('div')
        aiWrapper.className = 'mb-3 text-start'
        aiWrapper.innerHTML = `
            <div class="d-inline-block p-3 rounded-4 shadow-sm ai-message text-white" style="max-width:80%">
                <div class="fw-bold"><i class="fas fa-robot me-2"></i>Doctor AI</div>
                <div class="ai-content"></div>
            </div>
        `

        chatContainer.appendChild(aiWrapper)
        const contentDiv = aiWrapper.querySelector('.ai-content')
        const cleanHtml = renderMarkdown(data.response)

        typeMessage(contentDiv, cleanHtml, () => {
            setSendLoading(false)
            input.focus()
        })

    } catch (e) {
        removeTypingIndicator()
        setSendLoading(false)
        addMessage('Ulanishda xatolik. Iltimos, qayta urinib ko‘ring.')
    }
}

document.addEventListener('DOMContentLoaded', () => {
    sendButton.addEventListener('click', sendMessage)

    input.addEventListener('keydown', e => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            sendMessage()
        }
    })

    setInterval(() => location.reload(), 300000)
    input.focus()
})
